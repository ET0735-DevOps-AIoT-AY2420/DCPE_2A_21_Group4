document.addEventListener("DOMContentLoaded", async () => {
    const borrowedBooksContainer = document.getElementById("borrowed-books-list");
    const userId = sessionStorage.getItem("userId");
  

    if (!userId) {
        alert("You must be logged in to view borrowed books.");
        window.location.href = "/signin";
        return;
    }

    try {
        const response = await fetch(`get_loans?userId=${userId}`);
        const loans = await response.json();

        if (!loans.length) {
            borrowedBooksContainer.innerHTML = "<p>No borrowed books found.</p>";
            return;
        }

        loans.forEach((loan) => {
            const dueDate = loan.dueDate ? new Date(loan.dueDate) : calculateDueDate(new Date(), 18);
            addBookToUI(loan.id, loan.title, dueDate, loan.extendStatus, loan.genre, loan.image);
        });

    } catch (error) {
        console.error("Error fetching loaned books:", error);
        borrowedBooksContainer.innerHTML = "<p>Error loading books.</p>";
    }
});

// Function to calculate due date
function calculateDueDate(startDate, daysToAdd) {
    let dueDate = new Date(startDate);
    dueDate.setDate(dueDate.getDate() + daysToAdd);
    return dueDate;
}

function addBookToUI(loanId, title, dueDate, extendStatus, genre, image) {
    const borrowedBooksContainer = document.getElementById("borrowed-books-list");

    const bookItem = document.createElement("div");
    bookItem.classList.add("book-item");

    const bookImage = document.createElement('img');
    bookImage.src = image && (image.startsWith("http") || image.startsWith("https"))
        ? image
        : `/static/images/${image || "default-book.jpg"}`;

    const bookTitle = document.createElement("p");
    bookTitle.textContent = title || "No Title";

    const bookGenre = document.createElement("p");
    bookGenre.textContent = `Genre: ${genre || "Unknown"}`;

    const timeFrame = document.createElement("p");
    timeFrame.classList.add("time-frame");
    updateTimer(timeFrame, dueDate);

    const extendButton = document.createElement("button");
    extendButton.textContent = "Extend";
    extendButton.classList.add("extend-button");
    extendButton.disabled = extendStatus === "Yes";

    if (extendStatus === "Yes") {
        extendButton.style.opacity = "0.5";
    }

    extendButton.addEventListener("click", async () => {
        if (extendStatus !== "Yes") {
            const newDueDate = calculateDueDate(dueDate, 7);
            await extendLoan(loanId, newDueDate);
            extendButton.disabled = true;
            extendButton.style.opacity = "0.5";
            updateTimer(timeFrame, newDueDate);
        }
    });

    // Append elements to book item
    bookItem.appendChild(bookImage);
    bookItem.appendChild(bookTitle);
    bookItem.appendChild(bookGenre);
    bookItem.appendChild(timeFrame);
    bookItem.appendChild(extendButton);
    
    // Append book item to borrowed books container
    borrowedBooksContainer.appendChild(bookItem);
}


// Function to extend loan due date in the SQL database
async function extendLoan(loanId, newDueDate) {
    try {
        const response = await fetch("/extend_loan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ loanId, newDueDate: newDueDate.toISOString() })
        });
        const result = await response.json();
        if (result.message) {
            console.log("Loan extended successfully.");
        } else {
            console.error("Error extending loan:", result.error);
        }
    } catch (error) {
        console.error("Error updating due date:", error);
    }
}

// Function to update timer UI
function updateTimer(timeFrameElement, dueDate) {
    let simulatedDueDate = new Date(dueDate);

    function refreshTimer() {
        // Simulate each day passing every second (prototype behavior)
        simulatedDueDate.setDate(simulatedDueDate.getDate() - 1);

        const timeDifference = simulatedDueDate - new Date();
        const daysLeft = Math.max(Math.ceil(timeDifference / (1000 * 60 * 60 * 24)), 0);

        // Update the displayed countdown
        timeFrameElement.textContent = `Days Remaining: ${daysLeft}`;

        if (daysLeft > 0) {
            setTimeout(refreshTimer, 1000);  // Continue countdown every second
        } else {
            timeFrameElement.textContent = "Expired!";
            timeFrameElement.style.color = "red";  // Highlight expired status
        }
    }

    // Start the timer if the due date hasn't already expired
    if (simulatedDueDate > new Date()) {
        refreshTimer();
    } else {
        timeFrameElement.textContent = "Expired!";
        timeFrameElement.style.color = "red";
    }
}
