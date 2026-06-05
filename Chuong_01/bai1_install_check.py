"""
Bài 1: Kiểm tra cài đặt OpenCV và Pillow
- Kiểm tra phiên bản OpenCV
- Kiểm tra phiên bản Pillow
- Kiểm tra NumPy (thư viện hỗ trợ)
"""

import cv2
import numpy as np
from PIL import Image

print("=" * 50)
print("KIỂM TRA CÀI ĐẶT THƯ VIỆN XỬ LÝ ẢNH")
print("=" * 50)

# Kiểm tra OpenCV
print(f"\n✅ OpenCV version: {cv2.__version__}")

# Kiểm tra NumPy
print(f"✅ NumPy version: {np.__version__}")

# Kiểm tra Pillow
import PIL
print(f"✅ Pillow version: {PIL.__version__}")

print("\n🎉 Tất cả thư viện đã được cài đặt thành công!")
print("=" * 50)
