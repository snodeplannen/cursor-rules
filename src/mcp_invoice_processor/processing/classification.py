"""
Document classificatie module.
"""
from .models import DocumentType


# Trefwoorden voor CV classificatie
CV_KEYWORDS = {
    "ervaring", "opleiding", "vaardigheden", "curriculum vitae", "werkervaring",
    "education", "experience", "skills", "competenties", "diploma",
    "werkgever", "employer", "functie", "position", "carrière", "career"
}

# Trefwoorden voor factuur classificatie
INVOICE_KEYWORDS = {
    "factuur", "invoice", "totaal", "total", "bedrag", "amount", "btw", "vat",
    "klant", "customer", "leverancier", "supplier", "artikel", "item",
    "prijs", "price", "kosten", "costs", "betaling", "payment",
    "factuurnummer", "nummer", "datum", "date", "€", "eur", "euro",
    "subtotaal", "subtotal", "vervaldatum", "due"
}


def classify_document(text: str) -> DocumentType:
    """
    Classificeert het documenttype op basis van trefwoorden in de tekst.

    Args:
        text: De tekstinhoud van het document

    Returns:
        DocumentType: Het gedetecteerde documenttype
    """
    text_lower = text.lower()

    # Tel trefwoorden voor elk documenttype
    cv_score = sum(1 for keyword in CV_KEYWORDS if keyword in text_lower)
    invoice_score = sum(1 for keyword in INVOICE_KEYWORDS if keyword in text_lower)

    # Bepaal het documenttype op basis van scores
    # Verlaagde drempel voor betere detectie
    if cv_score > invoice_score and cv_score >= 1:
        return DocumentType.CV
    elif invoice_score > cv_score and invoice_score >= 1:
        return DocumentType.INVOICE
    elif invoice_score > 0:  # Als er enige invoice indicatie is, behandel als invoice
        return DocumentType.INVOICE
    elif cv_score > 0:  # Als er enige CV indicatie is, behandel als CV
        return DocumentType.CV
    else:
        # Default naar invoice voor onbekende documenten
        return DocumentType.INVOICE
