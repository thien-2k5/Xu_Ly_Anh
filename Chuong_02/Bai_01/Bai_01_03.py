from pathlib import Path
import argparse
import shutil
import cv2
import os

def negate_image(image):
    return cv2.bitwise_not(image)


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
    parser = argparse.ArgumentParser(description="Tạo ảnh âm bản.")
    parser.add_argument("--input", type=Path, default=default_input, help="Đường dẫn ảnh đầu vào")
    parser.add_argument("--output_dir", type=Path, default=base_dir / "output" / "output01_03", help="Thư mục lưu kết quả")
    args = parser.parse_args()

    image = load_image(args.input)
    ensure_output_dir(args.output_dir)

    negative = negate_image(image)

    shutil.copy2(args.input, args.output_dir / args.input.name)
    cv2.imwrite(str(args.output_dir / "negative.jpg"), negative)

    print(f"Lưu ảnh gốc và ảnh âm bản trong: {args.output_dir}")


if __name__ == "__main__":
    main()
