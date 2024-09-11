"""Script to extract data from Sweep API, 
   process it and visualise the emissions of CO2 
   for each facility in 2022
"""

import pandas as pd
import requests
import plotly.express as px


def extract_data(api_url, api_key, start_date, end_date) -> pd.DataFrame:
    """Function to extract data from API, process it
    and return agregated data of emissions and facilities

    Args:
        api_url (str): api url
        api_key (str): api key
        start_date (str): starte date
        end_date (str): end date

    Returns:
        pd.DataFrame: co2 emissions by facilities
    """
    # set the headers and parameters
    headers = {"X-Api-Key": api_key}
    params = {"start_date": start_date, "end_date": end_date}

    # make a GET request to the specified API endpoint
    response = requests.get(api_url, headers=headers, params=params)

    # check if HTTP request is successful
    if response.status_code == 200:
        # parse the JSON response to extract the data
        data = response.json()
        print("Data Extracted Successfully.")

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

    else:
        return f"Erreur {response.status_code} : {response.text}"


def data_viz(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    output_graphs: str,
    html_file_name: str,
):
    """Function to create a bar chart visualizing
       the total emissions for each facility

    Args:
        df (pd.DataFrame): data to use
        x (str): column name for x axis
        y (str): column name for y axis
        title (str): title of graph
        output_graphs (str): output path
        html_file_name (str): html file name
    """

    fig = px.bar(
        df,
        x=x,
        y=y,
        title=title,
        color=y,
        hover_data={
            x: True,
            y: ":.2f",
        },
        height=600,
    )

    # update layout figure and customize it
    fig.update_layout(
        title_font_size=24,
        title_x=0.5,  # Center title
        xaxis_title=x,
        yaxis_title=y,
        font={"family": "Arial", "size": 14},
        paper_bgcolor="rgb(243, 243, 243)",  # backgound color
    )
    # add interactive annotations
    fig.update_traces(texttemplate="%{y:.2f}", textposition="outside")
    # save the chart as an html file
    fig.write_html(output_graphs + html_file_name + ".html")
