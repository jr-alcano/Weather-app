import pytest
from app import app, db, User, FavoriteCity


@pytest.fixture
def client():
    """Setup the test client and in-memory database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.rollback()  # Cleanup any lingering transactions
            db.drop_all()  # Drop all tables to reset


def test_register_route(client):
    """Test registering a new user."""
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@test.com',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200  # Ensure response is OK
    assert b'Registration successful! Please log in.' in response.data


def test_login_route(client):
    """Test logging in with valid credentials."""
    with app.app_context():
        user = User(username='testuser', email='test@test.com', password='password')
        db.session.add(user)
        db.session.commit()

    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged in successfully!' in response.data


def test_register_duplicate_user(client):
    """Test registering a user with an existing username/email."""
    with app.app_context():
        user = User(username='testuser', email='test@test.com', password='password')
        db.session.add(user)
        db.session.commit()

    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@test.com',
        'password': 'password'
    }, follow_redirects=True)

    # Check flash messages
    with client.session_transaction() as session:
        flashed_messages = session['_flashes']  # Get flashed messages
        assert any('Email or username already exists.' in msg for category, msg in flashed_messages)



def test_add_favorite(client):
    """Test adding a city to favorites."""
    with app.app_context():
        user = User(username='testuser', email='test@test.com', password='password')
        db.session.add(user)
        db.session.commit()

    client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)

    response = client.post('/add-favorite', data={
        'city': 'Chicago',
        'state': 'Illinois',
        'country': 'USA'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Chicago, Illinois, USA has been added to your favorites!' in response.data


