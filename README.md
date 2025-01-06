# Weather-app
Deployed Application URL
https://weather-app-production-021d.up.railway.app

About the Application

The Weather Dashboard is a web application that allows users to search for weather information in various cities, add their favorite cities to a personalized list, and view detailed forecasts for those cities. The app provides weather details using the Open-Meteo API, making it simple to plan ahead based on weather conditions.

Features

    Search for Weather Information: Users can search for weather details of any city by specifying the city name, state, and country.
    Add to Favorites: Registered users can add cities to their list of favorite locations for quick access to weather details.
    Weather Forecast: The app provides current weather information and an 8-day forecast, including:
        Current temperature
        Weather description (e.g., Clear sky, Light rain)
        Minimum and maximum temperatures
    User Authentication: Users can register and log in to save their favorite cities.
    Favorites Dashboard: A dedicated section to view and manage favorite cities.

Technology Stack

    Backend: Flask (Python)
    Frontend: HTML, CSS, Jinja2 templating
    Database: PostgreSQL (managed on Railway)
    APIs Used:
        Open-Meteo API           https://open-meteo.com/
        Nominatim Geocoding API for latitude/longitude retrieval            https://nominatim.org/
    Deployment: Railway platform
    Dependencies:
        Flask, Flask-SQLAlchemy, Flask-Login, Gunicorn, psycopg2-binary

Standard User Flow

    Visit the Website: Access the app at the deployed URL.
    Search for Weather: Use the search bar to enter a city and view its current weather and forecast.
    Register or Log In: Sign up or log in to save favorite cities.
    Add to Favorites: Click "Add to Favorites" to save a city for quick access.
    View Favorites: Access the "Favorites" section to view weather details for your saved cities.

 API Notes

    The app uses the Open-Meteo API to fetch weather details and forecasts.
    The Nominatim Geocoding API is used to resolve city names into latitude and longitude for API requests.
    Both APIs are free to use.

 Why These Features?

The features were chosen to create a user experience for checking weather information and saving commonly searched cities. Adding favorites makes it easy for frequent users to keep track of their preferred locations.

Nominatim was not orginally part of the plan, I learned later that Open Meteo only took latitutde and longitude as arguments.
So Nominatim was used to convert a general location like Chicago, Illinois into coordinates which I could use for Open Meteo.
    
   

🗃️ Repository Notes

The repository includes:

    app.py: Main Flask application logic.
    templates/: HTML templates rendered by Flask.
    static/: CSS and JavaScript files for styling and interactivity.
    requirements.txt: List of dependencies.