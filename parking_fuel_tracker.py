import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim # type: ignore
import requests

# Custom Streamlit UI Styling for Dark/Neon Mode
st.markdown(
    """
    <style>
        body {
            background-color: #121212;
            color: #E0E0E0;
        }
        .big-title {
            font-size: 36px;
            font-weight: bold;
            color: #00E676;
            text-align: center;
        }
        .stSelectbox, .stButton, .stWarning, .stError {
            text-align: center;
        }
        .block-container {
            background-color: #1E1E1E;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0px 0px 15px #00E676;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# City and area mapping
city_areas = {
    "Kolkata": ["Salt Lake", "Park Street", "Dumdum", "New Town"],
    "Bengaluru": ["MG Road", "Whitefield", "Koramangala", "Indiranagar"],
    "Mumbai": ["Bandra", "Andheri", "Juhu", "Colaba"]
}

# Function to get parking & fuel stations
def get_parking_fuel_stations(city, area):
    geolocator = Nominatim(user_agent="geo_locator")
    location = geolocator.geocode(f"{area}, {city}")  # Ensure city is included
    
    if location:
        lat, lon = location.latitude, location.longitude
        
        # Fetch places using Overpass API (OSM)
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        (
            node["amenity"="parking"](around:5000,{lat},{lon});
            node["amenity"="fuel"](around:5000,{lat},{lon});
        );
        out;
        """
        
        try:
            response = requests.get(overpass_url, params={'data': overpass_query}, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("elements", []), lat, lon
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data: {e}")
            return [], lat, lon
    return [], None, None

# Streamlit UI
st.markdown("<p class='big-title'>🚗 Parking & ⛽ Fuel Station Finder</p>", unsafe_allow_html=True)

# City selection
title_city = "Select a city:" if city_areas else "No cities available"
city = st.selectbox(title_city, list(city_areas.keys()))

if city:
    areas = city_areas.get(city, [])
    selected_area = st.selectbox("Select an area:", areas)
    
    if st.button("🔍 Find Parking & Fuel Stations"):
        places, lat, lon = get_parking_fuel_stations(city, selected_area)
        
        # Create map even if no results
        if lat and lon:
            m = folium.Map(location=[lat, lon], zoom_start=14, tiles="cartodbdark_matter")
            
            if places:
                for place in places:
                    p_lat = place["lat"]
                    p_lon = place["lon"]
                    
                    if "parking" in place.get("tags", {}).values():
                        icon_color = "green"
                        popup_text = "🅿️ Parking Station"
                    elif "fuel" in place.get("tags", {}).values():
                        icon_color = "red"
                        popup_text = "⛽ Fuel Station"
                    else:
                        icon_color = "blue"
                        popup_text = "Unknown Station"
                    
                    folium.Marker([p_lat, p_lon], 
                                  popup=popup_text, 
                                  icon=folium.Icon(color=icon_color, icon="info-sign")).add_to(m)
            else:
                st.warning("⚠️ No parking or fuel stations found, but here’s the map of the area.")
            
            folium_static(m)
        else:
            st.error("❌ Could not find the selected area. Try another one.")




