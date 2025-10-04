import os
import pandas as pd
from typing import Dict

def get_dss_master_file_path(
    circuit_base_path: str,
    city: str,
    subregion: str,
    year: str,
    scenario: str,
    substation: str = None, # Permite que seja None
    feeder: str = None      # Permite que seja None
) -> str:
    """
    Constructs and validates the absolute path to the Master.dss file
    at different hierarchical levels (sub-region, substation, or feeder).

    Args:
        config (Dict): Configuration dictionary from config.yaml.
        # ... (outros args)
        substation (str, optional): Substation name. Defaults to None.
        feeder (str, optional): Feeder name. Defaults to None.

    Returns:
        str: The absolute path to the Master.dss file.
    """
    
    # Inicia a construção do caminho comum
    circuit_path = os.path.join(
        circuit_base_path, year, city, subregion, "scenarios", 
        scenario, "opendss"
    )
    
    # Adiciona partes ao caminho condicionalmente
    if substation:
        circuit_path = os.path.join(circuit_path, substation)
        if feeder:
            # Um feeder só pode existir dentro de uma subestação
            circuit_path = os.path.join(circuit_path, feeder)
    
    # Valida se o caminho final construído existe
    if not os.path.isdir(circuit_path):
        raise FileNotFoundError(f"Circuit directory not found for the specified level: {circuit_path}")

    dss_file = os.path.join(circuit_path, "Master.dss")
    if not os.path.isfile(dss_file):
        raise FileNotFoundError(f"Master.dss file not found in: {circuit_path}")

    return dss_file

def save_results_as_parquet(
    results_dict: Dict[str, pd.DataFrame],
    saving_dir: str,
    year: str,
    scenario: str,
    start_date: str,
    n_days: int,
    subregion: str,
    substation: str = None,
    feeder: str = None
):
    """
    Saves a dictionary of DataFrames to Parquet files in a structured directory
    that includes the simulation scope (subregion, substation, or feeder).

    Args:
        # ... (argumentos anteriores)
        subregion (str): The simulated sub-region.
        substation (str, optional): The simulated substation. Defaults to None.
        feeder (str, optional): The simulated feeder. Defaults to None.
    """
    if not results_dict:
        print("Warning: Results dictionary is empty. Nothing to save.")
        return

    # --- Lógica para determinar o nome da pasta de escopo ---
    # Usa o nome mais específico que foi fornecido.
    if feeder:
        scope_name = feeder
    elif substation:
        scope_name = substation
    else:
        scope_name = subregion
    
    run_folder_name = f'run_{start_date}_{n_days}_days'
    
    # Constrói o caminho completo, incluindo a nova pasta de escopo
    run_path = os.path.join(
        saving_dir, year, scenario, scope_name, run_folder_name
    )
    
    # Create the directory structure if it doesn't exist
    os.makedirs(run_path, exist_ok=True)
    print(f"Saving results to directory: {run_path}")
    
    for name, df in results_dict.items():
        file_name = f"{name}.parquet"
        file_path = os.path.join(run_path, file_name)
        df.to_parquet(file_path, engine='pyarrow')
        print(f"  - Saved: {file_name}")