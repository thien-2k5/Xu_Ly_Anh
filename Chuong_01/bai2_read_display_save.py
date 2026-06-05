"""
Bài 2: Đọc, hiển thị và lưu hình ảnh
- Đọc hình ảnh từ file bằng OpenCV và Pillow
- Hiển thị hình ảnh lên màn hình
- Lưu hình ảnh với định dạng khác (PNG -> JPG, BMP)
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
print("BÀI 2: ĐỌC, HIỂN THỊ VÀ LƯU HÌNH ẢNH")
print("=" * 60)

# =====================================================
# PHẦN 1: Đọc ảnh bằng OpenCV
# =====================================================
print("\n📖 [OpenCV] Đọc hình ảnh...")
img_cv = cv2.imread(INPUT_PATH)

if img_cv is None:
    print(f"❌ Không thể đọc file: {INPUT_PATH}")
    exit(1)

print(f"  ✅ Đọc thành công!")
print(f"  📐 Kích thước (Height x Width x Channels): {img_cv.shape}")
print(f"  📊 Kiểu dữ liệu: {img_cv.dtype}")
print(f"  💾 Kích thước trong bộ nhớ: {img_cv.nbytes / 1024:.1f} KB")

# =====================================================
# PHẦN 2: Đọc ảnh bằng Pillow
# =====================================================
print("\n📖 [Pillow] Đọc hình ảnh...")
img_pil = Image.open(INPUT_PATH)

print(f"  ✅ Đọc thành công!")
print(f"  📐 Kích thước (Width x Height): {img_pil.size}")
print(f"  🎨 Chế độ màu: {img_pil.mode}")
print(f"  📁 Định dạng: {img_pil.format}")

# =====================================================
# PHẦN 3: Hiển thị ảnh bằng OpenCV
# =====================================================
print("\n🖼️  [OpenCV] Hiển thị hình ảnh...")
print("  ➡️  Đóng cửa sổ ảnh để tiếp tục.")

cv2.namedWindow("OpenCV - Hinh anh goc", cv2.WINDOW_NORMAL)
cv2.imshow("OpenCV - Hinh anh goc", img_cv)

while True:
    # Kiểm tra cửa sổ còn mở hay không
    if cv2.getWindowProperty(
        "OpenCV - Hinh anh goc",
        cv2.WND_PROP_VISIBLE
    ) < 1:
        break

    cv2.waitKey(100)

cv2.destroyAllWindows()
cv2.waitKey(1)

print("  ✅ Đã đóng cửa sổ hiển thị OpenCV.")

# =====================================================
# PHẦN 4: Hiển thị ảnh bằng Pillow
# =====================================================
print("\n🖼️  [Pillow] Hiển thị hình ảnh...")
print("  ➡️  Đóng cửa sổ Preview để tiếp tục.")

img_pil.show()
print("  ✅ Đã mở ảnh bằng trình xem mặc định.")

# =====================================================
# PHẦN 5: Lưu ảnh với định dạng khác
# =====================================================
print("\n💾 Lưu hình ảnh với các định dạng khác nhau...")

# Lưu bằng OpenCV - PNG sang JPG
output_jpg_cv = os.path.join(OUTPUT_DIR, "output_opencv.jpg")
cv2.imwrite(output_jpg_cv, img_cv, [cv2.IMWRITE_JPEG_QUALITY, 95])
print(f"  ✅ [OpenCV] Đã lưu: {output_jpg_cv}")

# Lưu bằng OpenCV - PNG sang BMP
output_bmp_cv = os.path.join(OUTPUT_DIR, "output_opencv.bmp")
cv2.imwrite(output_bmp_cv, img_cv)
print(f"  ✅ [OpenCV] Đã lưu: {output_bmp_cv}")

# Lưu bằng Pillow - PNG sang JPG
output_jpg_pil = os.path.join(OUTPUT_DIR, "output_pillow.jpg")
img_pil_rgb = img_pil.convert("RGB")  # Đảm bảo chế độ RGB cho JPG
img_pil_rgb.save(output_jpg_pil, "JPEG", quality=95)
print(f"  ✅ [Pillow] Đã lưu: {output_jpg_pil}")

# Lưu bằng Pillow - PNG sang BMP
output_bmp_pil = os.path.join(OUTPUT_DIR, "output_pillow.bmp")
img_pil_rgb.save(output_bmp_pil, "BMP")
print(f"  ✅ [Pillow] Đã lưu: {output_bmp_pil}")

# Lưu bằng Pillow - PNG sang TIFF
output_tiff_pil = os.path.join(OUTPUT_DIR, "output_pillow.tiff")
img_pil_rgb.save(output_tiff_pil, "TIFF")
print(f"  ✅ [Pillow] Đã lưu: {output_tiff_pil}")

# So sánh kích thước file
print("\n📊 So sánh kích thước file:")
print(f"  {'Định dạng':<30} {'Kích thước':>12}")
print(f"  {'-'*42}")
original_size = os.path.getsize(INPUT_PATH)
print(f"  {'Gốc (PNG)':<30} {original_size/1024:>10.1f} KB")

for f in [output_jpg_cv, output_bmp_cv, output_jpg_pil, output_bmp_pil, output_tiff_pil]:
    size = os.path.getsize(f)
    name = os.path.basename(f)
    print(f"  {name:<30} {size/1024:>10.1f} KB")

print("\n🎉 Hoàn thành Bài 2!")
print("=" * 60)
