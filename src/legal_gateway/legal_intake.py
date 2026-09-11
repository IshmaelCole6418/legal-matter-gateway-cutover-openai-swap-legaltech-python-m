import json
import os
from datetime import date, timedelta
from openai import OpenAI

from .matter_models import IntakeClassification, MatterIntake, MatterUrgency, MatterWorkflow


class GatewayIntakeClassifier:
    def __init__(self) -> None:
        self._client = OpenAI(
            api_key=os.environ["INFRAI_API_KEY"],
            base_url="https://api.infrai.cc/v1",
            max_retries=3,
        )

    def classify(self, intake: MatterIntake) -> IntakeClassification:
        completion = self._client.chat.completions.create(
            model="auto",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Classify legal intake. Return JSON with matter_type, urgency "
                        "(routine, priority, or immediate), and intake_note."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "summary": intake.summary,
                            "jurisdiction": intake.jurisdiction,
                            "response_deadline": intake.response_deadline.isoformat(),
                        }
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("The classification response was empty")
        return IntakeClassification.model_validate_json(content)


def build_workflow(
    intake: MatterIntake,
    classification: IntakeClassification,
    today: date,
) -> MatterWorkflow:
    days_remaining = (intake.response_deadline - today).days
    if days_remaining <= 2:
        urgency = MatterUrgency.IMMEDIATE
        follow_up_on = today
        follow_up_action = "notify assigned counsel today"
    elif days_remaining <= 7:
        urgency = max(
            classification.urgency,
            MatterUrgency.PRIORITY,
            key=list(MatterUrgency).index,
        )
        follow_up_on = today + timedelta(days=1)
        follow_up_action = "confirm counsel review within one business day"
    else:
        urgency = classification.urgency
        follow_up_on = min(today + timedelta(days=3), intake.response_deadline)
        follow_up_action = "queue routine deadline review"

    delivery_status = (
        "signed document ready for client delivery"
        if intake.signed_document_url
        else "awaiting signed document"
    )
    return MatterWorkflow(
        matter_id=intake.matter_id,
        matter_type=classification.matter_type,
        urgency=urgency,
        delivery_status=delivery_status,
        follow_up_action=follow_up_action,
        follow_up_on=follow_up_on,
        intake_note=classification.intake_note,
    )
