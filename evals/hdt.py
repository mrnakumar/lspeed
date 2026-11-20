"""The HDT treebank: German sentences with case, gender, and number annotated
by hand. Its text may only be shared for academic use, so the test file is
downloaded into data/ and kept out of git (decision 014).
"""

import hashlib
import urllib.request
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


if __name__ == "__main__":
    print(fetch())
