from pathlib import Path
import argparse
import shutil
import cv2
import numpy as np
import os

def ensure_output_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def load_image(path: Path):
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Không tìm thấy ảnh đầu vào: {path}")
    return image


def prewitt_edges(gray):
    kernel_x = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]], dtype=np.float32)
    kernel_y = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=np.float32)
    grad_x = cv2.filter2D(gray, -1, kernel_x)
    grad_y = cv2.filter2D(gray, -1, kernel_y)
    magnitude = cv2.convertScaleAbs(cv2.addWeighted(grad_x, 0.5, grad_y, 0.5, 0))
    return grad_x, grad_y, magnitude


def main():
    base_dir = Path(__file__).resolve().parent
    default_input = base_dir.parent / "images" / "input.jpg"
    parser = argparse.ArgumentParser(description="Phát hiện cạnh với Prewitt.")
    parser.add_argument("--input", type=Path, default=default_input, help="Đường dẫn ảnh đầu vào")
    parser.add_argument("--output_dir", type=Path, default=base_dir / "output" / "output03_02", help="Thư mục lưu kết quả")
    args = parser.parse_args()

    image = load_image(args.input)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ensure_output_dir(args.output_dir)

    prewitt_x, prewitt_y, prewitt_mag = prewitt_edges(gray)

    shutil.copy2(args.input, args.output_dir / args.input.name)
    cv2.imwrite(str(args.output_dir / "prewitt_x.jpg"), prewitt_x)
    cv2.imwrite(str(args.output_dir / "prewitt_y.jpg"), prewitt_y)
    cv2.imwrite(str(args.output_dir / "prewitt_magnitude.jpg"), prewitt_mag)

    print(f"Lưu kết quả Prewitt trong: {args.output_dir}")


if __name__ == "__main__":
    main()
