import os
import pandas as pd
from dotenv import load_dotenv
from extract_data.extract_data import extract_data, data_viz
from transform_data.transform import (
    df_to_csv,
    process_cars_inc_data,
    process_energy_data,
    process_proc_cast_data,
)

load_dotenv()
############### Exercice 1 ##########################

# path to the input data file
EXCEL_FILE = os.path.join("data", "raw", "activity_data_sweep-input.xlsx")
# path to processed data
OUTPUT = "data/processed/"
# output path for graphs
OUTPUT_GRAPHS = "output_graph/"
# read excel sheets and set sheet_name to none to create a dataframe for each sheet
sheets = pd.read_excel(EXCEL_FILE, sheet_name=None)

# extract sheets
emission_factor_data = sheets["EF"]
energy_data = sheets["Energy data"]
cars_inc_data = sheets["CONCUR 2023 Cars Inc"]
proc_cast_data = sheets["Procurement Castel"]

# transform data
energy_data_processed = process_energy_data(energy_data, emission_factor_data)
cars_inc_data_processed = process_cars_inc_data(cars_inc_data, emission_factor_data)
proc_cast_data_processed = process_proc_cast_data(proc_cast_data, emission_factor_data)

# load to csv files
df_to_csv(energy_data_processed, OUTPUT, "energy_data_processed")
df_to_csv(cars_inc_data_processed, OUTPUT, "cars_inc_data_processed")
df_to_csv(proc_cast_data_processed, OUTPUT, "proc_cast_data_processed")


############### Exercice 2 ##########################
api_key = os.getenv("X_Api_Key")
api_url = os.getenv("api_url")
emissions_by_facility = extract_data(api_url, api_key, "2022-01-01", "2022-12-31")
data_viz(
    emissions_by_facility,
    "Facility",
    "Emissions",
    "CO2 Emissions per Facility in 2022",
    OUTPUT_GRAPHS,
    "emissions_facility_2022",
)
