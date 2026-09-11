from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from openai import APIConnectionError, APIStatusError, RateLimitError

from .legal_intake import GatewayIntakeClassifier, build_workflow
from .matter_models import MatterIntake, MatterWorkflow

service = FastAPI(title="Legal matter gateway cutover")


def classifier() -> GatewayIntakeClassifier:
    return GatewayIntakeClassifier()


@service.post("/matters/intake", response_model=MatterWorkflow)
def receive_matter(
    intake: MatterIntake,
    intake_classifier: GatewayIntakeClassifier = Depends(classifier),
) -> MatterWorkflow:
    try:
        classification = intake_classifier.classify(intake)
    except RateLimitError as exc:
        raise HTTPException(status_code=429, detail="Classification capacity is busy") from exc
    except APIStatusError as exc:
        raise HTTPException(status_code=exc.status_code, detail="Classification was rejected") from exc
    except APIConnectionError as exc:
        raise HTTPException(status_code=503, detail="Classification transport failed") from exc
    return build_workflow(intake, classification, date.today())
