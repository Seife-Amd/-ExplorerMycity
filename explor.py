import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
#from fpdf import FPDF
import io
import os
# API Key and User-Agent
USER_AGENT = "FuzzyCityExplorer/1.0 (aluyey@gmail.com)"
API_KEY = '9d262738e747d56be9e2bf0adb156a0f'  # OpenWeatherMap API Key

# Define Fuzzy Variables
mood = ctrl.Antecedent(np.arange(0, 11, 1), 'mood')
weather_condition = ctrl.Antecedent(np.arange(0, 11, 1), 'weather_condition')
time_available = ctrl.Antecedent(np.arange(0, 11, 1), 'time_available')
recommendation_strength = ctrl.Consequent(np.arange(0, 11, 1), 'recommendation_strength')

# Membership Functions for Mood
mood['bad'] = fuzz.trimf(mood.universe, [0, 0, 5])
mood['medium'] = fuzz.trimf(mood.universe, [3, 5, 7])
mood['good'] = fuzz.trimf(mood.universe, [5, 10, 10])

# Membership Functions for Weather Condition
weather_condition['poor'] = fuzz.trimf(weather_condition.universe, [0, 0, 5])
weather_condition['average'] = fuzz.trimf(weather_condition.universe, [3, 5, 7])
weather_condition['good'] = fuzz.trimf(weather_condition.universe, [5, 10, 10])

# Membership Functions for Time Available
time_available['short'] = fuzz.trimf(time_available.universe, [0, 0, 5])
time_available['medium'] = fuzz.trimf(time_available.universe, [3, 5, 7])
time_available['plenty'] = fuzz.trimf(time_available.universe, [5, 10, 10])

# Membership Functions for Recommendation Strength
recommendation_strength['poor'] = fuzz.trimf(recommendation_strength.universe, [0, 0, 5])
recommendation_strength['average'] = fuzz.trimf(recommendation_strength.universe, [3, 5, 7])
recommendation_strength['high'] = fuzz.trimf(recommendation_strength.universe, [7, 10, 10])

# Define Fuzzy Rules
rule1 = ctrl.Rule(mood['good'] & weather_condition['good'] & time_available['plenty'], recommendation_strength['high'])
rule2 = ctrl.Rule(mood['medium'] & weather_condition['average'] & time_available['medium'], recommendation_strength['average'])
rule3 = ctrl.Rule(mood['bad'] | weather_condition['poor'] | time_available['short'], recommendation_strength['poor'])

# Define Additional Fuzzy Rules
rule4 = ctrl.Rule(mood['good'] & weather_condition['average'] & time_available['medium'], recommendation_strength['average'])
rule5 = ctrl.Rule(mood['medium'] & weather_condition['good'] & time_available['plenty'], recommendation_strength['high'])
rule6 = ctrl.Rule(mood['bad'] & weather_condition['poor'] & time_available['short'], recommendation_strength['poor'])
rule7 = ctrl.Rule(mood['medium'] & weather_condition['average'] & time_available['plenty'], recommendation_strength['high'])
rule8 = ctrl.Rule(mood['good'] & weather_condition['poor'] & time_available['medium'], recommendation_strength['average'])
rule9 = ctrl.Rule(mood['bad'] & weather_condition['good'] & time_available['short'], recommendation_strength['poor'])

# Fuzzy Control System
#recommendation_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
#recommendation_simulation = ctrl.ControlSystemSimulation(recommendation_ctrl)
# Update the fuzzy control system with new rules
recommendation_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
recommendation_simulation = ctrl.ControlSystemSimulation(recommendation_ctrl)


# Function to fetch weather data
def fetch_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            weather_condition = data['weather'][0]['main']
            temperature = data['main']['temp'] - 273.15  # Convert Kelvin to Celsius
            lat = data['coord']['lat']
            lon = data['coord']['lon']
            return weather_condition, round(temperature, 2), lat, lon
        else:
            st.error("Error City not Found: Please Enter Your Prefered City")
            return None, None, None, None
    except Exception as e:
        st.error(f"Error: Failed to fetch weather data: {str(e)}")
        return None, None, None, None

# Function to generate recommendations

