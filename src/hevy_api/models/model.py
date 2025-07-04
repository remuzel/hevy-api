from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WorkoutCount(BaseModel):
    workout_count: int


class Set(BaseModel):
    index: int
    type: str
    weight_kg: Optional[float] = None
    reps: Optional[int] = None
    distance_meters: Optional[float] = None
    duration_seconds: Optional[int] = None
    rpe: Optional[float] = None
    custom_metric: Optional[float] = None

    @property
    def summary(self):
        return self.model_dump(exclude={"index", "type"}, exclude_none=True)


class Exercise(BaseModel):
    index: int
    title: str
    notes: Optional[str] = None
    exercise_template_id: str
    supersets_id: Optional[int] = None
    sets: list[Set]

    @property
    def summary(self):
        summary = self.model_dump(include={"title", "notes"}, exclude_none=True)
        if len(summary["notes"]) == 0:
            del summary["notes"]
        summary["sets"] = [set.summary for set in self.sets]
        return summary


class Workout(BaseModel):
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    updated_at: datetime
    created_at: datetime
    exercises: list[Exercise]

    @property
    def duration(self):
        return self.end_time - self.start_time

    @property
    def summary(self):
        summary = self.model_dump(
            include={"id", "title", "description"}, exclude_none=True
        )
        if len(summary["description"]) == 0:
            del summary["description"]
        summary["duration"] = str(self.duration)
        summary["exercises"] = [exercise.summary for exercise in self.exercises]
        return summary


class Routine(BaseModel):
    id: str
    title: str
    folder_id: Optional[int] = None
    updated_at: datetime
    created_at: datetime
    exercises: list[Exercise]

    @property
    def summary(self):
        summary = self.model_dump(include={"id", "title"}, exclude_none=True)
        summary["exercises"] = [exercise.summary for exercise in self.exercises]
        return summary
