# src/flyshell/misc/seasonal.py

from datetime import date, timedelta
import random


def _get_easter(year: int) -> date:
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def get_season(return_icons: bool) -> str:
    today = date.today()
    year = today.year
    # Halloween: 25 > 31 October
    halloween_start = date(year, 10, 25)
    halloween_end = date(year, 10, 31)
    # Winter / Christmas: 1 November > 31 December
    winter_start = date(year, 11, 1)
    winter_end = date(year, 12, 31)
    # Easter: Mon before Good Fri -> Easter Mon
    easter_sunday = _get_easter(year)
    easter_start = easter_sunday - timedelta(days=6)
    easter_end = easter_sunday + timedelta(days=1)
    if return_icons:
        halloween_icons = ["🎃", "👻", "🦇", "🕷️", "🧙"]
        winter_icons = ["🎄", "❄️", "⛄", "🎁", "🦌"]
        easter_icons = ["🐣", "🐰", "🥚", "🌷", "🍫"]
        if halloween_start <= today <= halloween_end:
            selected = random.sample(halloween_icons, 2)
        elif winter_start <= today <= winter_end:
            selected = random.sample(winter_icons, 2)
        elif easter_start <= today <= easter_end:
            selected = random.sample(easter_icons, 2)
        else:
            return ""
        return "".join(selected)
    if halloween_start <= today <= halloween_end:
        return "Halloween"
    elif winter_start <= today <= winter_end:
        return "Christmas"
    elif easter_start <= today <= easter_end:
        return "Easter"
    return ""
