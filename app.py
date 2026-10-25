from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime, timezone
import json
import time
import llm
from constants import FILE_OUTPUT, FILE_TAPS
from exceptions import ApiError
from explanation import Explanation, compare, explain
from german import mark_word, spacy_facts, tokenize
from fastapi.staticfiles import StaticFiles

app = FastAPI()


class ExplainRequest(BaseModel):
    text: str
    i: int


class ExplainResponse(Explanation):
    mismatches: list[str]


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
def api_explain(req: ExplainRequest) -> ExplainResponse:
    try:
        marked = mark_word(req.text, req.i)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    start = time.perf_counter()
    try:
        explanation = explain(marked)
    except ApiError as e:
        raise HTTPException(status_code=502, detail=str(e))
    seconds = time.perf_counter() - start
    facts = spacy_facts(req.text, req.i)
    mismatches = compare(explanation, facts)
    log_tap(marked, facts, explanation, mismatches, seconds)
    return ExplainResponse(**explanation.model_dump(), mismatches=mismatches)


def log_tap(marked, facts, explanation, mismatches, seconds):
    entry = {
        "time": datetime.now(timezone.utc).isoformat(),
        "model": llm.model,
        "seconds": round(seconds, 2),
        "marked_text": marked,
        "spacy": facts,
        "explanation": explanation.model_dump(),
        "mismatches": mismatches,
    }
    with open(FILE_TAPS, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


app.mount("/", StaticFiles(directory="static", html=True), name="static")
