import { initializeApp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-analytics.js";
import { getFirestore, doc, getDoc } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-firestore.js";

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
const analytics = getAnalytics(app);
const db = getFirestore(app);

//  get Book ID from URL
function getDocumentIDFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('documentId'); 
}

const DocumentID = getDocumentIDFromURL();
if (!DocumentID) {
    alert("No book ID found in the URL.");
} else {
    fetchBook(DocumentID);
}

document.addEventListener("DOMContentLoaded", function () {
    const borrowButton = document.getElementById("borrow-button");

    borrowButton.addEventListener("click", () => {
        const documentId = sessionStorage.getItem("documentId"); // Retrieve stored documentId
        if (documentId) {
            
            window.location.href = `/branch.html?documentId=${documentId}`;
        }
    });
});

// Fetch book details 
async function fetchBook(DocumentID) {
    try {
        const docRef = doc(db, "Books", DocumentID);
        const docSnap = await getDoc(docRef);

        if (docSnap.exists()) {
            const bookData = docSnap.data();
            console.log("Book data:", bookData);

            document.getElementById("book-title").textContent = bookData.Title || "No Title Available";
            document.getElementById("book-author").textContent = bookData.Author ? `by ${bookData.Author}` : "Author information not available";
            document.getElementById("book-description").textContent = bookData.Summary || "No Description Available";
            document.getElementById("book-genres").textContent = bookData.Genre || "No Genres Available";
            document.getElementById("book-status").textContent = bookData.Status || "Status not available";
            document.getElementById("book-language").textContent = bookData.Language || "Language not available";
            document.getElementById("book-image").src = bookData.Image || "default-image.jpg"; 

            const borrowButton = document.getElementById("borrow-button");

            if (bookData.Status && bookData.Status.toLowerCase() === "unavailable") {
                borrowButton.style.backgroundColor = "#ccc"; 
                borrowButton.style.cursor = "not-allowed";
                borrowButton.disabled = true; 
            } else {
                borrowButton.style.backgroundColor = "";
                borrowButton.style.cursor = "pointer";
                borrowButton.disabled = false;

                borrowButton.addEventListener("click", () => {
                    sessionStorage.setItem("selectedBook", JSON.stringify(bookData));
                    sessionStorage.setItem("documentId", DocumentID);
                   
                    window.location.href = `/branch.html?documentId=${DocumentID}`;
                });
            }
        } else {
            console.error("No such book found!");
            alert("Book not found. Please check the Book ID.");
        }
    } catch (error) {
        console.error("Error fetching book data:", error);
        alert("An error occurred while fetching the book details.");
    }
}

// Favorite button toggle
document.getElementById('favorite-btn').addEventListener('click', () => {
    const favoriteIcon = document.getElementById('favorite-icon');
    favoriteIcon.classList.toggle('filled');

    if (favoriteIcon.classList.contains('filled')) {
        favoriteIcon.classList.replace('far', 'fas'); 
    } else {
        favoriteIcon.classList.replace('fas', 'far');
    }
});
