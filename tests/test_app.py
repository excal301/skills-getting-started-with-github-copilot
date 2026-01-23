"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    global activities
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })
    yield
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_returns_correct_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        chess = data["Chess Club"]
        assert "description" in chess
        assert "schedule" in chess
        assert "max_participants" in chess
        assert "participants" in chess
        assert isinstance(chess["participants"], list)

    def test_get_activities_includes_participants(self, client):
        """Test that participants are included in response"""
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_returns_200(self, client):
        """Test that successful signup returns status 200"""
        response = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200

    def test_signup_adds_participant(self, client):
        """Test that signup adds the participant to the activity"""
        client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]

    def test_signup_returns_success_message(self, client):
        """Test that signup returns a success message"""
        response = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test that signup to non-existent activity returns 404"""
        response = client.post("/activities/Nonexistent%20Club/signup?email=student@mergington.edu")
        assert response.status_code == 404

    def test_signup_duplicate_activity_returns_400(self, client):
        """Test that signing up for two activities returns 400"""
        # First signup
        client.post("/activities/Chess%20Club/signup?email=student@mergington.edu")
        # Second signup with same email
        response = client.post("/activities/Programming%20Class/signup?email=student@mergington.edu")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_same_email_same_activity_returns_400(self, client):
        """Test that signing up again with same email returns 400"""
        email = "student@mergington.edu"
        # First signup
        client.post("/activities/Chess%20Club/signup?email=" + email)
        # Second signup with same email and activity
        response = client.post("/activities/Chess%20Club/signup?email=" + email)
        assert response.status_code == 400


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_returns_200(self, client):
        """Test that successful unregister returns status 200"""
        response = client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes the participant from the activity"""
        client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]

    def test_unregister_returns_success_message(self, client):
        """Test that unregister returns a success message"""
        response = client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregister from non-existent activity returns 404"""
        response = client.delete("/activities/Nonexistent%20Club/unregister?email=student@mergington.edu")
        assert response.status_code == 404

    def test_unregister_nonexistent_participant_returns_404(self, client):
        """Test that unregister of non-existent participant returns 404"""
        response = client.delete("/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu")
        assert response.status_code == 404

    def test_unregister_then_signup_again_works(self, client):
        """Test that after unregistering, a student can sign up again"""
        email = "newstudent@mergington.edu"
        # Sign up
        client.post("/activities/Chess%20Club/signup?email=" + email)
        # Unregister
        client.delete("/activities/Chess%20Club/unregister?email=" + email)
        # Sign up again
        response = client.post("/activities/Chess%20Club/signup?email=" + email)
        assert response.status_code == 200

    def test_unregister_other_activity_after_signup(self, client):
        """Test that after signing up, unregistering from another activity still fails"""
        email = "student@mergington.edu"
        # Sign up for Chess Club
        client.post("/activities/Chess%20Club/signup?email=" + email)
        # Try to unregister from Programming Class
        response = client.delete("/activities/Programming%20Class/unregister?email=" + email)
        assert response.status_code == 404


class TestIntegration:
    """Integration tests combining multiple operations"""

    def test_signup_unregister_signup_workflow(self, client):
        """Test complete workflow: signup, unregister, signup again"""
        email = "integration@mergington.edu"
        activity = "Chess Club"

        # Signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200

        # Verify signup
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]

        # Unregister
        response2 = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response2.status_code == 200

        # Verify unregister
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]

        # Signup again
        response3 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response3.status_code == 200

        # Verify signup again
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]

    def test_multiple_signups_and_unregisters(self, client):
        """Test multiple students signing up and unregistering"""
        activity = "Programming Class"
        students = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]

        # All students sign up
        for student in students:
            response = client.post(f"/activities/{activity}/signup?email={student}")
            assert response.status_code == 200

        # Verify all are signed up
        response = client.get("/activities")
        data = response.json()
        for student in students:
            assert student in data[activity]["participants"]

        # Unregister second student
        client.delete(f"/activities/{activity}/unregister?email={students[1]}")

        # Verify
        response = client.get("/activities")
        data = response.json()
        assert students[0] in data[activity]["participants"]
        assert students[1] not in data[activity]["participants"]
        assert students[2] in data[activity]["participants"]
