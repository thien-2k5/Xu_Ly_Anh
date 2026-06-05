"""
Bài 4: Cắt xén và thay đổi kích thước hình ảnh
- Cắt một vùng hình ảnh (crop)
- Thay đổi kích thước theo tỷ lệ (scale)
- Thay đổi kích thước theo kích thước cố định (resize)
"""

import cv2
import numpy as np
from PIL import Image
import os

# =====================================================
# Đường dẫn file
# =====================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(SCRIPT_DIR, "images", "sample_image.png")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("BÀI 4: CẮT XÉN VÀ THAY ĐỔI KÍCH THƯỚC HÌNH ẢNH")
print("=" * 60)

# Đọc ảnh
img_cv = cv2.imread(INPUT_PATH)
img_pil = Image.open(INPUT_PATH)

if img_cv is None:
    print(f"❌ Không thể đọc file: {INPUT_PATH}")
    exit(1)

h, w = img_cv.shape[:2]
print(f"\n📖 Ảnh gốc: {w}x{h} pixels")

# =====================================================
# PHẦN 1: Cắt xén hình ảnh (Crop)
# =====================================================
print("\n✂️  PHẦN 1: CẮT XÉN HÌNH ẢNH")
print("-" * 40)

# --- OpenCV Crop ---
# Cắt vùng trung tâm (50% ảnh)
crop_x1 = w // 4
crop_y1 = h // 4
crop_x2 = 3 * w // 4
crop_y2 = 3 * h // 4

# OpenCV sử dụng [y1:y2, x1:x2] (numpy array slicing)
img_crop_cv = img_cv[crop_y1:crop_y2, crop_x1:crop_x2]
print(f"\n  [OpenCV] Cắt vùng trung tâm:")
print(f"    Tọa độ: ({crop_x1}, {crop_y1}) -> ({crop_x2}, {crop_y2})")
print(f"    Kích thước mới: {img_crop_cv.shape[1]}x{img_crop_cv.shape[0]} pixels")

cv2.imwrite(os.path.join(OUTPUT_DIR, "crop_center_opencv.jpg"), img_crop_cv)
print(f"    ✅ Đã lưu.")

