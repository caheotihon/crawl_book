from flask import Flask, render_template, request
from render_template import get_book_detail, get_related_books, get_all_books_paginated, search_books, get_books_by_category, get_all_categories
from utils import connect_db
from urllib.parse import unquote
import os

app = Flask(__name__)

DB_PATH = "DB/crawlingBook.db"

if not os.path.exists(DB_PATH):
    print("File cơ sở dữ liệu không tồn tại!")

@app.context_processor
def inject_categories():
    conn = connect_db(DB_PATH)
    categories = get_all_categories(conn)
    conn.close()
    return dict(categories=categories)

@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 18
    conn = connect_db(DB_PATH)
    books, total_pages = get_all_books_paginated(conn, page, per_page)
    conn.close()
    return render_template('home.html', books=books, page=page, total_pages=total_pages)

@app.route('/story/<int:book_id>')
def story_detail(book_id):
    conn = connect_db(DB_PATH)
    book = get_book_detail(conn, book_id)
    related_books = get_related_books(conn, limit=4)
    conn.close()

    return render_template('story.html', book=book, related_books=related_books)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = 18
    sort_price = request.args.get('sort_price', '')
    selected_category = request.args.get('category_name', '')  # Thêm dòng này

    conn = connect_db(DB_PATH)
    books, total_pages = search_books(conn, query, page, per_page, sort_price, selected_category)
    conn.close()

    return render_template(
        'search.html', books=books, page=page, total_pages=total_pages, selected_category=selected_category, query=query,
        sort_price=sort_price, mode='search'
    )

@app.route('/category/<path:category_name>')
def category(category_name):
    category_name = unquote(category_name)
    page = request.args.get('page', 1, type=int)
    per_page = 18
    sort_price = request.args.get('sort_price', '', type=str)
    keyword = request.args.get('query', '', type=str)  # Lấy từ khóa tìm kiếm

    conn = connect_db(DB_PATH)
    books, total_pages = get_books_by_category(conn, category_name, page, per_page, sort_price, keyword)
    conn.close()

    return render_template('search.html', books=books, page=page, total_pages=total_pages,
                           selected_category=category_name,
                           sort_price=sort_price, query=keyword, mode='category')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
