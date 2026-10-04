# Chạy baseline bằng model thật

> **Đây là việc người dùng phải thực hiện. Phiên này chỉ kiểm chứng chế độ `mock`; chưa chạy model thật và không dùng API key.**

## Chuẩn bị

1. Cài môi trường dev: `pip install -e ".[dev]"`.
2. Cung cấp adapter runner thật qua `BENCH_REAL_RUNNER`. Adapter nhận đường dẫn task làm đối số, thực hiện agent trong một workspace cô lập, rồi trả mã thoát theo hợp đồng: `0` = grader pass (agent đúng), `1` = grader chạy nhưng không pass (agent sai), mã khác (`2+`, timeout, OOM, signal) = lỗi hạ tầng. `run_baseline.py` phân loại qua `classify_real_status()` để không gộp "agent dở" với "harness dở" thành một số. Adapter phải tự ghi chi phí/token nếu provider hỗ trợ; runner hiện lưu `cost_usd: null` khi adapter không cung cấp số liệu.
3. Export `MODEL`, `API_KEY`, `PROFILE` (khác `mock`) và `RUNS`. Không ghi API key vào file benchmark hay git.

## Lệnh

```bash
MODEL='provider/model' API_KEY="$YOUR_KEY" PROFILE=real RUNS=3 \
  BENCH_REAL_RUNNER=/duong/dan/adapter scripts/run_baseline.sh
```

Kết quả được ghi tại `benchmarks/baselines/<model>_<ngày>/results.json` và `report.md`. Tạo bản rút gọn dùng cho CI gate:

```bash
python scripts/make_baseline.py benchmarks/baselines/<model>_<ngày>/results.json
```

`baseline.json` chứa pass rate từng task, success rate tổng, vị trí CI (hiện đánh dấu `not_computed` để không bịa khoảng tin cậy), chi phí/task khi có, safety counters, git SHA, model và ngày. Mẫu định dạng nằm tại `benchmarks/baselines/baseline.json`.

## Đọc report và xử lý lỗi hạ tầng

`report.md` cho tổng số pass; xem `results.json` để phân biệt `failed` (agent/grader không pass) với `infra_error` (adapter/provider/tool không chạy được). Với `infra_error`, giữ lại stdout/stderr, kiểm tra API key, giới hạn rate, mạng và sandbox rồi chạy lại **chỉ sau khi nguyên nhân hạ tầng được xử lý**. Không gộp infra error thành thất bại chất lượng.

Chi phí tối thiểu phụ thuộc số lượt: **10 task × `RUNS`** lượt agent, chưa tính retry hoặc model phụ. Ví dụ `RUNS=3` là ít nhất 30 lượt; hãy đặt limit chi phí/token ở adapter/provider trước khi chạy.

## Kiểm thử không dùng model

```bash
MODEL=mock PROFILE=mock RUNS=1 scripts/run_baseline.sh
```

Mock áp oracle để kiểm đường ống kết quả, không phải đo năng lực model.
