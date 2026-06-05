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


def apply_custom_kernels(image):
    kernels = {
        "smooth": np.ones((3, 3), np.float32) / 9.0,
        "sharpen": np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32),
        "edge_detect": np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], np.float32),
    }
    results = {name: cv2.filter2D(image, -1, kernel) for name, kernel in kernels.items()}
    return results


def main():
    base_dir = Path(__file__).resolve().parent
    default_input = base_dir.parent / "images" / "input.jpg"
    parser = argparse.ArgumentParser(description="Kernel tùy chỉnh cho ảnh.")
    parser.add_argument("--input", type=Path, default=default_input, help="Đường dẫn ảnh đầu vào")
    parser.add_argument("--output_dir", type=Path, default=base_dir / "output" / "output02_02", help="Thư mục lưu kết quả")
    args = parser.parse_args()

    image = load_image(args.input)
    ensure_output_dir(args.output_dir)

    custom_results = apply_custom_kernels(image)
    shutil.copy2(args.input, args.output_dir / args.input.name)

    for name, result in custom_results.items():
        cv2.imwrite(str(args.output_dir / f"custom_{name}.jpg"), result)

    print(f"Lưu ảnh gốc và các kết quả kernel tùy chỉnh trong: {args.output_dir}")


if __name__ == "__main__":
    main()
