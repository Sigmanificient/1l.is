from typing import Final, Optional
from itertools import combinations
from string import ascii_lowercase, digits
from io import StringIO


BASE: Final[str] = digits + ascii_lowercase
LEN_BASE: Final[int] = len(BASE)


def base36_encode(n: int) -> str:
    r = StringIO()
    while n:
        n, t = divmod(n, LEN_BASE)
        r.write(BASE[t])
    return r.getvalue()[::-1]


def base36_decode(input: str) -> int:
    return int(input.lower(), 36)


def base36_valid(input: str) -> bool:
    return all(char in BASE for char in input)


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
    for i in range(1, LEN_BASE ** 3):
        n = i
        for _ in range(3):
            n = base36_decode(base36_encode(n))
        assert i == n
