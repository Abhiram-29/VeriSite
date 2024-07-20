document.addEventListener('DOMContentLoaded', function() {
    chrome.storage.local.get('urlData', function(data) {
      const container = document.getElementById('data-container');
      container.innerHTML = '';  
  
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
          container.appendChild(dataField);
        }
      } else {
        container.textContent = 'No data available.';
      }
    });
  
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (message.action === "updatePopup") {
        chrome.storage.local.get('urlData', function(data) {
          const container = document.getElementById('data-container');
          container.innerHTML = '';  // Clear any existing content
  
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
              container.appendChild(dataField);
            }
          } else {
            container.textContent = 'No data available.';
          }
        });
      }
    });
  });
  