# Storyboard PowerPoint

Tài liệu này dùng để làm slide nhanh. Đề xuất 12 slide, đủ cho phần trình bày 8-12 phút.

## Slide 1. Tiêu Đề

Tiêu đề:

```text
FaceTrust
Hệ thống kiểm định ảnh real/fake bằng AI
```

Nội dung phụ:

- Tên nhóm.
- Lớp/môn học.
- Giảng viên hướng dẫn.

Hình nên dùng:

- Logo chữ `FT` hoặc screenshot giao diện chính.

Lời nói:

> Nhóm em xây dựng FaceTrust, một web app hỗ trợ kiểm tra ảnh khuôn mặt và đưa ra kết luận real/fake kèm các tín hiệu giải thích.

## Slide 2. Bối Cảnh Và Vấn Đề

Bullet:

- Deepfake và ảnh AI-generated ngày càng phổ biến.
- Ảnh giả có thể gây hiểu nhầm, lừa đảo hoặc ảnh hưởng uy tín cá nhân.
- Người dùng cần công cụ kiểm tra nhanh ảnh nghi ngờ.
- Bài toán: phân loại ảnh khuôn mặt thành real hoặc fake.

Hình nên dùng:

- Ảnh minh họa real/fake trong `data/demo-images`.

Lời nói:

> Vấn đề nhóm tập trung không phải xác minh danh tính, mà là hỗ trợ nhận diện ảnh có dấu hiệu giả mạo hoặc tạo bởi AI.

## Slide 3. Mục Tiêu Đề Tài

Bullet:

- Xây dựng web app upload và kiểm tra ảnh.
- Tạo pipeline xử lý ảnh end-to-end.
- Tích hợp local detector.
- Hiển thị kết luận, risk score, confidence và lý do.
- Có benchmark đánh giá model và full pipeline.
- Ghi nhận giới hạn và hướng phát triển.

Hình nên dùng:

- Sơ đồ 5 bước: Upload -> Validate -> Detect -> Score -> Result.

## Slide 4. Kiến Trúc Tổng Quan

Bullet:

- Frontend: HTML/CSS/JavaScript.
- Backend: FastAPI.
- Detector: model chính trên crop khuôn mặt.
- Auxiliary: model phụ cho khuôn mặt nhỏ.
- Evaluation: script benchmark tự động.

Sơ đồ:

```text
User -> Browser -> FastAPI -> Face crop -> Primary + Auxiliary -> Response -> UI
```

Hình nên dùng:

- Vẽ sơ đồ architecture bằng PowerPoint SmartArt hoặc shapes.

Lời nói:

> Hệ thống được thiết kế theo hướng đơn giản: frontend gửi ảnh lên backend, backend chạy detector và trả response JSON để UI render kết quả.

## Slide 5. Luồng Xử Lý Ảnh

Bullet:

1. Người dùng chọn ảnh.
2. Frontend gửi ảnh tới `/api/detect`.
3. Backend validate định dạng và dung lượng.
4. Ảnh được xử lý trong thư mục tạm.
5. Detector dự đoán real/fake.
6. Backend tạo risk score và signals.
7. UI hiển thị kết quả.

Hình nên dùng:

- Sequence diagram hoặc timeline ngang.

Lời nói:

> Điểm quan trọng là benchmark cũng đi qua endpoint này, nên đánh giá được pipeline thực tế chứ không chỉ gọi model riêng.

## Slide 6. Giao Diện Hệ Thống

Bullet:

- Giao diện dạng verification console.
- Không hiển thị sẵn ảnh demo trên web.
- Người dùng chọn ảnh từ máy.
- Có scan animation trong lúc xử lý.
- Kết quả gồm kết luận, risk score, confidence và tín hiệu giải thích.

Hình nên dùng:

- Screenshot màn hình ban đầu.
- Screenshot kết quả sau khi scan.

Lời nói:

> Giao diện được tối giản để người dùng tập trung vào hành động chính: chọn ảnh và quét.

## Slide 7. API Và Response

Bullet:

- `GET /api/health`: kiểm tra backend.
- `POST /api/detect`: upload ảnh và nhận kết quả.
- Response gồm: `label`, `face_detected`, `scan_id`, `presentation`, `review`.
- `presentation.signals` dùng để giải thích kết quả.

Ví dụ response rút gọn:

```json
{
  "label": "real",
  "face_detected": true,
  "presentation": {
    "fake_risk_index": 0.192,
    "decision_margin": 0.616
  }
}
```

