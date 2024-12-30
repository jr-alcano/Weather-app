from flask import Flask, render_template, redirect, flash, session, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests
import os

# Local only
if os.environ.get('FLASK_ENV') != 'production':
    from dotenv import load_dotenv
    load_dotenv()


app = Flask(__name__)

# Configurations
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL',  'postgresql://postgres@localhost/weather_app_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

weather_emotes = {
    "Clear sky": "☀️",
    "Mainly clear": "🌤️",
    "Partly cloudy": "⛅",
    "Overcast": "☁️",
    "Foggy": "🌫️",
    "Freezing fog": "🌫️❄️",
    "Light drizzle": "🌦️",
    "Moderate drizzle": "🌧️",
    "Heavy drizzle": "🌧️",
    "Light rain": "🌧️",
    "Moderate rain": "🌧️",
    "Heavy rain": "🌧️💧",
    "Freezing rain (light)": "🌧️❄️",
    "Freezing rain (heavy)": "🌧️❄️",
    "Light snow": "❄️",
    "Moderate snow": "❄️🌨️",
    "Heavy snow": "❄️⛄",
    "Light rain showers": "🌦️",
    "Moderate rain showers": "🌧️",
    "Violent rain showers": "⛈️",
    "Light snow showers": "🌨️",
    "Heavy snow showers": "❄️🌨️",
    "Thunderstorm (light/moderate)": "⛈️",
    "Thunderstorm with slight hail": "⛈️❄️",
    "Thunderstorm with heavy hail": "⛈️🌨️"
}


# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

class FavoriteCity(db.Model):
    __tablename__ = 'favorite_cities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=True)
    country = db.Column(db.String(120), nullable=False)



# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Weather code dictionary
weather_descriptions = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Freezing fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Heavy drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Freezing rain (light)",
    67: "Freezing rain (heavy)",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Light rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm (light/moderate)",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

# Helper function to get latitude and longitude for a city
def get_coordinates(city, state=None, country=None):
    query = f"{city}"
    if state:
        query += f", {state}"
    if country:
        query += f", {country}"

    geocode_url = f'https://nominatim.openstreetmap.org/search?q={query}&format=json'
    headers = {'User-Agent': 'WeatherDashboardApp'}
    response = requests.get(geocode_url, headers=headers)

    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data['lat']), float(data['lon'])
    return None, None

# Helper function to get weather data
def get_weather_data(city, state=None, country=None):
    lat, lon = get_coordinates(city, state, country)
    if lat and lon:
        url = (
            f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
            f'&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,weathercode'
            f'&timezone=auto&current_weather=true&forecast_days=8'
        )
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            current_weather = data.get('current_weather', {})
            daily_weather = data.get('daily', {})

            # Calculate average daily temperatures
            if 'temperature_2m_max' in daily_weather and 'temperature_2m_min' in daily_weather:
                daily_weather['temperature_2m_avg'] = [
                    (max_temp + min_temp) / 2
                    for max_temp, min_temp in zip(
                        daily_weather['temperature_2m_max'],
                        daily_weather['temperature_2m_min']
                    )
                ]

            # Add weather descriptions for daily forecasts
            if 'weathercode' in daily_weather:
                daily_weather['descriptions'] = [
                    weather_descriptions.get(code, "Unknown")
                    for code in daily_weather['weathercode']
                ]

            # Adding current weather description based on the current weather code
            current_weather_description = weather_descriptions.get(current_weather.get('weathercode', None), "Unknown")

            return {
                'city': city,
                'state': state,
                'country': country,
                'current_temp': current_weather.get('temperature'),
                'current_description': current_weather_description,
                'daily': daily_weather,
            }
    return None


# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    favorites = []
    if current_user.is_authenticated:
        favorites = FavoriteCity.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        city = request.form.get('city')
        state = request.form.get('state')
        country = request.form.get('country', 'USA')

        if city:
            weather = get_weather_data(city, state, country)

    return render_template('index.html', weather=weather, favorites=favorites, weather_emotes=weather_emotes)

@app.route('/add-favorite', methods=['POST'])
@login_required
def add_favorite():
    city = request.form.get('city')
    state = request.form.get('state')
    country = request.form.get('country')

    if not city or not country:
        flash("City and Country are required to add to favorites.", "error")
        return redirect(url_for('index'))

    existing_favorite = FavoriteCity.query.filter_by(
        user_id=current_user.id,
        city=city,
        state=state,
        country=country
    ).first()

    if existing_favorite:
        flash(f"{city}, {state or ''}, {country} is already in your favorites.", "info")
        return redirect(url_for('index'))

    new_favorite = FavoriteCity(
        user_id=current_user.id,
        city=city,
        state=state,
        country=country
    )
    db.session.add(new_favorite)
    db.session.commit()

    flash(f"{city}, {state or ''}, {country} has been added to your favorites!", "success")
    return redirect(url_for('index'))



@app.route('/favorite/<int:favorite_id>')
@login_required
def show_favorite(favorite_id):
    """Show the weather dashboard for a clicked favorite city."""
    favorite = FavoriteCity.query.get(favorite_id)

    # Ensure the favorite belongs to the current user
    if favorite and favorite.user_id == current_user.id:
        weather = get_weather_data(favorite.city, favorite.state, favorite.country)
        favorites = FavoriteCity.query.filter_by(user_id=current_user.id).all()
        return render_template('index.html', weather=weather, favorites=favorites, weather_emotes=weather_emotes)
    else:
        flash("You do not have access to this favorite.", "error")
        return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check for duplicate username or email
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash('Email or username already exists.', 'error')
            return redirect('/register')

        # Create the new user
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect('/login')

    return render_template('register.html')






@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect('/')
        else:
            flash('Invalid username or password.', 'error')
            return redirect('/login')

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Tables created:", db.engine.table_names())
    app.run(debug=True)

