import pandas as pd
from typing import Dict, List, Optional
import py_dss_interface
import py_dss_toolkit as dss_tools

PHASE_COLUMN_MAP: Dict[int, List[str]] = {
    2: ['V_A', 'Angle_A'],  # Monofásico 
    4: ['V_A', 'Angle_A', 'V_B', 'Angle_B'],  # Bifásico 
    6: ['V_A', 'Angle_A', 'V_B', 'Angle_B', 'V_C', 'Angle_C']  # Trifásico
}

POWER_COLUMN_MAP: List[str] = ['P_1', 'Q_1', 'P_2', 'Q_2', 'P_3', 'Q_3']

def get_monitor_results(dss: py_dss_interface.DSS , dss_tools) -> Dict[str, pd.DataFrame]:
    """
     Extracts data from all monitors in the active OpenDSS circuit.

    Args:
        dss (py_dss_interface.DSS): The py-dss-interface DSS object.
        dss_tools: The py-dss-toolkit object.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary where keys are monitor names
                                 and values are DataFrames containing the
                                 monitor's results.
    """
    #checking if are there monitors:
    monitors = dss.monitors.names
    if not monitors:
        print("   - No OpenDSS monitors found in the circuit.")
        return {}
    
    results_dict = {}
    for name in dss.monitors.names:
        monitor_df = dss_tools.results.monitor(name)
        monitor_df = monitor_df.drop(columns=['Hour', 'sec'], errors='ignore')
        monitor_df.columns = monitor_df.columns.str.strip() 
        results_dict[name] = monitor_df

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

        #adicionando o índice de tempo:
        df_copy.index = datetime_index
        timestamped_results[name] = df_copy
        print(f"  -Prepared: {name}")

    return timestamped_results

def convert_bus_results_to_dataframes(
    buses_results_dict: Dict[str, List[List[float]]]
) -> Dict[str, pd.DataFrame]:
    """
    Converts a dictionary of bus voltage results (magnitude and angle) into
    a dictionary of pandas DataFrames. Column names are dynamically assigned
    based on the number of phases detected in the results.

    Args:
        buses_results_dict (Dict[str, List[List[float]]]): A dictionary where keys
            are bus names and values are lists of lists, with each inner list
            containing voltage magnitudes and angles for each time step.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary where keys are bus names and
                                 values are pandas DataFrames with structured
                                 columns for voltage and angle per phase.

    Raises:
        ValueError: If an unexpected number of columns (not 2, 4, or 6) is
                    found in the results for a bus.
    """
    dataframes_dict = {}
    if not buses_results_dict:
        return dataframes_dict

    for bus_name, results_list in buses_results_dict.items():
        if not results_list:
            # Se uma barra não tiver resultados, cria um DataFrame vazio.
            # Não podemos inferir colunas, então ele fica sem.
            df = pd.DataFrame()
            dataframes_dict[bus_name] = df
            continue  # Pula para a próxima iteração do loop

        # Determina os nomes das colunas dinamicamente com base no primeiro resultado.
        num_values = len(results_list[0])
        column_names = PHASE_COLUMN_MAP.get(num_values)

        if column_names is None:
            # "Fail Fast": Se o formato dos dados for inesperado, é melhor
            # levantar um erro claro do que produzir um resultado silenciosamente
            # incorreto.
            raise ValueError(
                f"Número de colunas inesperado ({num_values}) para a barra '{bus_name}'. "
                f"Os valores esperados são 2, 4 ou 6."
            )

        # Cria o DataFrame com os dados e as colunas dinamicamente selecionadas.
        df = pd.DataFrame(data=results_list, columns=column_names)
        df = df.astype(float)
        dataframes_dict[bus_name] = df

    return dataframes_dict

def convert_source_powers_to_dataframes(
    source_powers_results_dict: Dict[str, List[List[float]]]
) -> Dict[str, pd.DataFrame]:
    """
    Converts a dictionary of power results from multiple sources into
    a dictionary of pandas DataFrames.
    """
    dataframes_dict = {}
    if not source_powers_results_dict:
        return dataframes_dict

    for source_name, results_list in source_powers_results_dict.items():
        if any(len(row) != 6 for row in results_list):
            raise ValueError(f"Each power measurement for source '{source_name}' must contain 6 values.")
        
        df = pd.DataFrame(data=results_list, columns=POWER_COLUMN_MAP)
        df = df.astype(float)
        # Adiciona um sufixo para evitar conflito de nomes com outros resultados
        dataframes_dict[f"power_{source_name}"] = df
        
    return dataframes_dict