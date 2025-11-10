document.addEventListener("DOMContentLoaded", function () {
    // Listen for clicks on all "Add" buttons in the admin list page
    document.querySelectorAll("a.addlink").forEach((addBtn) => {
        addBtn.addEventListener("click", function (event) {
            event.preventDefault();

            const url = addBtn.href.startsWith("http")
                ? addBtn.href
                : ${window.location.origin}${addBtn.getAttribute("href")};

            // Create modal HTML
            const overlay = document.createElement("div");
            overlay.classList.add("custom-modal-overlay");
            overlay.innerHTML = `
                <div class="custom-modal">
                    <div class="custom-modal-header">
                        <h5>Add New Record</h5>
                        <button class="close-btn">&times;</button>
                    </div>
                    <div class="custom-modal-body">
                        <iframe src="${url}" frameborder="0"></iframe>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);

            // Close logic
            overlay.querySelector(".close-btn").onclick = () => overlay.remove();
            overlay.addEventListener("click", (e) => {
                if (e.target === overlay) overlay.remove();
            });
        });
    });
});