Lời nói:

> UI không tự đoán kết quả, mà render theo response từ backend.

## Slide 8. Bộ Ảnh Demo Và Evaluation

Bullet:

- Thư mục: `data/demo-images`.
- 18 ảnh demo; benchmark độc lập nằm trong `data/benchmarks`.
- Số lẻ là real.
- Số chẵn là fake / AI-generated / deepfake.
- Nguồn ảnh công khai được ghi trong `SOURCES.md`.

Hình nên dùng:

- Screenshot File Explorer thư mục `data/demo-images`.
- Một vài ảnh ví dụ: `001_barack-obama.jpg`, `002_donald-trump.jpg`.

Lời nói:

> Bộ ảnh không hiển thị sẵn trên web; khi demo sẽ chọn trực tiếp ảnh từ thư mục để mô phỏng thao tác người dùng thật.

## Slide 9. Benchmark Và Metric

Bullet:

- Script: `scripts/evaluate_system.py`.
- Chạy từng ảnh qua API `/api/detect`.
- Tính accuracy, precision, recall, F1.
- Tạo confusion matrix.
- Đo API success rate, face detection rate và latency.

Hình nên dùng:

- Screenshot `reports/evaluation_results.md`.
- Bảng metric.

Lời nói:

> Nhóm đánh giá cả model-level và pipeline-level để biết hệ thống chạy được đến đâu và model còn yếu ở đâu.

## Slide 10. Kết Quả Thực Nghiệm

Bullet: dùng bảng mới nhất trong `reports/cross_dataset_results.md`, gồm strict
accuracy, balanced accuracy, fake recall, real recall và uncertain rate.

Nhận xét:

- Pipeline chạy ổn định.
- Model local còn yếu với ảnh AI-generated public-figure.
- Kết quả này được dùng để đề xuất hướng cải thiện.

Lời nói:

> Điểm mạnh là pipeline chạy ổn định. Điểm cần cải thiện là model chưa nhận diện tốt nhóm ảnh fake ngoài domain train.

## Slide 11. Quy Trình Làm Việc Với AI

Bullet:

- AI hỗ trợ phân tích yêu cầu.
- AI hỗ trợ tái cấu trúc code và UI.
- AI hỗ trợ tích hợp và kiểm tra các checkpoint cục bộ.
- AI hỗ trợ viết benchmark script.
- AI hỗ trợ viết tài liệu kỹ thuật.
- Nhóm kiểm tra, chạy thử và xác nhận kết quả.

Hình nên dùng:

- Timeline: Requirement -> Design -> Implementation -> Testing -> Documentation.

Lời nói:

> AI được dùng như trợ lý kỹ thuật, không thay thế việc kiểm tra và ra quyết định của nhóm.

## Slide 12. Kết Luận Và Hướng Phát Triển

Bullet:

Kết luận:

- Đã xây dựng được web app kiểm định ảnh real/fake.
- Có pipeline end-to-end.
- Có UI, API, detector đa nhánh và evidence giải thích.
- Có benchmark và tài liệu đánh giá.

Hướng phát triển:

- Mở rộng dataset.
- Fine-tune model trên nhiều domain.
- Thêm cross-dataset test.
- Hiệu chuẩn confidence.
- Mở rộng sang video hoặc dashboard lịch sử.

Lời nói:

> Bản hiện tại hoàn thành mục tiêu xây dựng pipeline và đánh giá thực nghiệm. Hướng tiếp theo là nâng chất lượng model bằng dữ liệu đa nguồn và benchmark lớn hơn.

## Slide Dự Phòng 1. Demo Script

Các bước demo:

1. Mở web `http://127.0.0.1:8000`.
2. Chọn ảnh trong `data/demo-images`.
3. Bấm **Quét ảnh**.
4. Quan sát scan animation.
5. Giải thích kết luận, risk index, decision margin và signals.
6. Mở `reports/evaluation_results.md` để cho thấy benchmark.

## Slide Dự Phòng 2. Hạn Chế Kỹ Thuật

Bullet:

- Model chưa tốt với ảnh AI-generated public-figure.
- Bộ evaluation còn nhỏ.
- Chưa xử lý video.
- Hai detector cục bộ vẫn có giới hạn ngoài miền huấn luyện.
- Cần fine-tune và cross-dataset benchmark.

Lời nói:

> Nhóm ghi nhận rõ giới hạn để thể hiện đánh giá khách quan và có hướng phát triển tiếp theo.
