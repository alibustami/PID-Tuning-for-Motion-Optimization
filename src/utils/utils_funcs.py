from typing import Tuple


def floats_converter(num: float) -> Tuple[int, int]:
    dec_len = len(str(num)) - len(str(int(num))) - 1

    int_num = int(str(num).replace(".", ""))

    return int_num, max(dec_len, 0)
