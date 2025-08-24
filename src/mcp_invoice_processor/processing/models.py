"""
Pydantic modellen voor document data extractie.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Union


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


class InvoiceData(BaseModel):
    """Factuur data model."""
    invoice_id: str = Field(description="Unieke identificatie van de factuur.")
    invoice_number: Optional[str] = Field(None, description="Factuurnummer zoals vermeld op de factuur.")
    invoice_date: Optional[str] = Field(None, description="Factuurdatum.")
    due_date: Optional[str] = Field(None, description="Vervaldatum van de factuur.")
    
    # Bedrijfsinformatie
    supplier_name: str = Field(description="Naam van de leverancier/verkoper.")
    supplier_address: Optional[str] = Field(None, description="Adres van de leverancier.")
    supplier_vat_number: Optional[str] = Field(None, description="BTW-nummer van de leverancier.")
    
    customer_name: str = Field(description="Naam van de klant/koper.")
    customer_address: Optional[str] = Field(None, description="Adres van de klant.")
    customer_vat_number: Optional[str] = Field(None, description="BTW-nummer van de klant.")
    
    # Financiële informatie
    subtotal: float = Field(description="Subtotaal exclusief BTW.")
    vat_amount: float = Field(description="BTW-bedrag.")
    total_amount: float = Field(description="Totaalbedrag inclusief BTW.")
    currency: str = Field(default="EUR", description="Valuta van de factuur.")
    
    # Factuurregels
    line_items: List["InvoiceLineItem"] = Field(default_factory=list, description="Lijst van factuurregels.")
    
    # Betalingsinformatie
    payment_terms: Optional[str] = Field(None, description="Betalingsvoorwaarden.")
    payment_method: Optional[str] = Field(None, description="Betalingsmethode.")
    
    # Extra informatie
    notes: Optional[str] = Field(None, description="Opmerkingen of notities op de factuur.")
    reference: Optional[str] = Field(None, description="Referentie of ordernummer.")


class InvoiceLineItem(BaseModel):
    """Factuurregel model."""
    description: str = Field(description="Beschrijving van het product of de dienst.")
    quantity: float = Field(description="Aantal of hoeveelheid.")
    unit_price: float = Field(description="Eenheidsprijs exclusief BTW.")
    unit: Optional[str] = Field(None, description="Eenheid (stuks, uren, etc.).")
    line_total: float = Field(description="Regeltotaal exclusief BTW.")
    vat_rate: Optional[float] = Field(None, description="BTW-tarief percentage.")
    vat_amount: Optional[float] = Field(None, description="BTW-bedrag voor deze regel.")


class ProcessingResult(BaseModel):
    """Resultaat van documentverwerking."""
    document_type: str = Field(description="Type gedetecteerd document.")
    data: Union[CVData, InvoiceData, None] = Field(description="Geëxtraheerde gestructureerde data.")
    status: str = Field(description="Status van de verwerking.")
    error_message: Optional[str] = Field(None, description="Foutmelding indien verwerking mislukt.")
