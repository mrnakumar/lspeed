# lspeed

A tool for learning German with AI-generated, vocabulary-controlled content — text
tuned to what you already know, introducing only a few new words at a time.

Built as a learning project, for German and for LLM application engineering.

## Why

Most language apps either give you fixed content at a fixed level, or authentic
material that's far above your level. Neither adapts to the vocabulary you
personally know. An LLM can generate material calibrated to an individual
learner's word list — that's the idea being tested here.

## Status

Early. A CLI script that generates texts and saves them to disk.

Working:
- Generates a B1-level German paragraph on a given topic via the Anthropic API
- Takes a known-word list and a budget for new content words
- Returns structured JSON (title, text, new words with English glosses)
- Validates the JSON shape and appends results to `output.json`

Not built yet:
- Vocabulary validation — checking the generated text actually respects the budget
- Regeneration when the budget is exceeded
- Any persistence beyond a flat file, any UI

## How it works

The model receives a list of known words, a topic, and a budget for new content
words. Function words (articles, pronouns, prepositions, conjunctions, auxiliaries,
modals, particles) don't count against the budget — a learner at this level already
knows them.

Prompting alone can't reliably enforce a vocabulary budget: a model has no
dependable access to which words it just produced, and can't count them while also
writing coherent prose. So the intended design is **generate → verify in code →
regenerate on violation**, with the verification done by lemmatizing the output and
comparing against the known set. Only the generation step exists so far.

## Running it

Requires Python 3.12+ and an `ANTHROPIC_API_KEY` in a `.env` file.

    uv run main.py

Generates one text per entry in `topics` and appends each result to `output.json`
as JSONL.

## Layout

    main.py        prompt, API call, JSON parsing and validation, file output
    output.json    generated texts, one JSON object per line

## Direction

Not commitments, just where this could go, roughly in order:

- Spaced repetition (FSRS) over the new words from each text
- A web UI: read, tap a word for its gloss, review what's due
- Grounding texts in real news on topics the learner cares about
- Audio and listening practice
- Conversation with corrective feedback
- Pronunciation feedback

## Decisions

See `DECISIONS.md`.
