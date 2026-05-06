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