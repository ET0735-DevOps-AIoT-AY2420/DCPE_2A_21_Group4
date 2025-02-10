// Function to get Book ID from URL
function getBookIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('bookId');  
}

// Fetch book details from Flask API
async function fetchBook(bookId) {    
    try {
        console.log(`Fetching book details for bookId: ${bookId}`);

        const response = await fetch(`/api/book/${bookId}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const bookData = await response.json();

        if (bookData.error) {
            console.error("Book not found:", bookData.error);
            alert("Book not found. Please check the Book ID.");
            return;
        }

        console.log("Book data:", bookData);

        document.getElementById("book-title").textContent = bookData.title || "No Title Available";
        document.getElementById("book-author").textContent = bookData.author ? `by ${bookData.author}` : "Author information not available";
        document.getElementById("book-description").textContent = bookData.summary || "No Description Available";
        document.getElementById("book-genre").textContent = bookData.genre || "Unknown Genre";
        document.getElementById("book-status").textContent = bookData.status || "Unknown Status";
        document.getElementById("book-language").textContent = bookData.language || "Unknown Language";

        // Handle book image (Check if URL or local file)
        const bookImage = document.getElementById("book-image");
        if (bookData.image && (bookData.image.startsWith("http") || bookData.image.startsWith("https"))) {
            bookImage.src = bookData.image;  
        } else if (bookData.image) {
            bookImage.src = `/static/images/${bookData.image}`;  
        } else {
            bookImage.src = "/static/images/default-book.jpg";  
        }

        // Borrow button logic
        const borrowButton = document.getElementById("borrow-button");
        if (!borrowButton) {
            console.error("Borrow button not found!");
            return;
        }

        console.log("Borrow button found!");

        // Disable button if book is unavailable
        if (bookData.status && bookData.status.toLowerCase() === "unavailable") {
            borrowButton.style.backgroundColor = "#ccc"; 
            borrowButton.style.cursor = "not-allowed";
            borrowButton.disabled = true; 
        } else {
            borrowButton.style.backgroundColor = "";
            borrowButton.style.cursor = "pointer";
            borrowButton.disabled = false;

            // Add event listener AFTER book data is loaded
            borrowButton.addEventListener("click", () => {
                console.log("Borrow button clicked!");

                sessionStorage.setItem("selectedBook", JSON.stringify(bookData));
                sessionStorage.setItem("bookId", bookId);
                window.location.href = `/branch.html?bookId=${bookId}`;
            });
        }

        // Handle favorite button click
        const favoriteButton = document.getElementById('favorite-btn');
        const favoriteIcon = document.getElementById('favorite-icon');

        if (!favoriteButton || !favoriteIcon) {
            console.error("Favorite button not found!");
            return;
        }

        console.log("Favorite button found!");

        favoriteButton.addEventListener("click", () => {
            console.log("Favorite button clicked!");
            favoriteIcon.classList.toggle('filled');

            if (favoriteIcon.classList.contains('filled')) {
                favoriteIcon.classList.replace('far', 'fas'); 
            } else {
                favoriteIcon.classList.replace('fas', 'far');
            }
        });

    } catch (error) {
        console.error("Error fetching book data:", error);
        alert("An error occurred while fetching the book details.");
    }
}

// **Load book details**
const bookId = getBookIdFromURL();
if (!bookId) {
    console.error("No book ID found in the URL.");
    alert("No book ID found.");
} else {
    fetchBook(bookId);
}
