# Quy Trình Làm Việc Với AI

Tài liệu này tóm tắt cách nhóm sử dụng AI trong quá trình xây dựng FaceTrust, từ lập kế hoạch đến triển khai và đánh giá hệ thống.

## 1. Vai Trò Của AI Trong Dự Án

AI được dùng như một trợ lý kỹ thuật để hỗ trợ:

- Phân tích yêu cầu.
- Đọc và tái cấu trúc codebase.
- Đề xuất hướng model và benchmark.
- Viết script xử lý dữ liệu và đánh giá.
- Thiết kế lại giao diện theo hướng chuyên nghiệp.
- Kiểm thử API, UI và pipeline.
- Viết tài liệu kỹ thuật.

Con người vẫn giữ vai trò quyết định cuối cùng: chọn hướng đồ án, kiểm tra kết quả, quyết định nội dung trình bày và xác nhận các thay đổi.

## 2. Quy Trình Thực Hiện

### Giai Đoạn 1: Xác Định Lại Bài Toán

Ban đầu hệ thống đi theo hướng bảo vệ ảnh khỏi swapface. Sau khi trao đổi lại với giảng viên, yêu cầu được điều chỉnh thành: nhận diện ảnh sau khi bị deepfake hoặc ảnh có khả năng bị tạo/chỉnh sửa.

AI hỗ trợ:

- Tách lại scope bài toán.
- Loại bỏ các tính năng không còn phù hợp.
- Chuyển trọng tâm từ protection workflow sang detection workflow.

Kết quả:

- Giao diện chỉ còn luồng kiểm tra ảnh.
- Backend tập trung vào endpoint `/api/detect`.

### Giai Đoạn 2: Khảo Sát Dữ Liệu Và Model

Nhóm thử nhiều hướng dữ liệu và model khác nhau, gồm dataset deepfake, model local, detector từ Hugging Face và các tập ảnh kiểm thử thủ công.

AI hỗ trợ:

- Hướng dẫn cấu hình Kaggle/dataset.
- Tổ chức lại thư mục dữ liệu.
- Viết và chạy các lệnh benchmark.
- Nhận diện vấn đề overfit hoặc cross-dataset performance thấp.

Kết quả:

- Giữ lại local detector làm engine chính.
- Bổ sung detector phụ cho khuôn mặt nhỏ và evidence đa nhánh.
- Tạo bộ ảnh `data/demo-images` để trình bày và stress test.

### Giai Đoạn 3: Tái Cấu Trúc Giao Diện

Giao diện được chuyển từ dạng nhiều panel rối sang một verification console đơn giản.

AI hỗ trợ:

- Áp dụng guideline UI/UX cho sản phẩm bảo mật.
- Bỏ các phần không cần thiết như case demo hiển thị trực tiếp trên web.
- Thêm scan animation, risk index, biên quyết định và phần giải thích.
- Giữ giao diện gọn, dễ dùng, không quá giống trang demo tạm.

Kết quả:

- Người dùng chọn ảnh, bấm quét và nhận kết luận.
- Không còn danh sách ảnh mẫu hiển thị trên giao diện.

### Giai Đoạn 4: Tăng Khả Năng Giải Thích

Hệ thống đối chiếu score của detector chính và detector phụ, kích thước vùng mặt
và các chỉ số chất lượng ảnh. Gemini từng được khảo sát nhưng đã loại khỏi bản
triển khai vì không cải thiện phép đo deepfake một cách ổn định và làm tăng độ trễ.

### Giai Đoạn 5: Benchmark Và Full Pipeline Evaluation

Sau khi hệ thống chạy ổn, nhóm bổ sung script đánh giá tự động.

AI hỗ trợ:

- Viết `scripts/evaluate_system.py`.
- Tự động post từng ảnh qua API `/api/detect`.
- Tính accuracy, precision, recall, F1-score, confusion matrix.
- Đo API success rate, face detection rate và latency.
- Sinh báo cáo Markdown/JSON trong `reports/`.

Kết quả:

- Có báo cáo thực nghiệm thay vì chỉ mô tả lý thuyết.
- Kết quả hiện tại chỉ ra detector local còn yếu với ảnh AI-generated public-figure, đây là cơ sở cho phần hạn chế và hướng phát triển.

## 3. Cách AI Được Dùng Một Cách Có Kiểm Soát

Trong dự án, AI không được dùng để tự ý tạo kết quả benchmark giả. Các số liệu trong `reports/evaluation_results.md` được sinh từ script chạy thật trên bộ ảnh hiện có.

Các nguyên tắc kiểm soát:

- Không hard-code nhãn trả về trong UI.
- Không đưa API key vào git.
- Có `.gitignore` cho `.env`, `.venv`, cache và output tạm.
- Chạy test sau khi sửa code.
- Ghi rõ giới hạn model trong tài liệu đánh giá.
- Tách ảnh demo khỏi giao diện để tránh cảm giác hệ thống chỉ chạy case mẫu.

## 4. Artifact Do AI Hỗ Trợ Tạo

Các artifact chính:

- `src/facetrust_benchmark/web.py`: FastAPI app.
- `src/facetrust_benchmark/detector_storage.py`: upload pipeline và presentation score.
- `src/facetrust_benchmark/deepfake_detector.py`: detector backend.
- `src/facetrust_benchmark/static/`: giao diện web.
- `scripts/evaluate_system.py`: benchmark/full pipeline evaluation.
- `reports/evaluation_results.md`: báo cáo kết quả chạy thật.
- `docs/EVALUATION.md`: phương pháp đánh giá.
- `docs/IMPLEMENTATION_NOTES.md`: ghi chú triển khai hệ thống.

## 5. Tóm Tắt Cho Báo Cáo

Có thể trình bày ngắn gọn:

> Trong quá trình phát triển, nhóm sử dụng AI như một trợ lý kỹ thuật để phân tích yêu cầu, tái cấu trúc code, đề xuất pipeline, hỗ trợ viết script benchmark, kiểm thử và tạo tài liệu. Các quyết định chính như đổi hướng bài toán, chọn luồng giao diện, giữ local detector làm engine chính và ghi nhận giới hạn model đều do nhóm kiểm tra và xác nhận. Kết quả cuối cùng là một web app có pipeline nhận diện ảnh, có script đánh giá tự động và có báo cáo thực nghiệm minh bạch.
