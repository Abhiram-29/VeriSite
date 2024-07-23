document.getElementById('predictButton').addEventListener('click', async () => {

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  let url = tab.url;
  
  if (!url) {
      document.getElementById('result').innerText = 'Failed to get current URL.';
      return;
  }


  url = url.replace(/\/+$/, '');

  console.log('Cleaned URL being sent to /predict:', url);

  const extractResponse = await fetch('https://verisite.onrender.com/extract', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url })
  });

  if (extractResponse.ok) {
      const extractData = await extractResponse.json();
      
      let contentHtml = '<h3>Extracted Content:</h3>';
      for (const [key, value] of Object.entries(extractData)) {
          contentHtml += `<div class="content-item"><strong>${key}:</strong> ${value}</div>`;
      }
      document.getElementById('extractedContent').innerHTML = contentHtml;


      const predictResponse = await fetch('https://verisite.onrender.com/predict', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ url })
      });

      if (predictResponse.ok) {
          const predictData = await predictResponse.json();
          document.getElementById('result').innerText = `Predicted Score: ${predictData.predictedScore}`;
      } else {
          document.getElementById('result').innerText = 'Failed to get prediction.';
      }
  } else {
      document.getElementById('extractedContent').innerText = 'Failed to get extracted content.';
  }
});
