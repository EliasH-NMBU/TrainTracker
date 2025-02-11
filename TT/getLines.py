import requests
import json

# Function to fetch journey data using GraphQL
def fetch_journey_data(api_url, client_name):
    headers = {
        "Content-Type": "application/json",
        "ET-Client-Name": client_name  # Replace with your company-application name
    }

    # Updated GraphQL query to fetch journey data
    query = """
    {
      trip(from: {name: "Moss", coordinates: {latitude: 59.4321, longitude: 10.6543}},
           to: {name: "Stabekk", coordinates: {latitude: 59.9374, longitude: 10.6245}},
           numTripPatterns: 1, dateTime: "2025-02-10T14:07:26.102+01:00") {
        tripPatterns {
          expectedStartTime
          duration
          legs {
            mode
            distance
            line {
              id
              publicCode
            }
          }
        }
      }
    }
    """

    body = {
        "query": query
    }

    try:
        # Send the POST request with the query
        response = requests.post(api_url, headers=headers, json=body)
        
        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            response_data = response.json()
            print("Full Response Data:", json.dumps(response_data, indent=4))  # Print the full response for debugging
            return response_data  # Return the JSON data from the response
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Define the API URL and headers
api_url = "https://api.entur.io/journey-planner/v3/graphql"
client_name = "your_company-your_application"  # Replace with your actual company and application name

# Fetch journey data
journey_data = fetch_journey_data(api_url, client_name)

# Process and display journey data
if journey_data:
    if 'data' in journey_data:
        print("Fetched Journey Data:")
        # Check the structure of the 'trip' data to avoid errors
        if isinstance(journey_data['data']['trip'], list):
            for trip_pattern in journey_data['data']['trip']:
                print(f"Expected Start Time: {trip_pattern['expectedStartTime']}")
                print(f"Duration: {trip_pattern['duration']}")
                for leg in trip_pattern['legs']:
                    print(f"Mode: {leg['mode']}")
                    print(f"Distance: {leg['distance']}")
                    print(f"Line ID: {leg['line']['id']}, Line Public Code: {leg['line']['publicCode']}")
        else:
            print("Unexpected structure for trip data:", journey_data['data']['trip'])
    else:
        print("No 'data' field found in the response.")
