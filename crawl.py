import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os

DB_PATH = "sqlite:///DB/crawlingBook.db"
os.makedirs("DB", exist_ok=True)
Base = declarative_base()

class BookLink(Base):
    __tablename__ = 'book_links'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    link = Column(String)
    details = relationship("BookDetail", back_populates="book_link", cascade="all, delete-orphan")

class BookDetail(Base):
    __tablename__ = 'book_details'
    id = Column(Integer, primary_key=True)
    book_link_id = Column(Integer, ForeignKey('book_links.id'))
    category = Column(String)
    title = Column(String)
    old_price = Column(String)
    new_price = Column(String)
    discount = Column(String)
    supplier = Column(String)
    description = Column(Text)
    img_url = Column(String)
    book_link = relationship("BookLink", back_populates="details")

def crawl_all_books(max_pages=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    engine = create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    base_url = "https://www.vinabook.com/collections/all"
    page = 1

    while True:
        if max_pages and page > max_pages:
            print("Đã crawl đủ số trang yêu cầu. Dừng!")
            break
        
        url = f"{base_url}?page={page}"
        print(f"\n📘 Đang crawl trang: {url}")

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}, dừng.")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        book_elements = soup.find_all('div', class_='product-item')
        print(f"🔎 Số lượng sách tìm thấy: {len(book_elements)}")

        if not book_elements:
            print("➡ Không còn sách nữa. Dừng crawl.")
            break

        for book in book_elements:
            name_element = book.find('h3', class_='pro-name')
            name = name_element.text.strip() if name_element else "Không rõ"

            link_element = name_element.find('a') if name_element else None
            link = f"https://www.vinabook.com{link_element['href']}" if link_element else None

            if not link:
                continue

            # Kiểm tra xem link có trong DB chưa
            exists = session.query(BookLink).filter_by(link=link).first()
            if exists:
                print(f"✔ Đã có trong DB: {link}")
                continue

            # Crawl trang chi tiết
            detail = crawl_detail_page(link)
            if detail:
                book_link = BookLink(name=name, link=link)
                book_detail = BookDetail(
                    category=detail['category'],
                    title=detail['title'],
                    old_price=detail['old_price'],
                    new_price=detail['new_price'],
                    discount=detail['discount'],
                    supplier=detail['supplier'],
                    description=detail['description'],
                    img_url=detail['img_url']
                )
                book_link.details.append(book_detail)
                session.add(book_link)
                session.commit()
                print(f"Lưu thành công: {detail['title']}")

        print(f"✅ Hoàn thành crawl trang {page}")
        page += 1

    session.close()
    print("\nHoàn thành crawl sách trong Vinabook!")



def crawl_detail_page(url):
    """Hàm crawl chi tiết sách từ link."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        category_element = soup.select_one('ol.breadcrumb li:nth-last-child(2) span')
        category = category_element.text.strip() if category_element else "Không rõ"

        title_element = soup.select_one('div.product-title h1')
        title = title_element.text.strip() if title_element else "Không rõ"

        old_price_element = soup.find('del')
        old_price = old_price_element.text.strip() if old_price_element else "Không rõ"

        new_price_element = soup.find('span', class_='pro-price')
        new_price = new_price_element.text.strip() if new_price_element else "Không rõ"

        discount_element = soup.find('span', class_='pro-sale')
        discount = discount_element.text.strip() if discount_element else "0%"

        supplier_element = soup.find('p', class_='product-type')
        supplier = supplier_element.text.strip() if supplier_element else "Không rõ"

        description_div = soup.select_one('div.tab-content')
        if not description_div:
            description_div = soup.find('div', class_='product-description')

        if description_div:
            full_text = description_div.get_text(separator="\n", strip=True)
            
            split_text = full_text.split("Thông tin chi tiết")[0].strip()
            description = split_text if split_text else full_text
        else:
            description = "Không rõ"

        img_element = soup.select_one('img.product-image-feature')
        img_url = img_element['src'] if img_element else "Không rõ"

        return {
            'category': category,
            'title': title,
            'old_price': old_price,
            'new_price': new_price,
            'discount': discount,
            'supplier': supplier,
            'description': description,
            'img_url': img_url
        }
    except Exception as e:
        print(f"Lỗi khi crawl trang chi tiết {url}: {e}")
        return None

crawl_all_books(max_pages=10)
