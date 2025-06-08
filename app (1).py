import os
import re
import json
import gradio as gr
import pandas as pd
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from huggingface_hub import InferenceClient

# Initialize Hugging Face Inference Client
hf_token = os.getenv("HF_TOKEN")
client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.3", token=hf_token)

def extract_excel_data(file_path):
    """Extract text from Excel file"""
    df = pd.read_excel(file_path, engine='openpyxl')
    return df.to_string(index=False)

def extract_text_from_pdf(pdf_path, is_scanned=False):
    """Extract text from PDF with fallback OCR"""
    try:
        # Try native PDF extraction first
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Native PDF extraction failed: {str(e)}")
        # Fallback to OCR for scanned PDFs
        images = convert_from_path(pdf_path, dpi=200)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
        return text

def parse_bank_statement(text):
    """Parse bank statement using LLM with fallback to rule-based parser"""
    cleaned_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # Craft precise prompt for LLM
    prompt = f"""
You are a financial data parser. Extract transactions from bank statements.

Given this bank statement text:

Extract all transactions with these fields:
- Date
- Description
- Amount
- Debit
- Credit
- Closing Balance
- Category

Return JSON with "transactions" array containing these fields.

Example format:
{"transactions": [
  {"date": "2025-05-08", "description": "Company XYZ Payroll", "amount": "8315.40", "debit": "0.00", "credit": "8315.40", "closing_balance": "38315.40", "category": "Salary"},
  ...
]}

Rules:
1. Ensure numeric fields have valid numbers (e.g., "0.00" instead of "-")
2. Convert negative balances to standard format (e.g., "-2421.72")
3. Map category names consistently (e.g., "Groceries", "Medical", "Utilities")
"""

    try:
        # Call LLM via Hugging Face Inference API
        response = client.text_generation(prompt, max_new_tokens=1000, temperature=0.1)
        return json.loads(response)
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        # Fallback to rule-based parser
        return rule_based_parser(cleaned_text)

def rule_based_parser(text):
    """Fallback parser for structured tables with pipe delimiters"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Find header line containing '| Date'
    header_index = None
    for i, line in enumerate(lines):
        if re.search(r'\|Date', line):  # Improved pattern to match "|Date"
            header_index = i
            break
    
    if header_index is None or header_index + 1 >= len(lines):
        return {"transactions": []}
    
    data_lines = lines[header_index + 1:]
    transactions = []
    
    for line in data_lines:
        if not line.startswith('|'):
            continue
            
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) < 7:
            continue
            
        try:
            transactions.append({
                "date": parts[0],
                "description": parts[1],
                "amount": parts[2],
                "debit": parts[3],
                "credit": parts[4],
                "closing_balance": parts[5],
                "category": parts[6]
            })
        except Exception as e:
            print(f"Error parsing line: {str(e)}")
    
    return {"transactions": transactions}

def process_file(file, is_scanned):
    """Main processing function"""
    if not file:
        return pd.DataFrame(columns=[
            "Date", "Description", "Amount", "Debit", 
            "Credit", "Closing Balance", "Category"
        ])
    
    file_path = file.name
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext == '.xlsx':
            text = extract_excel_data(file_path)
        elif file_ext == '.pdf':
            text = extract_text_from_pdf(file_path, is_scanned=is_scanned)
        else:
            return pd.DataFrame(columns=[
                "Date", "Description", "Amount", "Debit", 
                "Credit", "Closing Balance", "Category"
            ])
        
        parsed_data = parse_bank_statement(text)
        df = pd.DataFrame(parsed_data["transactions"])
        
        # Ensure all required columns exist
        required_cols = ["date", "description", "amount", "debit", 
                        "credit", "closing_balance", "category"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
                
        df.columns = ["Date", "Description", "Amount", "Debit", 
                     "Credit", "Closing Balance", "Category"]
        return df
    
    except Exception as e:
        print(f"Processing error: {str(e)}")
        # Return empty DataFrame with correct columns on error
        return pd.DataFrame(columns=[
            "Date", "Description", "Amount", "Debit", 
            "Credit", "Closing Balance", "Category"
        ])

# Gradio Interface
interface = gr.Interface(
    fn=process_file,
    inputs=[
        gr.File(label="Upload Bank Statement (PDF/Excel)"),
        gr.Checkbox(label="Is Scanned PDF? (Use OCR)")
    ],
    outputs=gr.Dataframe(
        label="Parsed Transactions",
        headers=["Date", "Description", "Amount", "Debit", "Credit", "Closing Balance", "Category"]
    ),
    title="AI Bank Statement Parser",
    description="Extract structured transaction data from PDF/Excel bank statements using LLM and hybrid parsing techniques.",
    allow_flagging="never"
)

if __name__ == "__main__":
    interface.launch()