def generate_recommendation(mood_input, weather_condition, time_of_day, preference, budget, time_available):
    recommendation_simulation.input['mood'] = mood_input
    recommendation_simulation.input['weather_condition'] = weather_condition
    recommendation_simulation.input['time_available'] = time_available
    recommendation_simulation.compute()

    strength = recommendation_simulation.output['recommendation_strength']
    recommendations = []
    poi_category = ""

    if strength > 7:  # High recommendation strength
        if preference == "Exciting":
            if time_of_day == "Morning":
                recommendations.append("Take a morning hike or explore an adventure park.")
                recommendations.append("Try bird watching at a nature reserve.")
                poi_category = "park"
            elif time_of_day == "Afternoon":
                recommendations.append("Go kayaking or visit an amusement park.")
                recommendations.append("Explore a vibrant city district with street art.")
                poi_category = "adventure"
            elif time_of_day == "Evening":
                recommendations.append("Enjoy an outdoor concert or explore a vibrant night market.")
                recommendations.append("Try rooftop dining with city views.")
                poi_category = "market"
        elif preference == "Chill":
            if time_of_day == "Morning":
                recommendations.append("Have a peaceful breakfast by the lake or stroll in a garden.")
                recommendations.append("Do yoga or meditate at a serene park.")
                poi_category = "park"
            elif time_of_day == "Afternoon":
                recommendations.append("Relax in a spa or enjoy a book in a quiet café.")
                recommendations.append("Attend a painting or pottery workshop.")
                poi_category = "spa"
            elif time_of_day == "Evening":
                recommendations.append("Watch a movie or enjoy an evening walk in a serene park.")
                recommendations.append("Listen to live jazz at a cozy lounge.")
                poi_category = "cinema"
        elif preference == "Adventure":
            recommendations.append("Try rock climbing, paragliding, or an escape room experience.")
            recommendations.append("Plan a scuba diving session or zip-lining adventure.")
            poi_category = "adventure"
    elif 5 < strength <= 7:  # Medium recommendation strength
        recommendations.append("Explore local museums or historical landmarks.")
        recommendations.append("Take a leisurely bike ride through scenic paths.")
        recommendations.append("Try a cooking class to learn a local recipe.")
        poi_category = "museum"
    else:  # Low recommendation strength
        recommendations.append("Relax with a cozy drink at a café or unwind at home.")
        recommendations.append("Try a virtual reality game at an arcade.")
        recommendations.append("Catch up on your favorite series or read a book.")
        poi_category = "cafe"

    # Add dining suggestions based on budget
    if budget == "Free":
        recommendations.append("Visit free cultural exhibits or community events.")
        poi_category = poi_category or "market"
    elif budget == "Medium":
        recommendations.append("Try mid-ranged restaurants or trendy food spots.")
        poi_category = poi_category or "restaurant"
    elif budget == "Expensive":
        recommendations.append("Dine at a fine dining restaurant or enjoy a luxurious experience.")
        poi_category = poi_category or "fine_dining"

    return recommendations[:5], poi_category

# Add dining suggestions based on budget
    if budget == "Free":
        recommendations.append("Visit free cultural exhibits or community events.")
        recommendations.append("Enjoy a picnic in a public park.")
        poi_category = poi_category or "market"
    elif budget == "Medium":
        recommendations.append("Try mid-ranged restaurants or trendy food spots.")
        recommendations.append("Join a local food tour for affordable culinary delights.")
        poi_category = poi_category or "restaurant"
    elif budget == "Expensive":
        recommendations.append("Dine at a fine dining restaurant or enjoy a luxurious experience.")
        recommendations.append("Book a private wine tasting or a gourmet dinner cruise.")
        poi_category = poi_category or "fine_dining"

    return recommendations[:5], poi_category

# Function to fetch nearby places using Nominatim
def fetch_nearby_places_nominatim(lat, lon, query):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "addressdetails": 1,
            "extratags": 1,
            "bounded": 1,
            "viewbox": f"{lon - 0.05},{lat + 0.05},{lon + 0.05},{lat - 0.05}"
        }
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        places = [
            {"name": place.get("display_name", "Unknown Place"),
             "coords": [float(place["lon"]), float(place["lat"])]}
            for place in data
        ]
        return places
    except requests.RequestException as e:
        st.error(f"Error fetching nearby places: {e}")
        return []

# Function to calculate distances
def calculate_distances(user_location, places):
    distances = []
    for place in places:
        place_coords = (place["coords"][1], place["coords"][0])  # (lat, lon)
        distance = geodesic(user_location, place_coords).kilometers
        distances.append({"name": place["name"], "distance": round(distance, 2)})
    return distances

# Function to display the map with nearby places
def show_osm_map(lat, lon, city, places):
    city_map = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker([lat, lon], popup=f"City: {city}", icon=folium.Icon(color="blue")).add_to(city_map)
    for place in places:
        folium.Marker(
            location=[place["coords"][1], place["coords"][0]],
            popup=place["name"],
            icon=folium.Icon(color="green")
        ).add_to(city_map)
    folium_static(city_map)

# Streamlit app layout
st.set_page_config(page_title="  Explore MyCity")

