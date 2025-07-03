from typing import Any

from hevy_api.models.base import BaseRequest


class GetWorkoutRequest(BaseRequest):
    def __init__(self, trip_id: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.trip_id = trip_id

    def get_endpoint(self) -> str:
        return f"/trips/{self.trip_id}"

    def get_method(self) -> str:
        return "GET"
