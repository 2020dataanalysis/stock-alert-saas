from fastapi import FastAPI

app = FastAPI(title="Stock Alert SaaS")

@app.get("/")
def home():
    return {
        "status": "running",
        "app": "Stock Alert SaaS",
        "phase": "local MVP"
    }
