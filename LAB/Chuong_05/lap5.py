"""
================================================================
BÀI TẬP: Nhận diện khuôn mặt thời gian thực với MTCNN + FaceNet
================================================================
Pipeline:
    Webcam (OpenCV) -> Phát hiện khuôn mặt (MTCNN)
                     -> Trích xuất đặc trưng - embedding (FaceNet)
                     -> So sánh cosine similarity với khuôn mặt đã biết
                     -> similarity > 0.7  => "Matched"
                        similarity <= 0.7 => "Unknown"
 
Thư viện cần cài:
    pip install facenet-pytorch opencv-python torch torchvision numpy pillow
 
Cách dùng:
    1. Tạo thư mục "known_faces/" cùng cấp với file này.
    2. Bỏ vào đó các ảnh chân dung rõ mặt, mỗi người 1 ảnh,
       đặt tên file = tên người, ví dụ: an.jpg, binh.png ...
    3. Chạy: python realtime_face_recognition.py
    4. Nhấn "q" để thoát chương trình.
================================================================
"""
 
import os
import cv2
import torch
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
 
# ---------------------------------------------------------------
# 1. CẤU HÌNH CHUNG
# ---------------------------------------------------------------
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
KNOWN_DIR = "known_faces"          # thư mục chứa ảnh mẫu của người cần nhận diện
SIMILARITY_THRESHOLD = 0.7         # ngưỡng so sánh theo yêu cầu đề bài
MIN_FACE_PROB = 0.90                # độ tin cậy tối thiểu để MTCNN chấp nhận là khuôn mặt
 
print(f"[INFO] Thiết bị đang dùng: {DEVICE}")
 
# ---------------------------------------------------------------
# 2. KHỞI TẠO MÔ HÌNH
# ---------------------------------------------------------------
# MTCNN: dùng để PHÁT HIỆN khuôn mặt (trả về toạ độ box + ảnh mặt đã align sẵn 160x160)
mtcnn = MTCNN(keep_all=True, device=DEVICE)
 
# FaceNet (InceptionResnetV1 pretrained trên VGGFace2): dùng để TRÍCH XUẤT embedding 512 chiều
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(DEVICE)
 
 
# ---------------------------------------------------------------
# 3. CÁC HÀM TIỆN ÍCH
# ---------------------------------------------------------------
def get_embedding_from_tensor(face_tensor: torch.Tensor) -> np.ndarray:
    """Đưa 1 ảnh khuôn mặt (tensor 3x160x160, đã được MTCNN chuẩn hoá) qua FaceNet
    để lấy ra vector đặc trưng (embedding) 512 chiều."""
    with torch.no_grad():
        embedding = resnet(face_tensor.unsqueeze(0).to(DEVICE))
    return embedding.cpu().numpy()[0]
 
 
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Tính độ tương đồng cosine giữa 2 vector embedding."""
    a_norm = a / (np.linalg.norm(a) + 1e-10)
    b_norm = b / (np.linalg.norm(b) + 1e-10)
    return float(np.dot(a_norm, b_norm))
 
 
def load_known_faces() -> dict:
    """Đọc toàn bộ ảnh trong thư mục known_faces/, phát hiện khuôn mặt bằng MTCNN,
    trích xuất embedding bằng FaceNet, và lưu vào dict {tên: embedding}."""
    known_embeddings = {}
 
    if not os.path.isdir(KNOWN_DIR):
        os.makedirs(KNOWN_DIR, exist_ok=True)
        print(f"[WARN] Chưa có thư mục '{KNOWN_DIR}/'. Đã tự tạo. "
              f"Hãy bỏ ảnh chân dung vào đó rồi chạy lại.")
        return known_embeddings
 
    for filename in os.listdir(KNOWN_DIR):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
 
        name = os.path.splitext(filename)[0]
        path = os.path.join(KNOWN_DIR, filename)
 
        img = Image.open(path).convert("RGB")
        face_tensors = mtcnn(img)  # phát hiện + align + chuẩn hoá khuôn mặt
 
        if face_tensors is None:
            print(f"[WARN] Không phát hiện khuôn mặt nào trong ảnh mẫu: {filename}")
            continue
 
        # nếu ảnh có nhiều mặt, chỉ lấy mặt đầu tiên làm đại diện cho người đó
        face_tensor = face_tensors[0] if face_tensors.dim() == 4 else face_tensors
 
        embedding = get_embedding_from_tensor(face_tensor)
        known_embeddings[name] = embedding
        print(f"[INFO] Đã nạp khuôn mặt mẫu của: '{name}'")
 
    return known_embeddings
 
 
# ---------------------------------------------------------------
# 4. VÒNG LẶP CHÍNH: ĐỌC WEBCAM + NHẬN DIỆN THỜI GIAN THỰC
# ---------------------------------------------------------------
def main():
    known_faces = load_known_faces()
 
    cap = cv2.VideoCapture(0)  # 0 = webcam mặc định
    if not cap.isOpened():
        print("[ERROR] Không thể mở webcam. Kiểm tra lại thiết bị camera.")
        return
 
    print("[INFO] Nhấn phím 'q' để thoát chương trình.")
 
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Không đọc được khung hình từ webcam.")
            break
 
        # OpenCV đọc ảnh theo BGR, cần đổi sang RGB rồi sang PIL cho MTCNN
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_frame)
 
        # Bước 1: phát hiện khuôn mặt -> lấy toạ độ box để vẽ lên khung hình
        boxes, probs = mtcnn.detect(pil_img)
 
        # Bước 2: lấy luôn ảnh mặt đã crop + align sẵn (160x160) để đưa vào FaceNet
        face_tensors = mtcnn(pil_img)
 
        if boxes is not None:
            for i, box in enumerate(boxes):
                # bỏ qua nếu độ tin cậy phát hiện khuôn mặt quá thấp
                if probs[i] is None or probs[i] < MIN_FACE_PROB:
                    continue
 
                x1, y1, x2, y2 = [int(v) for v in box]
 
                label = "Unknown"
                color = (0, 0, 255)   # đỏ = Unknown
                best_score = 0.0
                best_name = None
 
                if face_tensors is not None and len(known_faces) > 0:
                    face_tensor = face_tensors[i]
                    embedding = get_embedding_from_tensor(face_tensor)
 
                    # Bước 3: so sánh với từng khuôn mặt đã biết bằng cosine similarity
                    for name, known_embedding in known_faces.items():
                        score = cosine_similarity(embedding, known_embedding)
                        if score > best_score:
                            best_score = score
                            best_name = name
 
                    # Bước 4: áp dụng điều kiện so sánh theo đề bài
                    if best_score > SIMILARITY_THRESHOLD:
                        label = f"Matched: {best_name} ({best_score:.2f})"
                        color = (0, 255, 0)   # xanh lá = Matched
                    else:
                        label = f"Unknown ({best_score:.2f})"
 
                # Vẽ khung và nhãn lên khung hình webcam
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, max(y1 - 10, 0)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
 
        cv2.imshow("Nhan dien khuon mat - MTCNN + FaceNet", frame)
 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
 
    cap.release()
    cv2.destroyAllWindows()
 
 
if __name__ == "__main__":
    main()