import streamlit as st
import requests
import pandas
import time
import json
st.set_page_config(layout="wide")
# Step 2: Install the required libraries
# pip install requests

# Step 4: Initialize the Google Maps client
api_key = "AIzaSyDt-xh1BRpmNO8HujgykkWZdkPe7v9FRv8"
base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# Step 2 & 3: Import dependencies
# import requests
# import json


def get_coordinates(city, state):
    # Replace 'YOUR_API_KEY' with your actual Google Maps API key
    # Format the city and state into a location string
    #nah

    # URL for the Geocoding API request
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={city},{state}&key={api_key}'

    try:
        # Send the API request
        response = requests.get(url)
        data = response.json()

        # Check if the response contains results
        if data['results']:
            # Extract the latitude and longitude coordinates
            latitude = data['results'][0]['geometry']['location']['lat']
            longitude = data['results'][0]['geometry']['location']['lng']

            # Return the coordinates
            return latitude, longitude
        else:
            print('No results found.')
            return None
    except requests.exceptions.RequestException as e:
        print(f'Request failed: {e}')
        return None


# Step 5: Make a Nearby Search Request
def fetch_legal_services(location, search_str, radius):
    lat,lng = get_coordinates(location.split(",")[0] , location.split(",")[1])
    st.write(lat, lng)
    # str(get_coordinates(location.split(",")[0] , location.split(",")[1]))

    search_request = f'{base_url}?keyword={search_str}s&location={lat},{lng}&radius={radius}&key={api_key}'
    response = requests.get(search_request)
    data = response.json()
    services=[]
    if 'results' in data:
        results = data['results']
        for result in results:
            # Process each result as needed
            services.append(result)

        # Check if there are more results to fetch
        while 'next_page_token' in data:
            pagetoken = data['next_page_token']
            st.write("pageinating")
            # Delay a few seconds before making the next request
            time.sleep(2.5)
            url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={pagetoken}&key={api_key}'
            response = requests.get(url)
            data = response.json()
            results = data['results']
            for result in results:
                # Process each result as needed
                services.append(result)
    #st.write(" search_request :  " + search_request)
    return services
    #return data["results"] if "results" in data else []

# Step 6: Handle the API Response
def process_legal_services(services):
    results = []
    for service in services:
        name = service["name"]
        address = service["vicinity"]
        contact = service.get("formatted_phone_number", "N/A")
        rating = service["rating"]
        types = service["types"]
        results.append({"Name": name, "Address": address, "Rating": rating, "Website":get_website(service["place_id"])})

    return results
def get_website(place_id):
    # Send a request to the Place Details API
    url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}'
    response = requests.get(url)
    data = response.json()

    # Retrieve the website link from the response data
    if 'result' in data:
        if 'website' in data['result']:
            website = data['result']['website']
            return website
        else:
            return "No Link"
    else:
        return "Error"


# Step 1, 2 & 6: Create UI components and display results
st.title("Juntos Service Finder")
location = st.text_input("Enter City, State")
search_str = st.text_input("Search For ...")
radius = st.number_input("Search Radius (in meters)", value=10000)
search_button = st.button("Find", 10000)

if search_button:
    if location and search_str:
        # Step 5: Fetch data
        legal_services = fetch_legal_services(location, search_str, radius)

        # Step 6: Process data
        processed_services = process_legal_services(legal_services)

        # Step 7: Display results
        if processed_services:
            st.subheader(f"{search_str} in {location}:")


            def make_clickable(link):
                # target _blank to open new window
                # extract clickable text to display for your link
                return f'<a target="_blank" href="{link}">{link}</a>'


            df = pandas.DataFrame(processed_services)
            # link is the column with hyperlinks
            df['Website'] = df['Website'].apply(make_clickable)
            df = df.to_html(escape=False)
            st.write(df, unsafe_allow_html=True)
