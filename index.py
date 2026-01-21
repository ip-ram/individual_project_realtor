# Создать файл записей, в котором хранится информация о квартирах, продаваемых
# риэлтерским агентством: адрес (улица, дом, квартира), количество комнат, общая площадь,
# жилая площадь, этаж, этажность дома, фамилия владельца, стоимость.
#
# Задачи проекта:
# ======= 1
# Полный список всех квартир, который будет отсортирован следующему ключу:
# количество комнат (по убыванию) + стоимость (по возрастанию)
# ======= 2
# Список всех квартир с заданным количеством комнат , отсортированный по
# следующему ключу: этаж (по возрастанию), этажность дома (по возрастанию) +
# стоимость (по убыванию).
# ======= 3
# Список всех квартир стоимостью в диапазоне от N1 до N2 рублей, отсортированный
# по следующему ключу: стоимость (по убыванию) + общая площадь (по
# возрастанию).
#
# База должна содержать такие записи, чтобы во всех списках явно
# прослеживался заданный вид сортировки по всем ключам. Для сортировки записей
# использовать сортировку Шелла.

from __future__ import annotations

from typing import Iterable

import windows_methods  # noqa: F401  (подключение по заданию)
from json_reader import Apartment, read_apartments
from sort_methods import shell_sort


def _format_price_rub(price: int) -> str:
    # 6500000 -> "6 500 000 ₽"
    s = str(price)
    parts: list[str] = []
    i = len(s)
    while i > 0:
        j = i - 3
        if j < 0:
            j = 0
        parts.append(s[j:i])
        i = j
    return " ".join(reversed(parts)) + " ₽"


def _print_apartments(title: str, items: Iterable[Apartment]) -> None:
    print("\n" + title)
    print("-" * len(title))
    for a in items:
        print(
            f"{a.address.format()} | "
            f"комн: {a.rooms} | "
            f"общ: {a.total_area} м² | жил: {a.living_area} м² | "
            f"этаж: {a.floor}/{a.total_floors} | "
            f"вл: {a.owner_last_name} | "
            f"цена: {_format_price_rub(a.price)}"
        )


def _shell_sorted(items: list[Apartment], key_fn) -> list[Apartment]:
    """
    Сортировка Шелла по составному ключу (кортежу).
    Реализовано через декорирование: (key, item) -> shell_sort -> item.
    """
    decorated = [(key_fn(a), a) for a in items]
    shell_sort(
        decorated
    )  # сортирует по первому элементу кортежа (key), затем по второму при равенстве
    return [a for _, a in decorated]


def main() -> None:
    """
    Главная зацикленная функция:
    1 — вывод всех квартир (комнаты ↓, цена ↑)
    2 — вывод квартир с заданным количеством комнат
    3 — вывод квартир в диапазоне цен [N1, N2]
    0 — выход
    """
    json_path = "/home/ivanbaran/Projects/labPython/ind_project/aprtment.json"
    apartments = read_apartments(json_path)

    if not apartments:
        print("Не удалось прочитать список квартир (пусто или ошибка формата).")
        return

    while True:
        print("\nВыберите задачу:")
        print("1 — полный список всех квартир (комнаты ↓, цена ↑)")
        print("2 — квартиры с заданным количеством комнат")
        print("3 — квартиры в диапазоне стоимости [N1..N2]")
        print("0 — выход")

        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            print("Выход из программы.")
            break

        elif choice == "1":
            # комнаты (убыв) + стоимость (возр)
            sorted_all = _shell_sorted(apartments, key_fn=lambda a: (-a.rooms, a.price))
            _print_apartments("1) Все квартиры (комнаты ↓, цена ↑)", sorted_all)

        elif choice == "2":
            # заданное число комнат, ключ: этаж ↑, этажность ↑, стоимость ↓
            try:
                rooms = int(input("\nВведите количество комнат: ").strip())
            except ValueError:
                print("Некорректное количество комнат.")
                continue

            filtered_rooms = [a for a in apartments if a.rooms == rooms]
            sorted_rooms = _shell_sorted(
                filtered_rooms,
                key_fn=lambda a: (a.floor, a.total_floors, -a.price),
            )
            _print_apartments(
                f"2) Квартиры с {rooms} комн (этаж ↑, этажность ↑, цена ↓)",
                sorted_rooms,
            )

        elif choice == "3":
            # цена в диапазоне [N1, N2], ключ: стоимость ↓ + общая площадь ↑
            try:
                n1 = int(input("\nВведите N1 (минимальная цена): ").strip())
                n2 = int(input("Введите N2 (максимальная цена): ").strip())
            except ValueError:
                print("Некорректный ввод цены.")
                continue

            if n1 > n2:
                n1, n2 = n2, n1

            filtered_price = [a for a in apartments if n1 <= a.price <= n2]
            sorted_price = _shell_sorted(
                filtered_price,
                key_fn=lambda a: (-a.price, a.total_area),
            )
            _print_apartments(
                f"3) Квартиры в цене [{_format_price_rub(n1)}..{_format_price_rub(n2)}] (цена ↓, общ.пл. ↑)",
                sorted_price,
            )

        else:
            print("Неизвестная команда, повторите ввод.")


if __name__ == "__main__":
    main()
