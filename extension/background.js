chrome.action.onClicked.addListener((tab) => {
    chrome.scripting.executeScript(
      {
        target: {tabId: tab.id},
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
      });
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }
  