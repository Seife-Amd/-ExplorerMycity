import streamlit as st
import requests
import folium
from streamlit_folium import folium_static

# OpenWeatherMap API Key (replace 'YOUR_API_KEY_HERE' with your actual API key)
API_KEY = '9d262738e747d56be9e2bf0adb156a0f'

# Function to fetch weather data from OpenWeatherMap
def fetch_weather(city):
    try:
        weather_api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        response = requests.get(weather_api_url)
        data = response.json()

        if response.status_code == 200:
            weather_condition = data['weather'][0]['main']
            temperature = data['main']['temp'] - 273.15  # Convert from Kelvin to Celsius
            return weather_condition, round(temperature, 2)
        else:
            st.error("City not found or API error")
            return None, None
    except Exception as e:
        st.error(f"Failed to fetch weather data: {str(e)}")
        return None, None

# Enhanced fuzzy logic for generating city-specific recommendations
def generate_recommendation(city, mood, time, preference, time_of_day):
    weather_condition, temperature = fetch_weather(city)
    if not weather_condition:
        return "Could not fetch weather data."

    st.write(f"**Weather:** {weather_condition}, **Temperature:** {temperature}°C")

    # City-specific rules
    if city.lower() == "london":
        return "Visit the Tower of London, enjoy a ride on the London Eye, or explore Covent Garden."

    elif city.lower() == "paris":
        return "Climb the Eiffel Tower, visit the Louvre Museum, or stroll along the Champs-Élysées."

    elif city.lower() == "lausanne":
        return "Visit the Olympic Museum or take a walk along the lakeside promenade in Ouchy."

    elif city.lower() == "zurich":
        return "Take a boat trip on Lake Zurich or visit the Swiss National Museum."

    elif city.lower() == "geneva":
        return "Visit the Jet d'Eau fountain or explore the United Nations headquarters."

    elif city.lower() == "fribourg":
        return "Explore the medieval architecture of Fribourg or visit the local art museum."

    elif city.lower() == "bern":
        return "Visit the Bear Park, explore the Einstein Museum, or stroll through the historic old town."

    elif city.lower() == "new york":
        return "Explore Central Park, visit Times Square, or see a Broadway show."

    else:
        return "Explore a local market, visit a famous landmark, or try a new restaurant."

# Function to display a map with a suggested location
def show_map(city):
    map = folium.Map(location=[0, 0], zoom_start=12)
    try:
        weather_api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        response = requests.get(weather_api_url)
        data = response.json()
        if response.status_code == 200:
            lat = data['coord']['lat']
            lon = data['coord']['lon']
            folium.Marker(location=[lat, lon], popup=f"Suggested Location in {city}").add_to(map)
        else:
            folium.Marker(location=[0, 0], popup="Suggested Location").add_to(map)
    except Exception as e:
        folium.Marker(location=[0, 0], popup="Error in fetching location").add_to(map)

    folium_static(map)

# Streamlit app layout
st.set_page_config(page_title="Fuzzy Logic City Explorer")
st.title("Fuzzy Based  City Exploration System")
st.markdown("<style>body { font-family: 'Times New Roman'; }</style>", unsafe_allow_html=True)
st.write("Get personalized recommendations for exploring your city based on fuzzy logic.")

# Input fields
city = st.text_input("Enter City")
mood = st.selectbox("Select Your Mood", ["Good", "Medium", "Bad"])
time = st.selectbox("How much time do you have?", ["Plenty", "Some", "A little"])
preference = st.selectbox("What kind of activity do you prefer?", ["Exciting", "Chill", "Adventure"])
time_of_day = st.selectbox("What time of day is it?", ["Morning", "Afternoon", "Evening"])

# Enhanced Get Recommendation button
button_style = """
<style>
    .stButton>button {
        background-color: #28a745;
        color: white;
        font-size: 18px;
        font-family: 'Times New Roman';
        border-radius: 10px;
        width: 220px;
        height: 50px;
    }
</style>
"""
st.markdown(button_style, unsafe_allow_html=True)

# Generate recommendation button
if st.button("Get Recommendation"):
    recommendation = generate_recommendation(city, mood, time, preference, time_of_day)
    st.success(recommendation)
    show_map(city)
