import os
from typing import Optional

import requests
from cachetools import TTLCache
from dotenv import load_dotenv

from hevy_api.models.base import BaseRequest, BaseResponse
from hevy_api.models.model import Routine, Workout
from hevy_api.models.request import (
    GetRoutineRequest,
    GetRoutinesRequest,
    GetWorkoutRequest,
    GetWorkoutsCountRequest,
    GetWorkoutsRequest,
    PostRoutineRequest,
    PostWorkoutRequest,
    PutRoutineRequest,
    PutWorkoutRequest,
)
from hevy_api.models.response import (
    RoutineResponse,
    RoutinesResponse,
    WorkoutCountResponse,
    WorkoutResponse,
    WorkoutsResponse,
)


class HTTPClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
    ):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

        # Set default headers from config
        headers = {
            "User-Agent": "HevyClient/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "api-key": api_key,
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
                json=request.get_body(),
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
    base_url: str = "https://api.hevyapp.com"

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_ttl: int = 300,  # 5 minutes,
        cache_maxsize: int = 1_000,
    ):
        if not api_key:
            load_dotenv()
            api_key = os.environ.get(self.env_token)
        if not api_key:
            raise ValueError(
                "api-key must be provided either directly or via configuration"
            )

        self.http_client = HTTPClient(
            base_url=self.base_url,
            api_key=api_key,
        )
        self._cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)

    #####################################################################
    # TODO - Check if we can merge these methods which are very similar #
    #####################################################################
    def get_workout_count(self) -> WorkoutCountResponse:
        # Check the cache first
        cache_key = WorkoutCountResponse.__name__
        cached_response = self._cache.get(cache_key)
        if cached_response is not None and isinstance(
            cached_response, WorkoutCountResponse
        ):
            return cached_response

        # Cache miss - make the API call
        response = self.http_client.execute(GetWorkoutsCountRequest())

        workouts_count = WorkoutCountResponse(
            data=response.data,
            status_code=response.status_code,
            headers=response.headers,
        )

        # Avoid caching error responses
        if workouts_count.is_success:
            self._cache[cache_key] = workouts_count

        return workouts_count

    def get_workout(self, workout_id: str) -> WorkoutResponse:
        # Check the cache first
        cached_response = self._cache.get(workout_id)
        if cached_response is not None and isinstance(cached_response, WorkoutResponse):
            return cached_response

        # Cache miss - make the API call
        request = GetWorkoutRequest(workout_id)
        response = self.http_client.execute(request)

        workout_response = WorkoutResponse(
            data=response.data,
            status_code=response.status_code,
            headers=response.headers,
        )

        # Avoid caching error responses
        if workout_response.is_success:
            self._cache[workout_id] = workout_response

        return workout_response

    def update_workout(self, workout_id: str, workout: Workout) -> WorkoutResponse:
        request = PutWorkoutRequest(workout_id, workout)
        response = self.http_client.execute(request)
        return WorkoutResponse(
            data=response.data,
            status_code=response.status_code,
            headers=response.headers,
        )

    def create_workout(self, workout: Workout) -> WorkoutResponse:
        request = PostWorkoutRequest(workout)
        response = self.http_client.execute(request)
        return WorkoutResponse(
            data=response.data,
            status_code=response.status_code,
            headers=response.headers,
        )

    def get_workouts(
        self, page_number: int = 1, page_size: int = 5
    ) -> WorkoutsResponse:
        # Check the cache first
        cache_key = f"{WorkoutsResponse.__name__}:{page_number}:{page_size}"
        cached_response = self._cache.get(cache_key)
        if cached_response is not None and isinstance(
            cached_response, WorkoutsResponse
        ):
            return cached_response

        # Cache miss - make the API call
        request = GetWorkoutsRequest(page_number, page_size)
        response = self.http_client.execute(request)

        workouts_response = WorkoutsResponse(
            data=response.data,
            status_code=response.status_code,
            headers=response.headers,
        )

        # Avoid caching error responses
        if workouts_response.is_success:
            self._cache[cache_key] = workouts_response

        return workouts_response

    def get_routine(self, routine_id: str) -> RoutineResponse:
        # Check the cache first
        cached_response = self._cache.get(routine_id)
        if cached_response is not None and isinstance(cached_response, RoutineResponse):
            return cached_response

        # Cache miss - make the API call
        request = GetRoutineRequest(routine_id)
        response = self.http_client.execute(request)

        routine_response = RoutineResponse(
            data=response.data,
            status_code=response.status_code,
            headers=response.headers,
        )

        # Avoid caching error responses
        if routine_response.is_success:
            self._cache[routine_id] = routine_response

        return routine_response

    def update_routine(self, routine_id: str, routine: Routine) -> RoutineResponse:
        request = PutRoutineRequest(routine_id, routine)
        response = self.http_client.execute(request)
        return RoutineResponse(
            data=response.data,
            status_code=response.status_code,
            headers=response.headers,
        )

    def create_routine(self, routine: Routine) -> RoutineResponse:
        request = PostRoutineRequest(routine)
        response = self.http_client.execute(request)
        return RoutineResponse(
            data=response.data,
            status_code=response.status_code,
            headers=response.headers,
        )

    def get_routines(
        self, page_number: int = 1, page_size: int = 5
    ) -> RoutinesResponse:
        # Check the cache first
        cache_key = f"{RoutinesResponse.__name__}:{page_number}:{page_size}"
        cached_response = self._cache.get(cache_key)
        if cached_response is not None and isinstance(
            cached_response, RoutinesResponse
        ):
            return cached_response

        # Cache miss - make the API call
        request = GetRoutinesRequest(page_number, page_size)
        response = self.http_client.execute(request)

        routines_response = RoutinesResponse(
            data=response.data,
            status_code=response.status_code,
            headers=response.headers,
        )

        # Avoid caching error responses
        if routines_response.is_success:
            self._cache[cache_key] = routines_response

        return routines_response
