# lspeed

A German reader where tapping any word explains its grammar — case, gender,
number, and *why* it has that form. Explanations are written by an LLM, grounded
in spaCy's analysis of the sentence, and checked against it.

Built as a learning project with two goals: learning German, and moving from Java
development into AI engineering. Its first user is its author — see decisions 011
and 012.

## Why

Vocabulary is the easy half of German. Lists, audio, and spaced repetition get a
learner to thousands of words. Grammar is the hard half: why it's `dem` and not
`der` after `mit`, why the adjective ends in `-en` here and `-e` there, where the
verb goes. Textbooks teach those rules in isolation; reading is where they
actually show up.

The idea: read any German text, and when a form doesn't make sense, tap it and get
the reason — for that word, in that sentence.

## Example

Tapping `dem` in *Ich fahre mit dem Bus*:

> **dem** — dative, masculine, singular. Article of *Bus* (der Bus).
> Dative because *mit* always takes the dative.

spaCy supplies the facts (`Case=Dat`, `Gender=Masc`, `Number=Sing`, head `Bus`,
governed by `mit`). The model turns them into an explanation and names the rule.
Code then checks that the explanation states the same case, gender, and number
spaCy found.

## Status

Early. The reader exists; the grammar explanations don't yet.

Working:
- A FastAPI endpoint that tokenizes a text with spaCy and returns each token with
  its lemma
- A reader page that renders the text as tappable words — every word except
  punctuation (decision 009)
- A generator that writes a B1 text on a topic — what's left of the first
  version (see History), and currently the only source of text for the reader

Not built yet:
- Tapping a word does nothing yet
- No way to read your own text — paste or URL
- No evals

## How it works

The design, carried over from the first version, is **the model writes, the code
checks**. A model explaining grammar will sometimes state the wrong case or invent
a rule. spaCy's morphological analysis is exact about what it reports, so it serves
as both the input to the explanation and the check on it:

1. spaCy parses the sentence: lemma, part of speech, case, gender, number, tense,
   and the word each token depends on.
2. The tapped token's analysis and the sentence go to the model, which returns
   structured JSON: the facts, the rule, and a short explanation.
3. Code compares the facts in the explanation with spaCy's. A mismatch triggers a
   retry or flags the explanation.

spaCy is not always right either. Disagreements between the two are logged and
reviewed — deciding which source to trust is part of the work.

## Running it

Requires Python 3.12+, an `ANTHROPIC_API_KEY` in a `.env` file, and the German
spaCy model:

    uv run python -m spacy download de_core_news_sm

Serve the reader:

    uv run uvicorn app:app --reload

Then open http://localhost:8000 — it renders the most recently generated text
from `output.jsonl`.

Generate a text (see History):

    uv run main.py

## Layout

    app.py            FastAPI routes: tokenized text endpoint, static files
    german.py         spaCy: tokenizing
    static/           the reader page
    main.py           text generator: prompt, topics
    llm.py            API call, JSON extraction and validation
    constants.py      JSON field names, output file name
    exceptions.py     API error types
    output.jsonl      generated texts, one JSON object per line

## Direction

Each step teaches one AI engineering skill and closes part of the grammar gap
(decision 012). Steps are added when the previous one shows a reason for them.

1. **Grammar on tap.** Tap → spaCy analysis → model explanation as structured JSON
   → check against spaCy. Plus pasting your own text into the reader.
2. **Evals.** A hand-labelled gold set of tapped words, exact checks of
   case/gender/number against spaCy, an LLM judge for whether the stated rule is
   true, and comparisons across prompts and models — including whether a small,
   fast model is good enough, since someone is waiting on every tap.
3. **Grounding in a grammar reference.** Retrieve the relevant rule (two-way
   prepositions, adjective endings) and cite it — once evals show the model
   stating wrong rules. Retrieval gets its own eval.
4. **Practice.** Sentences that exercise the grammar points tapped most often,
   generated and checked by spaCy to contain that structure; answers graded by a
   model.
5. **A tutor with tools.** spaCy analysis, dictionary lookup, grammar-rule search —
   for follow-up questions like "but why not `der`?"

Later, not yet planned: deploying it with a database and per-call cost tracking;
audio of texts for listening on walks; spaced repetition over tapped words.

Parked: anything commercial (decision 011).

## History

The first version generated vocabulary-controlled texts: a B1 paragraph on a topic
using at most N words outside the learner's known set, verified by lemmatizing with
spaCy and repaired with a targeted rewrite on violation. Roughly three texts in five
passed on the first attempt; the rest converged after one repair.

It was set aside because it controlled vocabulary, which the author already had,
rather than grammar, which they didn't — and because it depended on an accurate
list of known words, which proved hard to build (decision 008). The reasons it was
set aside are in decision 012. The budget, repair loop, and word lists have been
removed (they remain in git history); the generator now writes a plain B1 text on a
topic and feeds the reader.

One observation from that version needs a correction. The model's own list of new
words routinely disagreed with spaCy's, which was first read as evidence that a
model can't track the words it produces. But the model was given a 10-word list
while spaCy checked against about 2,000 known words, so the disagreement was built
in. Whether a model can track its own vocabulary was never fairly measured.

## Decisions

See `DECISIONS.md`.
