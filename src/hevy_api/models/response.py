from typing import Any, Optional

from hevy_api.models.base import BaseResponse
from hevy_api.models.model import Routine, Workout, WorkoutCount


class WorkoutCountResponse(BaseResponse):
    def __init__(self, data: Any, status_code: int, headers: dict[str, str]) -> None:
        super().__init__(data, status_code, headers)
        # Only create WorkoutCount model if response is successful and data is valid
        if self.is_success and data:
            try:
                self.workout_count: Optional[WorkoutCount] = WorkoutCount(**data)
            except Exception as e:
                print("Failed to serialize WorkoutCountResponse: ", e)
                self.workout_count = None
        else:
            self.workout_count = None


class WorkoutsResponse(BaseResponse):
    def __init__(self, data: Any, status_code: int, headers: dict[str, str]) -> None:
        super().__init__(data, status_code, headers)
        # Only create Workouts model if response is successful and data is valid
        if self.is_success and data:
            try:
                self.page: int = data["page"]
                self.page_count: int = data["page_count"]
                self.workouts: list[Workout] = [
                    Workout(**workout_data) for workout_data in data["workouts"]
                ]
            except Exception as e:
                print("Failed to serialize WorkoutsResponse: ", e)
                self.workouts = []
        else:
            self.workouts = []


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


class RoutinesResponse(BaseResponse):
    def __init__(self, data: Any, status_code: int, headers: dict[str, str]) -> None:
        super().__init__(data, status_code, headers)
        # Only create Routines model if response is successful and data is valid
        if self.is_success and data:
            try:
                self.page: int = data["page"]
                self.page_count: int = data["page_count"]
                self.routines: list[Routine] = [
                    Routine(**routine_data) for routine_data in data["routines"]
                ]
            except Exception as e:
                print("Failed to serialize RoutinesResponse: ", e)
                self.routines = []
        else:
            self.routines = []


class RoutineResponse(BaseResponse):
    def __init__(self, data: Any, status_code: int, headers: dict[str, str]) -> None:
        super().__init__(data, status_code, headers)
        # Only create Routine model if response is successful and data is valid
        if self.is_success and data:
            try:
                self.routine: Optional[Routine] = Routine(**data)
            except Exception as e:
                print("Failed to serialize RoutineResponse: ", e)
                self.routine = None
        else:
            self.routine = None
