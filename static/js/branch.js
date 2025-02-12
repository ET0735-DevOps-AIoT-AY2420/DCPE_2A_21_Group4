const dropdownButton = document.getElementById("branch-select");
const dropdownList = document.querySelector(".dropdown-list");
const selectedBranch = document.getElementById("selected-branch");

// Open/Close dropdown
dropdownButton.addEventListener("click", () => {
    dropdownList.style.display = dropdownList.style.display === "block" ? "none" : "block";
});

// Select Branch & Store in sessionStorage
document.querySelectorAll(".dropdown-item").forEach(item => {
    item.addEventListener("click", () => {
        selectedBranch.textContent = item.textContent;
        sessionStorage.setItem("selectedBranch", item.textContent);
        dropdownList.style.display = "none";
    });
});

// Popup functionality
const okButton = document.getElementById("ok-button");
const popup = document.getElementById("popup");
const borrowedBooksText = document.querySelector(".reminder");

// Retrieve stored book and branch selection
let borrowedBooks = JSON.parse(sessionStorage.getItem("borrowedBooks")) || [];
const selectedBook = JSON.parse(sessionStorage.getItem("selectedBook"));
const bookId = selectedBook?.bookId || sessionStorage.getItem("bookId"); // Ensure bookId is retrieved
const selectedBranchName = sessionStorage.getItem("selectedBranch");
const userId = sessionStorage.getItem("userId"); // Ensure userId is available

// Debugging logs
console.log("📌 Stored Book:", selectedBook);
console.log("📌 Book ID:", bookId);
console.log("📌 Selected Branch:", selectedBranchName);
console.log("📌 Stored Borrowed Books:", borrowedBooks);
console.log("📌 User ID:", userId);

// Function to update the book count in popup
function updateBorrowedBooksText() {
    borrowedBooksText.textContent = `Your Borrowed Books: ${borrowedBooks.length}/10`;
}

// OK Button - Store book and branch in sessionStorage & Send to Flask
okButton.addEventListener("click", async () => {
    if (!userId) {
        alert("⚠️ You must be logged in to borrow books.");
        return;
    }

    if (!selectedBranchName) {
        alert("⚠️ Please select a branch first!");
        return;
    }

    if (!selectedBook || !bookId) {
        alert("⚠️ Error: No book selected!");
        return;
    }

    // Prevent duplicate books from being added
    if (!borrowedBooks.some(book => book.id === bookId)) {
        borrowedBooks.push({ id: bookId, book: selectedBook, branch: selectedBranchName });
        sessionStorage.setItem("borrowedBooks", JSON.stringify(borrowedBooks));
        console.log("✅ Book added to borrowed list:", borrowedBooks);
    } else {
        console.log("⚠️ Book already in the list.");
    }

    // Send data to Flask to store in SQLite
    try {
        console.log("📡 Sending borrow request:", { bookId, userId, branch: selectedBranchName });

        const response = await fetch("/borrow", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                bookId: bookId,
                userId: userId,
                branch: selectedBranchName
            })
        });

        // Check if response is valid JSON
        if (!response.ok) {
            const errorText = await response.text(); // Get text response if it's not JSON
            throw new Error(`Server Error: ${errorText}`);
        }

        const result = await response.json();

        if (result.success) {
            console.log("✅ Borrow request successful:", result);
            popup.style.display = "flex";
            updateBorrowedBooksText();
        } else {
            console.error("❌ Borrow request failed:", result.error);
            alert("❌ Failed to borrow the book. " + result.error);
        }

    } catch (error) {
        console.error("❌ Error borrowing book:", error);
        alert("❌ Failed to borrow the book. Please try again.");
    }
});

// Close popup when clicking outside
document.querySelector(".popup-overlay").addEventListener("click", (event) => {
    if (!event.target.closest(".popup-content")) return;
    popup.style.display = "none";
});

// Continue Button - Allow selecting more books
document.querySelector(".popup-button.continue").addEventListener("click", () => {
    if (borrowedBooks.length >= 10) {
        alert("⚠️ You can only borrow up to 10 books.");
        return;
    }
    popup.style.display = "none";
    window.location.href = "/viewmore.html";
});

// Reserve Button - Redirect to `reserved.html`
document.querySelector(".popup-button.reserve").addEventListener("click", () => {
    if (borrowedBooks.length === 0) {
        alert("⚠️ You must select at least one book.");
        return;
    }
    sessionStorage.setItem("borrowedBooks", JSON.stringify(borrowedBooks));
    console.log("📡 Redirecting to reserved.html with books:", borrowedBooks);
    popup.style.display = "none";
    window.location.href = "/reserved.html";
});

// On page load, update book count
updateBorrowedBooksText();