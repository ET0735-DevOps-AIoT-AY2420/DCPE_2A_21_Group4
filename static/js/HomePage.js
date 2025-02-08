import { initializeApp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-analytics.js";
import { getFirestore, collection, getDocs } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-firestore.js";

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

let books = [];
let displayLimit = 5;  


async function fetchBooks() {
    const bookList = document.getElementById('book-list');
    try {
        const booksCollection = collection(db, 'Books');
        const querySnapshot = await getDocs(booksCollection);

        if (querySnapshot.empty) {
            bookList.innerHTML = "<p>No books available.</p>";
            return;
        }

        querySnapshot.forEach((doc) => {
            const book = doc.data();
            books.push(book); 
            book.DocumentID = doc.id; 
        });

        
        displayBooks(books.slice(0, displayLimit));

    } catch (error) {
        console.error("Error fetching books: ", error);
        bookList.innerHTML = "<p>Failed to load books. Please try again later.</p>";
    }
}

const searchBar = document.querySelector('.search-bar');

searchBar.addEventListener('input', (event) => {
    const query = event.target.value.toLowerCase();
    const filteredBooks = books.filter(book => {
        const title = book.Title ? book.Title.toLowerCase() : '';
        const author = book.Author ? book.Author.toLowerCase() : '';
        const genre = book.Genre ? book.Genre.toLowerCase() : '';

        return title.includes(query) || author.includes(query) || genre.includes(query);
    });

    displayBooks(filteredBooks.slice(0, displayLimit));
});


function displayBooks(booksToDisplay) {
    const bookList = document.getElementById('book-list');
    bookList.innerHTML = ''; 

    booksToDisplay.forEach(book => {
        const bookItem = document.createElement('div');
        bookItem.classList.add('book-item');
        
        const bookImage = document.createElement('img');
        bookImage.src = book.Image || 'default-image.png'; 
        bookImage.alt = book.Title || 'No Title';

        
        const bookTitle = document.createElement('p');
        bookTitle.style.fontSize = "20px";
        bookTitle.textContent = book.Title;

        bookItem.addEventListener('click', () => {
            window.location.href = `/bookinfo.html?documentId=${book.DocumentID}`;
        });

        bookItem.appendChild(bookImage);
        bookItem.appendChild(bookTitle);
        bookList.appendChild(bookItem);
    });
}

fetchBooks();
