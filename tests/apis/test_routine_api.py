from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import requests

from hevy_api.client import HevyClient
from hevy_api.models.model import Routine
from hevy_api.models.request import (
    GetRoutineRequest,
    GetRoutinesRequest,
    PostRoutineRequest,
    PutRoutineRequest,
)
from hevy_api.models.response import RoutineResponse, RoutinesResponse


class TestRoutineAPI:
    @pytest.fixture
    def client(self):
        return HevyClient(api_key="test_token")

    @pytest.fixture
    def sample_routine_data(self):
        return {
            "id": "routine-123",
            "title": "Upper Body Routine",
            "folder_id": 1,
            "updated_at": "2024-01-15T11:30:00Z",
            "created_at": "2024-01-15T10:00:00Z",
            "exercises": [
                {
                    "index": 0,
                    "title": "Pull-ups",
                    "notes": "Wide grip",
                    "exercise_template_id": "template-456",
                    "supersets_id": None,
                    "sets": [
                        {
                            "index": 0,
                            "type": "normal",
                            "weight_kg": None,
                            "reps": 12,
                            "distance_meters": None,
                            "duration_seconds": None,
                            "rpe": 7.0,
                            "custom_metric": None,
                        }
                    ],
                }
            ],
        }

    @pytest.fixture
    def sample_routine(self, sample_routine_data):
        return Routine(**sample_routine_data)

    @pytest.fixture
    def mock_successful_response(self):
        mock_response = Mock()
        mock_response.json.return_value = {"routine": {"id": "routine-123"}}
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

    # GET /v1/routines tests
    @patch("requests.Session.request")
    def test_get_routines_success(self, mock_request, client, sample_routine_data):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 3,
            "routines": [sample_routine_data],
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_routines(page_number=1, page_size=10)

        assert isinstance(result, RoutinesResponse)
        assert result.is_success
        assert result.page == 1
        assert result.page_count == 3
        assert len(result.routines) == 1
        assert result.routines[0].id == "routine-123"
        assert result.routines[0].title == "Upper Body Routine"

        # Verify HTTP request
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert (
            call_args[1]["url"]
            == "https://api.hevyapp.com/v1/routines?page=1&pageSize=10"
        )

    @patch("requests.Session.request")
    def test_get_routines_default_pagination(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {"page": 1, "page_count": 1, "routines": []}
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        client.get_routines()

        call_args = mock_request.call_args
        assert "page=1&pageSize=5" in call_args[1]["url"]

    @patch("requests.Session.request")
    def test_get_routines_empty_response(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 0,
            "routines": [],
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_routines()

        assert isinstance(result, RoutinesResponse)
        assert result.is_success
        assert len(result.routines) == 0

    @patch("requests.Session.request")
    def test_get_routines_serialization_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 1,
            "routines": [{"invalid": "data"}],  # Invalid routine data
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_routines()

        assert isinstance(result, RoutinesResponse)
        assert result.is_success
        assert result.routines == []  # Should be empty due to serialization error

    @patch("requests.Session.request")
    def test_get_routines_caching(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {"page": 1, "page_count": 1, "routines": []}
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        # First call
        result1 = client.get_routines(page_number=1, page_size=5)
        # Second call with same parameters should use cache
        result2 = client.get_routines(page_number=1, page_size=5)

        # Should only make one HTTP request due to caching
        mock_request.assert_called_once()
        assert result1.page == result2.page

    # GET /v1/routines/{id} tests
    @patch("requests.Session.request")
    def test_get_routine_success(self, mock_request, client, sample_routine_data):
        mock_response = Mock()
        mock_response.json.return_value = {"routine": sample_routine_data}
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_routine("routine-123")

        assert isinstance(result, RoutineResponse)
        assert result.is_success
        assert result.routine is not None
        assert result.routine.id == "routine-123"
        assert result.routine.title == "Upper Body Routine"
        assert len(result.routine.exercises) == 1

        # Verify HTTP request
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["url"] == "https://api.hevyapp.com/v1/routines/routine-123"

    @patch("requests.Session.request")
    def test_get_routine_not_found(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Routine not found"}
        mock_response.status_code = 404
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_routine("nonexistent-id")

        assert isinstance(result, RoutineResponse)
        assert result.is_error
        assert result.status_code == 404
        assert result.routine is None

    @patch("requests.Session.request")
    def test_get_routine_caching(self, mock_request, client, sample_routine_data):
        mock_response = Mock()
        mock_response.json.return_value = {"routine": sample_routine_data}
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        # First call
        result1 = client.get_routine("routine-123")
        # Second call should use cache
        result2 = client.get_routine("routine-123")

        # Should only make one HTTP request due to caching
        mock_request.assert_called_once()
        assert result1.routine.id == result2.routine.id

    @patch("requests.Session.request")
    def test_get_routine_serialization_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {"routine": {"invalid": "data"}}
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_routine("routine-123")

        assert isinstance(result, RoutineResponse)
        assert result.is_success
        assert result.routine is None  # Should be None due to serialization error

    # POST /v1/routines tests
    @patch("requests.Session.request")
    def test_create_routine_success(
        self, mock_request, client, sample_routine, sample_routine_data
    ):
        mock_response = Mock()
        mock_response.json.return_value = {"routine": sample_routine_data}
        mock_response.status_code = 201
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.create_routine(sample_routine)

        assert isinstance(result, RoutineResponse)
        assert result.is_success
        assert result.status_code == 201
        assert result.routine is not None
        assert result.routine.id == "routine-123"

        # Verify HTTP request
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["url"] == "https://api.hevyapp.com/v1/routines"
        assert call_args[1]["json"] is not None
        assert call_args[1]["json"]["title"] == "Upper Body Routine"

    @patch("requests.Session.request")
    def test_create_routine_validation_error(
        self, mock_request, client, sample_routine
    ):
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Invalid routine data"}
        mock_response.status_code = 400
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.create_routine(sample_routine)

        assert isinstance(result, RoutineResponse)
        assert result.is_error
        assert result.status_code == 400
        assert result.routine is None

    @patch("requests.Session.request")
    def test_create_routine_server_error(self, mock_request, client, sample_routine):
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_response.status_code = 500
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.create_routine(sample_routine)

        assert isinstance(result, RoutineResponse)
        assert result.is_error
        assert result.status_code == 500
        assert result.routine is None

    # PUT /v1/routines/{id} tests
    @patch("requests.Session.request")
    def test_update_routine_success(
        self, mock_request, client, sample_routine, sample_routine_data
    ):
        updated_data = sample_routine_data.copy()
        updated_data["title"] = "Updated Upper Body Routine"

        mock_response = Mock()
        mock_response.json.return_value = {"routine": updated_data}
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.update_routine("routine-123", sample_routine)

        assert isinstance(result, RoutineResponse)
        assert result.is_success
        assert result.routine is not None
        assert result.routine.title == "Updated Upper Body Routine"

        # Verify HTTP request
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "PUT"
        assert call_args[1]["url"] == "https://api.hevyapp.com/v1/routines/routine-123"
        assert call_args[1]["json"] is not None

    @patch("requests.Session.request")
    def test_update_routine_not_found(self, mock_request, client, sample_routine):
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Routine not found"}
        mock_response.status_code = 404
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.update_routine("nonexistent-id", sample_routine)

        assert isinstance(result, RoutineResponse)
        assert result.is_error
        assert result.status_code == 404
        assert result.routine is None

    @patch("requests.Session.request")
    def test_update_routine_unauthorized(self, mock_request, client, sample_routine):
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_response.status_code = 401
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.update_routine("routine-123", sample_routine)

        assert isinstance(result, RoutineResponse)
        assert result.is_error
        assert result.status_code == 401
        assert result.routine is None

    # Network error tests
    @patch("requests.Session.request")
    def test_routine_api_network_error(self, mock_request, client, sample_routine):
        mock_request.side_effect = requests.ConnectionError("Network error")

        # Test all routine methods handle network errors
        methods_to_test = [
            (client.get_routines, []),
            (client.get_routine, ["routine-123"]),
            (client.create_routine, [sample_routine]),
            (client.update_routine, ["routine-123", sample_routine]),
        ]

        for method, args in methods_to_test:
            result = method(*args)
            assert result.is_error
            assert result.status_code == 0
            assert "Network error" in str(result.data)

    @patch("requests.Session.request")
    def test_routine_api_timeout_error(self, mock_request, client, sample_routine):
        mock_request.side_effect = requests.Timeout("Request timeout")

        result = client.get_routine("routine-123")
        assert result.is_error
        assert result.status_code == 0
        assert "Request timeout" in str(result.data)

    # Request object tests
    def test_routine_request_objects(self):
        # Test GetRoutinesRequest
        routines_request = GetRoutinesRequest(page_number=2, page_size=10)
        assert routines_request.get_endpoint() == "/v1/routines?page=2&pageSize=10"
        assert routines_request.get_method() == "GET"
        assert routines_request.get_body() == {}

        # Test GetRoutineRequest
        routine_request = GetRoutineRequest("routine-123")
        assert routine_request.get_endpoint() == "/v1/routines/routine-123"
        assert routine_request.get_method() == "GET"

        # Test PostRoutineRequest
        sample_routine = Routine(
            id="test-id",
            title="Test Routine",
            folder_id=1,
            updated_at=datetime.now(),
            created_at=datetime.now(),
            exercises=[],
        )
        post_request = PostRoutineRequest(sample_routine)
        assert post_request.get_endpoint() == "/v1/routines"
        assert post_request.get_method() == "POST"
        assert post_request.get_body() == sample_routine.model_dump()

        # Test PutRoutineRequest
        put_request = PutRoutineRequest("routine-123", sample_routine)
        assert put_request.get_endpoint() == "/v1/routines/routine-123"
        assert put_request.get_method() == "PUT"
        assert put_request.get_body() == sample_routine.model_dump()

    # Edge cases and boundary tests
    @patch("requests.Session.request")
    def test_get_routines_large_page_size(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {"page": 1, "page_count": 1, "routines": []}
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        client.get_routines(page_number=1, page_size=1000)

        call_args = mock_request.call_args
        assert "pageSize=1000" in call_args[1]["url"]

    @patch("requests.Session.request")
    def test_routine_with_minimal_data(self, mock_request, client):
        minimal_routine_data = {
            "id": "minimal-routine",
            "title": "Minimal",
            "folder_id": None,
            "updated_at": "2024-01-15T11:30:00Z",
            "created_at": "2024-01-15T10:00:00Z",
            "exercises": [],
        }

        mock_response = Mock()
        mock_response.json.return_value = {"routine": minimal_routine_data}
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_routine("minimal-routine")

        assert isinstance(result, RoutineResponse)
        assert result.is_success
        assert result.routine is not None
        assert result.routine.folder_id is None
        assert len(result.routine.exercises) == 0
