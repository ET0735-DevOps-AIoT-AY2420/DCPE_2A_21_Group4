import { initializeApp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
import { getFirestore, doc, getDoc, collection, addDoc } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-firestore.js";

const firebaseConfig = {
    apiKey: "AIzaSyAVmQ8dh6pGV9pbTk1I6GmvZuXT-FR8Sus",
    authDomain: "library-system-67346.firebaseapp.com",
    databaseURL: "https://library-system-67346-default-rtdb.firebaseio.com",
    projectId: "library-system-67346",
    storageBucket: "library-system-67346.firebasestorage.app",
    messagingSenderId: "487833718014",
    appId: "1:487833718014:web:20e8256c3deb8e22d7a9af",
    measurementId: "G-W081J17K2Y"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

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
        const bookData = await fetchBookDataFromFirestore(book.id);
        if (bookData) {
            addBookToUI(book.id, bookData);
        }
    }
});

// Fetch book data from Firestore
async function fetchBookDataFromFirestore(bookId) {
    try {
        const docRef = doc(db, "Books", bookId);
        const docSnap = await getDoc(docRef);
        return docSnap.exists() ? docSnap.data() : null;
    } catch (error) {
        console.error("Error fetching book data:", error);
        return null;
    }
}

// Add book to UI
function addBookToUI(bookId, bookData) {
    const bookListContainer = document.getElementById("book-list");

    const bookItem = document.createElement("div");
    bookItem.classList.add("book-item");

    const bookImage = document.createElement("img");
    bookImage.src = bookData.Image || "default-image.jpg";
    bookImage.alt = bookData.Title || "No Title";

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

// **Reserve Books in Firebase**
document.getElementById("reserve-button").addEventListener("click", async () => {
    const borrowedBooks = JSON.parse(sessionStorage.getItem("borrowedBooks")) || [];
    const userId = sessionStorage.getItem("userId");
    const selectedBranch = sessionStorage.getItem("selectedBranch");

    if (!userId) {
        alert("You must be logged in to reserve books.");
        return;
    }

    if (borrowedBooks.length === 0) {
        alert("No books to reserve.");
        return;
    }

    try {
        for (let book of borrowedBooks) {
            await addDoc(collection(db, "Loans"), {
                userId: userId,
                bookId: book.id,
                cancelStatus: "No",
                borrowDate: new Date().toISOString(),
                extendStatus: "No",
                extendDate: null,
                dueDate: null,
                returnDate: null,
                branch: selectedBranch
            });
        }

        alert("Books successfully reserved!");
        sessionStorage.removeItem("borrowedBooks"); // Clear borrowed books after reservation
        window.location.href = "/HomePage.html"; // Redirect to homepage
    } catch (error) {
        console.error("Error reserving books:", error);
        alert("An error occurred while reserving books.");
    }
});
