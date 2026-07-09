from pathlib import Path

import pandas as pd
import streamlit as st


DEFAULT_CLEANING_DIR = Path("outputs/cleaning_demo_check")
DEFAULT_ANALYSIS_DIR = Path("outputs/analysis_demo_check")


st.set_page_config(
    page_title="Root Image Analysis Framework",
    layout="wide",
)


def read_csv_if_exists(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


def show_csv_section(title: str, path: Path) -> None:
    st.subheader(title)
    st.caption(str(path))

    df = read_csv_if_exists(path)
    if df is None:
        st.warning(f"File not found: {path}")
        return

    st.dataframe(df, use_container_width=True)
    st.caption(f"Rows: {len(df)} | Columns: {len(df.columns)}")


def image_id_from_output_name(path: Path) -> str:
    name = path.name
    for suffix in ["_mask.png", "_skeleton.png", "_overlay.png"]:
        if name.endswith(suffix):
            return name.removesuffix(suffix)
    return path.stem


def collect_analysis_images(analysis_dir: Path) -> dict[str, dict[str, Path]]:
    image_outputs: dict[str, dict[str, Path]] = {}

    output_specs = {
        "mask": analysis_dir / "masks",
        "skeleton": analysis_dir / "skeletons",
        "overlay": analysis_dir / "overlays",
    }

    for output_type, folder in output_specs.items():
        if not folder.exists():
            continue

        for image_path in sorted(folder.glob("*.png")):
            image_id = image_id_from_output_name(image_path)
            image_outputs.setdefault(image_id, {})[output_type] = image_path

    return image_outputs


def show_image_outputs(analysis_dir: Path) -> None:
    st.subheader("Image outputs")
    st.caption(
        "Mask, skeleton and overlay are shown side by side for each analyzed image."
    )

    image_outputs = collect_analysis_images(analysis_dir)

    if not image_outputs:
        st.warning(f"No image outputs found in: {analysis_dir}")
        return

    for image_id, outputs in sorted(image_outputs.items()):
        st.markdown(f"### {image_id}")

        col_mask, col_skeleton, col_overlay = st.columns(3)

        with col_mask:
            st.markdown("**Mask**")
            mask_path = outputs.get("mask")
            if mask_path is not None:
                st.image(str(mask_path), caption=mask_path.name, use_container_width=True)
            else:
                st.info("Mask not found")

        with col_skeleton:
            st.markdown("**Skeleton**")
            skeleton_path = outputs.get("skeleton")
            if skeleton_path is not None:
                st.image(
                    str(skeleton_path),
                    caption=skeleton_path.name,
                    use_container_width=True,
                )
            else:
                st.info("Skeleton not found")

        with col_overlay:
            st.markdown("**Overlay**")
            overlay_path = outputs.get("overlay")
            if overlay_path is not None:
                st.image(
                    str(overlay_path),
                    caption=overlay_path.name,
                    use_container_width=True,
                )
            else:
                st.info("Overlay not found")


st.title("Transparent Root Image Analysis Framework")
st.caption(
    "MVP Streamlit viewer for cleaning and analysis outputs. "
    "No data cleaning or image analysis logic is implemented in this GUI."
)

cleaning_dir = Path(
    st.sidebar.text_input(
        "Cleaning output directory",
        value=str(DEFAULT_CLEANING_DIR),
    )
)

analysis_dir = Path(
    st.sidebar.text_input(
        "Analysis output directory",
        value=str(DEFAULT_ANALYSIS_DIR),
    )
)

tab_cleaning, tab_analysis = st.tabs(["Data Cleaning Results", "Image Analysis Results"])

with tab_cleaning:
    st.header("Data Cleaning Results")

    show_csv_section(
        "Cleaning summary",
        cleaning_dir / "cleaning_summary.csv",
    )
    show_csv_section(
        "Clean manifest",
        cleaning_dir / "clean_manifest.csv",
    )
    show_csv_section(
        "Rejected records",
        cleaning_dir / "rejected_records.csv",
    )
    show_csv_section(
        "Audit log",
        cleaning_dir / "audit_log.csv",
    )

with tab_analysis:
    st.header("Image Analysis Results")

    show_csv_section(
        "Analysis summary",
        analysis_dir / "analysis_summary.csv",
    )
    show_csv_section(
        "Root measurements",
        analysis_dir / "root_measurements.csv",
    )
    show_csv_section(
        "Processing log",
        analysis_dir / "processing_log.csv",
    )
    show_image_outputs(analysis_dir)
