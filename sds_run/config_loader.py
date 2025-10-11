import yaml
import os
from typing import Dict
from colorama import Fore

def load_config(config_path: str = 'config.yaml') -> Dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f'Error: The file {config_path} does not exist')
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f'Error parsing YAML file: {e}')
        raise
    if not config:
        raise ValueError(f'Error: The config file {config_path} is empty')
    
    # Verifying if the keys for the application are there
    required_keys = ['circuit_base_path', 'results_base_path']
    for key in required_keys:
        if key not in config:
            raise ValueError(f'Error: The key {key} was not found in {config_path}')
    print(Fore.GREEN + "Config loaded and validated sucessfully ")
    return config