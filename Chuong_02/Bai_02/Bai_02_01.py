from pathlib import Path
import argparse
import shutil
import cv2
import numpy as np
import os

def average_filter(image, kernel_size=(5, 5)):
    return cv2.blur(image, kernel_size)


def gaussian_filter(image, kernel_size=(5, 5), sigma=1.5):
    return cv2.GaussianBlur(image, kernel_size, sigma)


def sharpen_image(image):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    return cv2.filter2D(image, -1, kernel)


def ensure_output_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def load_image(path: Path):
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Không tìm thấy ảnh đầu vào: {path}")
    return image


def main():
    base_dir = Path(__file__).resolve().parent
    default_input = base_dir.parent / "images" / "input.jpg"
    parser = argparse.ArgumentParser(description="Lọc tuyến tính: trung bình, Gaussian và làm sắc nét.")
    parser.add_argument("--input", type=Path, default=default_input, help="Đường dẫn ảnh đầu vào")
    parser.add_argument("--output_dir", type=Path, default=base_dir / "output" / "output02_01", help="Thư mục lưu kết quả")
    args = parser.parse_args()

    image = load_image(args.input)
    ensure_output_dir(args.output_dir)

    avg = average_filter(image)
    gauss = gaussian_filter(image)
    sharp = sharpen_image(image)

    shutil.copy2(args.input, args.output_dir / args.input.name)
    cv2.imwrite(str(args.output_dir / "average.jpg"), avg)
    cv2.imwrite(str(args.output_dir / "gaussian.jpg"), gauss)
    cv2.imwrite(str(args.output_dir / "sharpen.jpg"), sharp)

    print(f"Lưu ảnh gốc và các kết quả lọc tuyến tính trong: {args.output_dir}")


if __name__ == "__main__":
    main()
