# sds-run: A CLI Tool for SMART-DS Time Series Simulation

`sds-run` is a command-line interface (CLI) tool developed in Python to orchestrate quasi-static time series (QSTS) power flow simulations. It uses the circuit models from the [SMART-DS dataset](https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=SMART-DS%2F) and the OpenDSS engine.

> This tool was developed as part of a scientific initiation project at the **LABSPOT** laboratory at the Federal University of Santa Catarina (UFSC), Brazil.

The tool allows engineers to run simulations in a fast and reproducible manner, saving opendss monitor results to Parquet files for easy subsequent analysis.

## Features

-   Execution of simulations at different levels of granularity: sub-region, substation, or individual feeder.
-   External configuration via a `config.yaml` file for easy portability.
-   Automatic saving of results in Parquet format, organized into a logical folder structure.
-   Visual feedback in the terminal.

## Getting Started

Follow the steps below to set up and run the `sds-run` tool.

### Prerequisites

-   Python 3.8+
-   Access to a terminal or command line (cmd, PowerShell, bash, etc.).
-   Git installed on your system.
-   The [SMART-DS circuit models](https://data.openei.org/s3_viewer?bucket=oedi-data-lake&prefix=SMART-DS%2F) downloaded to your local machine.

### Data Acquisition (Downloading Circuit Models)

**Crucial:** This tool is designed to work with the exact directory structure provided by the SMART-DS dataset. The path to a circuit is built dynamically (e.g., `.../<year>/<city>/<subregion>/...`). Therefore, you must preserve this parent folder hierarchy for the tool to function correctly.

The easiest way to download specific circuits while preserving the required folder structure is by using the [AWS Command Line Interface (CLI)](https://aws.amazon.com/cli/).

After installing the AWS CLI, you can use the commands below. To run a simulation, you need to download two components: the specific **circuit files** and the corresponding **`profiles` folder** for that sub-region.

#### Command Templates

You must replace the placeholders (e.g., `[YEAR]`, `[CITY]`) in the commands with the values for the circuit you wish to simulate.

1.  **Download Circuit Files (Feeder, Substation, etc.)**
    ```bash
    aws s3 cp --no-sign-request s3://oedi-data-lake/SMART-DS/v1.0/[YEAR]/[CITY]/[SUBREGION]/scenarios/[SCENARIO]/opendss/[SUBSTATION]/[FEEDER]/ circuit_models/[YEAR]/[CITY]/[SUBREGION]/scenarios/[SCENARIO]/opendss/[SUBSTATION]/[FEEDER]/ --recursive
    ```

2.  **Download Profile Files**
    ```bash
    aws s3 cp --no-sign-request s3://oedi-data-lake/SMART-DS/v1.0/[YEAR]/[CITY]/[SUBREGION]/profiles/ circuit_models/[YEAR]/[CITY]/[SUBREGION]/profiles/ --recursive
    ```

#### Placeholder Definitions

-   `[YEAR]`: e.g., `2017`
-   `[CITY]`: e.g., `SFO`
-   `[SUBREGION]`: e.g., `P13U`
-   `[SCENARIO]`: e.g., `base_timeseries`
-   `[SUBSTATION]`: e.g., `p13uhs0_1247`
-   `[FEEDER]`: e.g., `p13uhs0_1247--p13udt13213`

#### Practical Example

The following two commands will download the `p13uhs0_1247--p13udt13213` feeder and its required profiles for the `base_timeseries` scenario of 2017. Execute them from the project's root directory.

1.  **Download the example circuit:**
    ```bash
    aws s3 cp --no-sign-request s3://oedi-data-lake/SMART-DS/v1.0/2017/SFO/P13U/scenarios/base_timeseries/opendss/p13uhs0_1247/p13uhs0_1247--p13udt13213/ circuit_models/2017/SFO/P13U/scenarios/base_timeseries/opendss/p13uhs0_1247/p13uhs0_1247--p13udt13213/ --recursive
    ```

2.  **Download the corresponding profiles:**
    ```bash
    aws s3 cp --no-sign-request s3://oedi-data-lake/SMART-DS/v1.0/2017/SFO/P13U/profiles/ circuit_models/2017/SFO/P13U/profiles/ --recursive
    ```


### Installation

1.  **Clone the Repository**
    Clone this repository to your local machine:
    ```bash
    git clone [https://github.com/eduardoborgonha/sds-run-labspot.git](https://github.com/eduardoborgonha/sds-run-labspot.git)
    cd sds-run-labspot
    ```

2.  **Create and Activate a Virtual Environment**
    It is strongly recommended to use a virtual environment to isolate project dependencies.
    ```bash
    # Create the environment
    python -m venv venv

    # Activate on Windows
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies**
    Install all required libraries using the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

The tool needs to know where the circuit models are located and where to save the simulation results.

1.  **Create the Configuration File**
    If it doesn't exist, create a `config.yaml` file in the root of the project. A template is provided in the repository.

2.  **Edit the Paths**
    Open `config.yaml` and edit the paths to point to the correct locations on your machine. **Using absolute paths is highly recommended for robust operation.**

    **Example `config.yaml`:**
    ```yaml
    # Path to the base folder containing the SMART-DS circuit models.
    circuit_base_path: "C:/Users/YourUser/Documents/SMART-DS_Models"

    # Path to the base folder where simulation results will be saved.
    results_base_path: "C:/Users/YourUser/Documents/sds-run-results"
    ```

## Usage

The tool is executed via the `run.py` script. The basic command structure is as follows:

```bash
python run.py <scenario> <start_date> <days> [options]
```

### Arguments

- `scenario` **(Required)**: The name of the SMART-DS scenario (e.g., 'base_timeseries').
- `start_date` **(Required)**: The simulation start date in `YYYY-MM-DD` format.
- `days` **(Required)**: The number of days to simulate.

### Options
- `-c, --city`: City code for the dataset (default: SFO).
- `-sr, --subregion`: Sub-region code for the dataset (default: P13U).
- `-ss, --substation`: Substation name. If omitted, the entire sub-region is simulated.
- `-f, --feeder`: Feeder name. If provided, simulates only this feeder. Requires --substation to be set.

## Examples
#### Simulate a specific feeder for 5 days:
```bash
python run.py base_timeseries 2017-07-20 5 --city SFO --subregion P13U --substation p13uhs0_1247 --feeder p13uhs0_1247--p13udt13213
```
#### Simulate an entire substation for 1 day:
```bash
python run.py base_timeseries 2018-01-15 1 --substation p13uhs0_1247
```

## Output Structure
Results will be saved within the results_base_path defined in your config.yaml, following the structure:
`<results_base_path>/<year>/<scenario>/<simulation_scope>/run_<date>_<days>_days/`
- `<simulation_scope>` will be the name of the feeder, substation, or sub-region, depending on the simulation level.

Inside the final folder, each monitor from the circuit will have its results saved in a separate .parquet file.

## Acknowledgments and Citation

This work was made possible by the use of open-data and open-source software. I gratefully acknowledge the following projects and organizations.

### SMART-DS Dataset

This tool is designed to work with the Synthetic Models for Advanced, Realistic Testing: Distribution Systems and Scenarios (SMART-DS) dataset, which was developed by the National Renewable Energy Laboratory (NREL) and is available through the Open Energy Data Initiative (OEDI).


### Key Software Libraries

The core functionality of this tool relies heavily on the work of Paulo Radatz and his powerful libraries for interacting with the OpenDSS engine.

    Radatz, P. (2025). py-dss-interface: A Python package that interfaces with OpenDSS powered by EPRI (Version X.X.X) [Computer software]. GitHub. https://github.com/PauloRadatz/py_dss_interface

These tools were fundamental to the creation of `sds-run`.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.