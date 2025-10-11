import argparse
from typing import Dict
from colorama import Fore, Style
import py_dss_interface
from py_dss_toolkit import dss_tools
import os
from sds_run.utils import convert_date_to_simulation_time
from sds_run.file_manager import get_dss_master_file_path, save_results_as_parquet
from sds_run.simulation import simulate_dynamic
from sds_run.processing import get_monitor_results, add_datetime_index_to_results, convert_bus_results_to_dataframes, convert_source_powers_to_dataframes


def main_pipeline(args: argparse.Namespace, config: Dict):
    """
    The main orchestration pipeline for the simulation tool.

    Args:
        args (argparse.Namespace): Arguments parsed from the command line.
        config (Dict): Configuration dictionary loaded from config.yaml.
    """
    print(Fore.CYAN + Style.BRIGHT + "=" * 50)
    print(Fore.CYAN + Style.BRIGHT + "      Starting SDS-RUN Simulation Pipeline")
    print(Fore.CYAN + Style.BRIGHT + "=" * 50)

    try:
        #difining the circuit and saving dirs:
        current_path = os.getcwd()
        #saving:
        if os.path.isabs(config['results_base_path']):
            saving_path = config['results_base_path'].replace("/", '\\')
        else:
            saving_path = os.path.join(current_path, config['results_base_path'])
        #ckt:
        if os.path.isabs(config['circuit_base_path']):
            circuit_base_path = config['circuit_base_path'].replace("/", '\\')
        else:
            circuit_base_path = os.path.join(current_path, config['circuit_base_path'])
        
        print(f"\n{Fore.YELLOW}Preparing simulation parameters...")
        
        user_required_results = config.copy()
        user_required_results.pop('circuit_base_path')
        user_required_results.pop('results_base_path')

        start_hour, n_points = convert_date_to_simulation_time(args.start_date, args.days)
        year = args.start_date[:4]

        print(f"  - Scenario: {args.scenario}")
        print(f"  - Start Date: {args.start_date} (Hour of year: {start_hour})")
        print(f"  - Duration: {args.days} day(s) ({n_points} points)")
        
        # --- 2. GET FILE PATH ---
        print(f"\n{Fore.YELLOW}Locating circuit model file...")
        dss_file = get_dss_master_file_path(
            circuit_base_path=circuit_base_path,
            city=args.city,
            subregion=args.subregion,
            year=year,
            scenario=args.scenario,
            substation=args.substation,
            feeder=args.feeder
        )
        print(f"  - DSS file found at: {dss_file}")


        # --- 3. RUN SIMULATION ---
        print(f"\n{Fore.YELLOW}Initializing and running OpenDSS simulation...")
       
        dss = py_dss_interface.DSS()
        dss_tools.update_dss(dss)
        #opendss simulation here:
        buses_results_dict, source_powers_dict = simulate_dynamic(
            dss=dss,
            dss_file_path=dss_file,
            start_hour=start_hour,
            n_points=n_points, 
            config=config
        )
        print(f"  - {Fore.GREEN}Simulation completed successfully.")

        print(f"\n{Fore.YELLOW}Processing simulation results...")

        #processing dynamic results...
        df_dict_buses = convert_bus_results_to_dataframes(buses_results_dict)
        df_dict_powers = convert_source_powers_to_dataframes(source_powers_dict)
       
       #unifying to a single dict:
        results_dict = df_dict_buses
        results_dict.update(df_dict_powers)

        if config.get('enable_opendss_monitors', False):
            monitor_results_dict = get_monitor_results(dss, dss_tools)
            results_dict.update(monitor_results_dict)

        results_time_stamped = add_datetime_index_to_results(
            results_dict=results_dict,
            start_date_str=args.start_date
        )
       
        print(f"  - Results processed and timestamped.")
        
        # --- 5. SAVE RESULTS ---
        print(f"\n{Fore.YELLOW}Saving results to Parquet files...")
        save_results_as_parquet(
            results_dict=results_time_stamped,
            saving_dir=saving_path,
            year=year,
            scenario=args.scenario,
            start_date=args.start_date,
            n_days=args.days,
            subregion=args.subregion,
            substation=args.substation,
            feeder=args.feeder
        )
        print(f"  - Results saved successfully.")

    except (ValueError, FileNotFoundError) as e:
        print(Fore.RED + f"\nPipeline stopped due to a configuration error: {e}")
        exit(1)
    except Exception as e:
        print(Fore.RED + f"\nAn unexpected error occurred during the pipeline execution: {e}")
        exit(1)

    print(Fore.GREEN + Style.BRIGHT + "\n" + "=" * 50)
    print(Fore.GREEN + Style.BRIGHT + "      SDS-RUN Pipeline Finished Successfully!")
    print(Fore.GREEN + Style.BRIGHT + "=" * 50)