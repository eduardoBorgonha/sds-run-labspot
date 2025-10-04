import os
from contextlib import contextmanager
import py_dss_interface
from colorama import Fore
from sds_run.utils import Spinner

@contextmanager
def change_dir(destination):
    """Context manager to safely change the current working directory."""
    try:
        cwd = os.getcwd()
        os.chdir(destination)
        yield
    finally:
        os.chdir(cwd)

def simulate(dss: py_dss_interface.DSS, dss_file_path: str, start_hour: int, n_points: int):
    """
    Sets up and runs the OpenDSS simulation for a given scenario.

    Args:
    dss: An initialized instance of the py_dss_interface.DSS object.
    dss_file_path: The full path to the Master.dss file to be compiled.
    start_hour: The hour of the year at which the simulation starts.
    n_points: The total number of 15-minute steps to simulate.
    """
    spinner = Spinner(f"Compiling OpenDSS model: {os.path.basename(dss_file_path)}")
    spinner.start()
    dss_directory = os.path.dirname(dss_file_path)
    with change_dir(dss_directory):
        #inicializando a interface
        try:
            dss.text(f"compile [{dss_file_path}]")
        finally:
            spinner.stop()
        print("  - Model compiled sucessfully.")
        print(f"Simulation set for yearly mode, stepsize: 15m, starting at hour {start_hour} with {n_points} points.")
        dss.text(f"set hour={start_hour}")
        dss.text(f"set mode=yearly stepsize=15m number={n_points}")
        print("  - Running simulation...")
        dss.text(f"solve")
        print(f"  - {Fore.GREEN}Simulation completed successfully.")