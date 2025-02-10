import sqlite3
import os

DB_NAME = "library.db"

def get_db_connection():
    """Create and return a connection to the database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database and create tables if they do not exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                finNumber TEXT DEFAULT NULL,
                studentCardQR TEXT DEFAULT NULL,
                payableFines INTEGER DEFAULT 0,
                createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create Books Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bookId TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                image TEXT DEFAULT NULL,
                language TEXT DEFAULT NULL,
                status TEXT DEFAULT 'Available',
                summary TEXT DEFAULT NULL
            )
        ''')

        # Create Loans Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bookId TEXT NOT NULL,
                userId TEXT NOT NULL,
                borrowDate TEXT NOT NULL,
                branch TEXT NOT NULL,
                cancelStatus TEXT DEFAULT 'No',
                dueDate TEXT DEFAULT NULL,
                extendDate TEXT DEFAULT NULL,
                extendStatus TEXT DEFAULT 'No',
                returnDate TEXT DEFAULT NULL,
                FOREIGN KEY (bookId) REFERENCES books (bookId),
                FOREIGN KEY (userId) REFERENCES users (id)
            )
        ''')

        conn.commit()

def insert_books():
    """Insert sample books manually into the books table."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Insert Sample Books
        cursor.executemany('''
            INSERT OR IGNORE INTO books (bookId, title, author, genre, isbn, image, language, status, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            ("10001", "The Hobbit", "J.R.R. Tolkien", "Fantasy", "978-0547928227",
             "https://i.pinimg.com/736x/bc/e5/ee/bce5ee49b4ac62ac04624682d89c1973.jpg", "English", "Available", "A fantasy novel about Bilbo Baggins."),
             
            ("10002", "1984", "George Orwell", "Dystopian", "978-0451524935",
             "https://i.pinimg.com/736x/c5/d2/1b/c5d21b7fb9ebc896cf46d5e6d67af4a7.jpg", "English", "Available", "A dystopian novel about totalitarianism."),
             
            ("10003", "To Kill a Mockingbird", "Harper Lee", "Fiction", "978-0060935467",
             "https://i.pinimg.com/736x/f4/42/f8/f442f8fd4a956ec12e885eec3af03058.jpg", "English", "Available", "A novel about racial injustice in the Deep South."),
             
            ("10004", "Pride and Prejudice", "Jane Austen", "Romance", "978-0141040349",
             "https://i.pinimg.com/736x/44/0c/f2/440cf26fbc56038f637e88c611cf2469.jpg", "English", "Available", "A classic novel about love and society."),
             
            ("10005", "The Catcher in the Rye", "J.D. Salinger", "Fiction", "978-0316769488",
             "https://i.pinimg.com/736x/9d/ae/50/9dae502a832263180e16aa8beeae0e47.jpg", "English", "Available", "A novel about teenage rebellion and alienation."),
             
            ("10006", "The Great Gatsby", "F. Scott Fitzgerald", "Classic", "978-0743273565",
             "https://i.pinimg.com/736x/0e/d2/96/0ed296c2515faca99b63d2df238cf98a.jpg", "English", "Available", "A novel about wealth, love, and the American Dream.")
        ])

        conn.commit()

if __name__ == "__main__":
    if not os.path.exists(DB_NAME):  # Only initialize if the DB doesn't exist
        init_db()
        insert_books()
        print("Database initialized and sample books added.")
    else:
        print("Database already exists.")
