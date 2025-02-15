document.addEventListener("DOMContentLoaded", function() {
    // Function to get Book ID and Branch ID from URL
    function getBookIdFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('bookId');
    }

    function getBranchIdFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('branchId');
    }

    // Fetch book details and availability from Flask API
    async function fetchBook(bookId, branchId) {
        try {
            console.log(`Fetching book details for bookId: ${bookId} and branchId: ${branchId}`);

            const response = await fetch(`/api/book/${bookId}/${branchId}`);
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            const bookData = await response.json();

            if (bookData.error) {
                console.error("Book not found:", bookData.error);
                alert("Book not found. Please check the Book ID or Branch ID.");
                return;
            }

            console.log("Book data:", bookData);

            // Populate the UI with book details
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
            const borrowModal = document.getElementById("borrowModal");
            const borrowButton = document.getElementById("borrow-button");
        
            // Ensure the modal is hidden initially
            borrowModal.style.display = "none";

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


                // Add event listener to open modal after clicking borrow button
                borrowButton.addEventListener("click", () => {
                    console.log("Borrow button clicked!");
                    openBorrowModal();  // Open the modal here
                    sessionStorage.setItem("selectedBook", JSON.stringify(bookData));
                    sessionStorage.setItem("bookId", bookId);
                });
            }

        } catch (error) {
            console.error("Error fetching book data:", error);
            alert("An error occurred while fetching the book details.");
        }
    }

    // Open Borrow Modal
    function openBorrowModal() {
        const borrowModal = document.getElementById("borrowModal");
        const bookCount = getBookCount();

        // Update book count in the modal
        document.getElementById("book-count").textContent = bookCount;

        // Display the modal
        borrowModal.style.display = "flex";

        // Reserve Now button logic
    const reserveButton = document.getElementById("reserve-now-button");
    if (reserveButton) {
        reserveButton.addEventListener("click", async () => {
            console.log("Reserve button clicked!");

            const bookId = sessionStorage.getItem("bookId");
            const selectedBook = JSON.parse(sessionStorage.getItem("selectedBook"));

            if (!bookId || !selectedBook) {
                alert("No book selected for reservation.");
                return;
            }

            
            try {
                const response = await fetch('/api/borrow_book', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        branchId: branchId,
                        bookId: bookId,
                        userId: sessionStorage.getItem("userId") 
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const data = await response.json();

                if (data.error) {
                    console.error("Reservation failed:", data.error);
                    alert("There was an issue with your reservation.");
                } else {
                    console.log("Book successfully reserved:", data.success);

                    if (data.updated_count !== undefined) {
                        sessionStorage.setItem("bookCount", data.updated_count);
                    }
    
                    window.location.href = `/reserved?user_id=${sessionStorage.getItem("userId")}&branchId=${branchId}`;

                }
            } catch (error) {
                console.error("Error reserving the book:", error);
                alert("An error occurred while reserving the book.");
            }
        });
    }

    // Continue button logic (borrow the book with pending status)
    const continueButton = document.getElementById("continue-button");
    if (continueButton) {
        continueButton.addEventListener("click", async () => {
            console.log("Continue button clicked!");

            const bookId = sessionStorage.getItem("bookId");
            const selectedBook = JSON.parse(sessionStorage.getItem("selectedBook"));

            if (!bookId || !selectedBook) {
                alert("No book selec ted for borrowing.");
                return;
            }

            // Send a POST request to borrow the book with 'pending' status
            try {

                const userId = sessionStorage.getItem("userId");
                const countResponse = await fetch(`/api/get_reserved_count?userId=${userId}`);
                const countData = await countResponse.json();

                if (countData.count >= 10) {
                    alert("You can only reserve up to 10 books at a time.");
                    return;
                }

                const response = await fetch('/api/borrow_book', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        bookId: bookId,
                        userId: sessionStorage.getItem("userId")  // Get user ID from sessionStorage
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const data = await response.json();

                if (data.error) {
                    console.error("Borrowing failed:", data.error);
                    alert("There was an issue with your borrowing request.");
                } else {
                    console.log("Book successfully added to loans with 'pending' status:", data.success);

                    if (data.updated_count !== undefined) {
                        sessionStorage.setItem("bookCount", data.updated_count);
                    }
                
                    window.location.href = "/homepage";  // Redirect to homepage after borrowing
                }
            } catch (error) {
                console.error("Error borrowing the book:", error);
                alert("An error occurred while borrowing the book.");
            }
        });
      }
    }

    // Dummy function for book count (you can adjust it based on your application logic)
    function getBookCount() {
        let count = sessionStorage.getItem("bookCount");
        count = count ? parseInt(count) : 0;
        if (count < 10) {
            sessionStorage.setItem("bookCount", count + 1);
        }
        return count;
    }

    // Close the modal when clicking outside of it
    window.onclick = function(event) {
        const borrowModal = document.getElementById("borrowModal");
        if (event.target === borrowModal) {
            borrowModal.style.display = "none";
        }
    }

    // **Load book details**
    const bookId = getBookIdFromURL();
    const branchId = getBranchIdFromURL();

    if (!bookId || !branchId) {
        console.error("No book ID or branch ID found in the URL.");
        alert("No book ID or branch ID found.");
    } else {
        fetchBook(bookId, branchId);
    }

});
