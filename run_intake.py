import uvicorn


if __name__ == "__main__":
    uvicorn.run("legal_gateway.intake_service:service", host="127.0.0.1", port=8000)
