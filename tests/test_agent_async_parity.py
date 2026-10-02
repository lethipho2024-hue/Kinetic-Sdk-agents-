"""Executable semantic parity contract for sync and async agent loops."""

from __future__ import annotations

from typing import Any

import pytest

from kinetic_sdk.agent.agent import Agent
from kinetic_sdk.agent.async_agent import AsyncAgent
from kinetic_sdk.agent.async_classifier import AsyncTaskClassifier
from kinetic_sdk.agent.budget import RunBudget
from kinetic_sdk.agent.classifier import Classification, TaskClassifier, TaskComplexity
from kinetic_sdk.agent.modes import AgentMode
from kinetic_sdk.context.manager import SimpleTruncateContextManager
from kinetic_sdk.event.bus import EventBus
from kinetic_sdk.llm.client import LLMResponse, ToolCall
from kinetic_sdk.security.policy import AllowListPolicy, PermissivePolicy
from kinetic_sdk.testing import MockLLMClient, MockTool, text_response
from kinetic_sdk.testing.async_mocks import AsyncMockLLMClient, AsyncMockTool
from kinetic_sdk.tool.base import ToolResult

pytestmark = pytest.mark.asyncio


def _call(name: str, arguments: dict[str, Any], call_id: str = "call") -> LLMResponse:
    return LLMResponse(tool_calls=[ToolCall(id=call_id, name=name, arguments=arguments)])


def _normalise(agent: Agent | AsyncAgent, events: list[str], calls: list[dict[str, Any]], results: list[ToolResult], final: str) -> dict[str, Any]:
    """Keep only public, deterministic observables shared by both loops."""
    return {
        "final": final,
        "events": events,
        "tool_calls": calls,
        "tool_results": [
            {"output": result.output, "error": result.error, "metadata": result.metadata,
             "failure_category": result.failure_category, "artifacts": result.artifacts}
            for result in results
        ],
        "messages": agent.state.messages,
        "usage": agent.usage.snapshot().to_dict(),
    }


class _FlashClassifier(TaskClassifier):
    def classify(self, task: str) -> Classification:
        return Classification(TaskComplexity.SIMPLE, AgentMode.FLASH, 1.0)


class _AsyncFlashClassifier(AsyncTaskClassifier):
    async def classify(self, task: str) -> Classification:
        return Classification(TaskComplexity.SIMPLE, AgentMode.FLASH, 1.0)


def _scenario(name: str) -> tuple[list[LLMResponse], dict[str, Any], ToolResult | str]:
    if name == "text":
        return [text_response("done")], {}, "ok"
    if name == "one_tool":
        return [_call("work", {"n": 1}), text_response("done")], {}, "ok"
    if name == "many_tools":
        return [
            LLMResponse(tool_calls=[
                ToolCall(id="a", name="work", arguments={"n": 1}),
                ToolCall(id="b", name="work", arguments={"n": 2}),
            ]),
            text_response("done"),
        ], {}, "ok"
    if name == "tool_error":
        return [_call("work", {}), text_response("recovered")], {}, ToolResult(error="boom")
    if name == "permission_denied":
        return [_call("work", {}), text_response("denied")], {"permission_policy": AllowListPolicy()}, "ok"
    if name == "run_budget":
        return [_call("work", {}), text_response("unreachable")], {"run_budget": RunBudget(max_llm_calls=1)}, "ok"
    if name == "max_iterations":
        return [_call("work", {}), _call("work", {})], {"max_iterations": 1}, "ok"
    if name == "structured_success":
        return [text_response('{"answer": "yes"}')], {"output_schema": {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}}, "ok"
    if name == "structured_failure":
        return [text_response("not json"), text_response("still not json"), text_response("no")], {"output_schema": {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}, "structured_retries": 2}, "ok"
    if name == "context_compaction":
        return [_call("work", {"n": 1}), _call("work", {"n": 2}), text_response("done")], {"context_manager": SimpleTruncateContextManager(keep_last_tool_results=1, safety_threshold=0.01), "model_context_limit": 1}, "x" * 200
    if name == "flash_escalation":
        return [_call("work", {}), text_response("escalated")], {"classifier": _FlashClassifier()}, ToolResult(error="boom")
    raise AssertionError(name)


