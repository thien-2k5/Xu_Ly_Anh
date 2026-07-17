# Kịch bản thuyết trình FaceTrust

Thời lượng mục tiêu: **10-12 phút trình bày + phản biện**  
Deck: `docs/FaceTrust_Thuyet_Trinh.pptx`  
Hai slide cuối là phụ lục, chỉ mở khi giảng viên hỏi.

## 1. Chuẩn bị trước khi trình bày

1. Mở PowerShell tại thư mục dự án và chạy:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   .\start-web.ps1
   ```

2. Mở `http://127.0.0.1:8000` và kiểm tra trạng thái `ONLINE`.
3. Quét thử một ảnh để model được warm-up. Lần đầu có thể chậm vì phải nạp checkpoint.
4. Mở sẵn thư mục `data/demo-images` trong File Explorer.
5. Chuẩn bị hai ảnh: `001_barack-obama.jpg` (real) và `002_portrait-01.jpg` (fake).
6. Mở sẵn `reports/cross_dataset_results.md` để đối chiếu sau demo.
7. Bật Presenter View. Nội dung nói đã được nhúng vào Speaker Notes của PowerPoint.

## 2. Kịch bản chính

### Slide 1 - Giới thiệu (0:00-0:40)

**Lời nói**

> Kính thưa cô và các bạn, nhóm em xin trình bày FaceTrust, hệ thống kiểm định ảnh khuôn mặt và phát hiện dấu hiệu deepfake. Mục tiêu của nhóm không phải xác minh danh tính hay đưa ra kết luận pháp lý. Mục tiêu là xây dựng một pipeline có thể nhận ảnh, chạy model cục bộ, trả kết luận real, fake hoặc uncertain, đồng thời lưu bằng chứng đánh giá. Bài trình bày sẽ trả lời ba câu hỏi: hệ thống có chạy model thật không, kết quả được đo như thế nào, và model hiện đạt mức nào.

**Chuyển ý:** Trước hết, nhóm cần xác định đúng độ khó của bài toán.

### Slide 2 - Bài toán và domain shift (0:40-1:20)

**Lời nói**

> Deepfake khó không chỉ vì ảnh giả ngày càng đẹp. Mỗi công cụ tạo giả, danh tính, độ phân giải và phương pháp nén có thể tạo ra phân phối dữ liệu khác nhau. Một detector có thể đạt điểm cao trên dữ liệu cùng miền huấn luyện nhưng giảm mạnh với ảnh từ nguồn khác. Vì vậy câu hỏi nghiên cứu của nhóm là: một checkpoint đã huấn luyện có thể được tích hợp thành hệ thống tái lập và khái quát hóa đến đâu?

**Nhấn mạnh:** Same-dataset tốt không đồng nghĩa ảnh ngoài mạng cũng tốt.

### Slide 3 - Kiến trúc thật của hệ thống (1:20-2:00)

**Lời nói**

> Kiến trúc có bốn lớp. Trình duyệt nhận ảnh và hiển thị kết quả. FastAPI kiểm tra tệp, gọi pipeline và trả JSON. Lớp suy luận định vị khuôn mặt, crop về 224 nhân 224, sau đó chạy model chính và model phụ. Cuối cùng, bộ benchmark và script đánh giá sinh báo cáo JSON và Markdown. Điểm quan trọng là giao diện không tự đoán theo tên tệp; kết luận được trả từ backend sau khi checkpoint PyTorch chạy cục bộ.

**Chuyển ý:** Tiếp theo là toàn bộ đường đi của một ảnh.

### Slide 4 - Full pipeline (2:00-2:45)

**Lời nói**

> Một ảnh đi qua bảy bước: nhận ảnh, xác thực, định vị mặt, chuẩn hóa, suy luận, quyết định và trả kết quả. Hệ thống đọc nội dung ảnh thật để chặn tệp giả phần mở rộng. Nếu không tìm được khuôn mặt đủ rõ, hệ thống trả uncertain thay vì ép classifier đoán. Full-pipeline evaluation kiểm tra toàn bộ luồng này, không chỉ gọi thẳng model bằng ảnh đã crop sẵn.

