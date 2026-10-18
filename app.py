from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json
from constants import FILE_OUTPUT
from german import tokenize
from fastapi.staticfiles import StaticFiles

app = FastAPI()


@app.get("/api/text")
def get_text():
    with open(FILE_OUTPUT, "r") as f:
        last_line = json.loads(f.readlines()[-1])
    content = last_line["response"]["content"]
    return {
        "title": content["title"],
        "text": content["text"],
        "tokens": tokenize(content["text"]),
    }


app.mount("/", StaticFiles(directory="static", html=True), name="static")
