import streamlit as st
import json
import requests
import time
import pandas as pd

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
    with st.spinner("Fetching Resale Flat Data from data.gov.sg ..."):
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
                        'remaining_lease': 'Unknown',
                        'resale_price': -1
                    }, inplace=True)

                    full_data['month'] = full_data['month'].astype(str)  
                    full_data['town'] = full_data['town'].astype(str)
                    full_data['flat_type'] = full_data['flat_type'].astype(str) 
                    full_data['block'] = full_data['block'].astype(str) 
                    full_data['street_name'] = full_data['street_name'].astype(str)  
                    full_data['storey_range'] = full_data['storey_range'].astype(str) 
                    full_data['floor_area_sqm'] = full_data['floor_area_sqm'].astype(float) 
                    full_data['flat_model'] = full_data['flat_model'].astype(str) 
                    full_data['lease_commence_date'] = full_data['lease_commence_date'].astype(float)
                    full_data['remaining_lease'] = full_data['remaining_lease'].astype(str)  
                    full_data['resale_price'] = full_data['resale_price'].astype(float)  

                    full_data = full_data.sort_values(by='month', ascending=False).reset_index(drop=True)
                    full_data.reset_index(drop=True, inplace=True)
                    #full_data['lease_commence_date'] = full_data['lease_commence_date'].astype(int)  # Example for float conversion

                    return full_data
            else:
                st.warning("No datasets found in the response.")

# Main function to display the resale prices
def display():
    st.title("🏠 HDB Resale Flat Price History")
    st.write("Latest HDB resale prices data from data.gov.sg. Includes data from 1990 - Present.")

    # Fetch data once and keep it in session state
    if 'data' not in st.session_state:
        st.session_state.data = fetch_full_data()
        st.session_state.filtered_data = st.session_state.data  # Initialize with full data
        st.session_state.selected_month = []
        st.session_state.selected_town = []
        st.session_state.selected_flat_type = []

    data = st.session_state.data

    # Create filter options
    selected_month = st.multiselect("Select Month", options=data['month'].unique(), default=st.session_state.selected_month)
    selected_town = st.multiselect("Select Town", options=data['town'].unique(), default=st.session_state.selected_town)
    selected_flat_type = st.multiselect("Select Flat Type", options=data['flat_type'].unique(), default=st.session_state.selected_flat_type)

    # Search button
    if st.button("Search"):
        # Store selections in session state
        st.session_state.selected_month = selected_month
        st.session_state.selected_town = selected_town
        st.session_state.selected_flat_type = selected_flat_type
        
        # Initialize a condition that is always True
        filtered_data = data.copy()  # Start with the full dataset
        
        # Apply filters only if selections are made
        if selected_month:
            filtered_data = filtered_data[filtered_data['month'].isin(selected_month)]
        if selected_town:
            filtered_data = filtered_data[filtered_data['town'].isin(selected_town)]
        if selected_flat_type:
            filtered_data = filtered_data[filtered_data['flat_type'].isin(selected_flat_type)]

        # Store the filtered data in session state
        st.session_state.filtered_data = filtered_data

    # Display the filtered data or the full data if no search has been performed yet
    filtered_data = st.session_state.get('filtered_data', data)
    
    # Display the DataFrame without flashing
    st.dataframe(filtered_data)

# This is a typical structure for a Streamlit app
if __name__ == "__main__":
    display()
