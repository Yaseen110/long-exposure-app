document.getElementById("drop-area").addEventListener("click", function () {
    document.getElementById("fileElem").click();
});

document.getElementById("uploadBtn").addEventListener("click", function () {
    let fileInput = document.getElementById("fileElem");
    if (fileInput.files.length === 0) {
        alert("Please select a video file.");
        return;
    }

    let file = fileInput.files[0];
    let formData = new FormData();
    formData.append("file", file);

    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/", true);

    // Show progress bar and animate it
    let progressBar = document.getElementById("progress-bar");
    let progressContainer = document.getElementById("progress-container");
    progressContainer.style.display = "block";
    progressBar.style.width = "5%";  // Start from 5%

    let progressInterval = setInterval(() => {
        let currentWidth = parseFloat(progressBar.style.width);
        if (currentWidth < 95) {
            progressBar.style.width = (currentWidth + 5) + "%";
        }
    }, 500); // Increase every 0.5 seconds

    xhr.onload = function () {
        clearInterval(progressInterval); // Stop animation
        progressBar.style.width = "100%"; // Complete progress

        if (xhr.status == 200) {
            let imageUrl = URL.createObjectURL(new Blob([xhr.response]));
            document.getElementById("outputImage").src = imageUrl;
            document.getElementById("outputImage").style.display = "block";

            let downloadLink = document.getElementById("downloadLink");
            downloadLink.href = imageUrl;
            downloadLink.style.display = "block";
        }
    };

    xhr.responseType = "blob";
    xhr.send(formData);
});
