# Overview

PROLIT (Provenance and Lineage Information Tracker) is a library capable of capturing provenance in a preprocessing pipeline. PROLIT provides a clear and clean interface for capturing provenance, at various levels of granularity, without the need to invoke additional functions. The data scientist simply needs to implement the pipeline and, after executing it, can analyze the corresponding graph using Neo4j.

## Table of Contents

- [Installation](#installation)
- [Neo4j (Docker)](#neo4j-docker)
- [Pipeline Assets](#pipeline-assets)
  - [Pipelines](pipelines)
  - [Datasets](datasets)
- [LLM Prompts](LLM)
- [Provenance Exploitation](NaturalLanguageGraphExploitation)
- [Provenance Explanation](Why+Narratives)
- [Getting Started](#getting-started)


## Installation

To use the tool, follow these steps:

1. **Clone the repository**:
   ```
   git clone https://github.com/pasqualeleonardolazzaro/PROLIT.git
   ```

2. **Navigate to the project directory**:
   ```
   cd PROLIT
   ```

3. **Create and activate a virtual environment (optional but recommended)**:
   On Unix or MacOS:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

   On Windows:
   ```
   python -m venv venv
   .\venv\Scripts\activate
   ```

4. **Install the requirements**:
   ```
   pip install -r requirements.txt
   ```

## Neo4j (Docker)


- **Start Neo4j in the background by executing the following command:**:
    
      cd neo4j
      docker compose up -d

- **To stop Neo4j, run the following command:**:

      cd neo4j
      docker compose down -v

### Access the Neo4j Web Interface

To access the Neo4j web interface, open the following URL in your web browser:

http://localhost:7474/browser/

#### Default Credentials

- **User**: `neo4j`
- **Password**: `adminadmin`

## Getting Started

To get started with the tool, follow these simple steps.

### How to run it

The main file for running the tool is **prolit_run.py**. Below is a description of the arguments you can pass via the command line.

### Example commands

Run PROLIT by specifying the dataset and pipeline you want to use, along with other options:

```bash
python prolit_run.py --dataset datasets/car_data.csv --pipeline pipelines/car_pipeline.py --frac 0.1 --granularity_level 3 --entity_type_level 2
```
### Arguments

- `--dataset`: Relative path to the dataset file. For example: `datasets/car_data.csv`
- `--pipeline`: Relative path to the pipeline file. For example: `pipelines/car_pipeline.py`
- `--frac`: Fraction of the dataset to use for sampling. Value between `0.0` and `1.0`. For example, `0.1` uses 10% of the dataset.
- `--granularity_level`: Granularity level. Can be `1`, `2`, `3` or `4` with specific meanings for each level of detail.
  - `1`: Sketch Level
  - `2`: Derivation Level
  - `3`: Full Level
  - `4`: Only Columns Level



