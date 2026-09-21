from fastapi import FastAPI

app = FastAPI(title="Stonks Maker API")

@app.get("/")
def read_root():
    return {"message": "Stonks Maker API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}