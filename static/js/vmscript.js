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

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

let books = [];

async function fetchBooks() {
    const bookContainer = document.getElementById('book-list');
    try {
        const booksCollection = collection(db, 'Books');
        const querySnapshot = await getDocs(booksCollection);

       
        books = [];

        querySnapshot.forEach((doc) => {
            const bookData = doc.data();
            bookData.DocumentID = doc.id;  
            books.push(bookData);
        });

        displayBooks(books);

    } catch (error) {
        console.error("Error fetching books:", error);
        bookContainer.innerHTML = "<p>Failed to load books.</p>";
    }
}

function displayBooks(booksToDisplay) {
    const bookContainer = document.getElementById('book-container');
    bookContainer.innerHTML = '';

    const genres = [...new Set(booksToDisplay.map(book => book.Genre))];
    genres.forEach(genre => {
        const genreSection = document.createElement('div');
        genreSection.classList.add('category');
        
        const genreTitle = document.createElement('h2');
        genreTitle.textContent = genre;
        genreSection.appendChild(genreTitle);
        
        const bookRow = document.createElement('div');
        bookRow.classList.add('book-row');

        booksToDisplay.filter(book => book.Genre === genre).forEach(book => {
            const bookCard = document.createElement('div');
            bookCard.classList.add('book-card');

            const bookImage = document.createElement('img');
            bookImage.src = book.Image || 'default-image.png';
            bookImage.alt = book.Title;

            const bookTitle = document.createElement('p');
            bookTitle.textContent = book.Title;

            bookCard.appendChild(bookImage);
            bookCard.appendChild(bookTitle);
            bookRow.appendChild(bookCard);

            bookCard.addEventListener('click', () => {
                if (book.DocumentID) {
                    window.location.href = `/bookinfo.html?documentId=${book.DocumentID}`;
                } else {
                    console.error('DocumentID missing for book:', book);
                    alert('This book information is unavailable.');
                }
            });
            
        });

        genreSection.appendChild(bookRow);
        bookContainer.appendChild(genreSection);
    });
}

function searchBooks() {
    const searchInput = document.getElementById('search').value.toLowerCase();
    const filteredBooks = books.filter(book => 
        book.Title.toLowerCase().includes(searchInput) || 
        (book.Author && book.Author.toLowerCase().includes(searchInput))||
        (book.Genre && book.Genre.toLowerCase().includes(searchInput))

    );

    displayBooks(filteredBooks);
}
document.getElementById('search').addEventListener('input', searchBooks);

fetchBooks();
