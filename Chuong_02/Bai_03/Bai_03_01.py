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


def sobel_edges(gray):
    grad_x = cv2.Sobel(gray, cv2.CV_16S, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_16S, 0, 1, ksize=3)
    abs_x = cv2.convertScaleAbs(grad_x)
    abs_y = cv2.convertScaleAbs(grad_y)
    magnitude = cv2.convertScaleAbs(cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0))
    return abs_x, abs_y, magnitude


def main():
    base_dir = Path(__file__).resolve().parent
    default_input = base_dir.parent / "images" / "input.jpg"
    parser = argparse.ArgumentParser(description="Phát hiện cạnh với Sobel.")
    parser.add_argument("--input", type=Path, default=default_input, help="Đường dẫn ảnh đầu vào")
    parser.add_argument("--output_dir", type=Path, default=base_dir / "output" / "output03_01", help="Thư mục lưu kết quả")
    args = parser.parse_args()

    image = load_image(args.input)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ensure_output_dir(args.output_dir)

    sobel_x, sobel_y, sobel_mag = sobel_edges(gray)

    shutil.copy2(args.input, args.output_dir / args.input.name)
    cv2.imwrite(str(args.output_dir / "sobel_x.jpg"), sobel_x)
    cv2.imwrite(str(args.output_dir / "sobel_y.jpg"), sobel_y)
    cv2.imwrite(str(args.output_dir / "sobel_magnitude.jpg"), sobel_mag)

    print(f"Lưu kết quả Sobel trong: {args.output_dir}")


if __name__ == "__main__":
    main()
