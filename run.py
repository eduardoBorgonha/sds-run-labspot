import argparse
from sds_run.config_loader import load_config
from sds_run.main import main_pipeline
from colorama import init

def main():

    init(autoreset=True)
    parser = argparse.ArgumentParser(
        description='Run a Quasi-Static Time Series simulation for a specified SMART-DS circuit.')   
    parser.add_argument(
        "scenario",
        type=str, 
        help="The name of the simulation scenario (e.g., 'base_timeseries'")
    parser.add_argument(
        "start_date",
        type=str ,
        help="The simulation start date in YYYY-MM-DD format")
    parser.add_argument(
        "days",
        type=int,
        help="The number of days to simulate."
    )
    
    # --- Argumentos Opcionais (com valores padrão) ---
    parser.add_argument(
        "-c", "--city", 
        type=str, 
        default="SFO",
        help="City code for the dataset. Default: SFO."
    )
    parser.add_argument(
        "-sr", "--subregion", 
        type=str, 
        default="P13U",
        help="Sub-region code for the dataset. Default: P13U."
    )
    parser.add_argument(
        "-ss", "--substation", 
        type=str, 
        default=None,
        help="Substation name. If omitted, the entire subregion is simulated."
    )
    parser.add_argument(
        "-f", "--feeder", 
        type=str, 
        default="p13uhs0_1247--p13udt13213",
        help="If omitted, the entire substation is simulated. Requires --substation to be set."
    )

    args = parser.parse_args()

    #validação lógica dos argumentos:
    if args.feeder and not args.substation:
        parser.error("The --feeder argument requires the --substation argument to be specified.")
    try:
        # Load configuration from the YAML file
        config = load_config('config.yaml')
        
        # Call the main pipeline orchestrator
        main_pipeline(args, config)

    except (FileNotFoundError, ValueError) as e:
        print(e) # Errors from config_loader will be printed in red
        # Exit with a non-zero status code to indicate failure
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()
    