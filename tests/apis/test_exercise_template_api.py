from unittest.mock import Mock, patch

import pytest
import requests

from hevy_api.client import HevyClient
from hevy_api.models.request import GetExerciseTemplate, GetExerciseTemplates
from hevy_api.models.response import ExerciseTemplateResponse, ExerciseTemplatesResponse


class TestExerciseTemplateAPI:
    @pytest.fixture
    def client(self):
        return HevyClient(api_key="test_token")

    @pytest.fixture
    def sample_exercise_template_data(self):
        return {
            "id": "template-123",
            "title": "Bench Press",
            "type": "barbell",
            "primary_muscle_group": "chest",
            "secondary_muscle_groups": ["shoulders", "triceps"],
            "is_custom": False,
        }

    @pytest.fixture
    def sample_custom_exercise_template_data(self):
        return {
            "id": "custom-template-456",
            "title": "Custom Cable Fly",
            "type": "cable",
            "primary_muscle_group": "chest",
            "secondary_muscle_groups": ["shoulders"],
            "is_custom": True,
        }

    @pytest.fixture
    def mock_successful_response(self):
        mock_response = Mock()
        mock_response.json.return_value = {"id": "template-123"}
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

    # GET /v1/exercise_templates tests
    @patch("requests.Session.request")
    def test_get_exercise_templates_success(
        self, mock_request, client, sample_exercise_template_data
    ):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 10,
            "exercise_templates": [sample_exercise_template_data],
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_exercise_templates(page_number=1, page_size=20)

        assert isinstance(result, ExerciseTemplatesResponse)
        assert result.is_success
        assert result.page == 1
        assert result.page_count == 10
        assert len(result.exercise_templates) == 1
        assert result.exercise_templates[0].id == "template-123"
        assert result.exercise_templates[0].title == "Bench Press"
        assert result.exercise_templates[0].primary_muscle_group == "chest"
        assert "shoulders" in result.exercise_templates[0].secondary_muscle_groups
        assert not result.exercise_templates[0].is_custom

        # Verify HTTP request
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert (
            call_args[1]["url"]
            == "https://api.hevyapp.com/v1/exercise_templates?page=1&pageSize=20"
        )

    @patch("requests.Session.request")
    def test_get_exercise_templates_default_pagination(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 1,
            "exercise_templates": [],
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        client.get_exercise_templates()

        call_args = mock_request.call_args
        assert "page=1&pageSize=5" in call_args[1]["url"]

    @patch("requests.Session.request")
    def test_get_exercise_templates_multiple_templates(
        self,
        mock_request,
        client,
        sample_exercise_template_data,
        sample_custom_exercise_template_data,
    ):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 1,
            "exercise_templates": [
                sample_exercise_template_data,
                sample_custom_exercise_template_data,
            ],
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_exercise_templates()

        assert isinstance(result, ExerciseTemplatesResponse)
        assert result.is_success
        assert len(result.exercise_templates) == 2

        # Check first template (standard)
        assert result.exercise_templates[0].id == "template-123"
        assert not result.exercise_templates[0].is_custom

        # Check second template (custom)
        assert result.exercise_templates[1].id == "custom-template-456"
        assert result.exercise_templates[1].is_custom

    @patch("requests.Session.request")
    def test_get_exercise_templates_empty_response(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 0,
            "exercise_templates": [],
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_exercise_templates()

        assert isinstance(result, ExerciseTemplatesResponse)
        assert result.is_success
        assert len(result.exercise_templates) == 0

    @patch("requests.Session.request")
    def test_get_exercise_templates_serialization_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 1,
            "exercise_templates": [{"invalid": "data"}],  # Invalid template data
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_exercise_templates()

        assert isinstance(result, ExerciseTemplatesResponse)
        assert result.is_success
        assert (
            result.exercise_templates == []
        )  # Should be empty due to serialization error

    @patch("requests.Session.request")
    def test_get_exercise_templates_caching(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 1,
            "exercise_templates": [],
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        # First call
        result1 = client.get_exercise_templates(page_number=1, page_size=5)
        # Second call with same parameters should use cache
        result2 = client.get_exercise_templates(page_number=1, page_size=5)

        # Should only make one HTTP request due to caching
        mock_request.assert_called_once()
        assert result1 == result2

    @patch("requests.Session.request")
    def test_get_exercise_templates_different_pagination_no_cache(
        self, mock_request, client
    ):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 1,
            "exercise_templates": [],
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        # Different pagination parameters should not use cache
        client.get_exercise_templates(page_number=1, page_size=5)
        client.get_exercise_templates(page_number=2, page_size=5)
        client.get_exercise_templates(page_number=1, page_size=10)

        # Should make three separate HTTP requests
        assert mock_request.call_count == 3

    # GET /v1/exercise_templates/{id} tests
    @patch("requests.Session.request")
    def test_get_exercise_template_success(
        self, mock_request, client, sample_exercise_template_data
    ):
        mock_response = Mock()
        mock_response.json.return_value = sample_exercise_template_data
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_exercise_template("template-123")

        assert isinstance(result, ExerciseTemplateResponse)
        assert result.is_success
        assert result.exercise_template is not None
        assert result.exercise_template.id == "template-123"
        assert result.exercise_template.title == "Bench Press"
        assert result.exercise_template.type == "barbell"
        assert result.exercise_template.primary_muscle_group == "chest"
        assert result.exercise_template.is_custom is False
        assert len(result.exercise_template.secondary_muscle_groups) == 2

        # Verify HTTP request
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert (
            call_args[1]["url"]
            == "https://api.hevyapp.com/v1/exercise_templates/template-123"
        )

    @patch("requests.Session.request")
    def test_get_exercise_template_not_found(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Exercise template not found"}
        mock_response.status_code = 404
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_exercise_template("nonexistent-id")

        assert isinstance(result, ExerciseTemplateResponse)
        assert result.is_error
        assert result.status_code == 404
        assert result.exercise_template is None

    @patch("requests.Session.request")
    def test_get_exercise_template_caching(
        self, mock_request, client, sample_exercise_template_data
    ):
        mock_response = Mock()
        mock_response.json.return_value = sample_exercise_template_data
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        # First call
        result1 = client.get_exercise_template("template-123")
        # Second call should use cache
        result2 = client.get_exercise_template("template-123")

        # Should only make one HTTP request due to caching
        mock_request.assert_called_once()
        assert result1 == result2

    @patch("requests.Session.request")
    def test_get_exercise_template_serialization_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_exercise_template("template-123")

        assert isinstance(result, ExerciseTemplateResponse)
        assert result.is_success
        assert (
            result.exercise_template is None
        )  # Should be None due to serialization error

    # Error handling tests
    @patch("requests.Session.request")
    def test_exercise_template_api_network_error(self, mock_request, client):
        mock_request.side_effect = requests.ConnectionError("Network error")

        # Test all exercise template methods handle network errors
        methods_to_test = [
            (client.get_exercise_templates, []),
            (client.get_exercise_template, ["template-123"]),
        ]

        for method, args in methods_to_test:
            result = method(*args)
            assert result.is_error
            assert result.status_code == 0
            assert "Network error" in str(result.data)

    @patch("requests.Session.request")
    def test_exercise_template_api_timeout_error(self, mock_request, client):
        mock_request.side_effect = requests.Timeout("Request timeout")

        result = client.get_exercise_template("template-123")
        assert result.is_error
        assert result.status_code == 0
        assert "Request timeout" in str(result.data)

    @patch("requests.Session.request")
    def test_exercise_template_api_server_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_response.status_code = 500
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_exercise_templates()

        assert isinstance(result, ExerciseTemplatesResponse)
        assert result.is_error
        assert result.status_code == 500
        assert result.exercise_templates == []

    @patch("requests.Session.request")
    def test_exercise_template_api_unauthorized(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_response.status_code = 401
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_exercise_template("template-123")

        assert isinstance(result, ExerciseTemplateResponse)
        assert result.is_error
        assert result.status_code == 401
        assert result.exercise_template is None

    # Request object tests
    def test_exercise_template_request_objects(self):
        # Test GetExerciseTemplates
        templates_request = GetExerciseTemplates(page_number=2, page_size=10)
        assert (
            templates_request.get_endpoint()
            == "/v1/exercise_templates?page=2&pageSize=10"
        )
        assert templates_request.get_method() == "GET"
        assert templates_request.get_body() == {}

        # Test GetExerciseTemplate
        template_request = GetExerciseTemplate("template-123")
        assert template_request.get_endpoint() == "/v1/exercise_templates/template-123"
        assert template_request.get_method() == "GET"
        assert template_request.get_body() == {}

    # Edge cases and boundary tests
    @patch("requests.Session.request")
    def test_get_exercise_templates_large_page_size(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 1,
            "exercise_templates": [],
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        client.get_exercise_templates(page_number=1, page_size=1000)

        call_args = mock_request.call_args
        assert "pageSize=1000" in call_args[1]["url"]

    @patch("requests.Session.request")
    def test_get_exercise_templates_zero_page_size(self, mock_request, client):
        mock_response = Mock()
        mock_response.json.return_value = {
            "page": 1,
            "page_count": 1,
            "exercise_templates": [],
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        client.get_exercise_templates(page_number=1, page_size=0)

        call_args = mock_request.call_args
        assert "pageSize=0" in call_args[1]["url"]

    @patch("requests.Session.request")
    def test_exercise_template_with_minimal_data(self, mock_request, client):
        minimal_template_data = {
            "id": "minimal-template",
            "title": "Minimal Exercise",
            "type": "bodyweight",
            "primary_muscle_group": "core",
            "secondary_muscle_groups": [],
            "is_custom": False,
        }

        mock_response = Mock()
        mock_response.json.return_value = minimal_template_data
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_exercise_template("minimal-template")

        assert isinstance(result, ExerciseTemplateResponse)
        assert result.is_success
        assert result.exercise_template is not None
        assert len(result.exercise_template.secondary_muscle_groups) == 0
        assert not result.exercise_template.is_custom

    @patch("requests.Session.request")
    def test_exercise_template_with_special_characters(self, mock_request, client):
        template_id = "template-with-special-chars_123"

        mock_response = Mock()
        mock_response.json.return_value = {
            "id": template_id,
            "title": "Special Exercise",
            "type": "machine",
            "primary_muscle_group": "legs",
            "secondary_muscle_groups": ["glutes"],
            "is_custom": True,
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        result = client.get_exercise_template(template_id)

        assert isinstance(result, ExerciseTemplateResponse)
        assert result.is_success
        assert result.exercise_template is not None
        assert result.exercise_template.id == template_id

        # Verify URL encoding is handled correctly
        call_args = mock_request.call_args
        assert template_id in call_args[1]["url"]
