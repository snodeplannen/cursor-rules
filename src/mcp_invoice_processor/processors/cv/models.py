"""
Pydantic models voor CV data extractie.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class WorkExperience(BaseModel):
    """Werkervaring model."""
    job_title: str = Field(description="De functietitel.")
    company: str = Field(description="De naam van het bedrijf.")
    start_date: Optional[str] = Field(None, description="Startdatum van de functie.")
    end_date: Optional[str] = Field(None, description="Einddatum van de functie.")
    description: str = Field(description="Beschrijving van de werkzaamheden.")


class Education(BaseModel):
    """Opleiding model."""
    degree: str = Field(description="De behaalde graad of diploma.")
    institution: str = Field(description="De onderwijsinstelling.")
    graduation_date: Optional[str] = Field(None, description="Afstudeerdatum.")


class CVData(BaseModel):
    """CV data model."""
    full_name: str = Field(description="De volledige naam van de kandidaat.")
    email: Optional[str] = Field(None, description="Het primaire e-mailadres.")
    phone_number: Optional[str] = Field(None, description="Het primaire telefoonnummer.")
    summary: str = Field(description="Een korte professionele samenvatting of doelstelling.")
    work_experience: List[WorkExperience] = Field(description="Lijst van werkervaringen.")
    education: List[Education] = Field(description="Lijst van opleidingen.")
    skills: List[str] = Field(description="Een lijst van belangrijke vaardigheden en technologieën.")

