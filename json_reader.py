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


def _has_negative_value(value: Any) -> bool:
    """Проверяет, содержит ли значение отрицательное число или минус-символ"""
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value < 0
    s = str(value).strip()
    # Проверяем на наличие минуса перед цифрой
    if "-" in s:
        # Проверяем, что это не просто дефис в тексте
        parts = s.replace("-", " -").split()
        for part in parts:
            if part.startswith("-") and len(part) > 1:
                try:
                    float(part)
                    return True  # Найдено отрицательное число
                except ValueError:
                    pass
    return False


def read_apartments(json_path: str) -> tuple[list[Apartment], int, list[str]]:
    """
    Reads apartments from aprtment.json and returns normalized records.
    Returns: (valid_apartments, invalid_count, error_messages)
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        return [], 0, [f"Ошибка чтения файла: {e}"]

    try:
        raw = _strip_json_comments(raw)
        data = json.loads(raw)
    except Exception as e:
        return [], 0, [f"Ошибка парсинга JSON: {e}"]

    items = data.get("apartments", [])
    if not isinstance(items, list):
        return [], 0, ["Ошибка: 'apartments' не является списком"]

    valid_apartments: list[Apartment] = []
    invalid_count = 0
    error_messages: list[str] = []

    for idx, item in enumerate(items, 1):
        if not isinstance(item, dict):
            invalid_count += 1
            error_messages.append(f"Запись #{idx}: не является словарем")
            continue

        # Проверка адреса
        addr = item.get("address")
        if not isinstance(addr, dict):
            invalid_count += 1
            error_messages.append(f"Запись #{idx}: отсутствует или некорректный адрес")
            continue

        # Валидация полей адреса
        street = str(addr.get("street", "")).strip()
        house_raw = addr.get("house")
        apartment_raw = addr.get("apartment")

        # Проверка на отрицательные значения в текстовых полях
        errors = []
        if not street:
            errors.append("улица пустая")
        if _has_negative_value(street):
            errors.append("улица содержит отрицательное значение")

        if house_raw is None:
            errors.append("дом не указан")
        elif _has_negative_value(house_raw):
            errors.append("дом содержит отрицательное значение")

        if apartment_raw is None:
            errors.append("квартира не указана")
        elif _has_negative_value(apartment_raw):
            errors.append("квартира содержит отрицательное значение")

        # Преобразование house и apartment в строки
        house = str(house_raw).strip() if house_raw is not None else ""
        apartment = str(apartment_raw).strip() if apartment_raw is not None else ""

        # Валидация числовых полей
        def _safe_to_int(value: Any, field_name: str) -> tuple[int, list[str]]:
            """Безопасное преобразование в int с валидацией"""
            errs = []
            if value is None:
                errs.append(f"{field_name} не указано")
                return 0, errs

            if _has_negative_value(value):
                errs.append(f"{field_name} отрицательное")

            int_value = _digits_to_int(value)
            if int_value <= 0:
                errs.append(f"{field_name} должно быть положительным (получено: {value})")

            return int_value, errs

        rooms, room_errors = _safe_to_int(item.get("rooms"), "комнаты")
        total_area, area_errors = _safe_to_int(item.get("total_area"), "общая площадь")
        living_area, living_errors = _safe_to_int(item.get("living_area"), "жилая площадь")
        floor, floor_errors = _safe_to_int(item.get("floor"), "этаж")
        total_floors, floors_errors = _safe_to_int(item.get("total_floors"), "этажность")
        price, price_errors = _safe_to_int(item.get("price"), "цена")

        errors.extend(room_errors)
        errors.extend(area_errors)
        errors.extend(living_errors)
        errors.extend(floor_errors)
        errors.extend(floors_errors)
        errors.extend(price_errors)

        # Проверка владельца
        owner_last_name = str(item.get("owner_last_name", "")).strip()
        if not owner_last_name:
            errors.append("фамилия владельца пустая")
        if _has_negative_value(owner_last_name):
            errors.append("фамилия владельца содержит отрицательное значение")

        # Проверка логики (этаж не может быть больше этажности)
        if floor > 0 and total_floors > 0 and floor > total_floors:
            errors.append(f"этаж ({floor}) превышает этажность ({total_floors})")

        # Если есть ошибки, добавляем в список некорректных
        if errors:
            invalid_count += 1
            error_msg = f"Запись #{idx} ({street}, д. {house}, кв. {apartment}): " + ", ".join(errors)
            error_messages.append(error_msg)
            continue

        # Все проверки пройдены, создаем валидную запись
        try:
            address = Address(
                street=street,
                house=house,
                apartment=apartment,
            )

            apt = Apartment(
                address=address,
                rooms=rooms,
                total_area=total_area,
                living_area=living_area,
                floor=floor,
                total_floors=total_floors,
                owner_last_name=owner_last_name,
                price=price,
            )
            valid_apartments.append(apt)
        except Exception as e:
            invalid_count += 1
            error_messages.append(f"Запись #{idx}: ошибка создания объекта - {e}")

    return valid_apartments, invalid_count, error_messages


