"""Функції для перевірки та аналізу бібліотечного каталогу з CSV."""

import csv
from collections import Counter
from pathlib import Path


REQUIRED_FIELDS = ("title", "author", "year", "genre", "available")
TRUE_VALUES = {"так", "yes", "true", "1", "наявна", "в наявності"}
FALSE_VALUES = {"ні", "no", "false", "0", "відсутня", "немає"}


def load_books(file_path):
    """Зчитує CSV, перевіряє поля й значення та повертає список словників.

    Рядки з помилками пропускаються, а їхні номери та причини виводяться
    у консоль. Порожні рядки і зайві пробіли обробляються без аварійного
    завершення програми.
    """
    books = []
    try:
        with Path(file_path).open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames:
                print("Помилка: CSV-файл порожній або не має заголовка.")
                return books
            missing = [field for field in REQUIRED_FIELDS if field not in reader.fieldnames]
            if missing:
                print("Помилка: у CSV бракує стовпців: " + ", ".join(missing))
                return books

            for line_number, row in enumerate(reader, start=2):
                try:
                    book = {key: (row.get(key) or "").strip() for key in REQUIRED_FIELDS}
                    if not book["title"] or not book["author"] or not book["genre"]:
                        raise ValueError("назва, автор і жанр не можуть бути порожніми")
                    book["year"] = int(book["year"])
                    if not 0 < book["year"] <= 2100:
                        raise ValueError("рік має бути в діапазоні 1–2100")
                    availability = book["available"].casefold()
                    if availability in TRUE_VALUES:
                        book["available"] = True
                    elif availability in FALSE_VALUES:
                        book["available"] = False
                    else:
                        raise ValueError("наявність має бути так/ні")
                    book["category"] = publication_period(book["year"])
                    books.append(book)
                except (TypeError, ValueError) as error:
                    print(f"Попередження: рядок {line_number} пропущено: {error}.")
    except OSError as error:
        print(f"Не вдалося відкрити файл {file_path}: {error}")
    return books


def publication_period(year):
    """Відносить книгу до категорії за роком видання."""
    if year < 1980:
        return "До 1980 року"
    if year < 2000:
        return "1980–1999"
    if year < 2020:
        return "2000–2019"
    return "2020 рік і новіші"


def count_by_genre(books):
    """Повертає кількість книг у кожному жанрі."""
    return Counter(book["genre"] for book in books)


def find_oldest_and_newest(books):
    """Повертає найстарішу й найновішу книгу або (None, None)."""
    if not books:
        return None, None
    return min(books, key=lambda book: book["year"]), max(books, key=lambda book: book["year"])


def availability_percentage(books):
    """Обчислює відсоток книг, які зараз є в наявності."""
    if not books:
        return 0.0
    return sum(book["available"] for book in books) / len(books) * 100


def median_publication_year(books):
    """Обчислює медіанний рік видання книг."""
    years = sorted(book["year"] for book in books)
    if not years:
        return None
    middle = len(years) // 2
    if len(years) % 2:
        return years[middle]
    return (years[middle - 1] + years[middle]) / 2


def sort_by_year(books, descending=False):
    """Повертає копію каталогу, відсортовану за роком видання."""
    return sorted(books, key=lambda book: (book["year"], book["title"].casefold()), reverse=descending)


def group_by_period(books):
    """Групує книги за періодами видання, визначеними умовами."""
    groups = {}
    for book in books:
        groups.setdefault(book["category"], []).append(book)
    return groups


def find_by_genre(books, genre):
    """Шукає книги за жанром без урахування регістру літер."""
    query = genre.strip().casefold()
    return [book for book in books if book["genre"].casefold() == query]


def save_processed(books, file_path):
    """Зберігає перевірені й відсортовані записи у форматі JSON або CSV."""
    path = Path(file_path)
    output_books = sort_by_year(books)
    try:
        if path.suffix.casefold() == ".json":
            import json

            with path.open("w", encoding="utf-8") as file:
                json.dump(output_books, file, ensure_ascii=False, indent=2)
        else:
            with path.open("w", encoding="utf-8-sig", newline="") as file:
                fields = list(REQUIRED_FIELDS) + ["category"]
                writer = csv.DictWriter(file, fieldnames=fields)
                writer.writeheader()
                for book in output_books:
                    row = book.copy()
                    row["available"] = "так" if row["available"] else "ні"
                    writer.writerow(row)
    except OSError as error:
        print(f"Не вдалося зберегти результат у {path}: {error}")
        return False
    return True