@pytest.mark.parametrize("name", ["text", "one_tool", "many_tools", "tool_error", "permission_denied", "run_budget", "max_iterations", "structured_success", "structured_failure", "context_compaction", "flash_escalation"])
async def test_sync_and_async_agents_have_normalised_parity(name: str) -> None:
    script, options, tool_value = _scenario(name)
    async_script, async_options, async_tool_value = _scenario(name)
    sync_events: list[str] = []
    async_events: list[str] = []
    sync_bus, async_bus = EventBus(), EventBus()
    sync_bus.subscribe("*", lambda event: sync_events.append(event.type))
    async_bus.subscribe("*", lambda event: async_events.append(event.type))
    sync_results: list[ToolResult] = []
    async_results: list[ToolResult] = []

    def sync_handler(**params: Any) -> ToolResult | str:
        result = tool_value if isinstance(tool_value, ToolResult) else ToolResult(output=tool_value)
        sync_results.append(result)
        return result

    async def async_handler(**params: Any) -> ToolResult | str:
        result = async_tool_value if isinstance(async_tool_value, ToolResult) else ToolResult(output=async_tool_value)
        async_results.append(result)
        return result

    agent_options = {key: value for key, value in options.items() if key not in {"output_schema", "structured_retries"}}
    agent_options.setdefault("permission_policy", PermissivePolicy())
    sync_tool = MockTool("work", handler=sync_handler)
    async_tool = AsyncMockTool("work", handler=async_handler)
    sync = Agent(llm=MockLLMClient(script), tools=[sync_tool], event_bus=sync_bus, **agent_options)
    async_agent_options = {key: value for key, value in async_options.items() if key not in {"output_schema", "structured_retries"}}
    async_agent_options.setdefault("permission_policy", PermissivePolicy())
    if name == "flash_escalation":
        async_agent_options["classifier"] = _AsyncFlashClassifier()
    asynchronous = AsyncAgent(llm=AsyncMockLLMClient(async_script), tools=[async_tool], event_bus=async_bus, **async_agent_options)
    run_options = {key: value for key, value in options.items() if key in {"output_schema", "structured_retries"}}
    async_run_options = {key: value for key, value in async_options.items() if key in {"output_schema", "structured_retries"}}
    sync_final = sync.run("parity", **run_options)
    async_final = await asynchronous.run("parity", **async_run_options)

    assert _normalise(sync, sync_events, sync_tool.calls, sync_results, sync_final) == _normalise(asynchronous, async_events, async_tool.calls, async_results, async_final)


async def test_sync_and_async_cancel_have_normalised_parity() -> None:
    # A response callback cancels after the turn has started; both loops check
    # cancellation before executing the requested tool and preserve valid history.
    sync_events: list[str] = []
    async_events: list[str] = []
    sync_bus, async_bus = EventBus(), EventBus()
    sync_bus.subscribe("*", lambda event: sync_events.append(event.type))
    async_bus.subscribe("*", lambda event: async_events.append(event.type))
    sync_holder: dict[str, Agent] = {}
    async_holder: dict[str, AsyncAgent] = {}

    def cancel_sync(*_: Any) -> LLMResponse:
        sync_holder["agent"].cancel()
        return _call("work", {})

    async def cancel_async(*_: Any) -> LLMResponse:
        async_holder["agent"].cancel()
        return _call("work", {})

    sync_tool, async_tool = MockTool("work", result="unused"), AsyncMockTool("work", result="unused")
    sync = Agent(llm=MockLLMClient([cancel_sync]), tools=[sync_tool], event_bus=sync_bus, permission_policy=PermissivePolicy())
    asynchronous = AsyncAgent(llm=AsyncMockLLMClient([cancel_async]), tools=[async_tool], event_bus=async_bus, permission_policy=PermissivePolicy())
    sync_holder["agent"], async_holder["agent"] = sync, asynchronous
    sync_final, async_final = sync.run("cancel"), await asynchronous.run("cancel")

    assert _normalise(sync, sync_events, sync_tool.calls, [], sync_final) == _normalise(asynchronous, async_events, async_tool.calls, [], async_final)
