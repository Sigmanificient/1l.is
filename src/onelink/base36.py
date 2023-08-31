from typing import Final, Optional


CHAR_LIST: Final[str] = "0123456789abcdefghijklmnopqrstuvwxyz"
NBR_CHAR: Final[int] = len(CHAR_LIST)


def base36_encode(input: int) -> Optional[str]:
    if input < 0:
        return None
    result = ""
    while input != 0:
        result += CHAR_LIST[input % NBR_CHAR]
        input //= NBR_CHAR
    return result


def base36_decode(input: str) -> Optional[int]:
    result = 0
    for i, c in enumerate(reversed(input)):
        index = CHAR_LIST.find(c)
        if index == -1:
            return None
        result += index * (NBR_CHAR ** i)
    return result
