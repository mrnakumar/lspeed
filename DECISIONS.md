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
