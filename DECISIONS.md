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

---

## 011 — Personal tool first, money later

The project has two goals: learning German, and moving from Java development into
AI engineering. Both are served by building a tool the author actually uses;
neither needs it to make money.

The author passed telc B1 on vocabulary alone: about 4000 Goethe B1 words and 4000
phrases as German–English audio, heard on walks, plus 40 hours of courses and a
prep book. The result was a big vocabulary and a weak grasp of grammar. That gap
is the target, so the next features are chosen by whether they help close it —
grammar explained on the word you tapped, and audio that fits the walking habit
that already works.

The career goal decides the order. Evals come first: they are the skill AI
engineering roles screen for most, and every later change to prompts or models
should be measured rather than judged by feel. The grammar panel comes next
because it serves both goals — it closes the grammar gap, and grounding the
model's explanation in spaCy's analysis and checking it is a core pattern of
the work.

Making money is a hypothesis to test later, not a goal to build toward. The space
is crowded (LingQ, Readle, Duolingo, plain ChatGPT), exact vocabulary control is
easy to copy and not visible to a learner, and a solo developer's bottleneck is
reaching users, not features. Commercial angles — teachers and language schools,
exam prep, practice from class notes — are recorded in the README and parked
until the tool has been used daily and helps.

Moved into evals: a blind comparison of budgeted texts against plain "write at
B1" texts. The German goal doesn't need it — for personal use the budget is one
parameter and can be loosened or dropped at any time — but it makes a good eval
case study: whether a constraint the code enforces produces a difference a
reader can see.

Rejected for now: a native iPad app. It adds a codebase and App Store overhead
(see 001), few learners have an iPad and Pencil, and the web reader already works
in Safari on iPad.

---

## 012 — A grammar reader, not a vocabulary-controlled generator

The first version generated texts with at most N words outside the learner's known
set. It worked — about three in five texts passed first time, the rest after one
repair — but it was aimed at the wrong problem.

The author knows about 4000 words; the gap is grammar (011). At that vocabulary,
most B1 texts, real ones included, already stay within a small budget of unknown
words. The budget was solving a problem the learner didn't have, at real cost:

- It rests on an accurate list of the learner's known words, and that list is hard
  to build (008). Every fix — seeding from phrases, building it from taps — is a
  workaround for that.
- Constraining which words the model may use makes the German stiffer.
- The model was judged against a list it never saw. It was given 10 words; spaCy
  checked against about 2,000. Giving it the full list would have made the check
  fair, but would not have changed what the tool teaches.

So the core becomes reading with grammar on tap. Any text can be read — pasted,
fetched, or generated. Tapping a word gives its case, gender, number, and the rule
behind the form, for that word in that sentence.

The pattern from 003 carries over, and is better motivated here. spaCy's analysis
goes to the model as the facts; the model writes the explanation; code checks the
explanation's facts against spaCy's. The model is now checked against exactly the
information it was given. And spaCy can be wrong too, so disagreements are logged
and reviewed rather than resolved automatically in spaCy's favour.

This also serves the career goal better. Explanations need structured output and
checks in code; their correctness is measurable against spaCy and a hand-labelled
gold set; a tap is interactive, so latency and model size matter; wrong rules give
a reason to ground explanations in a grammar reference; follow-up questions give a
reason for a tutor with tools. Each is added when the previous step shows the need,
not to fill a CV.

Changes to 011: the order is now grammar on tap first, then evals, since there is
nothing to evaluate until explanations exist. The planned comparison of budgeted
against unbudgeted texts is dropped.

Kept: the generator, as one source of text for the reader; tokenizing with spaCy;
the reader page; "everything is tappable" (009).

Dropped or deferred: seeding the known set from Goethe phrases; requiring texts to
use specific target words; the known-word budget as a goal. 004–008 describe the
first version and stay as a record of it.
