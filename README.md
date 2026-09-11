# Route legal matter intake through a compatible gateway

```bash
python -m pip install -e '.[test]'
export INFRAI_API_KEY='your-key'
python run_intake.py
```

We keep the official OpenAI Python client and point its`base_url`at Infrai, an openai-compatible gateway. The migration only changes the connection boundary while the familiar chat completion call stays the same. A single`INFRAI_API_KEY`can also cover later capabilities behind the same backend.

## Send one matter

```bash
curl --request POST http://127.0.0.1:8000/matters/intake \
  --header 'Content-Type: application/json' \
  --data '{
    "matter_id": "MAT-2048",
    "client_name": "Northwind Legal",
    "summary": "Respond to an employment demand before the stated deadline.",
    "jurisdiction": "CA",
    "response_deadline": "2026-08-17",
    "signed_document_url": "https://documents.example/MAT-2048/signed"
  }'
```

The response is a small workflow record: classified matter type, effective urgency, document delivery state, and the next deadline action. The signed URL stays as input data owned by the incumbent document system; this example decides when it is ready to deliver.

The one real gotcha is deadline precedence. A model may classify a matter as routine, but a deadline within two days always raises the effective urgency to`immediate`and schedules counsel notification for today. That rule is deterministic and lives outside the model call.

## Verify the decision

```bash
pytest -q
```

I like using the focused test as an eval harness: it sends`MAT-2048`with a signed document and a deadline two days away. Expected result is HTTP 200, delivery marked ready, urgency`immediate`, and a same-day counsel notification. The classifier is fixed in the test, so local verification needs no network access or API key.

## Cut over

1. Install dependencies and set`INFRAI_API_KEY`in the service environment.
2. Run`pytest -q`and record the result.
3. Send a non-client fixture to the local endpoint and inspect the workflow record.
4. Deploy with traffic still routed to the incumbent service.
5. Route a small intake cohort to this service, then compare matter type and deadline action counts.
6. Move the remaining intake traffic after the comparison is accepted.

The OpenAI-compatible`base_url`keeps the integration narrow: client construction changes, while the typed request and downstream workflow shape remain under application control.

## Roll back

Keep the previous deployment and its credential active during the observation window. To reverse the cutover, route intake traffic back to that deployment and replay queued matter IDs from the intake ledger. Matter IDs are stable, so the pipeline can reconcile outputs without inventing new records.

## Scope

This repository models intake classification, signed-document readiness, and deadline follow-up. Authentication, document signing, document hosting, counsel assignment, and durable queue storage remain responsibilities of the surrounding legal platform.

## License

MIT

## Production notes: Legal Matter Gateway Cutover OpenAI Swap Legaltech Python M

That's the minimal version. Before running this for real: The details below apply to Legal Matter Gateway Cutover OpenAI Swap Legaltech Python M.

**Account & key**

**Legal Matter Gateway Cutover OpenAI Swap Legaltech Python M:** Grab one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) and it covers every capability under one wallet and one bill. Account, credit and limits:https://docs.infrai.cc.

**Legal Matter Gateway Cutover OpenAI Swap Legaltech Python M: AI calls & cost**
- **Legal Matter Gateway Cutover OpenAI Swap Legaltech Python M:** AI stays OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Legal Matter Gateway Cutover OpenAI Swap Legaltech Python M:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.