**Nhấn mạnh:** Full pipeline bao gồm cả lỗi upload, giải mã và face detection.

### Slide 5 - Model và dữ liệu (2:45-3:35)

**Lời nói**

> Dự án có dữ liệu và trọng số AI thật. Model chính là MS-EffGCViT B0 công khai, được tác giả huấn luyện trên FaceForensics++. Nhóm không nhận công đã train checkpoint này từ đầu. Model phụ là EfficientNet-B0, chỉ hỗ trợ khi khuôn mặt nhỏ hơn 12 phần trăm diện tích ảnh. Repository lưu 2.384 frame DeepFake Facial, 200 frame Celeb-DF mẫu, 18 ảnh demo và hai checkpoint cục bộ. Đóng góp của nhóm là khảo sát, lựa chọn checkpoint, tích hợp, thiết kế ngưỡng, đánh giá, giao diện và tài liệu hóa.

**Nếu bị ngắt hỏi “có train không?”**

> Checkpoint đã được tác giả train thật. Phần nhóm thực hiện là tích hợp, hiệu chỉnh và đánh giá; nhóm không tuyên bố train model chính từ đầu.

### Slide 6 - Cách tính risk và margin (3:35-4:35)

**Lời nói**

> Chỉ số risk trên giao diện không phải xác suất dự đoán đúng. Gọi p là raw fake score của model chính. Nếu p nhỏ hơn 0,5 thì risk bằng p. Nếu p từ 0,5 trở lên, risk được ánh xạ từ 0,5 đến tối đa 0,8 để tránh tạo cảm giác chắc chắn tuyệt đối. Model phụ có nhánh riêng và risk cuối là giá trị lớn nhất của hai nhánh. Margin đo khoảng cách tương đối từ score đến ngưỡng đang kích hoạt. Với ảnh face-swap minh họa, p bằng 0,6465, score phụ bằng 0,4145, risk hiển thị là 58,8 trên 100 và margin là 29,3 phần trăm.

**Không được nói:** “58,8% xác suất ảnh là fake”.  
**Nên nói:** “Chỉ số rủi ro 58,8 trên thang 100; score chưa được calibration thành xác suất”.

### Slide 7 - Giao diện và bằng chứng (4:35-5:05)

**Lời nói**

> Workflow được rút về một thao tác: chọn ảnh, bấm kiểm định, chờ quét và đọc kết quả. Bên trái là ảnh đầu vào. Bên phải là label, risk, margin và các tín hiệu giải thích lấy từ evidence của chính lần suy luận đó. Nội dung giải thích thay đổi theo raw score, nhánh model, kích thước khuôn mặt và tín hiệu forensic, không dùng một câu cố định cho mọi ảnh.

### Slide 8 - Cross-dataset benchmark (5:05-6:10)

**Lời nói**

> Đây là benchmark chéo chính của dự án, gồm 400 frame: mỗi nguồn có 100 fake và 100 real. Khi tính strict, uncertain được xem là sai. Accuracy và balanced accuracy đều đạt 56,25 phần trăm. Fake recall đạt 76 phần trăm, nghĩa là bắt đúng 76 phần trăm số ảnh fake. Real recall chỉ đạt 36,5 phần trăm, nghĩa là hệ thống cảnh báo nhầm nhiều ảnh thật. Vì vậy model phù hợp cho đồ án và bước sàng lọc có người kiểm tra lại, nhưng chưa đủ cho pháp chứng độc lập.

**Không được nói:** “Model có accuracy 76%”.  
**Nói đúng:** “Fake recall là 76%; balanced accuracy là 56,25%”.

### Slide 9 - Ma trận nhầm lẫn (6:10-6:55)

**Lời nói**

> Ma trận nhầm lẫn cho thấy điều mà một con số accuracy có thể che khuất. Trong 200 ảnh fake, hệ thống bắt đúng 152 ảnh, bỏ sót 41 và có 7 ảnh uncertain. Trong 200 ảnh thật, chỉ 73 ảnh được giữ đúng, 122 ảnh bị cảnh báo nhầm và 5 ảnh uncertain. Như vậy detector đang thiên về lớp fake. Ưu tiên cải thiện tiếp theo là giảm false positive và đánh giá theo video hoặc identity để tránh rò rỉ dữ liệu.