# --- Pillow Crop ---
# Cắt vùng góc trên bên trái (1/4 ảnh)
crop_box_topleft = (0, 0, w // 2, h // 2)
img_crop_pil_tl = img_pil.crop(crop_box_topleft)
print(f"\n  [Pillow] Cắt góc trên-trái:")
print(f"    Box: {crop_box_topleft}")
print(f"    Kích thước mới: {img_crop_pil_tl.size}")

img_crop_pil_tl.save(os.path.join(OUTPUT_DIR, "crop_topleft_pillow.jpg"))
print(f"    ✅ Đã lưu.")

# Cắt vùng góc dưới bên phải
crop_box_bottomright = (w // 2, h // 2, w, h)
img_crop_pil_br = img_pil.crop(crop_box_bottomright)
print(f"\n  [Pillow] Cắt góc dưới-phải:")
print(f"    Box: {crop_box_bottomright}")
print(f"    Kích thước mới: {img_crop_pil_br.size}")

img_crop_pil_br.save(os.path.join(OUTPUT_DIR, "crop_bottomright_pillow.jpg"))
print(f"    ✅ Đã lưu.")

# =====================================================
# PHẦN 2: Thay đổi kích thước theo tỷ lệ (Scale)
# =====================================================
print("\n📏 PHẦN 2: THAY ĐỔI KÍCH THƯỚC THEO TỶ LỆ")
print("-" * 40)

# --- OpenCV Resize theo tỷ lệ ---
scales = [0.25, 0.5, 1.5, 2.0]
for scale in scales:
    new_w_scaled = int(w * scale)
    new_h_scaled = int(h * scale)
    img_scaled = cv2.resize(img_cv, (new_w_scaled, new_h_scaled),
                            interpolation=cv2.INTER_LINEAR)
    filename = f"scale_{scale}x_opencv.jpg"
    cv2.imwrite(os.path.join(OUTPUT_DIR, filename), img_scaled)
    print(f"  [OpenCV] Tỷ lệ {scale}x: {w}x{h} -> {new_w_scaled}x{new_h_scaled}  ✅")

# --- Pillow Resize theo tỷ lệ ---
print()
for scale in [0.25, 0.5]:
    new_size = (int(img_pil.width * scale), int(img_pil.height * scale))
    # Pillow sử dụng Image.Resampling.LANCZOS cho chất lượng tốt nhất
    img_scaled_pil = img_pil.resize(new_size, Image.Resampling.LANCZOS)
    filename = f"scale_{scale}x_pillow.jpg"
    img_scaled_pil.save(os.path.join(OUTPUT_DIR, filename))
    print(f"  [Pillow] Tỷ lệ {scale}x: {img_pil.size} -> {new_size}  ✅")

# =====================================================
# PHẦN 3: Thay đổi kích thước cố định (Fixed Resize)
# =====================================================
print(f"\n📐 PHẦN 3: THAY ĐỔI KÍCH THƯỚC CỐ ĐỊNH")
print("-" * 40)

fixed_sizes = [(640, 480), (320, 240), (1920, 1080), (100, 100)]

for target_w, target_h in fixed_sizes:
    # OpenCV resize
    img_fixed_cv = cv2.resize(img_cv, (target_w, target_h),
                               interpolation=cv2.INTER_AREA)
    filename_cv = f"fixed_{target_w}x{target_h}_opencv.jpg"
    cv2.imwrite(os.path.join(OUTPUT_DIR, filename_cv), img_fixed_cv)

    # Pillow resize
    img_fixed_pil = img_pil.resize((target_w, target_h), Image.Resampling.LANCZOS)
    filename_pil = f"fixed_{target_w}x{target_h}_pillow.jpg"
    img_fixed_pil.save(os.path.join(OUTPUT_DIR, filename_pil))

    print(f"  {w}x{h} -> {target_w}x{target_h}  ✅ (OpenCV + Pillow)")

# =====================================================
# PHẦN 4: So sánh các phương pháp nội suy (Interpolation)
# =====================================================
print(f"\n🔍 PHẦN 4: SO SÁNH PHƯƠNG PHÁP NỘI SUY")
print("-" * 40)

target = (300, 300)
interpolation_methods = {
    "NEAREST": cv2.INTER_NEAREST,
    "LINEAR": cv2.INTER_LINEAR,
    "AREA": cv2.INTER_AREA,
    "CUBIC": cv2.INTER_CUBIC,
    "LANCZOS4": cv2.INTER_LANCZOS4,
}

for name, method in interpolation_methods.items():
    img_interp = cv2.resize(img_cv, target, interpolation=method)
    filename = f"interp_{name.lower()}.jpg"
    cv2.imwrite(os.path.join(OUTPUT_DIR, filename), img_interp)
    print(f"  Phương pháp {name:<10}: {target[0]}x{target[1]}  ✅")

print("""
📚 GIẢI THÍCH PHƯƠNG PHÁP NỘI SUY:
  - NEAREST:  Nhanh nhất, chất lượng thấp (lấy pixel gần nhất)
  - LINEAR:   Cân bằng tốc độ/chất lượng (mặc định OpenCV)
  - AREA:     Tốt nhất khi thu nhỏ ảnh
  - CUBIC:    Chất lượng cao hơn LINEAR (dùng 4x4 pixels)
  - LANCZOS4: Chất lượng cao nhất (dùng 8x8 pixels)
""")

# =====================================================
# Hiển thị kết quả so sánh
# =====================================================
print("🖼️  Hiển thị so sánh...")
display_size = (300, 300)

img_original_small = cv2.resize(img_cv, display_size)
img_crop_display = cv2.resize(img_crop_cv, display_size)
img_scale_display = cv2.resize(
    cv2.resize(img_cv, (w // 4, h // 4)), display_size
)
img_fixed_display = cv2.resize(
    cv2.resize(img_cv, (100, 100)), display_size
)

# Thêm nhãn
font = cv2.FONT_HERSHEY_SIMPLEX
for img, label in [
    (img_original_small, "Original"),
    (img_crop_display, "Cropped"),
    (img_scale_display, "Scale 0.25x"),
    (img_fixed_display, "100x100"),
]:
    cv2.putText(img, label, (10, 25), font, 0.7, (0, 255, 0), 2)

grid = np.hstack([img_original_small, img_crop_display,
                   img_scale_display, img_fixed_display])
cv2.imwrite(os.path.join(OUTPUT_DIR, "crop_resize_comparison.jpg"), grid)

cv2.namedWindow(
    "So sanh Cat xen va Thay doi kich thuoc",
    cv2.WINDOW_NORMAL
)

cv2.imshow(
    "So sanh Cat xen va Thay doi kich thuoc",
    grid
)

print("  ➡️  Đóng cửa sổ ảnh để thoát.")

while True:
    # Nếu cửa sổ bị đóng thì thoát
    if cv2.getWindowProperty(
        "So sanh Cat xen va Thay doi kich thuoc",
        cv2.WND_PROP_VISIBLE
    ) < 1:
        break

    cv2.waitKey(100)

cv2.destroyAllWindows()
cv2.waitKey(1)

print("\n🎉 Hoàn thành Bài 4!")
print("=" * 60)
