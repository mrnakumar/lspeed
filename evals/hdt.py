"""The HDT treebank: German sentences with case, gender, and number annotated
by hand. Its text may only be shared for academic use, so the test file is
downloaded into data/ and kept out of git (decision 014).
"""

import hashlib
import urllib.request
from dataclasses import dataclass
from pathlib import Path

RELEASE = "r2.19"
URL = (
    "https://raw.githubusercontent.com/UniversalDependencies/UD_German-HDT/"
    f"{RELEASE}/de_hdt-ud-test.conllu"
)
SHA256 = "ebfc12668fdd968cc470169443216417364b1111abf6a79f2ba36df5a9976ada"
PATH = Path("data/de_hdt-ud-test.conllu")


def fetch() -> Path:
    """Download the test file once, and check it is exactly the pinned one."""
    if not PATH.exists():
        PATH.parent.mkdir(exist_ok=True)
        partial = PATH.with_suffix(".part")
        urllib.request.urlretrieve(URL, partial)
        partial.rename(PATH)
    digest = hashlib.sha256(PATH.read_bytes()).hexdigest()
    if digest != SHA256:
        raise ValueError(f"{PATH} has checksum {digest}, expected {SHA256}")
    return PATH


@dataclass
class Word:
    id: int
    form: str
    lemma: str
    upos: str  # broad word type: "PRON"
    xpos: str  # detailed word type: "PPER" (personal pronoun), "PIS" (indefinite)
    feats: dict[str, str]  # {"Case": "Dat", "Gender": "Masc", ...}


@dataclass
class Contraction:
    """A written word that HDT splits in two: im = in + dem."""

    form: str
    first: int  # id of the first word it joins
    last: int  # id of the last


@dataclass
class Sentence:
    id: str
    text: str
    words: list[Word]
    contractions: list[Contraction]


def read() -> dict[str, Sentence]:
    """All sentences of the test file, by sentence id.

    The file is CoNLL-U: comment lines start with #, each other line is one
    word with tab-separated columns, and a blank line ends a sentence.
    """
    sentences = {}
    meta, words, contractions = {}, [], []
    with open(fetch(), encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("#"):
                key, _, value = line[1:].partition("=")
                meta[key.strip()] = value.strip()
            elif line:
                cols = line.split("\t")
                if "-" in cols[0]:
                    first, last = cols[0].split("-")
                    contractions.append(Contraction(cols[1], int(first), int(last)))
                elif "." not in cols[0]:  # 3.1 would be an empty node; skip
                    words.append(
                        Word(
                            int(cols[0]),
                            cols[1],
                            cols[2],
                            cols[3],
                            cols[4],
                            _feats(cols[5]),
                        )
                    )
            elif words:
                sentence = Sentence(meta["sent_id"], meta["text"], words, contractions)
                sentences[sentence.id] = sentence
                meta, words, contractions = {}, [], []
    return sentences


def _feats(column: str) -> dict[str, str]:
    """Parse a feats column: "Case=Dat|Gender=Masc" -> {"Case": "Dat", ...}."""
    if column == "_":
        return {}
    return dict(pair.split("=", 1) for pair in column.split("|"))


if __name__ == "__main__":
    sentences = read()
    print(f"{len(sentences)} sentences")
    print(sentences["hdt-s10003"])
