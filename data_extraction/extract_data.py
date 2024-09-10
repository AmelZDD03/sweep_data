"""Script to extract data from Sweep API, 
   process it and visualise the emissions of CO2 
   for each facility in 2022
"""

import os
import pandas as pd
import requests
from dotenv import load_dotenv
import plotly.express as px

# load the API key from .env file
load_dotenv()


def extract_data() -> pd.DataFrame:
    """
    Function to extract data from API, process it
    and return agregated data of emissions and facilities
    """
    # set the api key, url, headers and parameters
    api_key = os.getenv("X_Api_Key")
    api_url = "https://api.sweep.net/api/v1/measurements"
    headers = {"X-Api-Key": api_key}
    params = {
        "start_date": "2022-01-01",
        "end_date": "2022-12-31",
        # "format": "csv",
        # "per_page": 100,
    }

    # make a GET request to the specified API endpoint
    response = requests.get(api_url, headers=headers, params=params)

    # check if HTTP request is successful
    if response.status_code == 200:
        # parse the JSON response to extract the data
        data = response.json()
        print("Données récupérées avec succès.")
    else:
        print(f"Erreur {response.status_code} : {response.text}")

    # Extract the measurments data
    measurements = data["measurements"]

    # list to store the extracted data (facility and emission)
    emission_data = []

    # iterate over data and extract Facility & resultValue columns
    for measure in measurements:
        facility = measure["customerData"]["Facility"]
        emission = measure["resultValue"]
        # append data to list
        emission_data.append({"Facility": facility, "Emissions": emission})

    # convert list to dataframe
    df = pd.DataFrame(emission_data)

    # agregate dataframe by facility and sum the emissions
    emissions_by_facility = df.groupby("Facility").sum().reset_index()
    return emissions_by_facility


def facilities_graph(df):
    """Function to create a bar chart visualizing
       the total emissions for each facility
    """

    fig = px.bar(
        df,
        x="Facility",
        y="Emissions",
        title="CO2 Emissions per Facility in 2022",
        labels={"Emissions": "CO2 Emissions", "Facility": "Facility name"},
        color="Emissions",
        hover_data={
            "Facility": True,
            "Emissions": ":.2f",
        },
        height=600,
    )

    # update layout figure and customize it
    fig.update_layout(
        title_font_size=24,
        title_x=0.5,  # Centrer le titre
        xaxis_title="Facility",
        yaxis_title="CO₂ Emissions",
        font={"family": "Arial", "size": 14},
        hoverlabel={"bgcolor": "white", "font_size": 14},  # hover label appearance
        paper_bgcolor="rgb(243, 243, 243)",  # backgound color
    )
    # add interactive annotations
    fig.update_traces(texttemplate="%{y:.2f}", textposition="outside")
    # save the chart as an html file
    fig.write_html("output_graph/emissions_facility_2022.html")

