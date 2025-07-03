import argparse
import random

from dotenv import load_dotenv

from hevy_api.client import HevyClient
from hevy_api.models.response import WorkoutResponse
from hevy_api.models.model import Workout

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Hevy API Client Demo")
    parser.add_argument("--username", help="Hevy username", required=True)
    parser.add_argument("--workout-id", help="Specific workout ID to fetch")

    args = parser.parse_args()

    print("Hello from hevy-api!")
    client = HevyClient()
    get_workout_response: WorkoutResponse = client.get_workout(args.workout_id)
    workout: Workout | None = get_workout_response.workout
    if get_workout_response.is_error or workout is None:
        exit()
    print(workout.model_dump_json())
    with open(f"data/{args.username}-{workout.id}.json", "w") as f:
        f.write(workout.model_dump_json(indent=4))


if __name__ == "__main__":
    main()
