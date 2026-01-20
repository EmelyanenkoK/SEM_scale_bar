import argparse
import os
import sys

from sem_scale_bar.core import process_file


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Process SEM images to add scale bars based on metadata."
        )
    )
    parser.add_argument(
        "input",
        help="Input file or folder containing SEM images",
    )
    parser.add_argument(
        "--language",
        choices=["English", "Russian"],
        default="English",
        help="Language for scale text (default: English)",
    )
    parser.add_argument(
        "--background-color",
        choices=["white", "black"],
        default="white",
        help="Background color for scale bar box (default: white)",
    )
    parser.add_argument(
        "--scale-bar-corner",
        choices=["left", "right"],
        default="right",
        help="Corner for the scale bar (default: right)",
    )
    parser.add_argument(
        "--label-text",
        default="",
        help="Optional label text to add to the image",
    )
    parser.add_argument(
        "--label-corner",
        choices=["left", "right"],
        default="left",
        help="Corner for the label (default: left)",
    )
    parser.add_argument(
        "-k",
        "--output-index",
        type=int,
        default=1,
        help="Index used in output filenames (default: 1)",
    )
    return parser


def iter_image_paths(path):
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file_name in files:
                yield os.path.join(root, file_name)
    else:
        yield path


def process_path(path, language, rect_color, corner, label, label_corner, k):
    for file_path in iter_image_paths(path):
        print(f"Processing {file_path}...")
        process_file(file_path, language, rect_color, corner, label, label_corner, k)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not os.path.exists(args.input):
        parser.error(f"Input path not found: {args.input}")

    process_path(
        args.input,
        args.language,
        args.background_color,
        args.scale_bar_corner,
        args.label_text,
        args.label_corner,
        args.output_index,
    )
    print("Processing complete. Check the input folder for outputs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
