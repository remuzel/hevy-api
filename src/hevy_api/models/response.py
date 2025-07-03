from typing import Any, Optional

from hevy_api.models.base import BaseResponse
from hevy_api.models.model import Workout


class WorkoutResponse(BaseResponse):
    def __init__(self, data: Any, status_code: int, headers: dict[str, str]) -> None:
        super().__init__(data, status_code, headers)
        # Only create Workout model if response is successful and data is valid
        if self.is_success and data:
            try:
                self.workout: Optional[Workout] = Workout(**data)
            except Exception as e:
                print("Failed to serialize WorkoutResponse: ", e)
                self.workout = None
        else:
            self.workout = None
