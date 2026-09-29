# lspeed

A tool for learning German with AI-generated, vocabulary-controlled content — text
tuned to what you already know, introducing only a few new words at a time.

Built as a learning project, for German and for LLM application engineering.

## Why

Most language apps either give you fixed content at a fixed level, or authentic
material that's far above your level. Neither adapts to the vocabulary you
personally know. An LLM can generate material calibrated to an individual
learner's word list — that's the idea being tested here.

## Example

Topic: *Meine Nachbarn*. Budget: 3 new content words.

> In meiner Straße in der Stadt wohnen viele freundliche Nachbarn. Neben meinem
> Haus lebt eine Familie mit zwei Kindern, einem Hund und einer Katze. Im Garten
> vor ihrem Haus steht ein großer Baum. Die Katze ist oft auf dem Baum, und der
> Hund ist im Garten. Am Wochenende wäscht mein Nachbar sein Auto auf der Straße,
> und wir sprechen dann über die Stadt, über den Garten und über unsere Familien.

The first attempt used nine words outside the known set. One targeted rewrite
brought it to zero.

## Status

Early but running end to end: generation, verification, repair, and a reader that
renders the result in a browser.

Working:
- Generates a B1-level German paragraph on a given topic via the Anthropic API
- Takes a known-word list and a budget for new content words
- Verifies the result by lemmatizing it with spaCy and comparing against the known set
- Repairs violations with a targeted rewrite, up to three attempts, keeping the
  history of each attempt
- Returns structured JSON (title, text, new words with English glosses) and
  validates its shape
- Serves a tokenized text over a JSON API and renders it as clickable words

At a budget of three new words, roughly three texts in five pass on the first
attempt; the rest converge after a single repair.

Not built yet:
- Clicking a word does nothing yet — no gloss, no grammar panel, no known-set update
- No spaced repetition, no review queue
- No persistence beyond flat files

## How it works

The model receives a list of known words, a topic, and a budget for new content
words. Function words (articles, pronouns, prepositions, conjunctions, auxiliaries,
modals, particles) don't count against the budget — a learner at this level already
knows them.

Prompting alone can't reliably enforce a vocabulary budget: a model has no
dependable access to which words it just produced, and can't count them while also
writing coherent prose. So the design is **generate → verify in code → repair on
violation**. Verification lemmatizes the output with spaCy and takes a set
difference against the known words. A violation triggers a rewrite naming the
specific offending words.

This gap is measurable. The model's own list of "new words" routinely disagrees
with what verification finds — it reports words the learner already knows, and
misses words it actually introduced. The model writes; the code decides.

## Running it

Requires Python 3.12+, an `ANTHROPIC_API_KEY` in a `.env` file, and the German
spaCy model:

    uv run python -m spacy download de_core_news_sm

Generate texts:

    uv run main.py

Generates one text per entry in `topics` and appends each result to `output.json`
as JSONL.

Serve the reader:

    uv run uvicorn app:app --reload

Then open http://localhost:8000 — it renders the most recently generated text.

## Layout

    main.py           prompt, API call, generation and repair loop, verification
    app.py            FastAPI routes: tokenized text endpoint, static files
    static/           the reader page
    known_words.txt   lemmas the learner knows
    free_words.txt    function words, exempt from the budget
    output.json       generated texts, one JSON object per line

## Direction

Not commitments, just where this could go, roughly in order:

- Clicking a word: gloss, gender and plural for nouns, case and agreement from
  spaCy's morphological features
- Known words built from what the learner taps, replacing the curated list
- Spaced repetition (FSRS) over the words collected that way
- Grounding texts in real news on topics the learner cares about
- Audio and listening practice
- Conversation with corrective feedback
- Pronunciation feedback

## Decisions

See `DECISIONS.md`.
