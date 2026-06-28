import argparse

from data_cleaning.config import DEFAULT_OUTPUT_DIR
from data_cleaning.pipeline import run_cleaning_pipeline


def parse_args():
    parser = argparse.ArgumentParser(description="Run transparent data cleaning pipeline.")
    parser.add_argument("--metadata", required=True, help="Path to raw_metadata.csv")
    parser.add_argument("--images", required=True, help="Path to image directory")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    return parser.parse_args()


def main():
    args = parse_args()
    manifest, audit_events, paths = run_cleaning_pipeline(args.metadata, args.images, args.output)

    print("Cleaning pipeline finished.")
    print(f"Total records: {len(manifest)}")
    print(f"Valid records: {(manifest['record_status'] == 'valid').sum()}")
    print(f"Rejected records: {(manifest['record_status'] == 'rejected').sum()}")
    print(f"Audit events: {len(audit_events)}")
    for name, path in paths.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
