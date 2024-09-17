import os
import googlemaps
import networkx as nx
import matplotlib.pyplot as plt
from itertools import permutations
import streamlit as st

# Streamlit page setup
st.title("Travel Planner - Shortest Path Using Google Maps API")
st.write("This app calculates the shortest path between selected places using real-world distances.")

# Get the API key from the environment variable or directly input it
API_KEY = st.secrets["general"]["API_KEY"]  # Ensure your secrets.toml has this key

# Initialize the Google Maps API client
gmaps = googlemaps.Client(key=API_KEY)

# Define the list of places in Chennai and Thiruvallur with more specificity
places_in_chennai = [
    'T. Nagar, Chennai, Tamil Nadu', 'Anna Nagar, Chennai, Tamil Nadu', 
    'Velachery, Chennai, Tamil Nadu', 'Adyar, Chennai, Tamil Nadu', 
    'Mylapore, Chennai, Tamil Nadu', 'Nungambakkam, Chennai, Tamil Nadu', 
    'Tambaram, Chennai, Tamil Nadu', 'Chrompet, Chennai, Tamil Nadu', 
    'Guindy, Chennai, Tamil Nadu', 'Alwarpet, Chennai, Tamil Nadu', 
    'Egmore, Chennai, Tamil Nadu', 'Triplicane, Chennai, Tamil Nadu', 
    'Perambur, Chennai, Tamil Nadu', 'Thiruvanmiyur, Chennai, Tamil Nadu', 
    'Royapettah, Chennai, Tamil Nadu', 'Vadapalani, Chennai, Tamil Nadu', 
    'Koyambedu, Chennai, Tamil Nadu', 'Ashok Nagar, Chennai, Tamil Nadu', 
    'Madipakkam, Chennai, Tamil Nadu', 'Sholinganallur, Chennai, Tamil Nadu'
]

places_in_thiruvallur = [
    'Thiruvallur, Tamil Nadu', 'Poonamallee, Tamil Nadu', 'Avadi, Tamil Nadu', 
    'Tiruttani, Tamil Nadu', 'Tiruvottiyur, Tamil Nadu', 'Minjur, Tamil Nadu', 
    'Ambattur, Tamil Nadu', 'Red Hills, Tamil Nadu', 'Gummidipoondi, Tamil Nadu', 
    'Pattabiram, Tamil Nadu'
]

# Combine places from Chennai and Thiruvallur
places = places_in_chennai + places_in_thiruvallur

# Streamlit multiselect for place selection
st.write("Select two places to calculate the shortest driving path:")
start = st.selectbox('Select Start Place:', places)
end = st.selectbox('Select End Place:', places)

# Create a directed graph
G = nx.DiGraph()

# Function to get distance between two places using Google Maps API
@st.cache_data(show_spinner=True)
def get_distance(origin, destination):
    try:
        result = gmaps.distance_matrix(origins=origin, destinations=destination, mode='driving')
        element = result['rows'][0]['elements'][0]

        # Check if the distance field is available
        if element.get('distance'):
            distance = element['distance']['value']  # distance in meters
            duration = element['duration']['value']  # duration in seconds
            return distance / 1000, duration / 3600  # convert to kilometers and hours
        else:
            st.error(f"No distance data available for {origin} to {destination}")
            return None, None
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None

# Add edges with distances and durations between all pairs of places
for origin, destination in permutations(places, 2):
    distance, duration = get_distance(origin, destination)
    if distance is not None:
        G.add_edge(origin, destination, distance=distance, duration=duration)

# Function to find the shortest path
def find_shortest_path(graph, start_place, end_place, weight='distance'):
    try:
        path = nx.shortest_path(graph, source=start_place, target=end_place, weight=weight)
        total_distance = nx.shortest_path_length(graph, source=start_place, target=end_place, weight=weight)
        return path, total_distance
    except nx.NetworkXNoPath:
        st.error("No path found between the selected places.")
        return None, None

# Function to visualize the graph with the shortest path
def plot_graph(graph, path=None):
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(graph, seed=42)  # Use spring layout for better spacing
    labels = nx.get_edge_attributes(graph, 'distance')

    # Draw the graph
    nx.draw(graph, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=10)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, font_color='green')

    # Highlight the shortest path in red
    if path:
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='red', width=3)

    plt.title("Place-to-Place Network")
    st.pyplot(plt)

# Streamlit button to trigger the shortest path calculation
if st.button('Find Shortest Path'):
    if start == end:
        st.error("Please select two different places.")
    else:
        shortest_path, total_distance = find_shortest_path(G, start, end, weight='distance')
        
        if shortest_path and total_distance:
            st.success(f"Shortest path from {start} to {end}: {shortest_path}")
            st.success(f"Total distance: {total_distance:.2f} km")

            # Plot the graph with the path
            plot_graph(G, shortest_path)
