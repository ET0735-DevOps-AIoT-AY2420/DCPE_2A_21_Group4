import sqlite3
import os

DB_NAME = "/home/pi/ET0735/DCPE_2A_21_Group4/DCPE_2A_21_Group4/library.db"

def get_db_connection():
    """Create and return a connection to the database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database and create tables if they do not exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Create Users Table with RFID ID
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                finNumber TEXT DEFAULT NULL,
                studentCardQR TEXT UNIQUE NOT NULL,
                payableFines INTEGER DEFAULT 0,
                rfid_id TEXT UNIQUE DEFAULT NULL,
                createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Index for faster lookup
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON users (email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rfid ON users (rfid_id);")

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
                branchBookId INTEGER NOT NULL,
                bookId TEXT NOT NULL,
                userId INTEGER NOT NULL,
                isbn TEXT NOT NULL,
                borrowDate TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                branch TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                cancelStatus TEXT DEFAULT 'No',
                dueDate TEXT DEFAULT NULL,
                extendDate TEXT DEFAULT NULL,
                extendStatus TEXT DEFAULT 'No',
                returnDate TEXT DEFAULT NULL,
                FOREIGN KEY (bookId) REFERENCES books (bookId) ON DELETE CASCADE,
                FOREIGN KEY (branchBookId) REFERENCES branch_books (id) ON DELETE CASCADE,
                FOREIGN KEY (userId) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
           CREATE TABLE IF NOT EXISTS branches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')

          # Create Branch Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS branch_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                branchId INTEGER NOT NULL,
                bookId TEXT NOT NULL,
                status TEXT DEFAULT 'Available',
                FOREIGN KEY (branchId) REFERENCES branches (id) ON DELETE CASCADE,
                FOREIGN KEY (bookId) REFERENCES books (bookId) ON DELETE CASCADE,
                UNIQUE (branchId, bookId)  
            )

        ''')

        conn.commit()

def insert_books():
    """Insert sample books manually into the books table."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        books = [
            ("10001", "The Hobbit", "J.R.R. Tolkien", "Fantasy", "book-10001", 
             "https://i.pinimg.com/736x/bc/e5/ee/bce5ee49b4ac62ac04624682d89c1973.jpg", "English", "Available", "A fantasy novel about Bilbo Baggins."),
            
            ("10002", "1984", "George Orwell", "Dystopian", "book-10002", 
             "https://i.pinimg.com/736x/c5/d2/1b/c5d21b7fb9ebc896cf46d5e6d67af4a7.jpg", "English", "Available", "A dystopian novel about totalitarianism."),
            
            ("10003", "To Kill a Mockingbird", "Harper Lee", "Fiction", "book-10003", 
             "https://i.pinimg.com/736x/f4/42/f8/f442f8fd4a956ec12e885eec3af03058.jpg", "English", "Available", "A novel about racial injustice in the Deep South."),
            
            ("10004", "Pride and Prejudice", "Jane Austen", "Romance", "book-10004", 
             "https://i.pinimg.com/736x/44/0c/f2/440cf26fbc56038f637e88c611cf2469.jpg", "English", "Available", "A classic novel about love and society."),
            
            ("10005", "The Catcher in the Rye", "J.D. Salinger", "Fiction", "book-10005", 
             "https://i.pinimg.com/736x/9d/ae/50/9dae502a832263180e16aa8beeae0e47.jpg", "English", "Available", "A novel about teenage rebellion and alienation."),
            
            ("10006", "The Great Gatsby", "F. Scott Fitzgerald", "Classic", "book-10006", 
             "https://i.pinimg.com/736x/0e/d2/96/0ed296c2515faca99b63d2df238cf98a.jpg", "English", "Available", "A novel about wealth, love, and the American Dream."),

             ("10007", "Death Note", "Tsugumi Ohba", "Manga", "book-10007", 
             "https://i.pinimg.com/736x/19/8e/c6/198ec67a64d88382c3f6432be9a9f5b8.jpg", "Japanese", "Available", "A psychological thriller about a notebook that can kill."),
    
            ("10008", "Attack on Titan", "Hajime Isayama", "Manga", "book-10008", 
            "https://i.pinimg.com/736x/e0/8a/44/e08a44338b9a05023f88f7804d9a811a.jpg", "Japanese", "Available", "A story of humanity's fight against Titans."),
            
            ("10009", "One Piece", "Eiichiro Oda", "Manga", "book-10009", 
            "https://i.pinimg.com/736x/9c/67/85/9c678519ec0383f1a69a5469f93246ed.jpg", "Japanese", "Available", "An adventure of a pirate seeking the One Piece treasure."),
            
            ("10010", "The Alchemist", "Paulo Coelho", "Philosophical Fiction", "book-10010", 
            "https://i.pinimg.com/474x/ac/87/5c/ac875c2d6ad4cb80d786a4a9e177354a.jpg", "English", "Available", "A journey of self-discovery and destiny."),
            
            ("10011", "Demon Slayer: Kimetsu no Yaiba", "Koyoharu Gotouge", "Manga", "book-10011", 
            "https://i.pinimg.com/736x/2a/fb/c7/2afbc7330c27de1174d243bdff245302.jpg", "Japanese", "Available", "A story of a boy fighting demons to avenge his family.")
        ]

        try:
            cursor.executemany('''
                INSERT OR IGNORE INTO books (bookId, title, author, genre, isbn, image, language, status, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', books)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting books: {e}")

def insert_users():
    """Insert predefined users into the users table."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        users = [
            ("John Doe", "john.doe@example.com", "password123", "G1234567X", "user-00001", 1, "765343767958"),
            ("Alice Smith", "alice.smith@example.com", "password456", "G7654321Y", "user-00002", 5, "1233333334"),
            ("Bob Johnson", "bob.johnson@example.com", "password789", "F9876543Z", "user-00003", 10, "123123123234")
        ]

        try:
            cursor.executemany('''
                INSERT OR IGNORE INTO users (name, email, password, finNumber, studentCardQR, payableFines, rfid_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', users)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting users: {e}")

def get_user_by_barcode(barcode_id):
    """Retrieve user details using Student Card QR Code (barcode)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE studentCardQR = ?", (barcode_id,))
        user = cursor.fetchone()
    return dict(user) if user else None

def get_book_by_barcode(book_isbn):
    """Retrieve book details using ISBN code."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE isbn = ?", (book_isbn,))
        book = cursor.fetchone()
    return dict(book) if book else None

def insert_branches():
    """Insert sample branches."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        branches = [("Branch 1",), ("Branch 2",)]
        cursor.executemany("INSERT INTO branches (name) VALUES (?)", branches)
        conn.commit()

def insert_branch_books():
    """Assign books to each branch."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM branches WHERE name = 'Branch 1'")
        branch1_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM branches WHERE name = 'Branch 2'")
        branch2_id = cursor.fetchone()[0]

        cursor.execute("SELECT bookId FROM books")
        books = cursor.fetchall()

        branch_books = []
        for book in books:
            branch_books.append((branch1_id, book[0], "Available"))
            branch_books.append((branch2_id, book[0], "Available"))

        cursor.executemany('''
            INSERT OR IGNORE INTO branch_books (branchId, bookId, status)
            VALUES (?, ?, ?)
        ''', branch_books)
        conn.commit()

if __name__ == "__main__":
    if not os.path.exists(DB_NAME):  # Only initialize if the DB doesn't exist
        print("Initializing database...")
        init_db()
        insert_books()
        insert_users()
        insert_branches()
        insert_branch_books()
        
    
        print("Database initialized, sample books, and predefined users added.")
    else:
        print("Database already exists.")