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
    print("=" * 120)
    
    # Заголовок таблицы
    header = "|| УЛИЦА || ДОМ || КВАРТИРА || КОМНАТЫ || ПЛОЩАДЬ ОБЩ. || ПЛОЩАДЬ ЖИЛ. || ЭТАЖ || ВЛАДЕЛЕЦ || ЦЕНА ||"
    print(header)
    print("=" * 120)
    
    # Преобразуем в список для проверки на пустоту
    items_list = list(items)
    
    if not items_list:
        print("||" + " " * 116 + "||")
        print("||" + " " * 40 + "Нет данных для отображения" + " " * 50 + "||")
        print("||" + " " * 116 + "||")
    else:
        # Строки таблицы
        for a in items_list:
            try:
                # Форматируем каждое поле с выравниванием
                street = (a.address.street[:20] if a.address.street else "").ljust(20)
                house = str(a.address.house if a.address.house else "").rjust(3)
                apartment = str(a.address.apartment if a.address.apartment else "").rjust(3)
                rooms = str(a.rooms if a.rooms else 0).rjust(3)
                total_area = f"{a.total_area if a.total_area else 0} м²".rjust(10)
                living_area = f"{a.living_area if a.living_area else 0} м²".rjust(10)
                floor = f"{a.floor if a.floor else 0}/{a.total_floors if a.total_floors else 0}".rjust(8)
                owner = (a.owner_last_name[:12] if a.owner_last_name else "").ljust(12)
                price = _format_price_rub(a.price if a.price else 0).rjust(15)
                
                row = f"|| {street} || {house} || {apartment} || {rooms} || {total_area} || {living_area} || {floor} || {owner} || {price} ||"
                print(row)
            except Exception as e:
                print(f"|| Ошибка при выводе записи: {e}" + " " * (116 - len(str(e))) + "||")
                continue
    
    print("=" * 120)


def _shell_sorted(items: list[Apartment], key_fn) -> list[Apartment]:
    """
    Сортировка Шелла по составному ключу (кортежу).
    Реализовано через декорирование: (key, item) -> shell_sort -> item.
    """
    if not items:
        return []
    
    try:
        decorated = [(key_fn(a), a) for a in items]
        shell_sort(
            decorated
        )  # сортирует по первому элементу кортежа (key), затем по второму при равенстве
        return [a for _, a in decorated]
    except Exception as e:
        # Если сортировка не удалась, возвращаем исходный список
        print(f"⚠️  Предупреждение: ошибка сортировки - {e}. Возвращен исходный порядок.")
        return items


def main() -> None:
    """
    Главная зацикленная функция:
    1 — вывод всех квартир (комнаты ↓, цена ↑)
    2 — вывод квартир с заданным количеством комнат
    3 — вывод квартир в диапазоне цен [N1, N2]
    0 — выход
    """
    json_path = "./aprtment.json"
    
    try:
        apartments, invalid_count, error_messages = read_apartments(json_path)
    except Exception as e:
        print(f"\n⚠️  КРИТИЧЕСКАЯ ОШИБКА: Не удалось загрузить данные - {e}")
        print("Программа завершена.")
        return

    # Вывод предупреждения о некорректных записях
    if invalid_count > 0:
        print("\n" + "=" * 120)
        print("⚠️  ВНИМАНИЕ: Обнаружены некорректные записи в базе данных!")
        print("=" * 120)
        print(f"Количество некорректных записей: {invalid_count}")
        print(f"Количество валидных записей: {len(apartments)}")
        print("\nДетали ошибок:")
        print("-" * 120)
        for error in error_messages[:10]:  # Показываем первые 10 ошибок
            print(f"  • {error}")
        if len(error_messages) > 10:
            print(f"  ... и еще {len(error_messages) - 10} ошибок")
        print("-" * 120)
        print("\n⚠️  Некорректные записи будут исключены из обработки и сортировки.")
        print("Работа программы продолжается только с валидными данными.\n")

    if not apartments:
        print("\n❌ ОШИБКА: Не удалось загрузить ни одной валидной записи.")
        print("Проверьте файл aprtment.json на наличие корректных данных.")
        return

    print(f"\n✓ Успешно загружено валидных квартир: {len(apartments)}")

    while True:
        try:
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
                try:
                    sorted_all = _shell_sorted(apartments, key_fn=lambda a: (-a.rooms, a.price))
                    _print_apartments("1) Все квартиры (комнаты ↓, цена ↑)", sorted_all)
                except Exception as e:
                    print(f"\n❌ Ошибка при сортировке: {e}")
                    continue

            elif choice == "2":
                # заданное число комнат, ключ: этаж ↑, этажность ↑, стоимость ↓
                try:
                    rooms = int(input("\nВведите количество комнат: ").strip())
                except ValueError:
                    print("❌ Некорректное количество комнат.")
                    continue
                except KeyboardInterrupt:
                    print("\n\nОперация отменена.")
                    continue
                except Exception as e:
                    print(f"\n❌ Ошибка ввода: {e}")
                    continue

                try:
                    filtered_rooms = [a for a in apartments if a.rooms == rooms]
                    if not filtered_rooms:
                        print(f"\n⚠️  Квартиры с {rooms} комнатами не найдены.")
                        continue

                    sorted_rooms = _shell_sorted(
                        filtered_rooms,
                        key_fn=lambda a: (a.floor, a.total_floors, -a.price),
                    )
                    _print_apartments(
                        f"2) Квартиры с {rooms} комн (этаж ↑, этажность ↑, цена ↓)",
                        sorted_rooms,
                    )
                except Exception as e:
                    print(f"\n❌ Ошибка при обработке данных: {e}")
                    continue

            elif choice == "3":
                # цена в диапазоне [N1, N2], ключ: стоимость ↓ + общая площадь ↑
                try:
                    n1_input = input("\nВведите N1 (минимальная цена): ").strip()
                    n2_input = input("Введите N2 (максимальная цена): ").strip()
                    n1 = int(n1_input)
                    n2 = int(n2_input)
                except ValueError:
                    print("❌ Некорректный ввод цены. Введите целые числа.")
                    continue
                except KeyboardInterrupt:
                    print("\n\nОперация отменена.")
                    continue
                except Exception as e:
                    print(f"\n❌ Ошибка ввода: {e}")
                    continue

                if n1 < 0 or n2 < 0:
                    print("❌ Цены не могут быть отрицательными.")
                    continue

                if n1 > n2:
                    n1, n2 = n2, n1
                    print(f"⚠️  Диапазон автоматически исправлен: [{n1}..{n2}]")

                try:
                    filtered_price = [a for a in apartments if n1 <= a.price <= n2]
                    if not filtered_price:
                        print(f"\n⚠️  Квартиры в диапазоне [{_format_price_rub(n1)}..{_format_price_rub(n2)}] не найдены.")
                        continue

                    sorted_price = _shell_sorted(
                        filtered_price,
                        key_fn=lambda a: (-a.price, a.total_area),
                    )
                    _print_apartments(
                        f"3) Квартиры в цене [{_format_price_rub(n1)}..{_format_price_rub(n2)}] (цена ↓, общ.пл. ↑)",
                        sorted_price,
                    )
                except Exception as e:
                    print(f"\n❌ Ошибка при обработке данных: {e}")
                    continue

            else:
                print("❌ Неизвестная команда, повторите ввод.")

        except KeyboardInterrupt:
            print("\n\nОперация прервана пользователем.")
            break
        except Exception as e:
            print(f"\n❌ Неожиданная ошибка: {e}")
            print("Попробуйте еще раз.")
            continue


if __name__ == "__main__":
    main()
