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

def get_source_power_results(dss: py_dss_interface.DSS, source_powers_results_dict: Dict[str, List]):
    """
    Gets the power from all Vsources in the circuit for the current time step
    and appends it to the results dictionary.
    """
    sources = dss.vsources.names
    for source in sources:
        dss.vsources.name = source
        raw_powers = dss.cktelement.powers #it comes with 6 zeros for a reason and all powers negative
        powers_no_zeros = [i*-1 for i in raw_powers if i != 0.0]
        source_powers_results_dict[source].append(powers_no_zeros)
    return source_powers_results_dict