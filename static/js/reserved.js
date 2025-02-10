document.addEventListener("DOMContentLoaded", async () => {
    const bookListContainer = document.getElementById("book-list");
    const selectedBranch = sessionStorage.getItem("selectedBranch");
    const borrowedBooks = JSON.parse(sessionStorage.getItem("borrowedBooks")) || [];
    const userId = sessionStorage.getItem("userId");

    // Ensure the user is logged in
    if (!userId) {
        alert("You must be logged in to reserve books.");
        window.location.href = "/signin";  // Redirect to login page
        return;
    }

    if (!selectedBranch || borrowedBooks.length === 0) {
        alert("No books or branch selected. Redirecting to homepage.");
        window.location.href = "/HomePage.html";
        return;
    }

    document.getElementById("selected-branch").textContent = selectedBranch;

    for (let book of borrowedBooks) {
        addBookToUI(book.id, book);
    }
});

// Add book to UI
function addBookToUI(bookId, bookData) {
    const bookListContainer = document.getElementById("book-list");

    const bookItem = document.createElement("div");
    bookItem.classList.add("book-item");

    const bookImage = document.createElement("img");
    bookImage.src = bookData.book.image.startsWith("http") ? bookData.book.image : `${bookData.book.image}`;
    bookImage.alt = bookData.book.title || "No Title";

    const removeButton = document.createElement("button");
    removeButton.textContent = "❌";
    removeButton.classList.add("remove-button");
    removeButton.addEventListener("click", () => {
        removeBookFromList(bookId);
    });

    bookItem.appendChild(bookImage);
    bookItem.appendChild(removeButton);
    bookListContainer.appendChild(bookItem);
}

// Remove book from session storage
function removeBookFromList(bookId) {
    let borrowedBooks = JSON.parse(sessionStorage.getItem("borrowedBooks")) || [];
    borrowedBooks = borrowedBooks.filter(book => book.id !== bookId);
    sessionStorage.setItem("borrowedBooks", JSON.stringify(borrowedBooks));
    location.reload();
}

// **Reserve Books in SQLite**
document.getElementById("reserve-button").addEventListener("click", async () => {
    const borrowedBooks = JSON.parse(sessionStorage.getItem("borrowedBooks")) || [];
    const userId = sessionStorage.getItem("userId");

    if (!userId) {
        alert("⚠️ You must be logged in to reserve books.");
        return;
    }

    if (borrowedBooks.length === 0) {
        alert("⚠️ No books selected for reservation.");
        return;
    }

    try {
        console.log("📡 Sending reservation request:", borrowedBooks);

        const response = await fetch("/reserve_books", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ borrowedBooks }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server Error: ${errorText}`);
        }

        const result = await response.json();

        if (result.success) {
            console.log("✅ Reservation successful:", result);
            alert("✅ Books reserved successfully!");
            sessionStorage.removeItem("borrowedBooks");
            window.location.href = "/homepage";
        } else {
            console.error("❌ Reservation failed:", result.error);
            alert("❌ Failed to reserve books: " + result.error);
        }

    } catch (error) {
        console.error("❌ Error reserving books:", error);
        alert("❌ Failed to reserve books. Please try again.");
    }
});
