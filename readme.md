# Verisite

An ML-based browser extension to detect malicious websites.

Verisite is a browser extension, that estimates the probability of a website being safe using only the URL of the website as input. It works using a fine-tuned DeBERTa v3 model, which acts like a text classifier to categorize the URLs into benign or malicious. The DeBERTa output along with some engineered features are then fed into a fully connected neural network, to estimate the probability of a website being benign. (A score out of 100 is given, with 100 being benign and 0 being malicious).

---

![Screenshot of the extension popup showing a benign website]((https://github.com/Abhiram-29/VeriSite/blob/main/images/92.png))
Extension showing a safe website score.

---

![Screenshot of the extension popup showing a malicious website](https://github.com/Abhiram-29/VeriSite/blob/main/images/47.png)
Extension showing a malicious website score.

---

![Screenshot of the model architecture or a key feature](https://github.com/Abhiram-29/VeriSite/blob/main/images/14.png)
Another malicious website with a lower score.

### Note

While a more robust defense against malicious websites typically involves analyzing features such as Domain Age, SSL Certificate Age, and potential vulnerabilities like XSS, this project serves to demonstrate the potential of machine learning when applied solely to the limited information available within a website's URL.
