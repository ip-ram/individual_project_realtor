from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class Address:
    street: str
    house: str
    apartment: str

    def format(self) -> str:
        return f"{self.street}, д. {self.house}, кв. {self.apartment}"


@dataclass(slots=True, frozen=True)
class Apartment:
    address: Address
    rooms: int
    total_area: int  # м²
    living_area: int  # м²
    floor: int
    total_floors: int
    owner_last_name: str
    price: int  # руб


def _digits_to_int(value: Any) -> int:
    """
    Extract digits from strings like:
    - "6 500 000 рублей" -> 6500000
    - "54 м²" -> 54
    Also accepts int/float-like.
    """
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    s = str(value)
    # Fast digit-only extraction (no regex)
    out = 0
    has_digit = False
    for ch in s:
        o = ord(ch) - 48
        if 0 <= o <= 9:
            has_digit = True
            out = out * 10 + o
    return out if has_digit else 0


def _strip_json_comments(text: str) -> str:
    """
    Removes:
    - // line comments
    - /* block comments */
    Not a full JSONC parser, but enough for typical учебный файл.
    """
    n = len(text)
    i = 0
    res: list[str] = []
    in_str = False
    esc = False

    while i < n:
        ch = text[i]
        if in_str:
            res.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            i += 1
            continue

        if ch == '"':
            in_str = True
            res.append(ch)
            i += 1
            continue

        # // ...
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            i += 2
            while i < n and text[i] not in "\r\n":
                i += 1
            continue

        # /* ... */
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i = i + 2 if i + 1 < n else n
            continue

        res.append(ch)
        i += 1

    return "".join(res)


def read_apartments(json_path: str) -> list[Apartment]:
    """
    Reads apartments from aprtment.json and returns normalized records.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        raw = f.read()

    raw = _strip_json_comments(raw)
    data = json.loads(raw)

    items = data.get("apartments", [])
    if not isinstance(items, list):
        return []

    out: list[Apartment] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        addr = item.get("address") or {}
        if not isinstance(addr, dict):
            addr = {}

        address = Address(
            street=str(addr.get("street", "")).strip(),
            house=str(addr.get("house", "")).strip(),
            apartment=str(addr.get("apartment", "")).strip(),
        )

        apt = Apartment(
            address=address,
            rooms=_digits_to_int(item.get("rooms")),
            total_area=_digits_to_int(item.get("total_area")),
            living_area=_digits_to_int(item.get("living_area")),
            floor=_digits_to_int(item.get("floor")),
            total_floors=_digits_to_int(item.get("total_floors")),
            owner_last_name=str(item.get("owner_last_name", "")).strip(),
            price=_digits_to_int(item.get("price")),
        )
        out.append(apt)

    return out


