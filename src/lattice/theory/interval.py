from typing import Final

P1: Final = 0
P5: Final = 1
M2: Final = 2
M6: Final = 3
M3: Final = 4
M7: Final = 5
A4: Final = 6
A1: Final = 7
A5: Final = 8
P4: Final = -1
m7: Final = -2
m3: Final = -3
m6: Final = -4
m2: Final = -5
d5: Final = -6
d7: Final = -9
M9: Final = M2


def semitones(iv: int) -> int:
    return (iv * 7) % 12
