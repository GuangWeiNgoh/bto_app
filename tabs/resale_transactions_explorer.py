import streamlit as st
import json
import requests
import time
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import os
import zipfile
import pickle

# File path for storing the data locally
LOCAL_DATA_ZIP_PATH = "resale_data.zip"
PICKLE_FILE_NAME = "resale_data.pkl"

# Function to load data from the ZIP file if available, else fetch new data
def load_or_fetch_data():
    # Check if the local ZIP file exists and load it if it does
    if os.path.exists(LOCAL_DATA_ZIP_PATH):
        with zipfile.ZipFile(LOCAL_DATA_ZIP_PATH, 'r') as zip_ref:
            with zip_ref.open(PICKLE_FILE_NAME) as pkl_file:
                data = pickle.load(pkl_file)
        return data
    else:
        # Fetch data and save to local ZIP file if not available
        data = fetch_full_data()
        save_data_to_zip(data)
        return data
    
# Function to save the data to a ZIP file with higher compression
def save_data_to_zip(data):
    with zipfile.ZipFile(LOCAL_DATA_ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_ref:
        with zip_ref.open(PICKLE_FILE_NAME, 'w') as pkl_file:
            pickle.dump(data, pkl_file)

# Function to get the modified date of the ZIP file
def get_zip_modified_date(LOCAL_DATA_ZIP_PATH):
    # Get the last modified timestamp
    modified_time = os.path.getmtime(LOCAL_DATA_ZIP_PATH)
    # Convert to a datetime object
    return datetime.fromtimestamp(modified_time)
    
# Button to fetch the latest data and update the ZIP file
def update_data():
    data = fetch_full_data()
    save_data_to_zip(data)
    st.success("Data updated successfully!")
    st.session_state.data = data

# Fetching the collection metadata from the main API
def fetch_collection_metadata(collection_id):
    url = f"https://api-production.data.gov.sg/v2/public/api/collections/{collection_id}/metadata"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch collection metadata.")
        return None
    
# Function to fetch data from each child dataset
def fetch_dataset(dataset_id):
    base_url = "https://api-production.data.gov.sg"
    url = base_url + f"/v2/public/api/datasets/{dataset_id}/metadata"
    response = requests.get(url)
    data = response.json()['data']
    columnMetadata = data.pop('columnMetadata', None)
    
    # initiate download
    initiate_download_response = requests.get(
        f"https://api-open.data.gov.sg/v1/public/api/datasets/{dataset_id}/initiate-download",
        headers={"Content-Type":"application/json"},
        json={}
    )

    MAX_POLLS = 5
    for i in range(MAX_POLLS):
        poll_download_response = requests.get(
            f"https://api-open.data.gov.sg/v1/public/api/datasets/{dataset_id}/poll-download",
            headers={"Content-Type":"application/json"},
            json={}
        )
        poll_data = poll_download_response.json()
        if "url" in poll_data['data']:
            DOWNLOAD_URL = poll_data['data']['url']
            df = pd.read_csv(DOWNLOAD_URL)
            return df  # Return data as soon as it's fetched successfully
        time.sleep(3)
    
    st.warning(f"Failed to fetch data for dataset {dataset_id} after {MAX_POLLS} attempts.")
    return pd.DataFrame()  # Return empty DataFrame if download fails

def fetch_full_data():
    with st.spinner("Fetching Resale Flat Transactions Data from data.gov.sg ..."):
        collection_id = 189  # Collection ID for HDB resale prices
        collection_data = fetch_collection_metadata(collection_id)

        if collection_data:
            # Extract metadata and list of child datasets
            metadata = collection_data.get("data", {}).get("collectionMetadata", {})
            #st.subheader(metadata.get("name", "Resale Flat Prices"))
            #st.write(f"**Description:** {metadata.get('description', 'No description available')}")

            # Prepare to collect records data from each child dataset
            all_records = []
            datasets = metadata.get("childDatasets", [])

            if datasets:
                for dataset_id in datasets:
                    df = fetch_dataset(dataset_id)
                    all_records.append(df)  # Append each dataset's DataFrame to all_records
                
                # Concatenate all DataFrames if any data was fetched
                if all_records:
                    full_data = pd.concat(all_records, ignore_index=True)
                    # Convert all values in "flat_model" to uppercase for standardisation
                    full_data['flat_model'] = full_data['flat_model'].str.upper()
                    #full_data['remaining_lease'] = pd.to_numeric(full_data['remaining_lease'], errors='coerce')

                    full_data.fillna({
                        'month': 'Unknown',
                        'town': 'Unknown',
                        'flat_type': 'Unknown',
                        'block': 'Unknown',
                        'street_name': 'Unknown',
                        'storey_range': 'Unknown',
                        'floor_area_sqm': -1,
                        'flat_model': 'Unknown',
                        'lease_commence_date': -1,
                        #'remaining_lease': 'Unknown',
                        'resale_price': -1
                    }, inplace=True)

                    full_data['remaining_lease'] = full_data['remaining_lease'].str.split(' ').str[0]

                    # Calculate the remaining lease based on the lease_commence_date for each row
                    full_data['calculated_remaining_lease'] = 100 - (datetime.now().year - full_data['lease_commence_date'])

                    # Use fillna to replace NaN values in remaining_lease with values from calculated_remaining_lease
                    full_data['remaining_lease'] = full_data['remaining_lease'].fillna(full_data['calculated_remaining_lease'])

                    # Drop the temporary column if it is no longer needed
                    full_data.drop(columns=['calculated_remaining_lease'], inplace=True)

                    full_data['flat_type'] = full_data['flat_type'].str.replace('-', ' ')


                    full_data['month'] = full_data['month'].astype(str)  
                    full_data['town'] = full_data['town'].astype(str)
                    full_data['flat_type'] = full_data['flat_type'].astype(str) 
                    full_data['block'] = full_data['block'].astype(str) 
                    full_data['street_name'] = full_data['street_name'].astype(str)  
                    full_data['storey_range'] = full_data['storey_range'].astype(str) 
                    full_data['floor_area_sqm'] = full_data['floor_area_sqm'].astype(float) 
                    full_data['flat_model'] = full_data['flat_model'].astype(str) 
                    full_data['lease_commence_date'] = full_data['lease_commence_date'].astype(int)
                    full_data['remaining_lease'] = full_data['remaining_lease'].astype(int)  
                    full_data['resale_price'] = full_data['resale_price'].astype(float)  

                    full_data = full_data.sort_values(by='month', ascending=False).reset_index(drop=True)
                    full_data.reset_index(drop=True, inplace=True)

                    return full_data
            else:
                st.warning("No datasets found in the response.")

def alt_plot_price_by_town(data):
    # Group by town and calculate the average resale price
    avg_price_by_town = data.groupby('town')['resale_price'].mean().sort_values(ascending=False)
    
    # Convert to DataFrame
    avg_price_by_town_df = avg_price_by_town.reset_index()
    avg_price_by_town_df.columns = ['Town', 'Average Resale Price']

    # Create an Altair bar chart with color gradient
    chart = alt.Chart(avg_price_by_town_df).mark_bar().encode(
        x=alt.X('Average Resale Price', title='Average Resale Price'),
        y=alt.Y('Town', sort='-x', title='Town'),  # Sort by x-axis values
        color=alt.Color('Average Resale Price', 
                        scale=alt.Scale(scheme='blues'), 
                        legend=None),  # Gradient based on resale price
        tooltip=['Town', 'Average Resale Price']
    ).properties(
        title='Average Resale Price by Town',
        width=700
    )

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)

