from typing import Any

from hevy_api.models.base import BaseRequest
from hevy_api.models.model import Routine, Workout


class GetWorkoutsCountRequest(BaseRequest):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def get_endpoint(self) -> str:
        return "/v1/workouts/count"

    def get_method(self) -> str:
        return "GET"


class GetExerciseTemplates(BaseRequest):
    def __init__(self, page_number: int, page_size: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.page_number = page_number
        self.page_size = page_size

    def get_endpoint(self) -> str:
        return (
            f"/v1/exercise_templates?page={self.page_number}&pageSize={self.page_size}"
        )

    def get_method(self) -> str:
        return "GET"


class GetExerciseTemplate(BaseRequest):
    def __init__(self, exercise_id: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.exercise_id = exercise_id

    def get_endpoint(self) -> str:
        return f"/v1/exercise_templates/{self.exercise_id}"

    def get_method(self) -> str:
        return "GET"


class GetWorkoutsRequest(BaseRequest):
    def __init__(self, page_number: int, page_size: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.page_number = page_number
        self.page_size = page_size

    def get_endpoint(self) -> str:
        return f"/v1/workouts?page={self.page_number}&pageSize={self.page_size}"

    def get_method(self) -> str:
        return "GET"


class GetWorkoutRequest(BaseRequest):
    def __init__(self, workout_id: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.workout_id = workout_id

    def get_endpoint(self) -> str:
        return f"/v1/workouts/{self.workout_id}"

    def get_method(self) -> str:
        return "GET"


class PutWorkoutRequest(BaseRequest):
    def __init__(self, workout_id: str, workout: Workout, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.workout = workout
        self.workout_id = workout_id

    def get_endpoint(self) -> str:
        return f"/v1/workouts/{self.workout_id}"

    def get_method(self) -> str:
        return "PUT"

    def get_body(self) -> dict[str, Any]:
        return self.workout.model_dump()


class PostWorkoutRequest(BaseRequest):
    def __init__(self, workout: Workout, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.workout = workout

    def get_endpoint(self) -> str:
        return "/v1/workouts"

    def get_method(self) -> str:
        return "POST"

    def get_body(self) -> dict[str, Any]:
        return self.workout.model_dump()


class GetRoutinesRequest(BaseRequest):
    def __init__(self, page_number: int, page_size: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.page_number = page_number
        self.page_size = page_size

    def get_endpoint(self) -> str:
        return f"/v1/routines?page={self.page_number}&pageSize={self.page_size}"

    def get_method(self) -> str:
        return "GET"


class GetRoutineRequest(BaseRequest):
    def __init__(self, routine_id: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.routine_id = routine_id

    def get_endpoint(self) -> str:
        return f"/v1/routines/{self.routine_id}"

    def get_method(self) -> str:
        return "GET"


class PutRoutineRequest(BaseRequest):
    def __init__(self, routine_id: str, routine: Routine, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.routine = routine
        self.routine_id = routine_id

    def get_endpoint(self) -> str:
        return f"/v1/routines/{self.routine_id}"

    def get_method(self) -> str:
        return "PUT"

    def get_body(self) -> dict[str, Any]:
        return self.routine.model_dump()


class PostRoutineRequest(BaseRequest):
    def __init__(self, routine: Routine, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.routine = routine

    def get_endpoint(self) -> str:
        return "/v1/routines"

    def get_method(self) -> str:
        return "POST"

    def get_body(self) -> dict[str, Any]:
        return self.routine.model_dump()
