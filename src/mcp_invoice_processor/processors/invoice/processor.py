"""
Invoice Document Processor.

Implementeert volledige invoice processing met classificatie, extractie,
validatie en merging van partiële resultaten.
"""

import time
import logging
import json as json_module
import re
from typing import Optional, List, Dict, Any, Set, Type, Tuple

import ollama
from pydantic import BaseModel, ValidationError
from rapidfuzz import fuzz

from ..base import BaseDocumentProcessor
from ...config import settings
from .models import InvoiceData, InvoiceLineItem
from .prompts import get_json_schema_prompt, get_prompt_parsing_prompt

logger = logging.getLogger(__name__)


class InvoiceProcessor(BaseDocumentProcessor):
    """
    Invoice document processor.
    
    Verwerkt facturen met:
    - Keyword-based classificatie
    - JSON schema en prompt parsing extractie
    - Hybrid mode voor beste resultaten
    - Validatie van geëxtraheerde data
    - Merging van gechunkte documenten
    """
    
    # ==================== METADATA ====================
    
    @property
    def document_type(self) -> str:
        return "invoice"
    
    @property
    def display_name(self) -> str:
        return "Factuur"
    
    @property
    def tool_name(self) -> str:
        return "process_invoice"
    
    @property
    def tool_description(self) -> str:
        return (
            "Verwerk facturen en extraheer gestructureerde data zoals "
            "factuurnummer, bedrijfsinformatie, bedragen, BTW, en factuurregels. "
            "Ondersteunt PDF en text bestanden met automatische detectie."
        )
    
    # ==================== CLASSIFICATIE ====================
    
    @property
    def classification_keywords(self) -> Set[str]:
        return {
            "factuur", "invoice", "totaal", "total", "bedrag", "amount", 
            "btw", "vat", "klant", "customer", "leverancier", "supplier", 
            "artikel", "item", "prijs", "price", "kosten", "costs", 
            "betaling", "payment", "factuurnummer", "nummer", "datum", 
            "date", "€", "eur", "euro", "subtotaal", "subtotal", 
            "vervaldatum", "due"
        }
    
    async def classify(
        self, 
        text: str
    ) -> float:
        """
        Classificeer tekst als invoice op basis van keywords.
        
        Returns confidence score 0-100.
        """
        self.log_debug("Classificeren als invoice...")
        
        text_lower = text.lower()
        
        # Tel voorkomens van keywords
        keyword_count = sum(
            1 for keyword in self.classification_keywords 
            if keyword in text_lower
        )
        
        # Bereken confidence score
        # Formule: min(keyword_count * 10, 100)
        confidence = min(keyword_count * 10.0, 100.0)
        
        self.log_debug(
            f"Invoice classificatie: {keyword_count} keywords, {confidence}% confidence",
            extra={"keyword_count": keyword_count, "confidence": confidence}
        )
        
        return confidence
    
    # ==================== DATA MODELLEN ====================
    
    @property
    def data_model(self) -> Type[BaseModel]:
        return InvoiceData
    
    def get_json_schema(self) -> Dict[str, Any]:
        return InvoiceData.model_json_schema()
    
    # ==================== PROMPTS ====================
    
    def get_extraction_prompt(self, text: str, method: str) -> str:
        if method == "json_schema":
            return get_json_schema_prompt(text)
        else:  # prompt_parsing
            return get_prompt_parsing_prompt(text)
    
    # ==================== EXTRACTIE ====================
    
    async def extract(
        self,
        text: str,
        method: str = "hybrid"
    ) -> Optional[BaseModel]:
        """
        Extraheer invoice data uit tekst.
        
        Ondersteunt hybrid, json_schema en prompt_parsing modes.
        """
        start_time = time.time()
        
        self.log_info(
            f"Start invoice extractie ({method} mode)",
            extra={"method": method, "text_length": len(text)}
        )
        
        try:
            # Hybrid mode: probeer json_schema eerst, fallback naar prompt_parsing
            if method == "hybrid":
                self.log_info("Hybrid mode: probeer JSON schema eerst")
                
                # Probeer JSON schema
                json_result = await self._extract_with_method(text, "json_schema")
                
                if json_result:
                    # Evalueer kwaliteit
                    _, completeness, _ = await self.validate_extracted_data(json_result)
                    
                    if completeness >= 90.0:
                        self.log_info(
                            f"JSON schema succesvol ({completeness:.1f}% compleet)",
                            extra={"completeness": completeness}
                        )
                        
                        # Update statistics
                        processing_time = time.time() - start_time
                        self.update_statistics(True, processing_time, completeness=completeness)
                        
                        return json_result
                    else:
                        self.log_warning(
                            f"JSON schema incomplete ({completeness:.1f}%), probeer prompt parsing",
                            extra={"completeness": completeness}
                        )
                
                # JSON schema niet goed genoeg, probeer prompt parsing
                self.log_info("Probeer prompt parsing als fallback")
                prompt_result = await self._extract_with_method(text, "prompt_parsing")
                
                if prompt_result:
                    _, completeness, _ = await self.validate_extracted_data(prompt_result)
                    self.log_info(
                        f"Prompt parsing succesvol ({completeness:.1f}% compleet)",
                        extra={"completeness": completeness}
                    )
                    
                    # Update statistics
                    processing_time = time.time() - start_time
                    self.update_statistics(True, processing_time, completeness=completeness)
                    
                    return prompt_result
                
                # Beide gefaald
                if json_result:
                    self.log_warning("Beide methodes incomplete, gebruik JSON schema resultaat")
                    
                    processing_time = time.time() - start_time
                    self.update_statistics(True, processing_time)
                    
                    return json_result
                
                self.log_error("Beide extractie methodes gefaald")
                
                processing_time = time.time() - start_time
                self.update_statistics(False, processing_time)
                
                return None
            
            # Single method mode
            result = await self._extract_with_method(text, method)
            
            processing_time = time.time() - start_time
            
            if result:
                _, completeness, _ = await self.validate_extracted_data(result)
                self.update_statistics(True, processing_time, completeness=completeness)
            else:
                self.update_statistics(False, processing_time)
            
            return result
            
        except Exception as e:
            self.log_error(f"Extractie fout: {e}", extra={"error": str(e)})
            
            processing_time = time.time() - start_time
            self.update_statistics(False, processing_time)
            
            return None
    
    async def _extract_with_method(
        self,
        text: str,
        method: str
    ) -> Optional[InvoiceData]:
        """Helper method voor extractie met specifieke methode."""
        
        try:
            prompt = self.get_extraction_prompt(text, method)
            
            self.log_debug(f"Ollama aanroepen met {method} methode")
            
            # Ollama request
            if method == "json_schema":
                json_schema = self.get_json_schema()
                response = ollama.chat(
                    model=settings.ollama.MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    format=json_schema,
                    options={
                        "temperature": 0.1,
                        "num_predict": 2048,
                    }
                )
            else:  # prompt_parsing
                response = ollama.chat(
                    model=settings.ollama.MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    options={
                        "temperature": 0.1,
                        "num_predict": 2048,
                        "stop": ["```", "```json", "```\n", "\n\n\n"]
                    }
                )
            
            response_content = response['message']['content'].strip()
            
            # JSON extractie
            json_str = self._extract_json_from_response(response_content, method)
            
            if not json_str:
                self.log_error("Geen JSON gevonden in response")
                return None
            
            # JSON parsen met reparatie
            parsed_data = self._parse_json_with_repair(json_str)
            
            if not parsed_data:
                return None
            
            # Valideren met Pydantic
            try:
                validated_data = InvoiceData(**parsed_data)
                self.log_info("Invoice data succesvol geëxtraheerd")
                return validated_data
            except ValidationError as e:
                self.log_error(f"Pydantic validatie fout: {e}")
                return None
                
        except Exception as e:
            self.log_error(f"Extractie fout: {e}")
            return None
    
    def _extract_json_from_response(self, response: str, method: str) -> Optional[str]:
        """Extract JSON from LLM response."""
        
        if method == "json_schema":
            # Direct JSON in response
            return response
        
        # Prompt parsing: zoek JSON in response
        # Methode 1: tussen ```json markers
        if "```json" in response:
            start_marker = "```json"
            end_marker = "```"
            start_idx = response.find(start_marker) + len(start_marker)
            end_idx = response.find(end_marker, start_idx)
            if start_idx != -1 and end_idx != -1:
                return response[start_idx:end_idx].strip()
        
        # Methode 2: tussen ``` markers
        elif "```" in response:
            parts = response.split("```")
            if len(parts) >= 3:
                return parts[1].strip()
        
        # Methode 3: tussen { en }
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            return response[json_start:json_end]
        
        # Methode 4: hele response
        return response.strip()
    
    def _parse_json_with_repair(self, json_str: str) -> Optional[Dict[str, Any]]:
        """Parse JSON met automatische reparatie van veelvoorkomende fouten."""
        
        try:
            parsed_data: Dict[str, Any] = json_module.loads(json_str)
            return parsed_data
        except json_module.JSONDecodeError as e:
            logger.warning(f"JSON parsing fout: {e}, probeer reparatie...")
            
            # Repareer JSON
            repaired_json = json_str.strip()
            
            # Verwijder trailing comma's
            repaired_json = re.sub(r',\s*([}\]])', r'\1', repaired_json)
            
            # Tel open/close brackets
            open_braces = repaired_json.count('{')
            close_braces = repaired_json.count('}')
            open_brackets = repaired_json.count('[')
            close_brackets = repaired_json.count(']')
            
            # Voeg missende sluit-tekens toe
            if open_braces > close_braces:
                repaired_json += '}' * (open_braces - close_braces)
            if open_brackets > close_brackets:
                repaired_json += ']' * (open_brackets - close_brackets)
            
            # Verwijder opnieuw trailing comma's
            repaired_json = re.sub(r',\s*([}\]])', r'\1', repaired_json)
            
            # Probeer opnieuw
            try:
                repaired_parsed_data: Dict[str, Any] = json_module.loads(repaired_json)
                return repaired_parsed_data
            except json_module.JSONDecodeError:
                logger.error("JSON reparatie gefaald")
                return None
    
    # ==================== MERGING ====================
    
    async def merge_partial_results(
        self, 
        partial_results: List[BaseModel]
    ) -> Optional[InvoiceData]:
        """
        Merge partiële invoice resultaten.
        
        Combineert line items en gebruikt eerste niet-lege waarde voor andere velden.
        """
        self.log_info(f"Mergen van {len(partial_results)} partiële resultaten")
        
        if not partial_results:
            self.log_error("Geen partiële resultaten om te mergen")
            return None
        
        # Filter alleen InvoiceData objecten
        invoice_results = [r for r in partial_results if isinstance(r, InvoiceData)]
        
        if not invoice_results:
            self.log_error("Geen invoice data gevonden in resultaten")
            return None
        
        # Start met eerste resultaat
        merged = invoice_results[0].model_copy()
        
        # Merge line items
        all_line_items = []
        for result in invoice_results:
            if result.line_items:
                all_line_items.extend(result.line_items)
        
        merged.line_items = self._deduplicate_line_items(all_line_items)
        
        # Voor andere velden: eerste niet-lege waarde
        for result in invoice_results[1:]:
            if not merged.invoice_number and result.invoice_number:
                merged.invoice_number = result.invoice_number
            if not merged.invoice_date and result.invoice_date:
                merged.invoice_date = result.invoice_date
            if not merged.due_date and result.due_date:
                merged.due_date = result.due_date
            if not merged.supplier_address and result.supplier_address:
                merged.supplier_address = result.supplier_address
            if not merged.supplier_vat_number and result.supplier_vat_number:
                merged.supplier_vat_number = result.supplier_vat_number
            if not merged.customer_address and result.customer_address:
                merged.customer_address = result.customer_address
            if not merged.customer_vat_number and result.customer_vat_number:
                merged.customer_vat_number = result.customer_vat_number
            if not merged.payment_terms and result.payment_terms:
                merged.payment_terms = result.payment_terms
            if not merged.payment_method and result.payment_method:
                merged.payment_method = result.payment_method
            if not merged.notes and result.notes:
                merged.notes = result.notes
            if not merged.reference and result.reference:
                merged.reference = result.reference
        
        # Herbereken totalen
        if merged.line_items:
            merged.subtotal = sum(item.line_total for item in merged.line_items)
            merged.vat_amount = sum(item.vat_amount or 0 for item in merged.line_items)
            merged.total_amount = merged.subtotal + merged.vat_amount
        
        self.log_info(
            f"Merge compleet: {len(merged.line_items)} line items",
            extra={"line_items_count": len(merged.line_items)}
        )
        
        return merged
    
    def _deduplicate_line_items(
        self, 
        line_items: List[InvoiceLineItem], 
        threshold: int = 85
    ) -> List[InvoiceLineItem]:
        """Ontdubbel line items met fuzzy matching."""
        
        if not line_items:
            return []
        
        unique_items: List[InvoiceLineItem] = []
        
        for item in line_items:
            is_duplicate = False
            
            for unique_item in unique_items:
                # Vergelijk beschrijving en prijs
                str1 = f"{item.description} {item.unit_price}".lower()
                str2 = f"{unique_item.description} {unique_item.unit_price}".lower()
                
                if fuzz.ratio(str1, str2) > threshold:
                    # Duplicaat: voeg quantities samen
                    unique_item.quantity += item.quantity
                    unique_item.line_total += item.line_total
                    if item.vat_amount:
                        unique_item.vat_amount = (unique_item.vat_amount or 0) + item.vat_amount
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_items.append(item)
        
        return unique_items
    
    # ==================== VALIDATIE ====================
    
    async def validate_extracted_data(
        self, 
        data: BaseModel
    ) -> Tuple[bool, float, List[str]]:
        """
        Valideer invoice data en bereken completeness.
        """
        if not isinstance(data, InvoiceData):
            return False, 0.0, ["Data is geen InvoiceData object"]
        
        issues = []
        
        # Required fields check
        if not data.invoice_id:
            issues.append("invoice_id is leeg")
        if not data.supplier_name:
            issues.append("supplier_name is leeg")
        if not data.customer_name:
            issues.append("customer_name is leeg")
        
        # Financial data check
        if data.total_amount <= 0:
            issues.append("total_amount is 0 of negatief")
        
        # Line items check
        if not data.line_items or len(data.line_items) == 0:
            issues.append("Geen line items gevonden")
        
        # Bereken completeness
        data_dict = data.model_dump()
        total_fields = 0
        filled_fields = 0
        
        for key, value in data_dict.items():
            if key == "line_items":
                total_fields += 1
                if isinstance(value, list) and len(value) > 0:
                    filled_fields += 1
                    # Tel ook line item velden
                    for item in value:
                        if isinstance(item, dict):
                            for item_value in item.values():
                                total_fields += 1
                                if item_value is not None and item_value != "" and item_value != 0:
                                    filled_fields += 1
            else:
                total_fields += 1
                if value is not None and value != "" and value != 0:
                    filled_fields += 1
        
        completeness = (filled_fields / total_fields * 100) if total_fields > 0 else 0.0
        is_valid = len(issues) == 0
        
        self.log_info(
            f"Validatie: {completeness:.1f}% compleet, {len(issues)} issues",
            extra={
                "completeness": completeness,
                "is_valid": is_valid,
                "issues_count": len(issues)
            }
        )
        
        return is_valid, completeness, issues
    
    # ==================== CUSTOM METRICS ====================
    
    async def get_custom_metrics(
        self, 
        data: BaseModel
    ) -> Dict[str, Any]:
        """
        Generate invoice-specific metrics.
        """
        if not isinstance(data, InvoiceData):
            return {}
        
        metrics = {
            "total_amount": data.total_amount,
            "subtotal": data.subtotal,
            "vat_amount": data.vat_amount,
            "currency": data.currency,
            "line_items_count": len(data.line_items) if data.line_items else 0,
            "has_vat": data.vat_amount > 0,
            "has_line_items": len(data.line_items) > 0 if data.line_items else False,
            "avg_line_item_value": (
                data.subtotal / len(data.line_items) 
                if data.line_items and len(data.line_items) > 0 
                else 0.0
            )
        }
        
        self.log_debug("Custom metrics gegenereerd", extra=metrics)
        
        return metrics

