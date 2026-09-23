# Data Requirement & Compatibility Layer

Pre-flight checks compare the selected Exercise Manifest with governed dataset columns.
States: ready, partial, missing_data, blocked.

The canonical run-from-dataset-version route repeats the gate server-side, so frontend checks cannot be bypassed.
Aliases support common canonical equivalents without inventing missing data.
