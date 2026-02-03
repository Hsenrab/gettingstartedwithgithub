"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    # Store original participants
    original_participants = {
        name: list(details["participants"]) 
        for name, details in activities.items()
    }
    yield
    # Restore original participants after each test
    for name, participants in original_participants.items():
        activities[name]["participants"] = participants


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that the GET /activities endpoint returns all activities.

        Verifies that the response:
        - Returns HTTP 200 status code
        - Contains all 9 expected activities
        """
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Soccer Team" in data
        assert "Basketball Team" in data
        assert "Art Club" in data
        assert "Drama Club" in data
        assert "Debate Team" in data
        assert "Science Olympiad" in data
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert len(data) == 9

    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Soccer Team/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert "newstudent@mergington.edu" in activities["Soccer Team"]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_already_registered(self, client):
        """Test signup when student is already registered"""
        response = client.post(
            "/activities/Soccer Team/signup",
            params={"email": "alex@mergington.edu"}  # Already in Soccer Team
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # First verify the student is registered
        assert "alex@mergington.edu" in activities["Soccer Team"]["participants"]
        
        response = client.delete(
            "/activities/Soccer Team/unregister",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert "alex@mergington.edu" not in activities["Soccer Team"]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_not_registered(self, client):
        """Test unregister when student is not registered"""
        response = client.delete(
            "/activities/Soccer Team/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not registered for this activity"


class TestRootRedirect:
    """Tests for the root endpoint redirect"""

    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
