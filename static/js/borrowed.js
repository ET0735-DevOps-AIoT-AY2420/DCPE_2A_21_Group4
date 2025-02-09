import { initializeApp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
import { getFirestore, collection, query, where, getDocs, updateDoc, doc, getDoc } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-firestore.js";

// Firebase Configuration
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
    const borrowedBooksContainer = document.getElementById("borrowed-books-list");
    const userId = sessionStorage.getItem("userId");

    if (!userId) {
        alert("You must be logged in to view borrowed books.");
        window.location.href = "/signin";
        return;
    }

    // Fetch loaned books for the logged-in user
    const loansQuery = query(collection(db, "Loans"), where("userId", "==", userId));
    const querySnapshot = await getDocs(loansQuery);

    if (querySnapshot.empty) {
        borrowedBooksContainer.innerHTML = "<p>No borrowed books found.</p>";
        return;
    }

    querySnapshot.forEach(async (loanDoc) => {
        const loanData = loanDoc.data();
        const bookId = loanData.bookId;
        const dueDate = loanData.dueDate ? new Date(loanData.dueDate) : calculateDueDate(new Date(loanData.borrowDate), 18);

        // Fetch book details from Firestore
        const bookData = await fetchBookData(bookId);
        if (!bookData) return;

        addBookToUI(loanDoc.id, bookId, bookData, dueDate, loanData.extendStatus);
    });
});

// Fetch book details from Firestore
async function fetchBookData(bookId) {
    const docRef = doc(db, "Books", bookId);
    const docSnap = await getDoc(docRef);
    return docSnap.exists() ? docSnap.data() : null;
}

// Calculate due date
function calculateDueDate(startDate, daysToAdd) {
    let dueDate = new Date(startDate);
    dueDate.setDate(dueDate.getDate() + daysToAdd);
    return dueDate;
}

// Add book to UI
function addBookToUI(loanId, bookId, bookData, dueDate, extendStatus) {
    const borrowedBooksContainer = document.getElementById("borrowed-books-list");

    const bookItem = document.createElement("div");
    bookItem.classList.add("book-item");

    const bookImage = document.createElement("img");
    bookImage.src = bookData.Image || "default-image.jpg";
    bookImage.alt = bookData.Title || "No Title";

    const bookTitle = document.createElement("p");
    bookTitle.textContent = bookData.Title || "No Title";

    const timeFrame = document.createElement("p");
    timeFrame.classList.add("time-frame");
    updateTimer(timeFrame, dueDate);

    const extendButton = document.createElement("button");
    extendButton.textContent = "Extend";
    extendButton.classList.add("extend-button");
    extendButton.disabled = extendStatus === "Yes"; // Disable if already extended

    if (extendStatus === "Yes") {
        extendButton.style.opacity = "0.5";
    }

    extendButton.addEventListener("click", async () => {
        if (extendStatus !== "Yes") {
            const newDueDate = calculateDueDate(dueDate, 7);
            await updateDoc(doc(db, "Loans", loanId), {
                dueDate: newDueDate.toISOString(),
                extendStatus: "Yes"
            });

            extendButton.disabled = true;
            extendButton.style.opacity = "0.5";
            updateTimer(timeFrame, newDueDate);
        }
    });

    bookItem.appendChild(bookImage);
    bookItem.appendChild(bookTitle);
    bookItem.appendChild(timeFrame);
    bookItem.appendChild(extendButton);
    borrowedBooksContainer.appendChild(bookItem);
}

// Countdown Timer (Update Days Remaining)
function updateTimer(timeFrameElement, dueDate) {
    function refreshTimer() {
        const now = new Date();
        const timeDifference = dueDate - now;
        const daysLeft = Math.max(Math.ceil(timeDifference / (1000 * 60 * 60 * 24)), 0);

        timeFrameElement.textContent = `Days Remaining: ${daysLeft}`;

        if (daysLeft > 0) {
            dueDate.setDate(dueDate.getDate() - 1);
            setTimeout(refreshTimer, 5000);
        } else {
            timeFrameElement.textContent = "Expired!";
            timeFrameElement.style.color = "red";
        }
    }
    refreshTimer();
}