import requests
import folium
import time
from flask import Flask, render_template, send_from_directory
from threading import Thread
import os

# Function to fetch vehicle data
def fetch_vehicle_data(api_url, client_name):
    headers = {
        "Content-Type": "application/json",
        "ET-Client-Name": client_name
    }

    query = """
    {
    vehicles(
        lineRef: "VYG:Line:R21"
    ) {
        line {
        lineRef
        }
        vehicleId
        occupancyStatus
        lastUpdated
        location {
        latitude
        longitude
        }
    }
    }
    """

    body = {
        "query": query
    }

    try:
        response = requests.post(api_url, headers=headers, json=body)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Function to update the map with new vehicle positions
def update_map(m, vehicles_data):
    if "data" not in vehicles_data or "vehicles" not in vehicles_data["data"]:
        print("No vehicle data found or invalid response format.")
        return

    # Clear previous markers
    #m.clear_layers()  # Removes all markers before adding new ones

    # Add new markers to the map
    for vehicle in vehicles_data["data"]["vehicles"]:
        lat = vehicle["location"]["latitude"]
        lon = vehicle["location"]["longitude"]
        vehicle_id = vehicle.get("vehicleId", "Unknown")
        last_updated = vehicle["lastUpdated"]

        addMarker(m, lat, lon, vehicle_id, last_updated)

# Function to add a marker to the map
def addMarker(m, lat, lon, vehicle_id, last_updated):
    popup_content = f"Vehicle ID: {vehicle_id}<br>Last Updated: {last_updated}"

    folium.Marker(
        location=[lat, lon],
        popup=popup_content,
        icon=folium.Icon(color="blue")
    ).add_to(m)

# Flask app setup
app = Flask(__name__, static_folder='static')

# Function to generate the map and save it as an HTML file
def generate_map():
    if not os.path.exists('static'):
        os.makedirs('static')

    # API URL and headers
    api_url = "https://api.entur.io/realtime/v2/vehicles/graphql"
    client_name = "your_company-your_application"

    m = folium.Map(location=[59.91, 10.75], zoom_start=9)
    
    while True:
        print("Fetching vehicle data...")
        vehicle_data = fetch_vehicle_data(api_url, client_name)

        if vehicle_data:
            update_map(m, vehicle_data)
            m.save("static/train_map_updated.html")
            print("Map saved to static/train_map_updated.html")

        time.sleep(30)  # Update the map every 30 seconds

# Flask route to serve the dynamic map
@app.route('/map')
def serve_map():
    try:
        with open('static/train_map_updated.html', 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "Map file not found", 404

# Flask route for the main page
@app.route('/')
def index():
    return render_template('base.html')

# Function to run the map generation in a separate thread
def start_map_generation():
    thread = Thread(target=generate_map)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    start_map_generation()
    app.run(debug=True, use_reloader=False)
