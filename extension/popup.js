document.addEventListener("DOMContentLoaded", function () {
  // Ensure the DOM is loaded before adding the event listener

  const predictButton = document.getElementById("predictButton");
  // Removed 'resultElement', now we use specific elements for score/errors
  const scoreContainer = document.getElementById("scoreContainer");
  const scoreTextElement = document.getElementById("scoreText");
  const scoreProgressCircle = scoreContainer
    ? scoreContainer.querySelector(".score-progress")
    : null;
  const errorMessageElement = document.getElementById("errorMessage"); // New error display

  // Define constants based on SVG setup
  const radius = 45; // Matches the 'r' in the SVG circle
  const circumference = 2 * Math.PI * radius;

  // Set initial state for the progress bar (hidden/0%)
  if (scoreProgressCircle) {
    scoreProgressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
    scoreProgressCircle.style.strokeDashoffset = circumference; // Hide the bar initially
  }

  // Helper function to update the score visualization
  function updateScoreVisualization(score) {
    if (!scoreTextElement || !scoreProgressCircle) {
      console.error("Score visualization elements not found.");
      if (errorMessageElement)
        errorMessageElement.innerText =
          "Initialization Error: Score elements missing.";
      return;
    }

    // Ensure score is a number within expected range
    const numericScore = parseFloat(score);
    if (isNaN(numericScore) || numericScore < 0 || numericScore > 100) {
      scoreTextElement.innerText = "N/A";
      scoreProgressCircle.style.strokeDashoffset = circumference; // Hide the bar
      scoreProgressCircle.classList.remove("score-green", "score-red");
      if (errorMessageElement)
        errorMessageElement.innerText = "Error: Invalid score received.";
      return;
    }

    const clampedScore = Math.max(0, Math.min(100, numericScore)); // Ensure it's between 0-100
    const progressOffset = (circumference * (100 - clampedScore)) / 100; // Calculate offset for percentage

    // Update text
    scoreTextElement.innerText = Math.round(clampedScore); // Display rounded score

    // Update progress bar
    scoreProgressCircle.style.strokeDashoffset = progressOffset;

    // Update color
    scoreProgressCircle.classList.remove("score-green", "score-red"); // Remove existing colors
    if (clampedScore >= 50) {
      scoreProgressCircle.classList.add("score-green");
    } else {
      scoreProgressCircle.classList.add("score-red");
    }
    if (errorMessageElement) errorMessageElement.innerText = ""; // Clear previous errors
  }

  // Helper function to display initial/error messages
  function setStatusMessage(message) {
    if (errorMessageElement) {
      errorMessageElement.innerText = message;
    }
    // Clear visualization when showing status/error
    if (scoreTextElement) scoreTextElement.innerText = "";
    if (scoreProgressCircle) {
      scoreProgressCircle.style.strokeDashoffset = circumference; // Hide the bar
      scoreProgressCircle.classList.remove("score-green", "score-red");
    }
  }

  // Check if essential elements exist
  if (!predictButton) {
    console.error("Predict button ('predictButton') not found!");
    setStatusMessage("Initialization Error: Button missing.");
    return; // Stop if the button isn't found
  }
  if (
    !scoreContainer ||
    !scoreTextElement ||
    !scoreProgressCircle ||
    !errorMessageElement
  ) {
    console.error("Score visualization or error elements not found!");
    // Can't display errors properly if these are missing
    return; // Stop if required elements aren't found
  }

  // Add click listener to the button
  predictButton.addEventListener("click", async () => {
    // Indicate processing started
    setStatusMessage("Processing..."); // Show processing message in error area

    try {
      // Call your local prediction endpoint
      console.log("Sending request to http://127.0.0.1:8000/predict");
      const predictResponse = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: {
          // No 'Content-Type' needed if no body is sent
        },
        // No 'body' needed as the Python endpoint doesn't expect one
      });

      // Check if the request was successful
      if (predictResponse.ok) {
        const predictData = await predictResponse.json();
        console.log("Received response from /predict:", predictData);

        // Check if the expected 'prediction' key exists in the response
        if (predictData.hasOwnProperty("prediction")) {
          // Display the score using the new visualization
          updateScoreVisualization(predictData.prediction);
        } else {
          // Handle case where the key is missing
          setStatusMessage("Error: Invalid response format.");
          console.error(
            "Response from /predict did not contain 'prediction' key:",
            predictData
          );
        }
      } else {
        // Handle HTTP errors (e.g., 404, 500)
        console.error(
          "Failed to get prediction. Status:",
          predictResponse.status,
          predictResponse.statusText
        );
        setStatusMessage(`Error: ${predictResponse.status}`);
      }
    } catch (error) {
      // Handle network errors (e.g., server down, CORS issue)
      console.error("An error occurred during fetch:", error);
      setStatusMessage("Error: Cannot connect.");
    }
  });
}); // End DOMContentLoaded listener
