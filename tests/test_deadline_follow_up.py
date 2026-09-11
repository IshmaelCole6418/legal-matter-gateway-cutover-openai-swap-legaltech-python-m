from datetime import date

from fastapi.testclient import TestClient

from legal_gateway.intake_service import classifier, service
from legal_gateway.matter_models import IntakeClassification, MatterIntake, MatterUrgency


class FixedClassifier:
    def classify(self, intake: MatterIntake) -> IntakeClassification:
        return IntakeClassification(
            matter_type="employment response",
            urgency=MatterUrgency.ROUTINE,
            intake_note=f"Review {intake.jurisdiction} response packet.",
        )


def test_signed_matter_near_deadline_is_escalated(monkeypatch) -> None:
    service.dependency_overrides[classifier] = FixedClassifier
    monkeypatch.setattr("legal_gateway.intake_service.date", FixedDate)
    try:
        response = TestClient(service).post(
            "/matters/intake",
            json={
                "matter_id": "MAT-2048",
                "client_name": "Northwind Legal",
                "summary": "Respond to an employment demand before the stated deadline.",
                "jurisdiction": "CA",
                "response_deadline": "2026-08-17",
                "signed_document_url": "https://documents.example/MAT-2048/signed",
            },
        )
    finally:
        service.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "matter_id": "MAT-2048",
        "matter_type": "employment response",
        "urgency": "immediate",
        "delivery_status": "signed document ready for client delivery",
        "follow_up_action": "notify assigned counsel today",
        "follow_up_on": "2026-08-15",
        "intake_note": "Review CA response packet.",
    }


class FixedDate(date):
    @classmethod
    def today(cls) -> "FixedDate":
        return cls(2026, 8, 15)
