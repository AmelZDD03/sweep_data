""" 
    - Clean and process energy_data, procurement Castel data and Concur 2023 Cars Inc data 
    - Compute the co2e emissions conversions
    - Function to Load transformed data into csv files including CO2 emissions 
"""

import pandas as pd


########### energy_data #############


def lower_upper_bound(data: pd.DataFrame, column: str):
    """compute quantiles, IQR to detect outliers

    Args:
        data (dataframe): the data to use
        column (str): column to use

    Returns:
        tuple: tuple with lower and upper bound to detect outliers
    """
    # compute quantiles and IQR
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1

    # compute lower ad upper bounds to detect outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    return lower_bound, upper_bound


def process_energy_data(
    energy_data: pd.DataFrame, emission_factor_data: pd.DataFrame
) -> pd.DataFrame:
    """function to clean and process energy_data including :
       table header, missing values, clean caracters, detect and clean outliers,
       mapping with emission factor data and compute co2e emissions

    Args:
        energy_data (pd.DataFrame): energy data to process
        emission_factor_data (pd.DataFrame): emission factor data for mapping

    Returns:
        pd.DataFrame: cleand and merged data
    """
    # set first row as header and then drop it
    energy_data = energy_data.rename(columns=energy_data.iloc[0]).drop(
        energy_data.index[0]
    )

    # set to 0 nan values in %missing column
    energy_data["%missing"] = energy_data["%missing"].fillna("0")

    # delete caracter /
    energy_data["Pro-rated/not pro-rated"] = energy_data[
        "Pro-rated/not pro-rated"
    ].str.rstrip("/")

    # convert quantity column type to float
    energy_data["Quantity"] = energy_data["Quantity"].astype(float)

    # get outliers from Quantity column
    lower_bound, upper_bound = lower_upper_bound(energy_data, "Quantity")
    outliers = (energy_data["Quantity"] < lower_bound) | (
        energy_data["Quantity"] > upper_bound
    )

    # replace outliers by median of GAZ type (Check with business team to decide how to handle it)
    energy_data.loc[outliers, "Quantity"] = energy_data[(energy_data["Type"] == "Gas")][
        "Quantity"
    ].median()

    # mapping with emissions factor data
    energy_data_merged = energy_data.merge(
        emission_factor_data,
        left_on="Emission Factor ID",
        right_on="Emission Factor ID",
        how="left",
    )
    # add emissions column to store co2 emissions value
    energy_data_merged["emission_co2e"] = energy_data_merged["Quantity"].astype(
        float
    ) * energy_data_merged["Emission Factor Value"].astype(float)
    energy_data_merged = energy_data_merged.drop(
        ["Emission Factor Value", "Emission Factor Name", "Emission Factor Unit"],
        axis=1,
    )

    return energy_data_merged


########## CONCUR 2023 Cars Inc ##############


def process_cars_inc_data(
    cars_inc: pd.DataFrame, emission_factor_data: pd.DataFrame
) -> pd.DataFrame:
    """function to clean and process CONCUR 2023 Cars Inc data

    Args:
        cars_inc (pd.DataFrame): data to process
        emission_factor_data (pd.DataFrame): emission factor data for mapping
    Returns:
        pd.DataFrame: cleaned and merged data
    """

    # set first row as header and then drop it
    cars_inc = cars_inc.rename(columns=cars_inc.iloc[0]).drop(cars_inc.index[0])

    # drop duplicates
    cars_inc = cars_inc.drop_duplicates()
    # mapping with EF
    cars_inc_merged = cars_inc.merge(
        emission_factor_data,
        left_on="Emission Factor ID",
        right_on="Emission Factor ID",
        how="left",
    )
    # create emission_co2e column to add co2e emissions
    cars_inc_merged["emission_co2e"] = cars_inc_merged["Quantity"].astype(
        float
    ) * cars_inc_merged["Emission Factor Value"].astype(float)
    cars_inc_merged = cars_inc_merged.drop(
        ["Emission Factor Value", "Emission Factor Name", "Emission Factor Unit"],
        axis=1,
    )

    return cars_inc_merged


############## Procurement Castel #################


def check_material(material_string: str, emission_factor_data: pd.DataFrame):
    """check for a material name in the emission factor table to match the material type and get the corresponding EF Id.

    Args:
        material_string (str): material name to search
        emission_factor_data (pd.DataFrame): emission factor data table

    Returns:
        None: no matching material
        int : emission factor id
    """
    # set material sting to lower case
    material_string = material_string.lower()

    # search for the material name in emission factor table
    matching = emission_factor_data[
        emission_factor_data["Emission Factor Name"]
        .str.lower()
        .str.contains(material_string)
    ]

    # if material exists than get the corresponding Emission Factor ID
    if not matching.empty:
        return matching.iloc[0]["Emission Factor ID"]

    return None


def process_proc_cast_data(
    proc_cast: pd.DataFrame, emission_factor_data: pd.DataFrame
) -> pd.DataFrame:
    """clean and process Procurement Castel data

    Args:
        proc_cast (pd.DataFrame): Procurement Castel data to process
        emission_factor_data (pd.DataFrame): emission factor data table

    Returns:
        pd.DataFrame: cleaned and merged data
    """

    # get rows without Emission Factor ID
    mask = pd.to_numeric(proc_cast["Emission Factor ID"], errors="coerce").isna()
    rows_without_id = proc_cast[mask]

    # apply check_material function to each row and set the corresponding Emission Factor ID
    rows_without_id.loc[:, "Emission Factor ID"] = rows_without_id["Material"].apply(
        lambda x: check_material("aluminum", emission_factor_data)
    )

    # set back the mask data to the original table
    proc_cast.loc[mask, "Emission Factor ID"] = rows_without_id["Emission Factor ID"]

    # convert t quantity to kg
    proc_cast.loc[proc_cast["Unit"] == "t", "Quantity in kg"] *= 1000

    # change t unit to kg
    proc_cast.loc[proc_cast["Unit"] == "t", "Unit"] = "kg"

    # convert Emission Factor ID to int to merge with EF
    proc_cast["Emission Factor ID"] = proc_cast["Emission Factor ID"].astype(int)

    # mapping emission factor
    proc_cast_merged = proc_cast.merge(
        emission_factor_data,
        left_on="Emission Factor ID",
        right_on="Emission Factor ID",
        how="left",
    )
    # create emission_co2e column to add co2e emissions
    proc_cast_merged["emission_co2e"] = proc_cast_merged["Quantity in kg"].astype(
        float
    ) * proc_cast_merged["Emission Factor Value"].astype(float)
    proc_cast_merged = proc_cast_merged.drop(
        ["Emission Factor Value", "Emission Factor Name", "Emission Factor Unit"],
        axis=1,
    )

    return proc_cast_merged


def df_to_csv(data: pd.DataFrame, output_path, filename):
    """load transformed data to csv files in the output file

    Args:
        data (pd.DataFrame): data to load
        output_path (str): output path to store csv files
        filename (str): csv file name
    """
    data.to_csv(output_path + filename + ".csv", index=False)
