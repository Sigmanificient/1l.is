from typing import Final, Optional
from itertools import combinations
from string import ascii_lowercase, digits


BASE: Final[str] = digits + ascii_lowercase
LEN_BASE: Final[int] = len(BASE)


def base36_encode(input: int) -> Optional[str]:
    if input < 0:
        return None
    result = []
    while input != 0:
        result += BASE[input % LEN_BASE]
        input //= LEN_BASE
    result.pop()
    return "".join(reversed(result))


def base36_decode(input: str) -> Optional[int]:
    if not input.isalnum():
        return None
    input = "a" + input.lower()
    result = 0
    for i, c in enumerate(reversed(input)):
        result += BASE.index(c) * (LEN_BASE ** i)
    return result


def test_encode_decode_4_chars():
    for letters in combinations(BASE, r=4):
        word = ''.join(letters)
        encoded = word

        for _ in range(3):
            decoded = base36_decode(encoded)
            assert decoded is not None
            encoded = base36_encode(decoded)
            assert encoded is not None
        assert encoded == word
