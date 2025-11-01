from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_inbody_record(client: TestClient, db_session: Session):
    response = client.post(
        "/api/v1/inbody-records",
        json={"date": "2025-01-01", "weight": 70.5, "muscle_mass": 35.2, "fat_percent": 15.1}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["weight"] == 70.5

def test_create_duplicate_inbody_record(client: TestClient, db_session: Session):
    # First, create a record
    client.post(
        "/api/v1/inbody-records",
        json={"date": "2025-01-02", "weight": 70.5, "muscle_mass": 35.2, "fat_percent": 15.1}
    )
    # Then, try to create another record with the same date
    response = client.post(
        "/api/v1/inbody-records",
        json={"date": "2025-01-02", "weight": 71.0, "muscle_mass": 35.5, "fat_percent": 15.0}
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "A record for this date already exists."}
