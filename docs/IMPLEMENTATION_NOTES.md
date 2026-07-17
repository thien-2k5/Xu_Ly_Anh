# Ghi Chú Triển Khai FaceTrust

## 1. Kiến Trúc Tổng Quan

FaceTrust là web app FastAPI + vanilla HTML/CSS/JS.

Luồng chính:

```text
Browser upload
  -> POST /api/detect
  -> validate image
  -> temporary file
  -> primary face-crop detector
  -> small-face auxiliary detector
  -> presentation result
  -> UI render
```

## 2. Thành Phần Chính

| Thành phần | File | Vai trò |
| --- | --- | --- |
| FastAPI app | `src/facetrust_benchmark/web.py` | Route `/`, `/api/health`, `/api/detect` |
| Upload pipeline | `src/facetrust_benchmark/detector_storage.py` | Đọc ảnh, validate, gọi detector, tạo response |
| Detector | `src/facetrust_benchmark/deepfake_detector.py` | Chạy model local và tạo evidence |
| Frontend | `src/facetrust_benchmark/static/` | Giao diện upload, scan animation, kết quả |
| Demo/evaluation images | `data/demo-images` | Ảnh chọn thủ công khi demo và benchmark |
| Evaluation script | `scripts/evaluate_system.py` | Chạy benchmark qua API và sinh report |

## 3. API

### `GET /api/health`

Kiểm tra backend sẵn sàng.

Trả về:

- `status`
- `service`
- `version`
- `task`
- `engine`

### `POST /api/detect`

Input:

- `image`: file ảnh

Output chính:

- `label`: `real`, `fake` hoặc `uncertain`
- `face_detected`: có phát hiện mặt hay không
- `scan_id`: mã hash ngắn của ảnh
- `presentation.fake_risk_index`
- `presentation.decision_margin`
- `presentation.signals`

## 4. Presentation Score

Raw score của model chưa phải xác suất đã hiệu chuẩn. Vì vậy UI tách score kỹ thuật
trong phần giải thích khỏi hai chỉ số trình bày.

Backend chuyển raw output thành:

- `fake_risk_index`: chỉ số rủi ro fake sau khi nén biên độ.
- `decision_margin`: khoảng cách chuẩn hóa từ raw score tới ngưỡng đã kích hoạt.

`decision_margin` không phải xác suất kết luận đúng.

## 5. Bộ Ảnh Demo

Thư mục: `data/demo-images`

Quy ước:


Tên file chỉ gồm số thứ tự và tên người/chủ thể. Ví dụ:

```text
001_barack-obama.jpg
002_donald-trump.jpg
003_donald-trump.jpg
```

Web không hiển thị sẵn ảnh demo. Khi trình bày, mở file picker và chọn ảnh từ thư mục này.

## 6. Chạy Benchmark

```powershell
$env:PYTHONPATH='D:\Xampp\htdocs\anti-deepfake-face\src'
.\.venv\Scripts\python.exe scripts\evaluate_system.py
```

Report sinh ra:

```text
reports/evaluation_results.md
reports/evaluation_results.json
```

## 7. Chạy Web

```powershell
.\start-web.ps1
```

Mở:

```text
http://127.0.0.1:8000
```

## 8. Kiểm Thử

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests scripts
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.\.venv\Scripts\python.exe -m pytest -q
```

## 9. Lưu Ý Bảo Mật

- Không commit `.env`.
- Không hard-code khóa API hoặc thông tin nhạy cảm.
- Không lưu ảnh upload của người dùng ra thư mục public.
- Ảnh upload chỉ được ghi tạm trong `TemporaryDirectory` rồi tự xóa sau khi xử lý.
