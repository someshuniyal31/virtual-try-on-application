let videoStream = null;
let countdownTimer;
let countdownSeconds;
const countdownDisplay = document.createElement("div");
countdownDisplay.style.fontSize = "30px";
countdownDisplay.style.color = "red";
countdownDisplay.style.fontWeight = "bold";
countdownDisplay.style.position = "absolute";
countdownDisplay.style.top = "10px";
countdownDisplay.style.left = "50%";
countdownDisplay.style.transform = "translateX(-50%)";
countdownDisplay.style.display = "none"; // Hidden initially
document.body.appendChild(countdownDisplay);

function toggleWebcamOption() {
  const webcamContainer = document.getElementById("webcam-container");
  const fileInput = document.getElementById("file-input");
  const isWebcam = document.getElementById("webcam-option").checked;
  webcamContainer.style.display = isWebcam ? "block" : "none";
  fileInput.style.display = isWebcam ? "none" : "block";

  if (isWebcam) {
    startWebcam(); // Start webcam only when the user selects it
  } else {
    stopWebcam(); // Stop webcam if the user selects upload photo
  }
}

function startWebcam() {
  const video = document.querySelector("video");
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then((stream) => {
      video.srcObject = stream;
      videoStream = stream; // Keep reference to the stream so we can stop it later
    })
    .catch((err) => console.error("Webcam error:", err));
}

function stopWebcam() {
  if (videoStream) {
    const tracks = videoStream.getTracks();
    tracks.forEach((track) => track.stop()); // Stop all webcam tracks to release the camera
    videoStream = null;
  }
}

function startCountdown() {
  countdownSeconds = parseInt(
    document.getElementById("countdown-select").value
  );
  countdownDisplay.style.display = "block";
  countdownDisplay.innerText = countdownSeconds;

  countdownTimer = setInterval(() => {
    countdownSeconds--;
    countdownDisplay.innerText = countdownSeconds;
    if (countdownSeconds === 0) {
      clearInterval(countdownTimer); // Stop countdown
      capturePhoto(); // Capture the photo when countdown ends
    }
  }, 1000);
}

function capturePhoto() {
  const video = document.querySelector("video");
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  const imageData = canvas.toDataURL("image/png");

  fetch("/capture_photo", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ image_data: imageData }),
  })
    .then((response) => response.json())
    .then((data) => {
      alert(data.message);
      if (data.success) {
        document.getElementById("shirtFittingLink").style.display = "block";
      }
    });
}
