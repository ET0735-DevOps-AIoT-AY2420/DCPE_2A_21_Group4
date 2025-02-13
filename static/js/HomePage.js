document.addEventListener("DOMContentLoaded", function () {
    let books = [];
    let displayLimit = 5; // Show first 5 books

    const branchId = document.getElementById('branch-id-container').getAttribute('data-branch-id');
    console.log(branchId);  // This will output the branch_id in the console


    if (!branchId) {
        alert("No branch selected!");
        window.location.href = "selectBranch.html"; // Redirect to branch selection page
        return;
    }

    console.log("Branch ID:", branchId);

    async function fetchBooks() {
        const bookList = document.getElementById('book-list');

        try {
            const response = await fetch(`/api/branch_books/${branchId}`);

            if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);

            books = await response.json();

            if (!Array.isArray(books)) {
                throw new Error("Invalid JSON response format");
            }

            if (books.length === 0) {
                bookList.innerHTML = "<p>No books available.</p>";
                return;
            }

            displayBooks(books.slice(0, displayLimit)); // Display only 5 books initially

        } catch (error) {
            console.error("Error fetching books:", error);
            bookList.innerHTML = "<p>Failed to load books. Please try again later.</p>";
        }
    }

    const searchBar = document.querySelector('.search-bar');

    searchBar.addEventListener('input', (event) => {
        const query = event.target.value.toLowerCase();
        const filteredBooks = books.filter(book => {
            const title = book.title ? book.title.toLowerCase() : '';
            const author = book.author ? book.author.toLowerCase() : '';
            const genre = book.genre ? book.genre.toLowerCase() : '';

            return title.includes(query) || author.includes(query) || genre.includes(query);
        });

        displayBooks(filteredBooks.slice(0, displayLimit));
    });

    function displayBooks(booksToDisplay) {
        const bookList = document.getElementById('book-list');
        bookList.innerHTML = ''; // Clear previous books
    
        if (booksToDisplay.length === 0) {
            bookList.innerHTML = "<p>No matching books found.</p>";
            return;
        }
    
        booksToDisplay.forEach(book => {
            const bookItem = document.createElement('div');
            bookItem.classList.add('book-item');
    
            const bookImage = document.createElement('img');
            bookImage.src = book.image && (book.image.startsWith("http") || book.image.startsWith("https"))
                ? book.image
                : `/static/images/${book.image || "default-book.jpg"}`;
            bookImage.alt = book.title || 'No Title';
    
            const bookTitle = document.createElement('p');
            bookTitle.style.fontSize = "20px";
            bookTitle.textContent = book.title;
    
            bookItem.addEventListener('click', () => {
                window.location.href = `/bookinfo/${book.bookId}`;
            });
    
            bookItem.appendChild(bookImage);
            bookItem.appendChild(bookTitle);
            bookList.appendChild(bookItem);
        });
    }

    fetchBooks();
});
