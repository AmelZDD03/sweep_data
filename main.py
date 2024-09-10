from data_extraction.extract_data import extract_data, facilities_graph
from data_processing.data_cleaning import (
    process_cars_inc_data,
    process_energy_data,
    process_proc_cast_data,
)

energy_data = process_energy_data()
proc_cast_data = process_proc_cast_data()
cars_inc_data = process_cars_inc_data()

emissions_by_facility = extract_data()
facilities_graph(emissions_by_facility)
