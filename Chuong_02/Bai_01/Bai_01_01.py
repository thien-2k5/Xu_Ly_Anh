from pathlib import Path
import argparse
import shutil
import cv2
import os

def change_brightness(image, delta):
    return cv2.convertScaleAbs(image, alpha=1.0, beta=delta)


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
    parser = argparse.ArgumentParser(description="Thay đổi độ sáng ảnh.")
    parser.add_argument("--input", type=Path, default=default_input, help="Đường dẫn ảnh đầu vào")
    parser.add_argument("--delta", type=int, default=50, help="Giá trị cộng trừ tăng giảm độ sáng")
    parser.add_argument("--output_dir", type=Path, default=base_dir / "output" / "output01_01", help="Thư mục lưu kết quả")
    args = parser.parse_args()

    image = load_image(args.input)
    ensure_output_dir(args.output_dir)

    bright = change_brightness(image, args.delta)
    dark = change_brightness(image, -args.delta)

    shutil.copy2(args.input, args.output_dir / args.input.name)
    cv2.imwrite(str(args.output_dir / "bright.jpg"), bright)
    cv2.imwrite(str(args.output_dir / "dark.jpg"), dark)

    print(f"Lưu ảnh gốc và ảnh tăng/giảm độ sáng trong: {args.output_dir}")


if __name__ == "__main__":
    main()
