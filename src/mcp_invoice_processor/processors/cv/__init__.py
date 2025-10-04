"""
CV Document Processor Module.

Volledige implementatie voor CV processing inclusief:
- Data models (CVData, WorkExperience, Education)
- Extraction prompts (JSON schema en prompt parsing)
- CVProcessor met classificatie, extractie, validatie en merging
"""

from .models import CVData, WorkExperience, Education
from .processor import CVProcessor

__all__ = [
    "CVData",
    "WorkExperience",
    "Education",
    "CVProcessor",
]

