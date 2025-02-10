
document.addEventListener("DOMContentLoaded", () => {
    const editButton = document.getElementById("edit-button");
    const saveButton = document.getElementById("save-button");
    const formFields = document.querySelectorAll("#user-info-form input");
    const uploadButton = document.getElementById("upload-button");
    const uploadInput = document.getElementById("upload-profile");
    const profileImage = document.getElementById("profile-image");

    // Disable fields and hide the upload button initially
    formFields.forEach(field => field.disabled = true);

    editButton.addEventListener("click", () => {
        formFields.forEach(field => field.disabled = false);
        editButton.style.display = "none";
        saveButton.style.display = "inline-block";
        uploadButton.style.display = "inline-block"; // Show pencil icon
    });

    saveButton.addEventListener("click", (e) => {
        e.preventDefault(); // Prevent form submission
        formFields.forEach(field => field.disabled = true);
        editButton.style.display = "inline-block";
        saveButton.style.display = "none";
        uploadButton.style.display = "none"; // Hide pencil icon
        alert("User info saved!");
    });

    uploadButton.addEventListener("click", () => {
        uploadInput.click(); // Simulate a click on the hidden file input
    });

    uploadInput.addEventListener("change", () => {
        const file = uploadInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                profileImage.src = e.target.result; // Update the profile image
            };
            reader.readAsDataURL(file);
        }
    });
});

function showPopup(title, description) {
    const popup = document.getElementById("popup");
    const popupTitle = document.getElementById("popup-title");
    const popupDescription = document.getElementById("popup-description");

    popupTitle.textContent = title;
    popupDescription.textContent = description;

    popup.style.display = "block";
}

function closePopup() {
    const popup = document.getElementById("popup");
    popup.style.display = "none";
}
