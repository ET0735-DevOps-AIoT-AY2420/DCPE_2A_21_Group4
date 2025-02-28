document.addEventListener("DOMContentLoaded", function () {
    const dropdownButton = document.getElementById("branch-select");
    const dropdownList = document.querySelector(".dropdown-list");
    const selectedBranchSpan = document.getElementById("selected-branch");
    const branchIdInput = document.getElementById("branch_id");  // The hidden input field

    // Open/close dropdown menu
    dropdownButton.addEventListener("click", function () {
        dropdownList.classList.toggle("show");
    });

    // Handle branch selection
    document.querySelectorAll(".dropdown-item").forEach(item => {
        item.addEventListener("click", function () {
            const branchId = this.dataset.branchId; // Get branch ID
            selectedBranchSpan.textContent = this.textContent; // Update button text
            
            // Store branch ID in the hidden input field
            branchIdInput.value = branchId;

            // Submit the form
            document.getElementById("branchForm").submit(); // Submit the form to backend
        
        });
    });

    // Close dropdown if clicked outside
    document.addEventListener("click", function (event) {
        if (!dropdownButton.contains(event.target) && !dropdownList.contains(event.target)) {
            dropdownList.classList.remove("show");
        }
    });
});
