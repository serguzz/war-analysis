# War Statistics

A Python-based data analysis project for processing, analyzing, and visualizing publicly available datasets.

The project provides a simple and reproducible pipeline for converting raw data into structured formats, performing statistical analysis, and generating visualizations for selected time periods.

## Project Structure

```text
war-analysis/
├── data/
│   ├── raw/                  # Original source datasets
│   └── processed/            # Processed datasets and generated results
├── scripts/
│   ├── read_ods.py           # Read and convert ODS data
│   └── month_diagram.py      # Generate monthly statistics
├── Dockerfile
├── compose.yml
├── Makefile
├── requirements.txt
└── README.md
```

## Technologies

* **Python** — data processing and analysis
* **Pandas** — data manipulation, filtering and aggregation
* **Matplotlib** — data visualization
* **PyArrow** — Parquet data storage
* **ODF / odfpy** — OpenDocument Spreadsheet support
* **Docker** — reproducible development environment
* **Makefile** — convenient project commands

## Data Pipeline

```text
Raw ODS data
     ↓
Data loading
     ↓
Data processing
     ↓
Parquet dataset
     ↓
Statistical analysis
     ↓
Visualizations
```

Raw source files are kept in `data/raw/`, while processed datasets and generated results are stored in `data/processed/`.

## Installation

### Requirements

The project requires:

* Docker
* Docker Compose
* Make

Python dependencies are installed inside the Docker container from `requirements.txt`.

### Build the Docker image

```bash
docker compose build
```

## Usage

The project uses a `Makefile` to simplify common commands.

### Run the default application

```bash
make run
```

### Read and process the ODS dataset

```bash
make read
```

This command reads the source ODS file and converts it into a Parquet dataset.

Input:

```text
data/raw/sad.ods
```

Output:

```text
data/processed/sad.parquet
```

### Generate a monthly diagram

```bash
make month_diagram
```

The script reads the source dataset, filters the selected date range, groups records by month, and generates a statistical bar chart.

The date range can be configured directly in:

```text
scripts/month_diagram.py
```

For example:

```python
DATE_START = "2022-01-01"
DATE_END = "2026-08-31"
```

The generated visualization is stored in:

```text
data/processed/month_diagram.png
```

## Running Scripts Directly

Scripts can also be executed inside the Docker container without using Make.

For example:

```bash
docker compose run --rm app python scripts/read_ods.py
```

or:

```bash
docker compose run --rm app python scripts/month_diagram.py
```

Using `make` is recommended for frequently used commands.

## Configuration

Analysis parameters are currently configured directly in the corresponding scripts.

For example, `month_diagram.py` contains:

```python
DATE_START = "2022-01-01"
DATE_END = "2026-08-31"
```

Changing these values allows the analysis to be performed for a different time period.

## Development

After modifying Python dependencies in `requirements.txt`, rebuild the Docker image:

```bash
docker compose build
```

Then run the required command:

```bash
make read
```

or:

```bash
make month_diagram
```

Generated files should be placed in `data/processed/` rather than mixed with the original source data.

## Reproducibility

The project uses Docker to keep the runtime environment consistent across machines.

A typical workflow is:

```bash
docker compose build
make read
make month_diagram
```

This makes the data processing and visualization workflow reproducible without requiring Python dependencies to be installed directly on the host system.
