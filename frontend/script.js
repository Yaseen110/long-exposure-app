const API_URL = "http://127.0.0.1:5000"; // Replace this with your deployed backend URL

document.getElementById("drop-area").addEventListener("click", function () {
    document.getElementById("fileElem").click();
});

document.getElementById("uploadBtn").addEventListener("click", async function () {
    let fileInput = document.getElementById("fileElem");
    if (!fileInput.files.length) {
        alert("Please select a video file to upload.");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput.files[0]);

    let progressBar = document.getElementById("progress-bar");
    let progressContainer = document.getElementById("progress-container");
    progressContainer.style.display = "block";
    progressBar.style.width = "5%";  // Start from 5%

    let progressInterval = setInterval(() => {
        let currentWidth = parseFloat(progressBar.style.width);
        if (currentWidth < 95) {
            progressBar.style.width = (currentWidth + 1) + "%";
        }
    }, 500); // Increase every 0.5 seconds

    try {
        let response = await fetch(`${API_URL}/upload`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Error processing file");
        }

        let result = await response.json(); // Expecting JSON response
        clearInterval(progressInterval);
        progressBar.style.width = "100%";  // Progress complete

        // Set the output image source dynamically
        let outputImage = document.getElementById("outputImage");
        outputImage.src = `${API_URL}${result.image_url}?t=${new Date().getTime()}`; // Prevent caching
        outputImage.style.display = "block";

        // Show download link
        let downloadLink = document.getElementById("downloadLink");
        downloadLink.href = `${API_URL}${result.image_url}`;
        downloadLink.style.display = "block";
    } catch (error) {
        alert(error.message);
    }
});
