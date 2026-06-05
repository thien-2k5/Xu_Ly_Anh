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


def compare_filters(image):
    average = cv2.blur(image, (5, 5))
    gaussian = cv2.GaussianBlur(image, (5, 5), 1.5)
    sharpen = cv2.filter2D(image, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32))
    return average, gaussian, sharpen


def main():
    base_dir = Path(__file__).resolve().parent
    default_input = base_dir.parent / "images" / "input.jpg"
    parser = argparse.ArgumentParser(description="So sánh các bộ lọc trung bình, Gaussian và làm sắc nét.")
    parser.add_argument("--input", type=Path, default=default_input, help="Đường dẫn ảnh đầu vào")
    parser.add_argument("--output_dir", type=Path, default=base_dir / "output" / "output02_03", help="Thư mục lưu kết quả")
    args = parser.parse_args()

    image = load_image(args.input)
    ensure_output_dir(args.output_dir)

    average, gaussian, sharpen = compare_filters(image)

    shutil.copy2(args.input, args.output_dir / args.input.name)
    cv2.imwrite(str(args.output_dir / "compare_average.jpg"), average)
    cv2.imwrite(str(args.output_dir / "compare_gaussian.jpg"), gaussian)
    cv2.imwrite(str(args.output_dir / "compare_sharpen.jpg"), sharpen)

    print(f"Lưu ảnh gốc và các kết quả so sánh bộ lọc trong: {args.output_dir}")


if __name__ == "__main__":
    main()
