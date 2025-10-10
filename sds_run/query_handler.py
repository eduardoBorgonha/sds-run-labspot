import py_dss_interface
import py_dss_toolkit as dss_tools
from typing import List, Dict, Optional

def get_buses_results(
        dss: py_dss_interface.DSS,
        buses_list: List[str],
        buses_results_dict: Dict[str, List]
    ): 
    '''
    Gets the voltages from the specified buses from a POWER FLOW solve. Its used for dynamic monitoring for each bus. See de simulate() function.

    Args:
    dss: dss object from py_dss_interface
    buses_list: list for the specified buses, from config.yaml
    buses_results_dict: dict for store the results from de buses. A list
    '''

    for bus in buses_list:
        dss.circuit.set_active_bus(bus)
        buses_results_dict[bus].append(dss.bus.vmag_angle)

    return buses_results_dict

def get_transformers_results(
        dss: py_dss_interface.DSS,
        transformers_list: List[str],
        transformers_results_dict: Dict[str, List]
    ):
    '''
    Gets the voltages from the specified transformers from a POWER FLOW solve. Its used for dynamic monitoring for each bus. See de simulate() function.

    Args:
    dss: dss object from py_dss_interface
    transformers_list: list for the specified tranfs, from config.yaml
    transformers_results_dict: dict for store the results from de tranfs
    '''
    for transformer in transformers_list:
        dss.transformers.name = transformer
        dss.circuit.set_active_bus(dss.cktelement.bus_names[1])
        transformers_results_dict[transformer].append(dss.bus.vmag_angle)

    return transformers_results_dict

def get_pvsystems_results(
        dss: py_dss_interface.DSS,
        pv_list: List[str],
        pv_results_dict: Dict[str, List]
    ):
    '''
    Gets the voltages from the specified pvsystems from a POWER FLOW solve. Its used for dynamic monitoring for each bus. See de simulate() function.

    Args:
    dss: dss object from py_dss_interface
    pv_list: list for the specified pvs, from config.yaml
    pv_results_dict: dict for store the results from de pvs
    '''
    for pvsystem in pv_list:
        dss.pvsystems.name = pvsystem
        pv_bus = dss.cktelement.bus_names[0]
        dss.circuit.set_active_bus(pv_bus)
        pv_results_dict[pvsystem].append(dss.bus.vmag_angle)
    return pv_results_dict

def get_power_result(dss: py_dss_interface.DSS):
    source = dss.vsources.names[0]
    dss.vsources.name = source
    raw_powers = dss.cktelement.powers #it comes with 6 zeros for a reason and all powers negative
    powers_no_zeros = [i*-1 for i in raw_powers if i != 0.0]
    return powers_no_zeros