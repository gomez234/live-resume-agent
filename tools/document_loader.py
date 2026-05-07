"""
This Python file is designed to read text from PDF and text files from a specified directory and compile their contents into a single string output. 
It first defines the directory where these documents are stored, then contains two functions: 
1. `read_pdf`: This function takes in a file path for a PDF, processes each page to extract text, and returns the combined text as a string.
2. `load_documents`: This function goes through all files in the defined data directory, checks their types, reads them using the `read_pdf` function if they are PDFs, or reads text directly if they are text files, 
    and compiles the contents into a single output string. The expected input is the path to the data directory containing PDF or text files, 
    while the output is a string containing all extracted text from these documents, formatted appropriately.
"""

#Import the necessary libraries
from pathlib import Path
from pypdf import PdfReader

#Define the data directory
DATA_DIR = Path("data")

#Define the function to read the PDF file
def read_pdf(path: Path) -> str:
    #Create the PDF reader
    reader = PdfReader(path)
    #Initialize the text variable
    text = ""
    #Loop through the pages of the PDF file
    for page in reader.pages:
        #Extract the text from the page
        page_text = page.extract_text()
        #Add the text to the text variable
        if page_text:
            text += page_text + "\n"
    #Return the text
    return text

#Define the function to load the documents
def load_documents() -> list[str]:
    #Initialize the text variable
    all_text = ""
    #Loop through the files in the data directory
    for file_path in DATA_DIR.iterdir():
        #Check if the file is a PDF file
        if file_path.suffix.lower() == ".pdf":
            #Add the document name to the text variable
            all_text += f"\n\n--- Document: {file_path.name} ---\n"
            all_text += read_pdf(file_path)
        #Check if the file is a text file
        elif file_path.suffix.lower() in [".txt", ".md"]:
            #Add the document name to the text variable
            all_text += f"\n\n--- Document: {file_path.name} ---\n"
            #Add the text to the text variable
            all_text += file_path.read_text(encoding="utf-8")
    #Return the text variable
    return all_text