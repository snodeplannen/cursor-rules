"""
Prompts voor CV data extractie.

Bevat alle prompts voor verschillende extractie methoden.
"""


def get_json_schema_prompt(text: str) -> str:
    """
    Prompt voor JSON schema mode (Ollama structured outputs).
    
    Args:
        text: CV tekst
        
    Returns:
        str: Prompt geoptimaliseerd voor JSON schema extractie
    """
    return f"""
Extract ALL structured information from the following CV text. Be thorough and complete.

REQUIRED fields to fill:
1. full_name (complete name of the person)
2. email (email address)
3. phone_number (phone number)
4. summary (professional summary or objective)
5. work_experience array - extract ALL job positions with:
   - job_title, company, start_date, end_date, description
6. education array - extract ALL education with:
   - degree, institution, graduation_date
7. skills array - extract ALL skills mentioned

Use empty string "" for missing text fields and empty array [] for missing lists.

Text:
{text}
"""


def get_prompt_parsing_prompt(text: str) -> str:
    """
    Prompt voor prompt parsing mode (traditionele LLM met JSON parsing).
    
    Args:
        text: CV tekst
        
    Returns:
        str: Prompt voor traditionele extractie met JSON output
    """
    return f"""
Extract structured information from the following CV text.

IMPORTANT: Return ONLY valid JSON without any explanation text, comments, or markdown formatting.
Use EXACTLY these field names in your JSON output:
- full_name (for the full name)
- email (for email address)
- phone_number (for phone number)
- summary (for summary/objective)
- work_experience (list of work experiences, each with: job_title, company, start_date, end_date, description)
- education (list of education, each with: degree, institution, graduation_date)
- skills (list of skills as strings)

Ensure all required fields are present. If a field cannot be found, use empty string or empty list.

Text:
{text}

Return ONLY the JSON object, no other text.
"""