def alt_plot_price_by_flat_type(data):
    # Group by flat type and calculate the average resale price
    avg_price_by_flat_type = data.groupby('flat_type')['resale_price'].mean().sort_values(ascending=False)

    # Convert to DataFrame
    avg_price_by_flat_type_df = avg_price_by_flat_type.reset_index()
    avg_price_by_flat_type_df.columns = ['Flat Type', 'Average Resale Price']

    # Create an Altair bar chart with color gradient
    chart = alt.Chart(avg_price_by_flat_type_df).mark_bar().encode(
        x=alt.X('Average Resale Price', title='Average Resale Price'),
        y=alt.Y('Flat Type', sort='-x', title='Flat Type'),  # Sort by x-axis values
        color=alt.Color('Average Resale Price', 
                        scale=alt.Scale(scheme='greens'), 
                        legend=None),  # Gradient based on resale price
        tooltip=['Flat Type', 'Average Resale Price']
    ).properties(
        title='Average Resale Price by Flat Type',
        width=700
    )

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)

def alt_plot_price_by_year(data):
    # Extract the year from the 'month' column
    data['year'] = pd.to_datetime(data['month']).dt.year

    # Calculate the average resale price per year
    avg_price_by_year = data.groupby('year', as_index=False)['resale_price'].mean()
    avg_price_by_year.columns = ['Year', 'Average Resale Price']

    # Create an Altair line chart
    line_chart = alt.Chart(avg_price_by_year).mark_line(point=True).encode(
        x=alt.X('Year:O', title='Year'),  # specify 'Year' as ordinal if it's discrete
        y=alt.Y('Average Resale Price', title='Average Resale Price'),
        tooltip=['Year', 'Average Resale Price']
    ).properties(
        title="Average Resale Price Over the Years",
        width=700,
        height=400
    )

    st.altair_chart(line_chart, use_container_width=True)