# Styling
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Calibri&display=swap');
        .main-title {
            color: green;
            font-size: 40px;
            font-weight: bold;
            font-family: 'Calibri', sans-serif;
            text-align: center;
            margin-bottom: 20px;
        }
        .bounded-box {
            border: 3px solid green;
            padding: 15px;
            margin-bottom: 20px;
            font-family: 'Calibri', sans-serif;
        }
        .poi-title {
            font-size: 20px;
            color: blue;
            font-weight: bold;
            font-family: 'Calibri', sans-serif;
        }
        .poi-item {
            font-size: 16px;
            color: indigo;
            font-family: 'Calibri', sans-serif;
            margin-bottom: 10px;
        }
        .interactive-bullet {
            color: green;
            margin-left: 10px;
        }
        .slider-green input[type=range]::-webkit-slider-thumb {
            background: green;
        }
        .slider-green input[type=range] {
            height: 8px;
            background: green;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown('<div class="main-title">Fuzzy Based City Exploration System</div>', unsafe_allow_html=True)

# User inputs
city = st.text_input("Enter City", placeholder="Enter a city name here...")
mood_input = st.slider("Rate your mood (0-10)", 0, 10, 5, key="mood_slider")
time_of_day = st.selectbox("What time of day is it?", ["Morning", "Afternoon", "Evening"])
preference = st.selectbox("What kind of activity do you prefer?", ["Exciting", "Chill", "Adventure"])
budget = st.selectbox("What is your budget?", ["Free", "Medium", "Expensive"])
time_available = st.selectbox("How much time do you have?", ["Short", "Medium", "Plenty"])

# Map time availability to fuzzy input
time_mapping = {"Short": 2, "Medium": 5, "Plenty": 8}
time_input = time_mapping[time_available]

# Add custom styling for the button
st.markdown(
    """
    <style>
        .custom-button {
            background-color: green;
            color: white;
            font-weight: bold;
            padding: 0.5em 1em;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        .custom-button:hover {
            background-color: darkgreen;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Button with custom style
if st.markdown('<button class="custom-button">Search Recommendation</button>', unsafe_allow_html=True):
    # Fetch weather and geolocation data
    weather_condition, temperature, lat, lon = fetch_weather(city)

    if weather_condition and lat and lon:
        # Process and display the results as needed

        # Display Weather Information
        st.markdown(
            f"""
            <div class="bounded-box">
                <p><strong>Weather Condition:</strong> {weather_condition.capitalize()}<br> 
                <strong>Temperature:</strong> {temperature}°C</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Generate Recommendations
        weather_rating = {"Sunny": 8, "Cloudy": 6, "Rainy": 3, "Snow": 2, "Fogy": 4, "Haze_Dust": 4}.get(weather_condition, 5)
        recommendations, poi_category = generate_recommendation(
            mood_input, weather_rating, time_of_day, preference, budget, time_input
        )

        # Display Recommendations
        st.markdown(
            f"""
            <div class="bounded-box">
                <h3><strong>Recommended Activities:</strong></h3>
                {''.join(f"<div class='interactive-bullet'><strong>• {rec}</strong></div>" for rec in recommendations)}
            </div>
            """,
            unsafe_allow_html=True
        )

        # Nearby Points of Interest based on the recommendations
        st.markdown(
            "<div class='poi-title'><strong>Nearby Points of Interest Based on the Recommendations:</strong></div>", 
            unsafe_allow_html=True
        )
        places = fetch_nearby_places_nominatim(lat, lon, poi_category)
        if places:
            distances = calculate_distances((lat, lon), places)
            for place in distances:
                st.markdown(
                    f"<div class='poi-item'><strong>• {place['name']}</strong> (<strong>{place['distance']} km</strong>)</div>", 
                    unsafe_allow_html=True
                )
            st.markdown("<br>", unsafe_allow_html=True)
            show_osm_map(lat, lon, city, places)
        else:
            st.error("Sorry, no nearby places found for the selected activity. Please try another.")
    else:
        st.error("Unable to fetch weather data. Please enter a valid city.")


# Function to save feedback to a text file
def save_feedback_to_txt(rating, comments, file_path="feedback.txt"):
    with open(file_path, "a") as file:  # Append mode
        file.write(f"Rating: {rating}, Feedback: {comments}\n")

# Page title
st.markdown("<hr><h4 style='color: red;'>We Value Your Feedback!</h4>", unsafe_allow_html=True)

# User Feedback Section
st.markdown("<h7 style='color: green;'>Please Provide Your Feedback:</h7>", unsafe_allow_html=True)
rating = st.slider("Rate the System (1-10)", 1, 10, 5)
comments = st.text_area("Your Comments")
submit_feedback = st.button("Submit Feedback")

# Handle feedback submission
if submit_feedback:
    if not comments:
        st.error("Please provide some comments before submitting.")
    else:
        save_feedback_to_txt(rating, comments)  # Save to feedback.txt
        st.success("Thank you for your feedback! It has been saved successfully.")
