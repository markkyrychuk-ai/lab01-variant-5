"""Головна програма аналізу бібліотечного каталогу (варіант 5)."""

from pathlib import Path

from catalog_analysis import (
    availability_percentage,
    count_by_genre,
    find_by_genre,
    find_oldest_and_newest,
    group_by_period,
    load_books,
    median_publication_year,
    save_processed,
    sort_by_year,
)


BASE_DIR = Path(__file__).resolve().parent


def print_report(books):
    """Виводить основні показники каталогу у читабельному вигляді."""
    print("\nЗВІТ: БІБЛІОТЕЧНИЙ КАТАЛОГ")
    print("=" * 34)
    print(f"Коректно завантажено книг: {len(books)}")
    if not books:
        print("Немає коректних записів для аналізу.")
        return

    print("\nКількість книг за жанрами:")
    for genre, amount in sorted(count_by_genre(books).items()):
        print(f"  {genre}: {amount}")

    oldest, newest = find_oldest_and_newest(books)
    print(f"\nНайстаріша книга: «{oldest['title']}» ({oldest['year']}), {oldest['author']}")
    print(f"Найновіша книга: «{newest['title']}» ({newest['year']}), {newest['author']}")
    print(f"Книг у наявності: {availability_percentage(books):.1f}%")
    print(f"Медіанний рік видання: {median_publication_year(books):g}")

    print("\nРозподіл за періодами видання:")
    for period, entries in sorted(group_by_period(books).items()):
        print(f"  {period}: {len(entries)}")

    print("\nПерші п'ять книг за роком видання:")
    for book in sort_by_year(books)[:5]:
        print(f"  {book['year']} — {book['title']} ({book['genre']})")


def main():
    """Завантажує дані, показує звіт, дає змогу шукати жанр і експортує CSV."""
    books = load_books(BASE_DIR / "books.csv")
    print_report(books)

    if books:
        try:
            genre = input("\nВведіть жанр для пошуку (Enter — пропустити): ").strip()
        except EOFError:
            genre = ""
        if genre:
            matches = find_by_genre(books, genre)
            if matches:
                print(f"Знайдено книг: {len(matches)}")
                for book in matches:
                    print(f"  {book['title']} — {book['author']} ({book['year']})")
            else:
                print(f"Книг у жанрі «{genre}» не знайдено.")

    output_path = BASE_DIR / "processed_books.csv"
    if save_processed(books, output_path):
        print(f"\nРезультат збережено у файл: {output_path.name}")


if __name__ == "__main__":
    main()
