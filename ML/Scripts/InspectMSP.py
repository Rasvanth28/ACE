from pypdf import PdfReader
import os
import re

def inspect_msp_pdf():
    script_dir = os.path.dirname(__file__)
    pdf_path = os.path.join(script_dir, "DataSet/Maharashtra/External Factors/msp.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    reader = PdfReader(pdf_path)
    print(f"Number of pages: {len(reader.pages)}")
    
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
        
    print("\n--- Extracted Text Preview (First 2000 chars) ---")
    print(full_text[:2000])
    
    print("\n--- Searching for 'Wheat' ---")
    # Simple search for lines containing Wheat
    lines = full_text.split('\n')
    wheat_lines = [line for line in lines if "Wheat" in line or "wheat" in line]
    for line in wheat_lines:
        print(line)

if __name__ == "__main__":
    inspect_msp_pdf()
