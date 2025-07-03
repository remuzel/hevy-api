import os
from typing import Optional

import requests
from cachetools import TTLCache
from dotenv import load_dotenv

from hevy_api.models.base import BaseRequest, BaseResponse
from hevy_api.models.request import GetWorkoutRequest
from hevy_api.models.response import WorkoutResponse


class HTTPClient:
    def __init__(
        self,
        base_url: str,
        remember_token: str,
    ):
        self.base_url = base_url.rstrip("/")
        self.remember_token = remember_token
        self.session = requests.Session()

        # Set default headers from config
        headers = {
            "User-Agent": "HevyClient/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Cookie": f"remember_token={remember_token}",
        }

        self.session.headers.update(headers)

    def execute(self, request: BaseRequest) -> BaseResponse:
        url = f"{self.base_url}{request.get_endpoint()}"

        # Merge request headers with session headers
        headers = {**self.session.headers, **request.headers}

        try:
            response = self.session.request(
                method=request.get_method(),
                url=url,
                headers=headers,
            )

            # Try to parse JSON, fallback to text
            try:
                data = response.json()
            except ValueError:
                data = response.text

            return BaseResponse(
                data=data,
                status_code=response.status_code,
                headers=dict(response.headers),
            )

        except requests.RequestException as e:
            # Return error response
            return BaseResponse(data={"error": str(e)}, status_code=0, headers={})


class HevyClient:
    env_token: str = "HEVY_API_KEY"
    base_url: str = "todo"

    def __init__(
        self,
        remember_token: Optional[str] = None,
        cache_ttl: int = 300,  # 5 minutes,
        cache_maxsize: int = 1_000,
    ):
        if not remember_token:
            load_dotenv()
            remember_token = os.environ.get(self.env_token)
        if not remember_token:
            raise ValueError(
                "Remember token must be provided either directly or via configuration"
            )

        self.http_client = HTTPClient(
            base_url=self.base_url,
            remember_token=remember_token,
        )
        self._cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)

    def get_workout(self, workout_id: str) -> WorkoutResponse:
        # Check the cache first
        cached_response = self._cache.get(workout_id)
        if cached_response is not None and isinstance(cached_response, WorkoutResponse):
            return cached_response

        # Cache miss - make the API call
        request = GetWorkoutRequest(workout_id)
        response = self.http_client.execute(request)

        trip_response = WorkoutResponse(
            data=response.data,
            status_code=response.status_code,
            headers=response.headers,
        )

        # Avoid caching error responses
        if trip_response.is_success:
            self._cache[workout_id] = trip_response

        return trip_response
