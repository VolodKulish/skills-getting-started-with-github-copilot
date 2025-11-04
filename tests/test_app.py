import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "description" in activities["Chess Club"]
    assert "schedule" in activities["Chess Club"]
    assert "max_participants" in activities["Chess Club"]
    assert "participants" in activities["Chess Club"]

def test_signup_success():
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    # Verify the participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate():
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # This email is already registered in the test data
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity():
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_signup_activity_full():
    # First, let's fill up an activity
    activity_name = "Chess Club"
    activities = client.get("/activities").json()
    max_participants = activities[activity_name]["max_participants"]
    current_participants = activities[activity_name]["participants"]
    
    # Add participants until full
    for i in range(len(current_participants), max_participants):
        email = f"student{i}@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Try to add one more
    response = client.post(f"/activities/{activity_name}/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()

def test_unregister_success():
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Using an email we know exists
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    # Verify the participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"].lower()

def test_unregister_nonexistent_activity():
    response = client.post("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()