from typing import NamedTuple


class Reference(NamedTuple):
    name: str
    key: str
    functions: tuple[str, ...]


CORPUS: tuple[Reference, ...] = (
    Reference("trust", "Fm", ("bVImaj7", "i7")),
    Reference("dead_man_walking", "Am", ("bVImaj7", "v7")),
    Reference("rehab", "Am", ("i7", "v7")),
    Reference("wasting_time", "Gm", ("i7", "ii7", "v7")),
    Reference("poison", "Dm", ("i7", "v7", "V7")),
    Reference("clouded", "D", ("Imaj7", "vii_m7")),
    Reference("all_mine", "C#m", ("i7", "bII")),
    Reference("gravity", "E", ("ii9", "V7maj", "Imaj7", "vi7")),
    Reference("rolling_stone", "Bm", ("iv6add9", "v7", "i7", "bVImaj7")),
    Reference("talk_2_u", "Cm", ("i7", "iv7", "V7b13")),
    Reference("stay_down", "G#m", ("i7", "ii7", "V7", "bVImaj7")),
    Reference("show_u_off", "Am", ("i7", "bVImaj7", "iv7")),
    Reference("been_away", "Gm", ("iv7", "i7", "bVImaj7", "V7")),
    Reference("make_it_out", "Bm", ("i7", "IV7", "iv7")),
    Reference("price_of_fame", "G#m", ("i7", "bII")),
    Reference("loose_change", "C#m", ("iv7", "v7", "bVImaj7")),
    Reference("upset_feet", "Dm", ("i9",)),
)
