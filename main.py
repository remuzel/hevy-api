from dotenv import load_dotenv

from hevy_api.client import HevyClient
from hevy_api.models.model import Workout, WorkoutCount

load_dotenv()


def main():
    print("Hello from hevy-api!")
    client = HevyClient()

    n_workouts: WorkoutCount | None = client.get_workout_count().workout_count
    if n_workouts is None:
        exit("Could not find workouts...")
    print(n_workouts.model_dump(exclude_none=True, exclude_unset=True))

    last_workout: Workout | None = (client.get_workouts().workouts or [None])[-1]
    if last_workout is None:
        exit("Could not find workouts.")
    print(last_workout.summary)
    with open(f"data/{last_workout.id}.json", "w") as f:
        f.write(last_workout.model_dump_json(indent=4, exclude_none=True))


if __name__ == "__main__":
    main()
