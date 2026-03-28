import fitz  # pymupdf - reads PDF files
from PIL import Image
import io

def extract_text_from_pdf(uploaded_file):
    """
    Reads EVERY single page of PDF
    Extracts ALL raw text and tables
    Nothing is skipped or cut off
    """
    file_bytes = uploaded_file.read()
    pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
    
    full_content = {
        "total_pages": len(pdf_document),
        "full_text": "",
        "tables": []
    }
    
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        
        # Extract ALL text from this page
        page_text = page.get_text()
        
        # Extract tables from this page
        try:
            tables = page.find_tables()
            if tables.tables:
                for table in tables.tables:
                    table_data = table.extract()
                    if table_data:
                        full_content["tables"].append({
                            "page": page_num + 1,
                            "data": table_data
                        })
        except:
            pass  # some PDFs dont have tables thats fine
        
        # Add page text to full text
        full_content["full_text"] += f"\n--- PAGE {page_num + 1} ---\n"
        full_content["full_text"] += page_text
    
    pdf_document.close()
    return full_content


def extract_text_from_image(uploaded_file):
    """
    Reads image file and prepares it for AI processing
    """
    image = Image.open(uploaded_file)
    
    img_bytes = io.BytesIO()
    image.save(img_bytes, format=image.format or "PNG")
    img_bytes = img_bytes.getvalue()
    
    return img_bytes, image.format or "PNG"


def format_for_ai(extracted_content):
    """
    Takes all the raw extracted content
    and formats it into one clean string
    so CrewAI agents can read and understand it perfectly
    """
    formatted = ""
    
    # Add basic info
    formatted += f"TOTAL PAGES IN REPORT: {extracted_content['total_pages']}\n\n"
    
    # Add complete text
    formatted += "=== COMPLETE REPORT TEXT ===\n"
    formatted += extracted_content["full_text"]
    formatted += "\n\n"
    
    # Add tables if found
    if extracted_content["tables"]:
        formatted += "=== TABLES FOUND IN REPORT ===\n"
        for i, table in enumerate(extracted_content["tables"]):
            formatted += f"\nTable {i+1} (Found on Page {table['page']}):\n"
            for row in table["data"]:
                # skip completely empty rows
                if any(cell for cell in row if cell):
                    formatted += " | ".join(
                        str(cell).strip() if cell else "" 
                        for cell in row
                    ) + "\n"
    
    return formatted


def extract_content(uploaded_file):
    """
    MAIN FUNCTION
    This is what app.py calls
    Detects file type and extracts everything
    Returns content ready to send to CrewAI
    """
    filename = uploaded_file.name.lower()
    
    # Handle PDF files
    if filename.endswith(".pdf"):
        
        extracted = extract_text_from_pdf(uploaded_file)
        
        # Check if anything was extracted
        if not extracted["full_text"].strip():
            return {
                "type": "error",
                "content": "Could not read this PDF. It may be scanned or corrupted. Please upload a clearer file."
            }
        
        # Format everything into clean text for CrewAI
        formatted_text = format_for_ai(extracted)
        
        return {
            "type": "text",
            "content": formatted_text,        # this goes to CrewAI
            "total_pages": extracted["total_pages"],
            "has_tables": len(extracted["tables"]) > 0,
            "table_count": len(extracted["tables"])
        }
    
    # Handle Image files
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        
        img_bytes, img_format = extract_text_from_image(uploaded_file)
        
        return {
            "type": "image",
            "content": img_bytes,             # this goes to CrewAI
            "format": img_format
        }
    
    # Unsupported file
    else:
        return {
            "type": "error",
            "content": "Unsupported file. Please upload a PDF or image (PNG, JPG, JPEG)."
        }


def get_file_info(uploaded_file):
    """
    Returns basic file information
    Used by app.py to show user what they uploaded
    """
    filename = uploaded_file.name
    file_size = uploaded_file.size / 1024  # convert bytes to KB
    file_type = filename.split(".")[-1].upper()
    
    return {
        "filename": filename,
        "size": f"{file_size:.1f} KB",
        "type": file_type
    }






# What this does step by step:**

# extract_text_from_pdf` → Opens every page of PDF, reads all text, finds all tables, stores everything

# extract_text_from_image` → Opens image and converts it to bytes for AI to read

# format_for_ai` → Takes all raw text and tables and organizes it into one clean formatted string that CrewAI agents can perfectly understand

# extract_content` → Main function that app.py calls. Detects PDF or image automatically and returns everything ready for CrewAI

# get_file_info` → Small helper that returns filename, size and type to show user in UI

