# ParseBank 🏦  
**An AI-Powered Bank Statement Parser and Transaction Analyzer**

ParseBank is a web-based application designed to automatically extract and analyze transaction data from bank statements (PDF, CSV, and image formats). The app utilizes OCR and parsing logic to generate structured data tables, enabling users to view, clean, and export their financial data interactively.  

The application is deployed on Hugging Face Spaces and is accessible here:  
🔗 [https://huggingface.co/spaces/Subhasya/ParseBank](https://huggingface.co/spaces/Subhasya/ParseBank)

---

## 🔍 Features

- **File Upload & Parsing**: Upload PDF statements and extract transaction tables using OCR and pattern recognition.
- **Transaction Extraction**: Captures key fields such as `Date`, `Description`, `Amount`, `Type`, and `Balance`.
- **Data Cleaning & Formatting**: Cleans extracted tables for consistent formatting using Pandas.
- **Export Capability**: Allows users to download the parsed data as a CSV file.
- **Web Interface**: A simple and intuitive Streamlit-based UI for interaction.

---

## 📂 Files Overview

- `app.py`: Main script containing the Streamlit UI and integration logic for upload, parse, and display.
- `requirements.txt`: Python libraries needed for the application.
  
---

## ⚙️ Setup & Installation

## Step 1: Clone the Repository
git clone https://github.com/Santhoshi129/ParseBank.git
cd ParseBank

---

## Step 2: Install Dependencies
pip install -r requirements.txt

---

## Step 3: Run the Application
streamlit run app.py

---

## Step 4: Use the Interface
Open the local server link (typically http://localhost:8501).

Upload your bank statement file.

The app will display extracted transactions in a table.


