from fastapi import FastAPI

app = FastAPI(title="CodeJam Backend API")


@app.get("/")
def root():
    return {
        "message": "CodeJam Backend API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }