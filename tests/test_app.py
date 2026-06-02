import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: snapshot the in-memory activities and restore after each test
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_root_redirect():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers.get("location") == "/static/index.html"


def test_get_activities():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # spot-check a known activity
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_success():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "test.added@mergington.edu"
    assert email not in activities[activity_name]["participants"]

    # Act
    path = f"/activities/{quote(activity_name)}/signup"
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "Signed up" in body.get("message", "")
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_rejected():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    existing = activities[activity_name]["participants"][0]

    # Act
    path = f"/activities/{quote(activity_name)}/signup"
    response = client.post(path, params={"email": existing})

    # Assert
    assert response.status_code == 400
    body = response.json()
    assert "already signed up" in body.get("detail", "")


def test_remove_participant_success():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    assert email in activities[activity_name]["participants"]

    # Act
    path = f"/activities/{quote(activity_name)}/participants"
    response = client.delete(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "Removed" in body.get("message", "")
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "missing.person@mergington.edu"
    assert email not in activities[activity_name]["participants"]

    # Act
    path = f"/activities/{quote(activity_name)}/participants"
    response = client.delete(path, params={"email": email})

    # Assert
    assert response.status_code == 404
    body = response.json()
    assert "Participant not found" in body.get("detail", "")
