from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app import schemas

def test_create_workout_log(client: TestClient, db_session: Session):
    # 1. Create an exercise first
    exercise_response = client.post(
        "/api/v1/exercises",
        json={"name": "벤치프레스", "category": "Push", "calc_multiplier": 1.0}
    )
    assert exercise_response.status_code == 200

    # 2. Now, create the workout log
    response = client.post(
        "/api/v1/workout-logs",
        json={"date": "2025-01-01", "exercise_name": "벤치프레스", "set_type": "Main", "set_num": "1", "weight": 100, "reps_or_time": 10, "unit": "회"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["exercise"]["name"] == "벤치프레스"
    assert data["weight"] == 100
