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


def convert_bus_results_to_dataframes(
    buses_results_dict: Dict[str, List[List[float]]]
) -> Dict[str, pd.DataFrame]:
    """
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

def convert_power_result_to_dataframe(results_list: List[List[float]]):
    """
    Converts a list of power results into a pandas DataFrame with labeled columns.
    
    Args:
        results_list (List[List[float]]): List of lists containing power measurements
                                         Each inner list should have 6 values [P1,Q1,P2,Q2,P3,Q3]
    
    Returns:
        pd.DataFrame: DataFrame with columns ['P_1', 'Q_1', 'P_2', 'Q_2', 'P_3', 'Q_3']
        
    Raises:
        ValueError: If any row in results_list doesn't have exactly 6 values
    """
    if not results_list:
        return pd.DataFrame(columns=POWER_COLUMN_MAP)
    # Validate input data
    if any(len(row) != 6 for row in results_list):
        raise ValueError("Each power measurement must contain exactly 6 values (P1,Q1,P2,Q2,P3,Q3)")
    # Create DataFrame with predefined column names
    df = pd.DataFrame(data=results_list, columns=POWER_COLUMN_MAP)
    df = df.astype(float)
    return df