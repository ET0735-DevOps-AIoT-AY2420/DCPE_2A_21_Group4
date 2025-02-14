document.addEventListener("DOMContentLoaded", function () {
    const dropdownButton = document.getElementById("branch-select");
    const dropdownList = document.querySelector(".dropdown-list");
    const selectedBranchSpan = document.getElementById("selected-branch");

    // Open/close dropdown menu
    dropdownButton.addEventListener("click", function () {
        dropdownList.classList.toggle("show");
    });

    // Handle branch selection
    document.querySelectorAll(".dropdown-item").forEach(item => {
        item.addEventListener("click", function () {
            const branchId = this.dataset.branchId; // Get branch ID
            selectedBranchSpan.textContent = this.textContent; // Update button text
            sessionStorage.setItem("selectedBranch", branchId); // Store in sessionStorage

            // Redirect to homepage.html with branchId as a query parameter
            window.location.href = `/homepage.html?branchId=${branchId}`;
        });
    });

    // Close dropdown if clicked outside
    document.addEventListener("click", function (event) {
        if (!dropdownButton.contains(event.target) && !dropdownList.contains(event.target)) {
            dropdownList.classList.remove("show");
        }
    });
});
