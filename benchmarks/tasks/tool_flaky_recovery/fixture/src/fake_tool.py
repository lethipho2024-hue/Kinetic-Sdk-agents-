from src.retry import TemporaryError

class FlakyTool:
    def __init__(self): self.calls = 0
    def call(self):
        self.calls += 1
        if self.calls == 1: raise TemporaryError("temporary")
        return "ok"
