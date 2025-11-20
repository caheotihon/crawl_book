from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import unicodedata
import re

# Hàm loại bỏ dấu tiếng Việt
def remove_accents(text):
    text = unicodedata.normalize('NFD', text)
    text = ''.join([c for c in text if unicodedata.category(c) != 'Mn'])
    text = re.sub(r'[^\w\s]', '', text)
    return text.lower()

# Hàm tìm kiếm
def search_books_by_tfidf(keyword, all_books):
    normalized_keyword = remove_accents(keyword)

    # Tạo danh sách tiêu đề sách đã loại bỏ dấu
    titles = [remove_accents(book['title']) for book in all_books]

    # Thêm từ khóa tìm kiếm vào cuối danh sách để tính TF-IDF
    documents = titles + [normalized_keyword]

    # Tính TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Tính độ tương đồng cosine giữa từ khóa và tiêu đề
    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

    # Sắp xếp kết quả theo mức độ tương đồng giảm dần
    related_docs_indices = cosine_similarities.argsort()[::-1]

    # Trả về danh sách sách có độ tương đồng cao
    result_books = []
    for idx in related_docs_indices:
        if cosine_similarities[idx] > 0.1:
            result_books.append(all_books[idx])
    return result_books
