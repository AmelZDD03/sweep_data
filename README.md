# Project Description

### Exercise 1: 
  - Extract data from activity_data_sweep_input.xlsx file stored in data/raw.
  - Clean and transform energy data, emission factor data, concur 2023 cars Inc data and Procurement Castel data and compute CO2e emissions after mapping the corresponding emission factor id.
  - Load cleaned and agregated data to CSV files stored in "data/processed".

### Exercise 2: 
  - Extract data from Sweep API.
  - Process data and agregate co2 emissions with facilities data.
  - Visualize the emissions of CO2 for each facility in 2022.


## Used technologies 
Python
Pandas
Plotly
Python-dotenv
Requests
Openpyxl
Pylint

## Run Project

- Make sure you have Docker installed on your system.
### Execution steps
- Clone this repository to your local machine.
- Open a terminal and navigate to the project directory.
- Create a .env file and store the corresponding values of X_Api_Key and api_url.
- Run the following command to launch the project with Docker :  **docker-compose up --build**
-  After execution, the following files will be generated in:
  - data/processed output folder:
    - energy_data_processed.csv: energy data cleaned and processed
    - cars_inc_data_processed.csv: concur 2023 cars Inc data cleaned and processed  
    - proc_cast_data_processed.csv: procurement Castel data cleaned and processed
  - output_graph/ folder:
    - emissions_facility_2022.html: bar chart for the emissions of CO2 for each facility in 2022.



## Data cleaning and processing
  - Delete useless headers and set first row, containing column names, as header.
  - Check duplicates and drop them if exist.
  - Check missing values: 
    - replace by 0 missing values in energy data %missing column (for all Complete status %missing is missing).
    - In procurement Castel data, some emission factor ids were not identified. I Used a function to mapp material name with the emission factor name to get the EF Id. NOTE: For now, I used the given material name Aluminium. But note that aluminum material is in english in the EF data but in french (aluminium) in Proc Castel Data while others are in english. We should consider using english for all material names. In addition, not all material names are listed in the emission factor name. (Check with business team if it's possible to get all the material names)
  - Convert units data to the corresponding units.
  - In Proc Castel Data: Convert quantities to kg where units were in t.
  - In Energy data:
    - Clean pro-rated/not pro-rated column by deleting the slash / caracter.
    - Detected an outlier: For now, I replaced it by the median of the same Type data. However, it needs to be reviewed or checked with the business team, if it's possible, to see if it’s a data entry error or whether it can be corrected or not. The appropriate transformation depends on the use case. For example, if it's for machine learning, we should consider what value would be the most accurate to use.
  
  - Mapping each data table with EF data to compute the co2e emissions.

## Data extract

  - Extract data from Sweep Api using the api key, api url, headers and parameters.
  - Process data to get emissions and facilities.
  - Visualize data for CO2 emissions per facility.


## Functions Docstrings

### Module: extract_data.py    
  - **Function: extract_data**
    - Docstring: Function to extract data from API, process it
    and return agregated data of emissions and facilities

    Args:
        api_url (str): api url
        api_key (str): api key
        start_date (str): starte date
        end_date (str): end date

    Returns:
        pd.DataFrame: co2 emissions by facilities
    

### Module: transform.py
  - **Function: check_material**
    - Docstring: check for a material name in the emission factor table to match the material type and get the corresponding EF Id.

    Args:
        material_string (str): material name to search
        emission_factor_data (pd.DataFrame): emission factor data table

    Returns:
        None: no matching material
        int : emission factor id
    
  - **Function: df_to_csv**
    - Docstring: load transformed data to csv files in the output file

    Args:
        data (pd.DataFrame): data to load
        output_path (str): output path to store csv files
        filename (str): csv file name
    
  - **Function: lower_upper_bound**
    - Docstring: compute quantiles, IQR to detect outliers

    Args:
        data (dataframe): the data to use
        column (str): column to use

    Returns:
        tuple: tuple with lower and upper bound to detect outliers
    
  - **Function: process_cars_inc_data**
    - Docstring: function to clean and process CONCUR 2023 Cars Inc data

    Args:
        cars_inc (pd.DataFrame): data to process
        emission_factor_data (pd.DataFrame): emission factor data for mapping
    Returns:
        pd.DataFrame: cleaned and merged data
    
  - **Function: process_energy_data**
    - Docstring: function to clean and process energy_data including :
       table header, missing values, clean caracters, detect and clean outliers,
       mapping with emission factor data and compute co2e emissions

    Args:
        energy_data (pd.DataFrame): energy data to process
        emission_factor_data (pd.DataFrame): emission factor data for mapping

    Returns:
        pd.DataFrame: cleand and merged data
    
  - **Function: process_proc_cast_data**
    - Docstring: clean and process Procurement Castel data

    Args:
        proc_cast (pd.DataFrame): Procurement Castel data to process
        emission_factor_data (pd.DataFrame): emission factor data table

    Returns:
        pd.DataFrame: cleaned and merged data
    

