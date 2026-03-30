import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesAPI:
    """Test suite for the Activities API using AAA pattern"""

    def test_get_activities_success(self):
        # Arrange: No special setup needed as activities are predefined

        # Act: Make GET request to /activities
        response = client.get("/activities")

        # Assert: Check response status and content
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

        # Verify structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_signup_for_activity_success(self):
        # Arrange: Choose an activity and email not already signed up
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"

        # Act: Make POST request to signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Check response status and message
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify the student was added to participants
        get_response = client.get("/activities")
        activities = get_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_for_nonexistent_activity(self):
        # Arrange: Use an activity that doesn't exist
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act: Attempt to signup for nonexistent activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Should return 404
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email(self):
        # Arrange: Use an activity and email already signed up
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants

        # Act: Attempt to signup again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Should return 400
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student already signed up" in data["detail"]

    def test_unregister_from_activity_success(self):
        # Arrange: First signup a student
        activity_name = "Art Club"
        email = "teststudent@mergington.edu"

        # Signup first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act: Unregister the student
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Check response status and message
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify the student was removed from participants
        get_response = client.get("/activities")
        activities = get_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_from_nonexistent_activity(self):
        # Arrange: Use an activity that doesn't exist
        activity_name = "Fake Club"
        email = "student@mergington.edu"

        # Act: Attempt to unregister from nonexistent activity
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Should return 404
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_not_signed_up_student(self):
        # Arrange: Use an activity and email not signed up
        activity_name = "Debate Club"
        email = "notsignedup@mergington.edu"

        # Act: Attempt to unregister student not signed up
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Should return 400
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student not signed up" in data["detail"]