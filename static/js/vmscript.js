let books = [];

// Fetch books from Flask API
async function fetchBooks() {
    const bookContainer = document.getElementById('book-list');
    try {
        const response = await fetch("/api/books");  // Fetch books from Flask API
        books = await response.json();

        if (books.length === 0) {
            bookContainer.innerHTML = "<p>No books available.</p>";
            return;
        }

        displayBooks(books);
    } catch (error) {
        console.error("Error fetching books:", error);
        bookContainer.innerHTML = "<p>Failed to load books.</p>";
    }
}

// Display books grouped by genre
function displayBooks(booksToDisplay) {
    const bookContainer = document.getElementById('book-container');
    bookContainer.innerHTML = '';

    // Group books by genre
    const genres = [...new Set(booksToDisplay.map(book => book.genre))];
    genres.forEach(genre => {
        const genreSection = document.createElement('div');
        genreSection.classList.add('category');

        const genreTitle = document.createElement('h2');
        genreTitle.textContent = genre;
        genreSection.appendChild(genreTitle);

        const bookRow = document.createElement('div');
        bookRow.classList.add('book-row');

        booksToDisplay.filter(book => book.genre === genre).forEach(book => {
            const bookCard = document.createElement('div');
            bookCard.classList.add('book-card');

            const bookImage = document.createElement('img');
            bookImage.src = book.image.startsWith("http") ? book.image : `${book.image}`;
            bookImage.alt = book.title;

            const bookTitle = document.createElement('p');
            bookTitle.textContent = book.title;

            bookCard.appendChild(bookImage);
            bookCard.appendChild(bookTitle);
            bookRow.appendChild(bookCard);

            // Redirect to book details page
            bookCard.addEventListener('click', () => {
                window.location.href = `/bookinfo.html?bookId=${book.bookId}`;
            });
        });

        genreSection.appendChild(bookRow);
        bookContainer.appendChild(genreSection);
    });
}

// Search books by title, author, or genre
function searchBooks() {
    const searchInput = document.getElementById('search').value.toLowerCase();
    const filteredBooks = books.filter(book =>
        book.title.toLowerCase().includes(searchInput) ||
        (book.author && book.author.toLowerCase().includes(searchInput)) ||
        (book.genre && book.genre.toLowerCase().includes(searchInput))
    );

    displayBooks(filteredBooks);
}

// Add event listener for search input
document.getElementById('search').addEventListener('input', searchBooks);

// Fetch books on page load
fetchBooks();
