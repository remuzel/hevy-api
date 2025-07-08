from unittest.mock import patch

import pytest

from hevy_api.client import HevyClient, HTTPClient


class TestHevyClient:
    def test_init_with_default_values(self):
        client = HevyClient(api_key="test_token")

        assert isinstance(client.http_client, HTTPClient)
        assert client.env_token == "HEVY_API_KEY"
        assert client.http_client.base_url == "https://api.hevyapp.com"
        assert client.http_client.session.headers["api-key"] == "test_token"
        assert client._cache.ttl == 300  # 5 minutes default
        assert client._cache.maxsize == 1000  # 1000 default
        assert hasattr(client, "_cache")
        assert client._cache.maxsize == 1000
        assert client._cache.ttl == 300

    @pytest.mark.parametrize(
        "env_value,should_raise",
        [
            ("valid_token", False),
            ("", True),
            (None, True),
        ],
    )
    @patch("hevy_api.client.load_dotenv")
    def test_init_with_env_token(
        self, mock_load_dotenv, env_value, should_raise, monkeypatch
    ):
        if env_value is not None:
            monkeypatch.setenv("HEVY_API_KEY", env_value)
        else:
            monkeypatch.delenv("HEVY_API_KEY", raising=False)

        if should_raise:
            with pytest.raises(
                ValueError,
                match="api-key must be provided either directly or via configuration",
            ):
                HevyClient()
        else:
            client = HevyClient()
            assert client.http_client.session.headers["api-key"] == env_value

        mock_load_dotenv.assert_called_once()

    @pytest.mark.parametrize("api_key", ["", None])
    @patch("hevy_api.client.load_dotenv")
    def test_init_none_token_loads_from_env(
        self, mock_load_dotenv, api_key, monkeypatch
    ):
        monkeypatch.setenv("HEVY_API_KEY", "env_token")

        client = HevyClient(api_key=api_key)
        assert client.http_client.session.headers["api-key"] == "env_token"
        mock_load_dotenv.assert_called_once()

    @patch("hevy_api.client.load_dotenv")
    def test_init_prioritizes_provided_token_over_env(
        self, mock_load_dotenv, monkeypatch
    ):
        monkeypatch.setenv("HEVY_API_KEY", "env_token")

        client = HevyClient(api_key="provided_token")
        assert client.http_client.session.headers["api-key"] == "provided_token"
        # load_dotenv should not be called when token is provided
        mock_load_dotenv.assert_not_called()
