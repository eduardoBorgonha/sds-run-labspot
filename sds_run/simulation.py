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
    Compila e simula o circuito DSS para o cenário informado. Por padrão resolve para 1 dia com stepsize de 15m. Begin é a hora em que começa a simulação, a.
    Retorna o objeto dss já simulado.
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
        print("  - Model compiles sucessfully.")
        print(f"Simulation defined for yearly, stepsize: 15m, beginning  at {start_hour}h with {n_points} points.")
        dss.text(f"set hour={start_hour}")
        dss.text(f"set mode=yearly stepsize=15m number={n_points}")
        print("Simulating...")
        dss.text(f"solve")
        print(Fore.GREEN + "Simulation Completed")