# Main function to display the resale prices
def display():
    st.title("🏠 HDB Resale Transactions Explorer")
    st.write("Explore resale flat transactions data. HDB resale prices data from data.gov.sg. Includes data from 1990 - Present.")

    # Get the modified date
    if os.path.exists(LOCAL_DATA_ZIP_PATH):
        modified_date = get_zip_modified_date(LOCAL_DATA_ZIP_PATH)
        last_updated_message = f"Last updated on: **{modified_date.strftime('%Y-%m-%d %H:%M:%S')} (GMT)**"
    else:
        last_updated_message = "ZIP file not found!"

    button_col, note_col, spacer = st.columns([1.5, 10, 5])  # Adjust the width ratio as needed

    # Create a placeholder for messages
    message_placeholder = st.empty()

    with button_col:
        if st.button("Update Data"):
            with message_placeholder.container():
                update_data()

    with note_col:
        st.write("Click to update with the most recent transactions data from data.gov.sg. " + last_updated_message)


    # Initialize session state data
    if 'data' not in st.session_state:
        st.session_state.data = load_or_fetch_data()
        st.session_state.filtered_data = st.session_state.data
        st.session_state.selected_years = (int(st.session_state.data['month'].str[:4].min()), int(st.session_state.data['month'].str[:4].max()))
        st.session_state.selected_month = []
        st.session_state.selected_town = []
        st.session_state.selected_flat_type = []
        st.session_state.selected_storey_range = []
        st.session_state.floor_area_sqm_range = (
            int(st.session_state.data['floor_area_sqm'].min()), 
            int(st.session_state.data['floor_area_sqm'].max())
        )
        st.session_state.selected_flat_model = []
        st.session_state.lease_commence_date_range = (
            int(st.session_state.data['lease_commence_date'].min()), 
            datetime.now().year
        )
        st.session_state.remaining_lease_range = (
            int(st.session_state.data['remaining_lease'].min()), 
            int(st.session_state.data['remaining_lease'].max())
        )
        st.session_state.resale_price_range = (
            int(st.session_state.data['resale_price'].min()), 
            int(st.session_state.data['resale_price'].max())
        )

    data = st.session_state.data

    # Get min and max year from the month data
    min_year = int(data['month'].str[:4].min())
    max_year = int(data['month'].str[:4].max())

    # Create a slider for year selection
    selected_years = st.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=st.session_state.selected_years,
        step=1
    )

    # Create two rows of filters
    row1_col1, row1_col2, row1_col3 = st.columns(3)

    with row1_col1:
        # Filter months based on the selected year range
        years_range = list(range(selected_years[0], selected_years[1] + 1))
        months_in_years = data[data['month'].str[:4].isin(map(str, years_range))]['month'].unique()
        selected_month = st.multiselect(
            "Select Month", 
            options=sorted(months_in_years, reverse=True), 
            default=st.session_state.selected_month
        )
        selected_storey_range = st.multiselect(
            "Select Storey Range", 
            options=sorted(data['storey_range'].unique()), 
            default=st.session_state.selected_storey_range
        )

    with row1_col2:
        selected_town = st.multiselect(
            "Select Town", 
            options=sorted(data['town'].unique()), 
            default=st.session_state.selected_town
        )
        selected_flat_model = st.multiselect(
            "Select Flat Model", 
            options=sorted(data['flat_model'].unique()), 
            default=st.session_state.selected_flat_model
        )

    with row1_col3:
        selected_flat_type = st.multiselect(
            "Select Flat Type", 
            options=sorted(data['flat_type'].unique(), reverse=True), 
            default=st.session_state.selected_flat_type
        )

    # Second row for sliders
    row2_col1, spacer1, row2_col2 = st.columns([1,0.05,1])

    with row2_col1:
        floor_area_sqm_range = st.slider(
            "Select Floor Area (sqm)", 
            min_value=int(data['floor_area_sqm'].min()), 
            max_value=int(data['floor_area_sqm'].max()), 
            value=st.session_state.floor_area_sqm_range,
            step=1
        )
        
        remaining_lease_range = st.slider(
            "Select Remaining Lease (Years)", 
            min_value=int(data['remaining_lease'].min()), 
            max_value=int(data['remaining_lease'].max()), 
            value=st.session_state.remaining_lease_range,
            step=1
        )    

    with row2_col2:
        lease_commence_date_range = st.slider(
            "Select Lease Commence Date", 
            min_value=int(data['lease_commence_date'].min()), 
            max_value=datetime.now().year, 
            value=st.session_state.lease_commence_date_range,
            step=1
        )
        
        resale_price_range = st.slider(
            "Select Resale Price ($)", 
            min_value=int(data['resale_price'].min()), 
            max_value=int(data['resale_price'].max()), 
            value=st.session_state.resale_price_range,
            step=1000
        )

    # Create a row for the Search button and warning
    button_col, warning_col, spacer2 = st.columns([1, 6, 9])  # Adjust the width ratio as needed

    with button_col:
        if st.button("Search"):
            # Store selections in session state
            st.session_state.selected_years = selected_years
            st.session_state.selected_month = selected_month
            st.session_state.selected_town = selected_town
            st.session_state.selected_flat_type = selected_flat_type
            st.session_state.selected_storey_range = selected_storey_range
            st.session_state.floor_area_sqm_range = floor_area_sqm_range
            st.session_state.selected_flat_model = selected_flat_model
            st.session_state.lease_commence_date_range = lease_commence_date_range
            st.session_state.remaining_lease_range = remaining_lease_range
            st.session_state.resale_price_range = resale_price_range
            
            # Initialize filtered data with the full dataset
            filtered_data = data.copy()
            
            # Apply filters only if selections are made
            if selected_years:
                # Get the start and end years from the selected_years tuple
                start_year, end_year = selected_years

                # Filter the data to include only rows with months in the selected year range
                filtered_data = filtered_data[
                    filtered_data['month'].str[:4].astype(int).between(start_year, end_year)
                ]
            if selected_month:
                filtered_data = filtered_data[filtered_data['month'].isin(selected_month)]
            if selected_town:
                filtered_data = filtered_data[filtered_data['town'].isin(selected_town)]
            if selected_flat_type:
                filtered_data = filtered_data[filtered_data['flat_type'].isin(selected_flat_type)]
            if selected_storey_range:
                filtered_data = filtered_data[filtered_data['storey_range'].isin(selected_storey_range)]
            if selected_flat_model:
                filtered_data = filtered_data[filtered_data['flat_model'].isin(selected_flat_model)]

            # Apply slider filters
            filtered_data = filtered_data[
                (filtered_data['floor_area_sqm'].between(*floor_area_sqm_range)) &
                (filtered_data['lease_commence_date'].between(*lease_commence_date_range)) &
                (filtered_data['remaining_lease'].between(*remaining_lease_range)) &
                (filtered_data['resale_price'].between(*resale_price_range))
            ]

            # Store the filtered data in session state
            st.session_state.filtered_data = filtered_data

    with warning_col:
        st.write("Note: Results will update only after clicking on the Search button.")

    # Display the filtered data or the full data if no search has been performed yet
    filtered_data = st.session_state.get('filtered_data', data)

    # Save a separate DataFrame for display
    display_data = filtered_data.copy()

    # Convert lease_commence_date to string format without commas
    display_data['lease_commence_date'] = display_data['lease_commence_date'].astype(str)

    # Add vertical spacing above using markdown
    st.markdown("<br>" * 1, unsafe_allow_html=True)  # Adjust the number for more spacing

    # Create a row for the Search button and warning
    num_results, spacer3, sort_warning = st.columns([1, 2, 1.1])  # Adjust the width ratio as needed

    with num_results:
        # Display the number of results found above the table
        st.write(f"Resale Flat Records Found: **{len(display_data)}**")

    with sort_warning:
        st.write("Sort by clicking the column headers (<~150k Results)")

    st.dataframe(display_data, hide_index=True, use_container_width=True)  # Ensure the table fills the width

    # Add vertical spacing above using markdown
    st.markdown("<br>" * 1, unsafe_allow_html=True)  # Adjust the number for more spacing

    alt_plot_price_by_town(display_data)
    alt_plot_price_by_flat_type(display_data)
    alt_plot_price_by_year(display_data)

if __name__ == "__main__":
    display()
