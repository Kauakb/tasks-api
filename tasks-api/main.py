from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "hello"}

@app.get("/about")
def about():
    return {"project": "tasks-api", "author": "Kaua B"}