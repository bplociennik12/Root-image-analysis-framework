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


def format_summary_value(value: object) -> str:
    if pd.isna(value):
        return ""

    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    if number.is_integer():
        return str(int(number))

    return f"{number:.3f}".rstrip("0").rstrip(".")


def show_summary_metrics(
    path: Path,
    metric_names: list[str],
) -> None:
    df = read_csv_if_exists(path)

    if df is None:
        return

    if not {"metric", "value"}.issubset(df.columns):
        st.warning(f"Summary file has unexpected columns: {path}")
        return

    summary_values = dict(zip(df["metric"].astype(str), df["value"]))

    available_metrics = [
        metric_name
        for metric_name in metric_names
        if metric_name in summary_values
    ]

    if not available_metrics:
        return

    st.markdown("### Key metrics")

    columns = st.columns(min(4, len(available_metrics)))

    for index, metric_name in enumerate(available_metrics):
        with columns[index % len(columns)]:
            st.metric(
                label=metric_name.replace("_", " "),
                value=format_summary_value(summary_values[metric_name]),
            )


def filter_dataframe(
    df: pd.DataFrame,
    filter_columns: list[str],
    key_prefix: str,
) -> pd.DataFrame:
    filtered = df.copy()

    available_columns = [column for column in filter_columns if column in filtered.columns]
    if not available_columns:
        return filtered

    with st.expander("Filters", expanded=False):
        for column in available_columns:
            values = (
                filtered[column]
                .dropna()
                .astype(str)
                .sort_values()
                .unique()
                .tolist()
            )

            selected_values = st.multiselect(
                label=f"Filter by {column}",
                options=values,
                key=f"{key_prefix}_{column}",
            )

            if selected_values:
                filtered = filtered[
                    filtered[column].astype(str).isin(selected_values)
                ]

    return filtered


def show_csv_section(
    title: str,
    path: Path,
    filter_columns: list[str] | None = None,
    key_prefix: str | None = None,
) -> None:
    st.subheader(title)
    st.caption(str(path))

    df = read_csv_if_exists(path)
    if df is None:
        st.warning(f"File not found: {path}")
        return

    if filter_columns is not None:
        filtered_df = filter_dataframe(
            df=df,
            filter_columns=filter_columns,
            key_prefix=key_prefix or title.lower().replace(" ", "_"),
        )
    else:
        filtered_df = df

    st.dataframe(filtered_df, use_container_width=True)

    if len(filtered_df) == len(df):
        st.caption(f"Rows: {len(df)} | Columns: {len(df.columns)}")
    else:
        st.caption(
            f"Filtered rows: {len(filtered_df)} / {len(df)} | "
            f"Columns: {len(df.columns)}"
        )


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

    cleaning_summary_path = cleaning_dir / "cleaning_summary.csv"
    show_summary_metrics(
        cleaning_summary_path,
        metric_names=[
            "total_records",
            "valid_records",
            "warning_records",
            "rejected_records",
            "missing_files",
            "unsupported_formats",
            "corrupted_images",
        ],
    )
    show_csv_section(
        "Cleaning summary",
        cleaning_summary_path,
    )
    show_csv_section(
        "Clean manifest",
        cleaning_dir / "clean_manifest.csv",
        filter_columns=[
            "record_status",
            "reason",
            "image_id",
            "image_name_clean",
            "sample_id_clean",
            "file_format",
            "is_valid",
        ],
        key_prefix="clean_manifest",
    )
    show_csv_section(
        "Rejected records",
        cleaning_dir / "rejected_records.csv",
    )
    show_csv_section(
        "Audit log",
        cleaning_dir / "audit_log.csv",
        filter_columns=[
            "record_id",
            "image_name",
            "step",
            "status",
            "reason",
        ],
        key_prefix="audit_log",
    )

with tab_analysis:
    st.header("Image Analysis Results")

    analysis_summary_path = analysis_dir / "analysis_summary.csv"
    show_summary_metrics(
        analysis_summary_path,
        metric_names=[
            "manifest_records",
            "records_selected_for_analysis",
            "records_skipped_not_valid",
            "analysis_success",
            "analysis_warning",
            "analysis_failed",
            "empty_masks",
            "multiple_components",
            "mean_area_px",
            "mean_skeleton_length_px",
        ],
    )
    show_csv_section(
        "Analysis summary",
        analysis_summary_path,
    )
    show_csv_section(
        "Root measurements",
        analysis_dir / "root_measurements.csv",
        filter_columns=[
            "processing_status",
            "reason",
            "image_id",
            "image_name",
            "sample_id",
            "component_count",
        ],
        key_prefix="root_measurements",
    )
    show_csv_section(
        "Processing log",
        analysis_dir / "processing_log.csv",
        filter_columns=[
            "record_id",
            "image_name",
            "step",
            "status",
            "reason",
        ],
        key_prefix="processing_log",
    )
    show_image_outputs(analysis_dir)
