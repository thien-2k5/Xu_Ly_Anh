from pathlib import Path
import argparse
import shutil
import cv2
import os

def ensure_output_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def load_image(path: Path):
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Không tìm thấy ảnh đầu vào: {path}")
    return image


def bilateral_filter(image, diameter=9, sigma_color=75, sigma_space=75):
    return cv2.bilateralFilter(image, diameter, sigma_color, sigma_space)


def main():
    base_dir = Path(__file__).resolve().parent
    default_input = base_dir.parent / "images" / "input.jpg"
    parser = argparse.ArgumentParser(description="Áp dụng lọc bilateral giữ cạnh.")
    parser.add_argument("--input", type=Path, default=default_input, help="Đường dẫn ảnh đầu vào")
    parser.add_argument("--output_dir", type=Path, default=base_dir / "output" / "output03_04", help="Thư mục lưu kết quả")
    args = parser.parse_args()

    image = load_image(args.input)
    ensure_output_dir(args.output_dir)

    bilateral = bilateral_filter(image)

    shutil.copy2(args.input, args.output_dir / args.input.name)
    cv2.imwrite(str(args.output_dir / "bilateral.jpg"), bilateral)

    print(f"Lưu ảnh gốc và kết quả bilateral filter trong: {args.output_dir}")


if __name__ == "__main__":
    main()
