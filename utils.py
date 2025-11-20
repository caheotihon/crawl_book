import sqlite3

DB_PATH = "DB/crawlingBook.db"

# Hàm kết nối cơ sở dữ liệu SQLite
def connect_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_books_paginated(conn, offset, limit):
    cursor = conn.cursor()
    query = """
        SELECT bd.id, bd.category, bd.title, bd.new_price, bd.old_price, bd.discount, bd.img_url, bl.link
        FROM book_details bd
        JOIN book_links bl ON bd.book_link_id = bl.id
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, (limit, offset))
    return cursor.fetchall()

def fetch_all_books(conn):
    cursor = conn.cursor()
    query = """
        SELECT bd.id, bd.category, bd.title, bd.new_price, bd.old_price, bd.discount, bd.img_url, bl.link
        FROM book_details bd
        JOIN book_links bl ON bd.book_link_id = bl.id
    """
    cursor.execute(query)
    return cursor.fetchall()

def fetch_book_detail(conn, book_id):
    cursor = conn.cursor()
    query = """
        SELECT bd.category, bd.title, bd.new_price, bd.old_price, bd.discount, bd.img_url, bd.description, bd.supplier, bl.link
        FROM book_details bd
        JOIN book_links bl ON bd.book_link_id = bl.id
        WHERE bd.id = ?
    """
    cursor.execute(query, (book_id,))
    return cursor.fetchone()

def fetch_related_books(conn, limit):
    cursor = conn.cursor()
    query = """
        SELECT bd.id, bd.category, bd.title, bd.new_price, bd.old_price, bd.discount, bd.img_url, bl.link
        FROM book_details bd
        JOIN book_links bl ON bd.book_link_id = bl.id
        ORDER BY RANDOM()
        LIMIT ?
    """
    cursor.execute(query, (limit,))
    return cursor.fetchall()

def fetch_books_by_keyword(conn, keyword):
    cursor = conn.cursor()
    query = """
        SELECT bd.id, bd.category, bd.title, bd.new_price, bd.old_price, bd.discount, bd.img_url, bl.link
        FROM book_details bd
        JOIN book_links bl ON bd.book_link_id = bl.id
        WHERE bd.title LIKE ?
    """
    cursor.execute(query, (f"%{keyword}%",))
    return cursor.fetchall()

def fetch_books_by_category(conn, category_name):
    cursor = conn.cursor()
    query = """
        SELECT bd.id, bd.category, bd.title, bd.new_price, bd.old_price, bd.discount, bd.img_url, bl.link
        FROM book_details bd
        JOIN book_links bl ON bd.book_link_id = bl.id
        WHERE LOWER(TRIM(bd.category)) = LOWER(TRIM(?))
    """
    cursor.execute(query, (category_name,))
    return cursor.fetchall()

def fetch_categories(conn):
    cursor = conn.cursor()
    query = "SELECT DISTINCT category FROM book_details ORDER BY category"
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]