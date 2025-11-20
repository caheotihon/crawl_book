from utils import (
    fetch_books_paginated, fetch_all_books, fetch_book_detail,
    fetch_related_books, fetch_books_by_keyword, fetch_books_by_category,
    fetch_categories,
)
from search import search_books_by_tfidf

def get_all_books_paginated(conn, page, per_page):
    offset = (page - 1) * per_page
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM book_details")
    total_books = cursor.fetchone()[0]
    total_pages = (total_books + per_page - 1) // per_page

    books_raw = fetch_books_paginated(conn, offset, per_page)
    books = [
        {
            "id": book[0],
            "category": book[1],
            "title": book[2],
            "new_price": book[3],
            "old_price": book[4],
            "discount": book[5],
            "img_url": book[6],
            "link": book[7]
        }
        for book in books_raw
    ]
    return books, total_pages

def get_all_books(conn):
    books_raw = fetch_all_books(conn)
    if not books_raw:
        print("Không tìm thấy sách nào trong cơ sở dữ liệu.")
        return []
    return [
        {
            "id": book[0],
            "category": book[1],
            "title": book[2],
            "new_price": book[3],
            "old_price": book[4],
            "discount": book[5],
            "img_url": book[6],
            "link": book[7]
        }
        for book in books_raw
    ]

def get_book_detail(conn, book_id):
    book = fetch_book_detail(conn, book_id)
    if not book:
        return None
    return {
        "category": book[0],
        "title": book[1],
        "new_price": book[2],
        "old_price": book[3],
        "discount": book[4],
        "img_url": book[5],
        "description": book[6],
        "supplier": book[7],
        "link": book[8]
    }

def get_related_books(conn, limit=4):
    books_raw = fetch_related_books(conn, limit)
    if not books_raw:
        print("Không tìm thấy sách liên quan nào trong cơ sở dữ liệu.")
        return []
    return [
        {
            "id": book[0],
            "category": book[1],
            "title": book[2],
            "new_price": book[3],
            "old_price": book[4],
            "discount": book[5],
            "img_url": book[6],
            "link": book[7]
        }
        for book in books_raw
    ]

def parse_price(price_str):
    if not price_str:
        return 0
    price_str = price_str.replace('₫', '').replace(',', '').strip()
    try:
        return float(price_str)
    except ValueError:
        return 0

def search_books(conn, keyword, page=1, per_page=18, sort_price=None, category_name=None):
    all_books = fetch_all_books(conn)
    # Convert sqlite3.Row to dict
    all_books = [{k: book[k] for k in book.keys()} for book in all_books]

    # Tìm theo từ khóa
    if not keyword:
        matched_books = all_books
    else:
        matched_books = search_books_by_tfidf(keyword, all_books)

    # Lọc theo danh mục nếu có
    if category_name:
        matched_books = [
            book for book in matched_books
            if book['category'].strip().lower() == category_name.strip().lower()
        ]

    def safe_parse_price(book):
        price_str = book.get('new_price', '')
        return parse_price(price_str) if price_str else float('inf')

    # Sắp xếp theo giá
    if sort_price == 'asc':
        matched_books = sorted(matched_books, key=safe_parse_price)
    elif sort_price == 'desc':
        matched_books = sorted(matched_books, key=safe_parse_price, reverse=True)

    # Phân trang
    total_books = len(matched_books)
    total_pages = (total_books + per_page - 1) // per_page
    offset = (page - 1) * per_page
    books_paginated = matched_books[offset:offset + per_page]

    return books_paginated, total_pages



def get_books_by_category(conn, category_name, page=1, per_page=18, sort_price=None, keyword=None):
    books_raw = fetch_books_by_category(conn, category_name)

    # Nếu có từ khóa, lọc lại danh sách theo từ khóa
    if keyword:
        books_raw = [book for book in books_raw if keyword.lower() in book[2].lower()]  # book[2] là title

    # Sắp xếp nếu có yêu cầu
    if sort_price == 'asc':
        books_raw = sorted(books_raw, key=lambda book: parse_price(book[3]))  # new_price
    elif sort_price == 'desc':
        books_raw = sorted(books_raw, key=lambda book: parse_price(book[3]), reverse=True)

    total_books = len(books_raw)
    total_pages = (total_books + per_page - 1) // per_page
    offset = (page - 1) * per_page
    books_paginated = books_raw[offset:offset + per_page]

    books = [
        {
            "id": book[0],
            "category": book[1],
            "title": book[2],
            "new_price": book[3],
            "old_price": book[4],
            "discount": book[5],
            "img_url": book[6],
            "link": book[7]
        }
        for book in books_paginated
    ]
    return books, total_pages


def get_all_categories(conn):
    return fetch_categories(conn)