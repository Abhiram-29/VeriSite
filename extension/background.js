chrome.action.onClicked.addListener((tab) => {
    chrome.scripting.executeScript(
      {
        target: { tabId: tab.id },
        function: sendUrlToBackend
      }
    );
  });
  
  function sendUrlToBackend() {
    const url = window.location.href;
    fetch('http://127.0.0.1:8000/extract', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
      chrome.storage.local.set({ urlData: data }, () => {
        chrome.runtime.sendMessage({ action: "updatePopup" });
        sendPredictionRequest(data);  // Send data for prediction
      });
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }
  
  function sendPredictionRequest(features) {
    fetch('http://127.0.0.1:8000/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(features)
    })
    .then(response => response.json())
    .then(prediction => {
      chrome.storage.local.set({ predictionData: prediction }, () => {
        chrome.runtime.sendMessage({ action: "updatePopup" });
      });
    })
    .catch(error => {
      console.error('Prediction Error:', error);
    });
  }
  