### Slide 10 - Demo khác benchmark (6:55-7:40)

**Lời nói**

> Nhóm đánh giá full pipeline trên 18 ca demo tuyển chọn. API success và face detection đều đạt 100 phần trăm; median latency sau warm-up khoảng 524 mili giây. Kết quả 18 trên 18 chỉ chứng minh các ca demo chạy end-to-end. Nó không được dùng để công bố accuracy tổng quát. Benchmark tổng quát hóa sử dụng 400 frame độc lập với bộ demo. Nhóm tách hai lớp bằng chứng để không đánh tráo demo đẹp với hiệu năng thật.

### Slide 11 - Quy trình làm việc với AI (7:40-8:25)

**Lời nói**

> AI được dùng như trợ lý kỹ thuật qua nhiều vòng: làm rõ yêu cầu, khảo sát dataset và checkpoint, lập kế hoạch, triển khai, đánh giá, sửa lỗi và tài liệu hóa. Nhưng AI không phải ground truth và không được tự tạo số liệu. Mỗi claim phải truy được tới file, mã nguồn, test hoặc output đo được. Khi một nhánh như Gemini không cải thiện ổn định và tạo phụ thuộc ngoài, nhóm loại khỏi pipeline chính.

**Chuyển ý:** Sau đây nhóm chứng minh luồng chạy thực tế trong khoảng 90 giây.

### Slide 12 - Demo trực tiếp (8:25-9:55)

**Thao tác và lời nói**

1. Mở trình duyệt, chỉ vào trạng thái `ONLINE`.

   > Backend đang hoạt động và model đã được nạp cục bộ.

2. Chọn `001_barack-obama.jpg`, bấm **Bắt đầu kiểm định**.

   > Đây là ảnh số lẻ, ground truth của bộ demo là real. Hệ thống vẫn chạy model; quy ước số chỉ giúp nhóm chọn đúng ảnh khi trình bày.

3. Khi có kết quả, chỉ vào label, risk, margin và 1-2 tín hiệu giải thích.

   > Risk là chỉ số ánh xạ từ raw score, không phải xác suất. Margin cho biết score cách ngưỡng quyết định bao xa.

4. Đổi sang `002_portrait-01.jpg`, quét lại.

   > Đây là frame khuôn mặt bị thao túng từ nguồn được ghi trong `SOURCES.md`. Kết luận vừa hiển thị đến từ lần suy luận mới.

5. Mở `reports/cross_dataset_results.md`.

   > Hai ảnh vừa rồi chỉ là demo. Kết quả đánh giá tổng quát phải đọc từ benchmark 400 frame này.

**Nếu quét lần đầu lâu:**

> Đây là cold start do tiến trình phải nạp checkpoint. Sau warm-up, median đo được khoảng 524 mili giây trên môi trường thử nghiệm của nhóm.

### Slide 13 - Kết quả và giới hạn (9:55-10:40)

**Lời nói**

> Kết quả quan trọng nhất là nhóm đã xây dựng được hệ thống có thể tái chạy và tự kiểm chứng: web và API end-to-end, hai checkpoint thật, công thức score công khai, 400 frame benchmark chéo và báo cáo lưu được. Tuy nhiên model còn yếu ngoài miền huấn luyện, đặc biệt là false positive cao. Hướng phát triển là split theo video hoặc identity, fine-tune đa nguồn, calibration xác suất và mở rộng từ ảnh sang video.

### Slide 14 - Kết luận (10:40-11:05)

**Lời nói**

> Nhóm không che giấu giới hạn của model. FaceTrust hiện phù hợp với mục tiêu đồ án và hỗ trợ sàng lọc, chưa phù hợp để đưa ra kết luận pháp lý. Mọi bằng chứng có thể kiểm tra lại: dữ liệu trong `data/benchmarks`, trọng số trong `models`, kết quả từng ảnh trong `reports`. Nhóm xin cảm ơn cô và các bạn, nhóm sẵn sàng trả lời câu hỏi.

## 3. Phản biện nhanh

