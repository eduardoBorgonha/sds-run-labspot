import os
from contextlib import contextmanager
import py_dss_interface
from colorama import Fore
from sds_run.utils import Spinner
from sds_run.query_handler import get_buses_results, get_pvsystems_results, get_transformers_results, get_power_result
from typing import Dict

@contextmanager
def change_dir(destination):
    """Context manager to safely change the current working directory."""
    try:
        cwd = os.getcwd()
        os.chdir(destination)
        yield
    finally:
        os.chdir(cwd)

def simulate_dynamic(
        dss: py_dss_interface.DSS, 
        dss_file_path: str,
        start_hour: int, 
        n_points: int, 
        requires_results: Dict):

    spinner = Spinner(f"Compiling OpenDSS model: {os.path.basename(dss_file_path)}")
    spinner.start()
    dss_directory = os.path.dirname(dss_file_path)

    buses_results_dict = {bus: [] for bus in requires_results['buses']}
    power_results = list()

    with change_dir(dss_directory):
        #inicializando a interface
        try:
            dss.text(f"compile [{dss_file_path}]")
        finally:
            spinner.stop()
        print("  - Model compiled sucessfully.")
        dss.text("set mode=yearly stepsize=15m number=1")
        dss.text(f"set hour={start_hour}")
        print("Running power flow...")
        for i in range(n_points):
            dss.text('solve')
            get_buses_results(dss, requires_results['buses'], buses_results_dict)
            #get_transformers_results(dss, requires_results['transformers'], transformers_results_dict)
            #get_pvsystems_results(dss, requires_results['pvsystems'], pvsystems_results_dict)
            power_results.append(get_power_result(dss))
            if(i%96 == 0):
                print(f"   -Step {i}")

    print(f"  - {Fore.GREEN}Simulation completed successfully.")
    return buses_results_dict ,power_results