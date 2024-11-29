document.getElementById("copy-btn").addEventListener("click", function () {
    navigator.clipboard.writeText(document.querySelector("#copy-text").innerText);
});