### Câu 1 - Dự án có dataset và train AI thật không? Dataset ở đâu?

> Có dataset và checkpoint thật. Dữ liệu benchmark nằm trong `data/benchmarks`; ảnh demo nằm trong `data/demo-images`; trọng số nằm trong `models`. Checkpoint chính MS-EffGCViT B0 đã được tác giả mô hình huấn luyện trên FaceForensics++. Nhóm không nhận công train từ đầu; nhóm tích hợp, hiệu chỉnh ngưỡng, đánh giá cross-dataset và xây full pipeline.

### Câu 2 - Làm sao biết kết quả không được trả theo cảm tính hoặc theo tên file?

> API đọc pixel của ảnh, định vị và crop khuôn mặt, nạp checkpoint `safetensors`, chạy forward pass rồi mới trả JSON. Đổi nội dung pixel làm raw score thay đổi. Script benchmark chạy từng ảnh, lưu kết quả và tính lại TP, FP, TN, FN trong `reports/cross_dataset_results.json`. Tên file chỉ giúp chọn demo; pipeline không dùng tên file để phân loại.

### Câu 3 - Đánh giá mức độ model như thế nào?

> Trên benchmark chéo 400 frame, balanced accuracy là 56,25%, fake recall 76% và real recall 36,5%. Model bắt fake tương đối tốt nhưng báo nhầm ảnh thật nhiều. Vì vậy mức hiện tại là prototype học thuật và hỗ trợ sàng lọc có người xác minh, không phải hệ thống pháp chứng.

### Câu 4 - Evaluation, benchmark và full pipeline khác nhau ra sao?

> Evaluation là quá trình và protocol đo: cách chia dữ liệu, chạy suy luận, đặt ngưỡng và tính metric. Benchmark là bộ dữ liệu cộng protocol cố định để có thể chạy lại và so sánh. Full-pipeline evaluation kiểm tra cả upload, validation, face detection, crop, model, score mapping, API và UI. Model-only evaluation chỉ kiểm tra classifier trên đầu vào đã chuẩn hóa.

### Câu 5 - Vì sao model card gần 98% nhưng dự án chỉ 56,25%?

> Số gần 98% là kết quả same-dataset trong điều kiện của tác giả trên FaceForensics++. Dự án đo cross-dataset, dùng nguồn, cách nén, crop và full pipeline khác nên chịu domain shift. Hai con số trả lời hai câu hỏi khác nhau và không được so trực tiếp như cùng một thí nghiệm.

### Câu 6 - Cách tính metric

- `Accuracy = (TP + TN) / N`.
- `Fake recall = TP / (TP + FN)`.
- `Real recall = TN / (TN + FP)`.
- `Balanced accuracy = (Fake recall + Real recall) / 2`.
- Trong strict accuracy, `uncertain` được tính là sai nhưng vẫn báo riêng.

### Câu 7 - Vì sao risk không bằng raw score?

> Raw score chưa được calibration thành xác suất. Giao diện ánh xạ score để hạn chế cảm giác chắc chắn quá mức: dưới ngưỡng 0,5 thì giữ nguyên; từ 0,5 trở lên thì nén về vùng 0,5 đến 0,8. Risk cuối lấy nhánh cảnh báo mạnh hơn. Công thức này là quy tắc trình bày có thể kiểm tra trong mã, không phải xác suất thống kê.

## 4. Các câu cần tránh

- Không nói: “Nhóm đã train MS-EffGCViT từ đầu”.
- Không nói: “Độ chính xác của model là 76%”.
- Không nói: “Risk 60 nghĩa là xác suất fake 60%”.
- Không dùng kết quả 18/18 demo để suy ra model tổng quát tốt.
- Không khẳng định FaceTrust có thể xác minh danh tính hoặc kết luận pháp lý.
- Không che con số 56,25%; giải thích bằng domain shift và ma trận nhầm lẫn.

## 5. Câu chốt khi hết giờ

> FaceTrust chứng minh được một pipeline AI thật, tái lập và có bằng chứng đo lường. Nhóm đồng thời chỉ ra trung thực giới hạn cross-dataset của model và hướng cải thiện tiếp theo. Em xin kết thúc phần trình bày.
