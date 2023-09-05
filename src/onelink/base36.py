from functools import partial
from io import StringIO
from itertools import combinations
from string import ascii_lowercase, digits

from typing import Final, Set

BASE: Final[str] = digits + ascii_lowercase
BASE_LEN: Final[int] = len(BASE)
BASE_SET: Final[Set[str]] = set(BASE)


def base36_encode(n: int) -> str:
    r = StringIO()
    while n:
        n, t = divmod(n, BASE_LEN)
        r.write(BASE[t])
    return r.getvalue()[::-1]


base36_decode = partial(int, base=BASE_LEN)


def base36_valid(s: str) -> bool:
    return all(map(BASE_SET.__contains__, s))


def test_encode_decode_4_chars():
    for letters in combinations(BASE, r=4):
        word = ''.join(letters)
        if word[0] == '0':
            continue

        encoded = word
        for _ in range(3):
            encoded = base36_encode(base36_decode(encoded))
        assert encoded == word

def test_decode_encode():
    for i in range(1, BASE_LEN ** 3):
        n = i
        for _ in range(3):
            n = base36_decode(base36_encode(n))
        assert i == n
