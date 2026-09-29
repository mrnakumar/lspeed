# lspeed

A tool for learning German with AI-generated, vocabulary-controlled content — text
tuned to what you already know, introducing only a few new words at a time.

Built as a learning project with two goals: learning German, and moving from Java
development into AI engineering. Its first user is its author — see decision 011.

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
- The known set is still a curated Goethe B1 list, which decision 008 rejects
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

Generates one text per entry in `topics` and appends each result to `output.jsonl`.

Serve the reader:

    uv run uvicorn app:app --reload

Then open http://localhost:8000 — it renders the most recently generated text.

## Layout

    main.py           prompts, generation and repair loop
    llm.py            API call, JSON extraction and validation
    german.py         spaCy: new-word detection, tokenizing, word-list loading
    app.py            FastAPI routes: tokenized text endpoint, static files
    constants.py      JSON field names, output file name
    exceptions.py     API error types
    static/           the reader page
    known_words.txt   lemmas the learner knows (curated for now, see 008)
    free_words.txt    function words, exempt from the budget
    output.jsonl      generated texts, one JSON object per line

## Direction

Built for the author's own German first (decision 011). The gap to close is
grammar, not vocabulary.

Next, in order:

1. **Evals.** A fixed set of topics and budgets, a runner that records first-try
   pass rate, repairs, convergence, tokens, cost, and latency per case, and a
   comparison between runs — so every later change to prompts or models is
   measured rather than judged by feel.
2. **Grammar on tap.** Clicking a word shows case, gender, number, and why it has
   that form — `dem` after `mit` because `mit` takes the dative. The explanation is
   grounded in spaCy's morphological features and checked against them, plus a
   gloss.
3. **Seed the known set from phrases.** Run ~4000 Goethe B1 example phrases through
   spaCy once and keep the lemmas. Phrases are sentences, so the lemmas come out in
   context, the same way verification produces them, and they include the basic
   words (`sein`, `haben`, `fahren`) the B1 word list lacks. Replaces the curated
   `known_words.txt`; taps adjust it from there. Untested — becomes a decision once
   it works.
4. **Deploy and audio.** A hosted version with a real database, logging and cost
   tracking for every model call, so it works on a phone — then text-to-speech for
   each generated text, to listen to while walking.

Then read with it daily for two weeks and let that decide what comes after.

Later, not yet planned:
- Spaced repetition (FSRS) over tapped words
- Raising the level to B2, where the budget meters B2 vocabulary
- Texts grounded in real news on topics the learner cares about
- Practice generated from photos or PDFs of class notes
- Conversation and pronunciation feedback

Parked until the tool proves itself in daily use: anything commercial — teachers
and language schools, B1 exam prep, a native iPad app, handwritten answers with
Apple Pencil.

## Decisions

See `DECISIONS.md`.
