""" 
    Clean and process data to create csv files including CO2 emissions 
"""

import os
import pandas as pd


# path to the input data file
EXCEL_FILE = os.path.join("data", "raw", "activity_data_sweep-input.xlsx")
# path to processed data
OUTPUT = "data/processed/"
# read excel sheets and set sheet_name to none to create a dataframe for each sheet
sheets = pd.read_excel(EXCEL_FILE, sheet_name=None)
# emission factor data
ef = sheets["EF"]

# rename columns
# def clean_column_name(column):
#     return column.lower().replace(' ', '_')

# columns_dict = dict()

# for c in ef.columns:
#     columns_dict[c] = clean_column_name(c)


# ef = ef.rename(columns=columns_dict)


# check duplicates & na
def check_duplicates_na(df):
    """function to check duplicates and nan values in the data"""
    return df.duplicated().sum(), df.isna().sum()


print(check_duplicates_na(ef))
# print(ef.duplicated().sum())
# print(ef.isna().sum())

########### energy_data #############


def process_energy_data() -> pd.DataFrame:
    """clean and process energy data"""

    energy_data = sheets["Energy data"]
    # set first row as header and then drop it
    energy_data = energy_data.rename(columns=energy_data.iloc[0]).drop(
        energy_data.index[0]
    )

    print(energy_data.duplicated().sum())
    print(energy_data.isna().sum())

    # set to 0 nan values in %missing column
    energy_data["%missing"] = energy_data["%missing"].fillna("0")

    # delete caracter /
    energy_data["Pro-rated/not pro-rated"] = energy_data[
        "Pro-rated/not pro-rated"
    ].str.rstrip("/")

    # mapping with ef
    energy_data_merged = energy_data.merge(
        ef, left_on="Emission Factor ID", right_on="Emission Factor ID", how="left"
    )
    # add emissions column to store co2 emissions value
    energy_data_merged["emission_co2e"] = energy_data_merged["Quantity"].astype(
        float
    ) * energy_data_merged["Emission Factor Value"].astype(float)
    # save data to csv file
    energy_data_merged.to_csv(OUTPUT + "Energy_data_cleaned.csv", index=False)

    return energy_data_merged


########## CONCUR 2023 Cars Inc ##############


def process_cars_inc_data() -> pd.DataFrame:
    """clean and process CONCUR 2023 Cars Inc data"""
    cars_inc = sheets["CONCUR 2023 Cars Inc"]
    # set first row as header and then drop it
    cars_inc = cars_inc.rename(columns=cars_inc.iloc[0]).drop(cars_inc.index[0])
    check_duplicates_na(cars_inc)

    # drop duplicates
    cars_inc = cars_inc.drop_duplicates()
    # mapping with EF
    cars_inc_merged = cars_inc.merge(
        ef, left_on="Emission Factor ID", right_on="Emission Factor ID", how="left"
    )

    cars_inc_merged["emission_co2e"] = cars_inc_merged["Quantity"].astype(
        float
    ) * cars_inc_merged["Emission Factor Value"].astype(float)

    cars_inc_merged.to_csv(OUTPUT + "CONCUR_2023_Cars_Inc_cleaned.csv", index=False)

    return cars_inc_merged


############## Procurement Castel #################


def process_proc_cast_data() -> pd.DataFrame:
    """clean and process Procurement Castel data"""
    proc_cast = sheets["Procurement Castel"]

    # set the corresponding emission factor id
    proc_cast.loc[0:12, "Emission Factor ID"] = "259795"

    # convert t quantity to kg
    proc_cast.loc[proc_cast["Unit"] == "t", "Quantity in kg"] *= 1000

    # change t unit to kg
    proc_cast.loc[proc_cast["Unit"] == "t", "Unit"] = "kg"

    # convert Emission Factor ID to int to merge with EF
    proc_cast["Emission Factor ID"] = proc_cast["Emission Factor ID"].astype(int)

    # mapping EF
    proc_cast_merged = proc_cast.merge(
        ef, left_on="Emission Factor ID", right_on="Emission Factor ID", how="left"
    )

    proc_cast_merged["emission_co2e"] = proc_cast_merged["Quantity in kg"].astype(
        float
    ) * proc_cast_merged["Emission Factor Value"].astype(float)

    proc_cast_merged.to_csv(OUTPUT + "procurement_castel_cleaned.csv", index=False)

    return proc_cast_merged
