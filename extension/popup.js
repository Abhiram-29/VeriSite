document.addEventListener('DOMContentLoaded', function() {
    const fetchButton = document.getElementById('fetch-button');
    const dataContainer = document.getElementById('data-container');
    const predictionContainer = document.getElementById('prediction-container');
  
    fetchButton.addEventListener('click', function() {
      dataContainer.textContent = 'Loading...';
      predictionContainer.textContent = 'Loading...';
  
      chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
        const tab = tabs[0];
        const url = tab.url;
  
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
          dataContainer.textContent = 'Error fetching data.';
        });
      });
    });
  
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
        predictionContainer.textContent = 'Error fetching prediction.';
      });
    }
  
    function updatePopup(data) {
      dataContainer.innerHTML = '';
      predictionContainer.innerHTML = '';
  
      if (data.urlData) {
        for (const [key, value] of Object.entries(data.urlData)) {
          const dataField = document.createElement('div');
          dataField.classList.add('data-field');
  
          const dataLabel = document.createElement('span');
          dataLabel.classList.add('data-label');
          dataLabel.textContent = `${key}: `;
  
          const dataValue = document.createElement('span');
          dataValue.textContent = value;
  
          dataField.appendChild(dataLabel);
          dataField.appendChild(dataValue);
          dataContainer.appendChild(dataField);
        }
      } else {
        dataContainer.textContent = 'No data available.';
      }
  
      if (data.predictionData) {
        const predictionField = document.createElement('div');
        predictionField.classList.add('data-field');
  
        const predictionLabel = document.createElement('span');
        predictionLabel.classList.add('data-label');
        predictionLabel.textContent = 'Prediction: ';
  
        const predictionValue = document.createElement('span');
        predictionValue.textContent = data.predictionData.prediction;
  
        predictionField.appendChild(predictionLabel);
        predictionField.appendChild(predictionValue);
        predictionContainer.appendChild(predictionField);
      } else {
        predictionContainer.textContent = 'No prediction available.';
      }
    }
  
    chrome.storage.local.get(['urlData', 'predictionData'], function(data) {
      updatePopup(data);
    });
  
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (message.action === "updatePopup") {
        chrome.storage.local.get(['urlData', 'predictionData'], function(data) {
          updatePopup(data);
        });
      }
    });
  });
  