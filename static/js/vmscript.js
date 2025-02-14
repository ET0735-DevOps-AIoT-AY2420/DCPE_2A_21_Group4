document.addEventListener("DOMContentLoaded", function () {
    let books = [];

    const branchId = document.getElementById('branch-id-container').getAttribute('data-branch-id');

    if (!branchId) {
        alert("Branch ID is missing!");
        window.location.href = "selectBranch.html"; // Redirect to branch selection
        return;
    }

    console.log("Branch ID:", branchId);



    // Fetch books for the selected branch
    async function fetchBooks(branchId) {
        const bookContainer = document.getElementById('book-container');

        try {
            const response = await fetch(`/api/branch_books/${branchId}`);  // ✅ Correct API
            if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);

            books = await response.json();
            if (!Array.isArray(books)) throw new Error("Invalid JSON format");

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

                bookCard.dataset.bookId = book.bookId;

                const bookImage = document.createElement('img');
                bookImage.src = book.image && (book.image.startsWith("http") || book.image.startsWith("https"))
                    ? book.image
                    : `/static/images/${book.image || "default-book.jpg"}`;
                bookImage.alt = book.title;

                const bookTitle = document.createElement('p');
                bookTitle.textContent = book.title;

                bookCard.appendChild(bookImage);
                bookCard.appendChild(bookTitle);
                bookRow.appendChild(bookCard);

                // Redirect to book details page on click
                bookCard.addEventListener('click', () => {
                    const bookId = bookCard.dataset.bookId;
       
                    sessionStorage.setItem('selectedBookId', bookId);
       
                    window.location.href = `/bookinfo?bookId=${bookId}&branchId=${branchId}`;
                });
            });

            genreSection.appendChild(bookRow);
            bookContainer.appendChild(genreSection);
        });
    }

    // Search books
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
    fetchBooks(branchId);
});
