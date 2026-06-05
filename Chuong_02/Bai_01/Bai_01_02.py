from pathlib import Path
import argparse
import shutil
import cv2
import os

def change_contrast(image, alpha):
    return cv2.convertScaleAbs(image, alpha=alpha, beta=0)


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
    parser = argparse.ArgumentParser(description="Thay đổi độ tương phản ảnh.")
    parser.add_argument("--input", type=Path, default=default_input, help="Đường dẫn ảnh đầu vào")
    parser.add_argument("--alpha", type=float, default=1.3, help="Hệ số nhân để tăng/giảm tương phản")
    parser.add_argument("--output_dir", type=Path, default=base_dir / "output" / "output01_02", help="Thư mục lưu kết quả")
    args = parser.parse_args()

    image = load_image(args.input)
    ensure_output_dir(args.output_dir)

    higher = change_contrast(image, args.alpha)
    lower = change_contrast(image, 1.0 / args.alpha)

    shutil.copy2(args.input, args.output_dir / args.input.name)
    cv2.imwrite(str(args.output_dir / f"contrast_{args.alpha:.2f}.jpg"), higher)
    cv2.imwrite(str(args.output_dir / f"contrast_{1.0/args.alpha:.2f}.jpg"), lower)

    print(f"Lưu ảnh gốc và ảnh điều chỉnh tương phản trong: {args.output_dir}")


if __name__ == "__main__":
    main()
