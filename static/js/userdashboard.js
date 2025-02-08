document.addEventListener("DOMContentLoaded", () => {
    const editButton = document.getElementById("edit-button");
    const saveButton = document.getElementById("save-button");
    const nameDisplay = document.getElementById("name-display");
    const emailDisplay = document.getElementById("email-display");

    // Variables to hold the original values
    let originalName = "";
    let originalEmail = "";

    editButton.addEventListener("click", () => {
        // Make the name and email editable
        nameDisplay.contentEditable = true;
        emailDisplay.contentEditable = true;
        nameDisplay.classList.add("editable");
        emailDisplay.classList.add("editable");

        // Show save button and hide edit button
        editButton.style.display = "none";
        saveButton.style.display = "inline-block";
    });

    saveButton.addEventListener("click", async (e) => {
        e.preventDefault(); // Prevent default action

        // Get the updated values
        const updatedName = nameDisplay.textContent;
        const updatedEmail = emailDisplay.textContent;

        // Save user info to Firestore
        try {
            const user = auth.currentUser ;
            if (user) {
                const userDocRef = doc(db, "users", user.uid);
                await setDoc(userDocRef, { name: updatedName, email: updatedEmail }, { merge: true });
                alert("User  info saved successfully!");

                // Update original values
                originalName = updatedName;
                originalEmail = updatedEmail;
            } else {
                alert("No authenticated user!");
            }
        } catch (error) {
            console.error("Error saving user info:", error);
            alert("Failed to save user info. Please try again.");
        }

        // Make the name and email non-editable
        nameDisplay.contentEditable = false;
        emailDisplay.contentEditable = false;
        nameDisplay.classList.remove("editable");
        emailDisplay.classList.remove("editable");

        // Show edit button and hide save button
        editButton.style.display = "inline-block";
        saveButton.style.display = "none";
    });

    async function fetchUserInfo() {
        const user = auth.currentUser ;
        if (!user) {
            console.error("No authenticated user!");
            return; // Exit the function if no user is authenticated
            }

        if (user) {
            try {
                const userDocRef = doc(db, "users", user.uid);
                const userDoc = await getDoc(userDocRef);

                if (userDoc.exists()) {
                    const userData = userDoc.data();
                    // Set the display text to the fetched user data
                    nameDisplay.textContent = userData.name || "N/A";
                    emailDisplay.textContent = userData.email || "N/A";

                    // Store original values
                    originalName = userData.name || "";
                    originalEmail = userData.email || "";
                } else {
                    console.error("No user document found!");
                }
            } catch (error) {
                console.error("Error fetching user data:", error);
            }
        } else {
            console.error("No authenticated user!");
        }
    }

    // Fetch and populate user info when the page loads
    fetchUserInfo();
});