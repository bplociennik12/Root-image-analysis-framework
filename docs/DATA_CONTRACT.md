# Data Contract

## raw_metadata.csv

Minimalne wymagane kolumny:

```text
image_name
sample_id
```

Opcjonalne kolumny biologiczne:

```text
species
treatment
replicate
notes
```

## clean_manifest.csv

Minimalne kolumny:

```text
record_id
image_id
image_name_original
image_name_clean
image_path
sample_id_original
sample_id_clean
file_format
width_px
height_px
is_valid
record_status
reason
message
audit_events_count
```

Dozwolone statusy:

```text
valid
warning
rejected
```

## root_measurements.csv

Minimalne kolumny:

```text
record_id
image_id
image_name
sample_id
roi_used
area_px
skeleton_length_px
branch_points_count
endpoints_count
bbox_width_px
bbox_height_px
aspect_ratio
centroid_x_px
centroid_y_px
component_count
processing_status
reason
message
```

Bez jawnej kalibracji skali nie raportujemy `length_mm` ani `area_mm2`.
