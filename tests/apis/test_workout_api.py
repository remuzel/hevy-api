from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import requests

from hevy_api.client import HevyClient
from hevy_api.models.model import Workout
from hevy_api.models.request import (
    GetWorkoutRequest,
    GetWorkoutsCountRequest,
    GetWorkoutsRequest,
    PostWorkoutRequest,
    PutWorkoutRequest,
)
from hevy_api.models.response import (
    WorkoutCountResponse,
    WorkoutResponse,
    WorkoutsResponse,
)


class TestWorkoutAPI:
    @pytest.fixture
    def client(self):
        return HevyClient(api_key="test_token")

    @pytest.fixture
    def sample_workout_data(self):
        return {
            "id": "workout-123",
            "title": "Push Day",
            "description": "Chest, shoulders, triceps",
            "start_time": "2024-01-15T10:00:00Z",
            "end_time": "2024-01-15T11:30:00Z",
            "updated_at": "2024-01-15T11:30:00Z",
            "created_at": "2024-01-15T10:00:00Z",
            "exercises": [
                {
                    "index": 0,
                    "title": "Bench Press",
                    "notes": "Focus on form",
                    "exercise_template_id": "template-123",
                    "supersets_id": None,
                    "sets": [
                        {
                            "index": 0,
                            "type": "normal",
                            "weight_kg": 80.0,
                            "reps": 10,
                            "distance_meters": None,
                            "duration_seconds": None,
                            "rpe": 8.0,
                            "custom_metric": None,
                        }
                    ],
                }
            ],
        }

    @pytest.fixture
    def sample_workout(self, sample_workout_data):
        return Workout(**sample_workout_data)

    @pytest.fixture
    def mock_successful_response(self):
        mock_response = Mock()
        mock_response.json.return_value = {"workout_count": 42}
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        return mock_response

    @pytest.fixture
    def mock_error_response(self):
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Not found"}
        mock_response.status_code = 404
        mock_response.headers = {"Content-Type": "application/json"}
        return mock_response

    # GET /v1/workouts/count tests
    @patch("requests.Session.request")
    def test_get_workout_count_success(
        self, mock_request, client, mock_successful_response
    ):
        mock_request.return_value = mock_successful_response

        result = client.get_workout_count()

        # Verify response structure
        assert isinstance(result, WorkoutCountResponse)
        assert result.is_success
        assert result.status_code == 200
        assert result.workout_count is not None
        assert result.workout_count.workout_count == 42

        # Verify HTTP request details
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["url"] == "https://api.hevyapp.com/v1/workouts/count"
        assert call_args[1]["headers"]["api-key"] == "test_token"

    @patch("requests.Session.request")
    def test_get_workout_count_error(self, mock_request, client, mock_error_response):
        mock_request.return_value = mock_error_response

        result = client.get_workout_count()

        assert isinstance(result, WorkoutCountResponse)
        assert result.is_error
        assert result.status_code == 404
        assert result.workout_count is None

    @patch("requests.Session.request")
    def test_get_workout_count_caching(
        self, mock_request, client, mock_successful_response
    ):
        mock_request.return_value = mock_successful_response

        # First call
        result1 = client.get_workout_count()
        # Second call should use cache
        result2 = client.get_workout_count()

        # Should only make one HTTP request due to caching
        mock_request.assert_called_once()
        assert (
            result1.workout_count.workout_count == result2.workout_count.workout_count
        )

    # GET /v1/workouts tests
    @patch("requests.Session.request")
    def test_get_workouts_success(self, mock_request, client, sample_workout_data):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 5,
            "workouts": [sample_workout_data],
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_workouts(page_number=1, page_size=10)

        assert isinstance(result, WorkoutsResponse)
        assert result.is_success
        assert result.page == 1
        assert result.page_count == 5
        assert len(result.workouts) == 1
        assert result.workouts[0].id == "workout-123"
        assert result.workouts[0].title == "Push Day"

        # Verify HTTP request
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert (
            call_args[1]["url"]
            == "https://api.hevyapp.com/v1/workouts?page=1&pageSize=10"
        )

    @patch("requests.Session.request")
    def test_get_workouts_default_pagination(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {"page": 1, "page_count": 1, "workouts": []}
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        client.get_workouts()

        call_args = mock_request.call_args
        assert "page=1&pageSize=5" in call_args[1]["url"]

    @patch("requests.Session.request")
    def test_get_workouts_serialization_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 1,
            "workouts": [{"invalid": "data"}],  # Invalid workout data
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_workouts()

        assert isinstance(result, WorkoutsResponse)
        assert result.is_success
        assert result.workouts == []  # Should be empty due to serialization error

    # GET /v1/workouts/{id} tests
    @patch("requests.Session.request")
    def test_get_workout_success(self, mock_request, client, sample_workout_data):
        mock_response = Mock()
        mock_response.json.return_value = sample_workout_data
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_workout("workout-123")

        assert isinstance(result, WorkoutResponse)
        assert result.is_success
        assert result.workout is not None
        assert result.workout.id == "workout-123"
        assert result.workout.title == "Push Day"
        assert len(result.workout.exercises) == 1

        # Verify HTTP request
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["url"] == "https://api.hevyapp.com/v1/workouts/workout-123"

    @patch("requests.Session.request")
    def test_get_workout_not_found(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Workout not found"}
        mock_response.status_code = 404
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_workout("nonexistent-id")

        assert isinstance(result, WorkoutResponse)
        assert result.is_error
        assert result.status_code == 404
        assert result.workout is None

    @patch("requests.Session.request")
    def test_get_workout_caching(self, mock_request, client, sample_workout_data):
        mock_response = Mock()
        mock_response.json.return_value = sample_workout_data
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        # First call
        result1 = client.get_workout("workout-123")
        # Second call should use cache
        result2 = client.get_workout("workout-123")

        # Should only make one HTTP request due to caching
        mock_request.assert_called_once()
        assert result1.workout.id == result2.workout.id

    # POST /v1/workouts tests
    @patch("requests.Session.request")
    def test_create_workout_success(
        self, mock_request, client, sample_workout, sample_workout_data
    ):
        mock_response = Mock()
        mock_response.json.return_value = sample_workout_data
        mock_response.status_code = 201
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.create_workout(sample_workout)

        assert isinstance(result, WorkoutResponse)
        assert result.is_success
        assert result.status_code == 201
        assert result.workout is not None
        assert result.workout.id == "workout-123"

        # Verify HTTP request
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["url"] == "https://api.hevyapp.com/v1/workouts"
        assert call_args[1]["json"] is not None
        assert call_args[1]["json"]["title"] == "Push Day"

    @patch("requests.Session.request")
    def test_create_workout_validation_error(
        self, mock_request, client, sample_workout
    ):
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Invalid workout data"}
        mock_response.status_code = 400
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.create_workout(sample_workout)

        assert isinstance(result, WorkoutResponse)
        assert result.is_error
        assert result.status_code == 400
        assert result.workout is None

    # PUT /v1/workouts/{id} tests
    @patch("requests.Session.request")
    def test_update_workout_success(
        self, mock_request, client, sample_workout, sample_workout_data
    ):
        updated_data = sample_workout_data.copy()
        updated_data["title"] = "Updated Push Day"

        mock_response = Mock()
        mock_response.json.return_value = updated_data
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.update_workout("workout-123", sample_workout)

        assert isinstance(result, WorkoutResponse)
        assert result.is_success
        assert result.workout is not None
        assert result.workout.title == "Updated Push Day"

        # Verify HTTP request
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "PUT"
        assert call_args[1]["url"] == "https://api.hevyapp.com/v1/workouts/workout-123"
        assert call_args[1]["json"] is not None

    @patch("requests.Session.request")
    def test_update_workout_not_found(self, mock_request, client, sample_workout):
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Workout not found"}
        mock_response.status_code = 404
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.update_workout("nonexistent-id", sample_workout)

        assert isinstance(result, WorkoutResponse)
        assert result.is_error
        assert result.status_code == 404
        assert result.workout is None

    # Network error tests
    @patch("requests.Session.request")
    def test_workout_api_network_error(self, mock_request, client, sample_workout):
        mock_request.side_effect = requests.ConnectionError("Network error")

        # Test all workout methods handle network errors
        methods_to_test = [
            (client.get_workout_count, []),
            (client.get_workouts, []),
            (client.get_workout, ["workout-123"]),
            (client.create_workout, [sample_workout]),
            (client.update_workout, ["workout-123", sample_workout]),
        ]

        for method, args in methods_to_test:
            result = method(*args)
            assert result.is_error
            assert result.status_code == 0
            assert "Network error" in str(result.data)

    # Request object tests
    def test_workout_request_objects(self):
        # Test GetWorkoutsCountRequest
        count_request = GetWorkoutsCountRequest()
        assert count_request.get_endpoint() == "/v1/workouts/count"
        assert count_request.get_method() == "GET"
        assert count_request.get_body() == {}

        # Test GetWorkoutsRequest
        workouts_request = GetWorkoutsRequest(page_number=2, page_size=10)
        assert workouts_request.get_endpoint() == "/v1/workouts?page=2&pageSize=10"
        assert workouts_request.get_method() == "GET"

        # Test GetWorkoutRequest
        workout_request = GetWorkoutRequest("workout-123")
        assert workout_request.get_endpoint() == "/v1/workouts/workout-123"
        assert workout_request.get_method() == "GET"

        # Test PostWorkoutRequest
        sample_workout = Workout(
            id="test-id",
            title="Test Workout",
            description="Test Description",
            start_time=datetime.now(),
            end_time=datetime.now(),
            updated_at=datetime.now(),
            created_at=datetime.now(),
            exercises=[],
        )
        post_request = PostWorkoutRequest(sample_workout)
        assert post_request.get_endpoint() == "/v1/workouts"
        assert post_request.get_method() == "POST"
        assert post_request.get_body() == sample_workout.model_dump()

        # Test PutWorkoutRequest
        put_request = PutWorkoutRequest("workout-123", sample_workout)
        assert put_request.get_endpoint() == "/v1/workouts/workout-123"
        assert put_request.get_method() == "PUT"
        assert put_request.get_body() == sample_workout.model_dump()
