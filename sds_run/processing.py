import pandas as pd
from typing import Dict
import py_dss_interface
import py_dss_toolkit as dss_tools
from colorama import Fore

def get_monitor_results(dss: py_dss_interface.DSS , dss_tools) -> Dict[str, pd.DataFrame]:
    results_dict = {}
    for name in dss.monitors.names:
        results_dict[name] = dss_tools.results.monitor(name)
    return results_dict

def add_datetime_index_to_results(
        results_dict: Dict[str, pd.DataFrame],
    start_date_str: str,
    stepsize_str: str = '15min'
) -> Dict[str, pd.DataFrame]:
    """
    Substitui o índice numérico dos DataFrames de resultado por um
    DatetimeIndex, baseado na data de início e no stepsize da simulação. Apaga as colunas "Hour" e "sec". Passa os axes por um strip()

    Args:
        results_dict (Dict[str, pd.DataFrame]): Dicionário com os DFs da simulação.
        start_date_str (str): Data de início no formato 'YYYY-MM-DD'.
        stepsize_str (str): Frequência dos dados, no formato de string do pandas (ex: '15min', '1h').

    Returns:
        Dict[str, pd.DataFrame]: Um novo dicionário com os DataFrames atualizados
                                 com um DatetimeIndex.
    """
    if not results_dict:
        print("Warning: Results dictionary is empty.")
        return{}
    #pegando tamanho:
    any_df = next(iter(results_dict.values()))
    n_points = len(any_df)
    
    #corrigindo o início para os primeiros 15 minutos
    start_timestamp = pd.to_datetime(start_date_str)
    # Adiciona a duração do primeiro step para definir o início real do índice
    first_timestamp = start_timestamp + pd.to_timedelta(stepsize_str)

    #criando o índice de tempo:
    datetime_index = pd.date_range(
        start=first_timestamp,
        periods=n_points,
        freq=stepsize_str
    )
    #novo dict:
    timestamped_results = {}
    print(f"  - Adding DatetimeIndex to {len(results_dict)} DataFrames...")
    for name, df in results_dict.items():
        df_copy = df.copy()

        #removendo as colunas "Hour" e "sec"
        cols_to_drop = ['Hour', 'sec']
        df_copy = df_copy.drop(columns=cols_to_drop, errors='ignore')

        #tirando o espaço dos axes:
        df_copy.columns = df_copy.columns.str.strip()
        #adicionando o índice de tempo:
        df_copy.index = datetime_index
        timestamped_results[name] = df_copy
        print(f"  -Prepared: {name}")

    return timestamped_results