"""
Prompts voor Invoice data extractie.

Bevat alle prompts voor verschillende extractie methoden.
"""


def get_json_schema_prompt(text: str) -> str:
    """
    Prompt voor JSON schema mode (Ollama structured outputs).
    
    Args:
        text: Invoice tekst
        
    Returns:
        str: Prompt geoptimaliseerd voor JSON schema extractie
    """
    return f"""
Extract ALL structured information from the following invoice text. Be extremely thorough and complete.

CRITICAL: The line_items array is MANDATORY - extract ALL products/services from the invoice table/list.
Look for any table, list, or itemized section showing products, services, descriptions, quantities, and prices.

REQUIRED fields to fill:
1. invoice_id AND invoice_number (use same value if only one number found)
2. invoice_date and due_date (extract all dates)
3. supplier_name, supplier_address, supplier_vat_number (from "Van:" section)
4. customer_name, customer_address, customer_vat_number (from "Aan:" section)
5. subtotal, vat_amount, total_amount (extract all monetary amounts as numbers)
6. line_items array - MUST contain ALL itemized products/services with:
   - description (product/service name)
   - quantity (as number, default 1 if not specified)
   - unit_price (price per unit as number)
   - line_total (total for this line as number)
   - vat_rate (VAT percentage if available)
   - vat_amount (VAT amount for this line if available)
7. payment_terms, payment_method, notes, reference (any additional info)

DO NOT leave line_items empty if there are any products/services listed in the invoice!

Text:
{text}
"""


def get_prompt_parsing_prompt(text: str) -> str:
    """
    Prompt voor prompt parsing mode (traditionele LLM met JSON parsing).
    
    Args:
        text: Invoice tekst
        
    Returns:
        str: Prompt voor traditionele extractie met JSON output
    """
    return f"""
Extract structured information from the following invoice text.

IMPORTANT: Return ONLY valid JSON without any explanation text, comments, or markdown formatting.
Use EXACTLY these field names in your JSON output:

Basic information:
- invoice_id (for unique identification, use invoice number or generate unique ID)
- invoice_number (for invoice number)
- invoice_date (for invoice date)
- due_date (for due date)

Company information:
- supplier_name (for supplier name)
- supplier_address (for supplier address)
- supplier_vat_number (for supplier VAT number)
- customer_name (for customer name)
- customer_address (for customer address)
- customer_vat_number (for customer VAT number)

Financial information:
- subtotal (for subtotal excluding VAT)
- vat_amount (for VAT amount)
- total_amount (for total including VAT)
- currency (for currency, default "EUR")

Invoice lines (line_items):
- description (for product/service description)
- quantity (for quantity, must be a number, use 1 if not specified)
- unit_price (for unit price)
- unit (for unit: pieces, hours, etc.)
- line_total (for line total)
- vat_rate (for VAT rate percentage)
- vat_amount (for VAT amount per line)

Payment information:
- payment_terms (for payment terms)
- payment_method (for payment method)

Extra information:
- notes (for notes)
- reference (for reference/order number)

CRITICAL: All quantity fields must be numbers (not strings). Use 1 for single items, 0 for discounts/promotions.
Ensure all required fields are present. If a field cannot be found, use empty string or empty list.

Text:
{text}

Return ONLY the JSON object, no other text.
"""

