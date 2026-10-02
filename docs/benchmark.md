# Kinetic benchmark

Bộ benchmark filesystem nằm tại `benchmarks/tasks/`. Mỗi task có `task.json`, `fixture/`, `hidden_tests/` và `solution.patch`. Agent chỉ được thấy các file khai báo trong `agent_workspace_files`; hidden tests là dữ liệu grader, không được mount vào workspace agent.

`kpi_sdk.bench.harness` kiểm oracle bằng cách copy fixture, áp patch và chạy pytest cùng hidden tests. Mỗi fixture chưa áp oracle phải thất bại, còn fixture đã áp oracle phải xanh.

Hiện có 10 task, bao gồm đổi tên đa tệp, recovery test biên, tìm lỗi long-context (40 module), retry tool, prompt injection/canary, feature ba tệp, và task docs/typing không có public test.
