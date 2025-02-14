document.addEventListener("DOMContentLoaded", async () => {
    function getUserId() {
        return sessionStorage.getItem("userId");
    }

    function getBranchIdFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get("branchId");
    }

    const userId = getUserId();
    const branchId = getBranchIdFromURL();

    if (!userId) {
        alert("⚠️ You must be logged in to view reservations.");
        window.location.href = "/signin";
        return;
    }

    if (!branchId) {
        alert("⚠️ No branch selected. Redirecting to homepage.");
        window.location.href = "/homepage";
        return;
    }

    // Fetch reserved books from the database
    try {
        const response = await fetch(`/api/reserved?user_id=${userId}&branchId=${branchId}`);
        if (!response.ok) {
            throw new Error(`Server Error: ${await response.text()}`);
        }

        const reservedBooks = await response.json();
        if (reservedBooks.length === 0) {
            alert("⚠️ No reserved books found.");
        } else {
            reservedBooks.forEach(addBookToUI);
        }
    } catch (error) {
        console.error("❌ Error fetching reserved books:", error);
        alert("❌ Failed to fetch reserved books. Please try again.");
    }

    // Attach event listener to reserve button
    document.getElementById("reserve-button").addEventListener("click", reserveBooks);
});

// Function to add book details to UI
function addBookToUI(bookData) {
    const bookListContainer = document.getElementById("book-list");

    const bookItem = document.createElement("div");
    bookItem.classList.add("book-item");
    bookItem.dataset.bookId = bookData.bookId;

    const bookImage = document.createElement("img");
    bookImage.src = bookData.image && (bookData.image.startsWith("http") || bookData.image.startsWith("https"))
        ? bookData.image
        : `/static/images/${bookData.image || "default-book.jpg"}`;
    bookImage.alt = bookData.title || "No Title";

    const bookDetails = document.createElement("div");
    bookDetails.classList.add("book-details");
    bookDetails.innerHTML = `
        <p><strong>Title:</strong> ${bookData.title}</p>
        <p><strong>Author:</strong> ${bookData.author}</p>
        <p><strong>Branch:</strong> ${bookData.branch}</p>
    `;

    // Create "Remove" button
    const removeButton = document.createElement("button");
    removeButton.textContent = "❌ Remove";
    removeButton.classList.add("remove-button");
    removeButton.addEventListener("click", async () => {
        const bookId = bookItem.dataset.bookId;
        await removeBookFromList(bookId, bookItem);
    });

    bookItem.appendChild(bookImage);
    bookItem.appendChild(bookDetails);
    bookItem.appendChild(removeButton);
    bookListContainer.appendChild(bookItem);
}

// Function to reserve selected books
async function reserveBooks() {
    const userId = sessionStorage.getItem("userId");
    if (!userId) {
        alert("⚠️ You must be logged in to reserve books.");
        return;
    }

    const selectedBooks = [];
    document.querySelectorAll(".book-item").forEach((bookItem) => {
        const bookId = bookItem.dataset.bookId;
        const branch = bookItem.querySelector(".book-details p:nth-child(3)").textContent.split(": ")[1];

        selectedBooks.push({ id: bookId, branch: branch });
    });

    if (selectedBooks.length === 0) {
        alert("⚠️ No books selected for reservation.");
        return;
    }

    if (selectedBooks.length > 10) {
        alert("⚠️ You can only reserve up to 10 books.");
        return;
    }

    try {
        const response = await fetch("/api/reserve_book", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ borrowedBooks: selectedBooks })
        });

        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.error);
        }

        alert("✅ " + result.success);
        window.location.reload();
    } catch (error) {
        console.error("❌ Error reserving books:", error);
        alert("❌ Failed to reserve books. Please try again.");
    }
}


// Function to remove book from list and call API
async function removeBookFromList(bookId, bookItem) {
    if (!confirm("Are you sure you want to cancel this book?")) return;

    const userId = sessionStorage.getItem("userId"); 

    try {
        const response = await fetch(`/api/cancel_borrowed_book/${bookId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ userId }) 
        });

        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.error);
        }

        alert("✅ " + result.success);
        bookItem.remove(); // Remove from UI after successful cancelation
    } catch (error) {
        console.error("❌ Error canceling book:", error);
        alert("❌ Failed to cancel the book. Please try again.");
    }
}
