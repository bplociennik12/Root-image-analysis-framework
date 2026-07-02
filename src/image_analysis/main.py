import argparse

from image_analysis.config import DEFAULT_OUTPUT_DIR, FOREGROUND
from image_analysis.pipeline import run_analysis_pipeline


def parse_args():
    parser = argparse.ArgumentParser(description="Run transparent root image analysis pipeline.")
    parser.add_argument("--manifest", required=True, help="Path to clean_manifest.csv")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    parser.add_argument(
        "--foreground",
        choices=["dark", "light"],
        default=FOREGROUND,
        help="Foreground direction for root segmentation: dark or light",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    measurements, processing_events, paths = run_analysis_pipeline(args.manifest, args.output, foreground=args.foreground)

    print("Image analysis pipeline finished.")
    print(f"Analyzed records: {len(measurements)}")
    print(f"Processing events: {len(processing_events)}")
    for name, path in paths.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
