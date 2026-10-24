from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
from constants import FILE_OUTPUT
from exceptions import ApiError
from explanation import Explanation, explain
from german import mark_word, tokenize
from fastapi.staticfiles import StaticFiles

app = FastAPI()


class ExplainRequest(BaseModel):
    text: str
    i: int


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


@app.post("/api/explain")
def api_explain(req: ExplainRequest) -> Explanation:
    try:
        marked = mark_word(req.text, req.i)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        return explain(marked)
    except ApiError as e:
        raise HTTPException(status_code=502, detail=str(e))


app.mount("/", StaticFiles(directory="static", html=True), name="static")
