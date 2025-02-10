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
const documentId = sessionStorage.getItem("documentId");
const selectedBranchName = sessionStorage.getItem("selectedBranch");

// Debugging logs
console.log("Stored Book:", selectedBook);
console.log("Selected Branch:", selectedBranchName);
console.log("Stored Borrowed Books:", borrowedBooks);

// Function to update the book count in popup
function updateBorrowedBooksText() {
    borrowedBooksText.textContent = `Your Borrowed Books: ${borrowedBooks.length}/10`;
}

// OK Button - Store book and branch in sessionStorage
okButton.addEventListener('click', () => {
    if (!selectedBranchName) {
        alert("Please select a branch first!");
        return;
    }

    if (!selectedBook || !documentId) {
        alert("Error: No book selected!");
        return;
    }

    // Prevent duplicate books from being added
    if (!borrowedBooks.some(book => book.id === documentId)) {
        borrowedBooks.push({ id: documentId, book: selectedBook, branch: selectedBranchName });
        sessionStorage.setItem("borrowedBooks", JSON.stringify(borrowedBooks));
        console.log("Book added:", borrowedBooks);
    } else {
        console.log("Book already in the list.");
    }

    popup.style.display = 'flex';
    updateBorrowedBooksText();
});

// Close popup when clicking outside
document.querySelector('.popup-overlay').addEventListener('click', (event) => {
    if (!event.target.closest(".popup-content")) return;
    popup.style.display = 'none';
});

// Continue Button - Allow selecting more books
document.querySelector('.popup-button.continue').addEventListener('click', () => {
    if (borrowedBooks.length >= 10) {
        alert("You can only borrow up to 10 books.");
        return;
    }
    popup.style.display = 'none';
    window.location.href = '/viewmore.html';
});

// Reserve Button - Redirect to `reserved.html`
document.querySelector('.popup-button.reserve').addEventListener('click', () => {
    if (borrowedBooks.length === 0) {
        alert("You must select at least one book.");
        return;
    }
    sessionStorage.setItem("borrowedBooks", JSON.stringify(borrowedBooks));
    console.log("Redirecting to reserved.html with books:", borrowedBooks);
    popup.style.display = 'none';
    window.location.href = '/reserved.html';
});

// On page load, update book count
updateBorrowedBooksText();
