# Decisions

Short records of non-obvious choices and why they were made. Newest at the bottom.

---

## 001 — Web app, not native mobile

Solo developer with limited hours. A native app means two more codebases, app
store review cycles, and platform fees. A responsive web app (later a PWA for
offline review) gets most of the benefit at a fraction of the cost, and can be
wrapped with Capacitor if it ever needs to be in a store.

---

## 002 — Python backend, not Java

Java is the stronger language here by experience, but the LLM ecosystem,
libraries, and tooling are Python-first. Part of the point of this project is
learning that ecosystem.

---

## 003 — Generate, then verify in code — not prompt-only

A prompt can ask for a vocabulary budget but can't enforce one. The model has no
reliable access to which lemmas it just emitted, and can't count them while also
writing coherent prose. Python can do it exactly, with a set difference.

So: the model handles fluency and meaning, code handles compliance. Generation
produces a candidate, a validator checks it, violations trigger a targeted
regeneration ("replace these specific words"). Rejected: trying to make the
prompt strong enough on its own.

---

## 004 — Word budget applies to content words only

Function words (articles, pronouns, prepositions, conjunctions, auxiliaries,
modals, negation, numbers, question words, common particles) don't count against
the new-word budget.

There are only a few hundred of them in German and a learner at this level
already knows them. If they counted, the budget would be consumed by "der, die,
ist, mit, und" before a single interesting word appeared. The budget exists to
meter genuinely new vocabulary.

---

## 005 — Count distinct lemmas, not tokens

A new word appearing three times is one new word, not three. What's being
measured is how much new material the learner has to absorb; repetition helps
rather than costs.

---

## 006 — Compounds count as new

"Autobahn" counts as new even if "Auto" is known. German compounds are often not
transparent — Handschuh (glove), Fernseher (television), Krankenhaus (hospital).
Knowing the parts doesn't mean knowing the word. A transparent-compound exception
could be added later if texts turn out too easy.

---

## 007 — Free list, not part-of-speech tags, decides what's free

"Adverb" covers two different things: lexical adverbs that are real vocabulary
(schnell, gestern, plötzlich) and grammatical adverbs that are glue (auch, noch,
schon, immer, sehr, doch, mal). A POS tag can't tell them apart in a way that
matches what a learner needs to learn.

So the rule is: an explicit free list of lemmas is checked first; anything not on
it and tagged NOUN/VERB/ADJ/ADV counts against the budget. The free list is a
file that gets corrected whenever the validator flags something obviously wrong.
Proper nouns (Berlin, Anna) are exempt.

---

## 008 — Known words come from the reader, not a curated list

The first known-word list was a Goethe B1 vocabulary file. Two things went wrong
with it, and both are fatal to the approach rather than fixable within it.

First, it disagreed with spaCy about what a lemma is. The list had `andere`,
`nächst`, `zweit`; spaCy, reading those words in a sentence, produces `anderer`,
`nächstes`, `zweiter`. Same words, different strings, so the set lookup missed and
the validator flagged words the learner knows. The cause is that the two sides were
built by different processes — a lexicographer's citation forms on one side, spaCy's
in-context output on the other. Lemmatizing a bare word gives a different answer
than lemmatizing it in a sentence, so even normalizing the file through spaCy
wouldn't reconcile them.

Second, a B1 list is a list of words *added* at B1. It contains `abfahren` and
`losfahren` but not `fahren`; not `sein`, `haben`, `gehen`, `kommen`, `geben`.
The repair loop, told those were unknown, dutifully rewrote them out and replaced
them with `sein` and `haben` — the texts converged on the budget and got worse as
German. The constraint was satisfied and the output degraded.

So: the known set is built from what the learner taps while reading. spaCy produces
the lemma when the word is tapped and produces the same lemma when it next appears,
so it is the only authority on both sides of the comparison and the mismatch cannot
occur. Cold start is handled by the learner tapping, or later by a frequency list
run through spaCy once — never by a hand-maintained file.

Rejected: patching the list word by word. It doesn't converge, and every patch
encodes one more of spaCy's quirks into a file that has no way to stay in sync.

---

## 009 — Everything is clickable except punctuation

The first version reused the validator's NOUN/VERB/ADJ/ADV filter to decide which
words could be tapped. Wrong for two reasons.

A learner needs to ask about function words. `gegenüber`, `obwohl`, and why it's
`dem` and not `der` after `mit` are exactly the hard parts of German. Making them
untappable hides what most needs explaining.

And it coupled two unrelated decisions: what counts against the budget, and what a
learner can interact with. Those should move independently.

Tapping and recording are also separate actions. A tap shows an explanation for any
word; a second, explicit action adds a lemma to the known set. That keeps function
words out of vocabulary tracking without making them inert.

---

## 010 — No frontend framework

One page, a few DOM elements, one piece of state — which word is selected. React
and friends earn their cost when many components share complex state; that is not
this.

The stronger reason is that the UI requirements are still guesses. Nothing here has
been used for a day of real reading yet, and what the word panel should contain will
change once it has. Committing to a framework now means building abstractions around
assumptions that haven't been tested.

The backend returns JSON and the page renders it, so the frontend can be replaced
without touching the API. If a review screen later makes hand-written DOM updates
painful, that's the signal to revisit — probably with something small rather than
React.
