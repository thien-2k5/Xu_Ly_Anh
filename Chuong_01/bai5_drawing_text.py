"""
Bài 5: Vẽ hình cơ bản và thêm văn bản
- Vẽ đường thẳng (line)
- Vẽ hình tròn (circle)
- Vẽ hình chữ nhật (rectangle)
- Vẽ ellipse
- Vẽ đa giác (polygon)
- Thêm văn bản vào hình ảnh
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# =====================================================
# Đường dẫn file
# =====================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(SCRIPT_DIR, "images", "sample_image.png")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("BÀI 5: VẼ HÌNH CƠ BẢN VÀ THÊM VĂN BẢN")
print("=" * 60)

# =====================================================
# PHẦN 1: Vẽ trên canvas trắng bằng OpenCV
# =====================================================
print("\n🎨 PHẦN 1: VẼ TRÊN CANVAS TRẮNG (OpenCV)")
print("-" * 40)

# Tạo canvas trắng 800x600
canvas = np.ones((600, 800, 3), dtype=np.uint8) * 255

# 1. Vẽ đường thẳng
# cv2.line(image, pt1, pt2, color_BGR, thickness)
cv2.line(canvas, (50, 50), (750, 50), (255, 0, 0), 3)           # Đường ngang xanh dương
cv2.line(canvas, (50, 50), (50, 550), (0, 128, 0), 3)           # Đường dọc xanh lá
cv2.line(canvas, (50, 550), (750, 50), (0, 0, 255), 2)          # Đường chéo đỏ
cv2.arrowedLine(canvas, (100, 100), (300, 100), (128, 0, 128), 2)  # Mũi tên
print("  ✅ Đã vẽ đường thẳng (line, arrowedLine)")

# 2. Vẽ hình chữ nhật
# cv2.rectangle(image, pt1, pt2, color_BGR, thickness) (-1 = tô đặc)
cv2.rectangle(canvas, (400, 80), (600, 200), (0, 165, 255), 3)  # Viền cam
cv2.rectangle(canvas, (620, 80), (780, 200), (147, 20, 255), -1)  # Tô đặc hồng
print("  ✅ Đã vẽ hình chữ nhật (rectangle)")

# 3. Vẽ hình tròn
# cv2.circle(image, center, radius, color_BGR, thickness)
cv2.circle(canvas, (200, 350), 80, (0, 200, 0), 3)              # Viền xanh lá
cv2.circle(canvas, (200, 350), 40, (0, 200, 0), -1)             # Tô đặc xanh lá
print("  ✅ Đã vẽ hình tròn (circle)")

# 4. Vẽ ellipse
# cv2.ellipse(image, center, axes, angle, startAngle, endAngle, color, thickness)
cv2.ellipse(canvas, (450, 350), (120, 60), 0, 0, 360, (200, 0, 0), 2)    # Ellipse đầy đủ
cv2.ellipse(canvas, (450, 350), (120, 60), 30, 0, 180, (0, 0, 200), 3)   # Nửa ellipse xoay
print("  ✅ Đã vẽ ellipse")

# 5. Vẽ đa giác (polygon)
# Hình tam giác
pts_triangle = np.array([[650, 280], [580, 420], [720, 420]], np.int32)
pts_triangle = pts_triangle.reshape((-1, 1, 2))
cv2.polylines(canvas, [pts_triangle], isClosed=True, color=(0, 128, 255), thickness=3)
print("  ✅ Đã vẽ đa giác (polygon)")

# Hình ngôi sao
def draw_star(img, center, size, color, thickness=2):
    """Vẽ ngôi sao 5 cánh"""
    angles = np.linspace(-90, 270, 6)[:-1]  # 5 đỉnh
    outer = np.array([(center[0] + size * np.cos(np.radians(a)),
                       center[1] + size * np.sin(np.radians(a))) for a in angles])
    inner_angles = angles + 36
    inner = np.array([(center[0] + size * 0.4 * np.cos(np.radians(a)),
                       center[1] + size * 0.4 * np.sin(np.radians(a))) for a in inner_angles])
    points = []
    for i in range(5):
        points.append(outer[i])
        points.append(inner[i])
    pts = np.array(points, np.int32).reshape((-1, 1, 2))
    cv2.polylines(img, [pts], isClosed=True, color=color, thickness=thickness)

draw_star(canvas, (150, 500), 50, (0, 215, 255), 2)
print("  ✅ Đã vẽ ngôi sao")

# 6. Thêm văn bản
# cv2.putText(image, text, org, fontFace, fontScale, color, thickness)
cv2.putText(canvas, "OpenCV Drawing Demo", (200, 550),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (50, 50, 50), 2)
cv2.putText(canvas, "Duong thang", (100, 85),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
cv2.putText(canvas, "Hinh chu nhat", (430, 230),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
cv2.putText(canvas, "Hinh tron", (160, 460),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
cv2.putText(canvas, "Ellipse", (420, 440),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
cv2.putText(canvas, "Tam giac", (625, 450),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
print("  ✅ Đã thêm văn bản")

cv2.imwrite(os.path.join(OUTPUT_DIR, "drawing_opencv_canvas.jpg"), canvas)
print("  💾 Đã lưu canvas OpenCV.")

# =====================================================
# PHẦN 2: Vẽ trên ảnh thật bằng OpenCV
# =====================================================
print("\n🖼️  PHẦN 2: VẼ TRÊN ẢNH THẬT (OpenCV)")
print("-" * 40)

img_cv = cv2.imread(INPUT_PATH)
h, w = img_cv.shape[:2]
img_draw = img_cv.copy()  # Tạo bản sao để vẽ

# Vẽ khung viền
cv2.rectangle(img_draw, (20, 20), (w - 20, h - 20), (0, 255, 255), 3)
print("  ✅ Vẽ khung viền")

# Vẽ đường chéo
cv2.line(img_draw, (0, 0), (w, h), (0, 0, 255), 2)
cv2.line(img_draw, (w, 0), (0, h), (0, 0, 255), 2)
print("  ✅ Vẽ đường chéo")

# Vẽ hình tròn ở trung tâm
center = (w // 2, h // 2)
cv2.circle(img_draw, center, 100, (0, 255, 0), 3)
cv2.circle(img_draw, center, 5, (0, 0, 255), -1)  # Tâm điểm
print("  ✅ Vẽ hình tròn tại trung tâm")

# Thêm text overlay
cv2.putText(img_draw, f"Size: {w}x{h}", (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
cv2.putText(img_draw, f"Size: {w}x{h}", (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 1)
print("  ✅ Thêm text overlay")

cv2.imwrite(os.path.join(OUTPUT_DIR, "drawing_on_image_opencv.jpg"), img_draw)
print("  💾 Đã lưu ảnh vẽ OpenCV.")

# =====================================================
# PHẦN 3: Vẽ bằng Pillow
# =====================================================
print("\n🎨 PHẦN 3: VẼ BẰNG PILLOW")
print("-" * 40)

# Tạo canvas trắng
canvas_pil = Image.new("RGB", (800, 600), (255, 255, 255))
draw = ImageDraw.Draw(canvas_pil)

# Vẽ đường thẳng
draw.line([(50, 50), (750, 50)], fill=(255, 0, 0), width=3)
draw.line([(50, 50), (50, 550)], fill=(0, 128, 0), width=3)
print("  ✅ [Pillow] Đã vẽ đường thẳng")

# Vẽ hình chữ nhật
draw.rectangle([(400, 80), (600, 200)], outline=(255, 165, 0), width=3)
draw.rectangle([(620, 80), (780, 200)], fill=(255, 20, 147))
print("  ✅ [Pillow] Đã vẽ hình chữ nhật")

# Vẽ hình tròn (bằng ellipse)
draw.ellipse([(120, 270), (280, 430)], outline=(0, 200, 0), width=3)
draw.ellipse([(160, 310), (240, 390)], fill=(0, 200, 0))
print("  ✅ [Pillow] Đã vẽ hình tròn")

# Vẽ ellipse
draw.ellipse([(330, 290), (570, 410)], outline=(200, 0, 0), width=2)
print("  ✅ [Pillow] Đã vẽ ellipse")

# Vẽ đa giác
draw.polygon([(650, 280), (580, 420), (720, 420)],
             outline=(255, 128, 0), width=3)
print("  ✅ [Pillow] Đã vẽ đa giác")

# Thêm văn bản (sử dụng font mặc định)
try:
    # Thử tìm font hệ thống
    font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
except (IOError, OSError):
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

draw.text((200, 500), "Pillow Drawing Demo", fill=(50, 50, 50), font=font_large)
draw.text((100, 85), "Duong thang", fill=(100, 100, 100), font=font_small)
draw.text((430, 210), "Hinh chu nhat", fill=(100, 100, 100), font=font_small)
draw.text((160, 440), "Hinh tron", fill=(100, 100, 100), font=font_small)
draw.text((410, 420), "Ellipse", fill=(100, 100, 100), font=font_small)
draw.text((620, 440), "Tam giac", fill=(100, 100, 100), font=font_small)
print("  ✅ [Pillow] Đã thêm văn bản")

canvas_pil.save(os.path.join(OUTPUT_DIR, "drawing_pillow_canvas.jpg"))
print("  💾 Đã lưu canvas Pillow.")

# =====================================================
# PHẦN 4: Vẽ trên ảnh thật bằng Pillow
# =====================================================
print("\n🖼️  PHẦN 4: VẼ TRÊN ẢNH THẬT (Pillow)")
print("-" * 40)

img_pil = Image.open(INPUT_PATH)
draw_pil = ImageDraw.Draw(img_pil)
pw, ph = img_pil.size

# Vẽ khung viền
draw_pil.rectangle([(20, 20), (pw - 20, ph - 20)],
                    outline=(255, 255, 0), width=3)
print("  ✅ Vẽ khung viền")

# Vẽ hình tròn tại trung tâm
cx, cy = pw // 2, ph // 2
r = 100
draw_pil.ellipse([(cx - r, cy - r), (cx + r, cy + r)],
                  outline=(0, 255, 0), width=3)
print("  ✅ Vẽ hình tròn tại trung tâm")

# Thêm watermark text
try:
    watermark_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
except (IOError, OSError):
    watermark_font = ImageFont.load_default()

draw_pil.text((30, 30), f"Size: {pw}x{ph}",
              fill=(255, 255, 255), font=watermark_font,
              stroke_width=2, stroke_fill=(0, 0, 0))
print("  ✅ Thêm watermark text")

img_pil.save(os.path.join(OUTPUT_DIR, "drawing_on_image_pillow.jpg"))
print("  💾 Đã lưu ảnh vẽ Pillow.")

# =====================================================
# PHẦN 5: Hiển thị kết quả
# =====================================================
print("\n🖼️  Hiển thị kết quả...")

# Tạo cửa sổ
cv2.namedWindow("OpenCV Canvas", cv2.WINDOW_NORMAL)
cv2.namedWindow("OpenCV Drawing on Image", cv2.WINDOW_NORMAL)

# Hiển thị ảnh
cv2.imshow("OpenCV Canvas", canvas)

cv2.imshow(
    "OpenCV Drawing on Image",
    cv2.resize(img_draw, (600, 450))
)

print("  ➡️  Đóng tất cả cửa sổ ảnh để thoát.")

while True:
    canvas_visible = cv2.getWindowProperty(
        "OpenCV Canvas",
        cv2.WND_PROP_VISIBLE
    )

    draw_visible = cv2.getWindowProperty(
        "OpenCV Drawing on Image",
        cv2.WND_PROP_VISIBLE
    )

    # Nếu cả 2 cửa sổ đều đã đóng
    if canvas_visible < 1 and draw_visible < 1:
        break

    cv2.waitKey(100)

cv2.destroyAllWindows()
cv2.waitKey(1)

# =====================================================
# Tổng kết
# =====================================================
print(f"""
📚 TỔNG KẾT CÁC HÀM VẼ:
{'='*50}
  OpenCV:
    cv2.line()         - Vẽ đường thẳng
    cv2.arrowedLine()  - Vẽ mũi tên
    cv2.rectangle()    - Vẽ hình chữ nhật
    cv2.circle()       - Vẽ hình tròn
    cv2.ellipse()      - Vẽ ellipse
    cv2.polylines()    - Vẽ đa giác
    cv2.putText()      - Thêm văn bản

  Pillow:
    draw.line()        - Vẽ đường thẳng
    draw.rectangle()   - Vẽ hình chữ nhật
    draw.ellipse()     - Vẽ hình tròn/ellipse
    draw.polygon()     - Vẽ đa giác
    draw.text()        - Thêm văn bản
""")

print("🎉 Hoàn thành Bài 5!")
print("=" * 60)
