import os
from contextlib import contextmanager
import py_dss_interface
import py_dss_toolkit as dss_tools
from colorama import Fore
from sds_run.utils import Spinner
from sds_run.query_handler import get_buses_results, get_source_power_results
from typing import Dict, Tuple, List

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
        config: Dict) -> Tuple[Dict, Dict]:

    spinner = Spinner(f"Compiling OpenDSS model: {os.path.basename(dss_file_path)}")
    spinner.start()
    dss_directory = os.path.dirname(dss_file_path)

    buses_to_monitor = config.get('buses', [])
    sources_to_monitor = dss.vsources.names
    
    buses_results_dict = {bus: [] for bus in buses_to_monitor}
    sources_power_result_dict = {}

    with change_dir(dss_directory):
        #inicializando a interface
        try:
            dss.text(f"compile [{dss_file_path}]")
        finally:
            spinner.stop()

        print("  - Model compiled sucessfully.")
        dss.text("set mode=yearly stepsize=15m number=1")
        dss.text(f"set hour={start_hour}")

        sources_to_monitor = dss.vsources.names
        sources_power_result_dict = {source: [] for source in sources_to_monitor}
        
        print("Running power flow...")
        for i in range(n_points):
            dss.text('solve')
            #only gets the results if the list is not empty
            if buses_to_monitor:
                get_buses_results(dss, config['buses'], buses_results_dict)

            get_source_power_results(dss, sources_power_result_dict)

            if((i+ 1)%96 == 0):
                print(f"   -Step {i+1}")

    print(f"  - Leaving simulation...")
    return buses_results_dict ,sources_power_result_dict