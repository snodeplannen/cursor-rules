"""
Tekstextractie module voor PDF documenten.
"""

import warnings
import fitz  # PyMuPDF 

# Onderdruk DeprecationWarnings van PyMuPDF
warnings.filterwarnings("ignore", category=DeprecationWarning, module="fitz")

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extraheert alle tekst uit een PDF op basis van de byte-inhoud.

    Args:
        pdf_bytes: De PDF als bytes

    Returns:
        str: De geëxtraheerde tekst

    Raises:
        ValueError: Als tekstextractie mislukt
    """
    try:
        # Onderdruk warnings tijdens PDF verwerking
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            text = ""
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text() + "\n"
            return text
            
    except Exception as e:
        # Log de fout en raise een specifieke exceptie
        raise ValueError(f"Kon tekst niet extraheren uit PDF: {e}")
