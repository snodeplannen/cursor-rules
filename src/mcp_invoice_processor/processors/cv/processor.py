"""
CV Document Processor.

Implementeert volledige CV processing met classificatie, extractie,
validatie en merging van partiële resultaten.
"""

import time
import logging
import json as json_module
import re
from typing import Optional, List, Dict, Any, Set, Type, Tuple

import ollama
from pydantic import BaseModel, ValidationError
from fastmcp import Context
from rapidfuzz import fuzz

from ..base import BaseDocumentProcessor
from ...config import settings
from ...monitoring.metrics import metrics_collector
from .models import CVData, WorkExperience, Education
from .prompts import get_json_schema_prompt, get_prompt_parsing_prompt

logger = logging.getLogger(__name__)


class CVProcessor(BaseDocumentProcessor):
    """
    CV document processor.
    
    Verwerkt CV's met:
    - Keyword-based classificatie
    - JSON schema en prompt parsing extractie
    - Hybrid mode voor beste resultaten
    - Validatie van geëxtraheerde data
    - Merging van gechunkte documenten
    """
    
    # ==================== METADATA ====================
    
    @property
    def document_type(self) -> str:
        return "cv"
    
    @property
    def display_name(self) -> str:
        return "Curriculum Vitae"
    
    @property
    def tool_name(self) -> str:
        return "process_cv"
    
    @property
    def tool_description(self) -> str:
        return (
            "Verwerk CV's en extraheer gestructureerde data zoals "
            "persoonlijke gegevens, werkervaring, opleiding en vaardigheden. "
            "Ondersteunt PDF en text bestanden met automatische detectie."
        )
    
    # ==================== CLASSIFICATIE ====================
    
    @property
    def classification_keywords(self) -> Set[str]:
        return {
            "ervaring", "opleiding", "vaardigheden", "curriculum vitae", 
            "werkervaring", "education", "experience", "skills", 
            "competenties", "diploma", "werkgever", "employer", 
            "functie", "position", "carrière", "career", "cv", "resume"
        }
    
    async def classify(
        self, 
        text: str, 
        ctx: Optional[Context] = None
    ) -> float:
        """
        Classificeer tekst als CV op basis van keywords.
        
        Returns confidence score 0-100.
        """
        await self.log_debug("Classificeren als CV...", ctx)
        
        text_lower = text.lower()
        
        # Tel voorkomens van keywords
        keyword_count = sum(
            1 for keyword in self.classification_keywords 
            if keyword in text_lower
        )
        
        # Bereken confidence score
        # Formule: min(keyword_count * 10, 100)
        confidence = min(keyword_count * 10.0, 100.0)
        
        await self.log_debug(
            f"CV classificatie: {keyword_count} keywords, {confidence}% confidence",
            ctx,
            extra={"keyword_count": keyword_count, "confidence": confidence}
        )
        
        return confidence
    
    # ==================== DATA MODELLEN ====================
    
    @property
    def data_model(self) -> Type[BaseModel]:
        return CVData
    
    def get_json_schema(self) -> Dict[str, Any]:
        return CVData.model_json_schema()
    
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
        ctx: Optional[Context] = None,
        method: str = "hybrid"
    ) -> Optional[BaseModel]:
        """
        Extraheer CV data uit tekst.
        
        Ondersteunt hybrid, json_schema en prompt_parsing modes.
        """
        start_time = time.time()
        
        await self.log_info(
            f"Start CV extractie ({method} mode)",
            ctx,
            extra={"method": method, "text_length": len(text)}
        )
        await self.report_progress(0, 100, ctx)
        
        try:
            # Hybrid mode: probeer json_schema eerst, fallback naar prompt_parsing
            if method == "hybrid":
                await self.log_info("Hybrid mode: probeer JSON schema eerst", ctx)
                await self.report_progress(10, 100, ctx)
                
                # Probeer JSON schema
                json_result = await self._extract_with_method(text, "json_schema", ctx)
                
                if json_result:
                    # Evalueer kwaliteit
                    _, completeness, _ = await self.validate_extracted_data(json_result, ctx)
                    
                    if completeness >= 90.0:
                        await self.log_info(
                            f"JSON schema succesvol ({completeness:.1f}% compleet)",
                            ctx,
                            extra={"completeness": completeness}
                        )
                        await self.report_progress(100, 100, ctx)
                        
                        # Update statistics
                        processing_time = time.time() - start_time
                        self.update_statistics(True, processing_time, completeness=completeness)
                        
                        return json_result
                    else:
                        await self.log_warning(
                            f"JSON schema incomplete ({completeness:.1f}%), probeer prompt parsing",
                            ctx,
                            extra={"completeness": completeness}
                        )
                
                await self.report_progress(50, 100, ctx)
                
                # JSON schema niet goed genoeg, probeer prompt parsing
                await self.log_info("Probeer prompt parsing als fallback", ctx)
                prompt_result = await self._extract_with_method(text, "prompt_parsing", ctx)
                
                if prompt_result:
                    _, completeness, _ = await self.validate_extracted_data(prompt_result, ctx)
                    await self.log_info(
                        f"Prompt parsing succesvol ({completeness:.1f}% compleet)",
                        ctx,
                        extra={"completeness": completeness}
                    )
                    await self.report_progress(100, 100, ctx)
                    
                    # Update statistics
                    processing_time = time.time() - start_time
                    self.update_statistics(True, processing_time, completeness=completeness)
                    
                    return prompt_result
                
                # Beide gefaald
                if json_result:
                    await self.log_warning("Beide methodes incomplete, gebruik JSON schema resultaat", ctx)
                    await self.report_progress(100, 100, ctx)
                    
                    processing_time = time.time() - start_time
                    self.update_statistics(True, processing_time)
                    
                    return json_result
                
                await self.log_error("Beide extractie methodes gefaald", ctx)
                await self.report_progress(100, 100, ctx)
                
                processing_time = time.time() - start_time
                self.update_statistics(False, processing_time)
                
                return None
            
            # Single method mode
            await self.report_progress(20, 100, ctx)
            result = await self._extract_with_method(text, method, ctx)
            await self.report_progress(100, 100, ctx)
            
            processing_time = time.time() - start_time
            
            if result:
                _, completeness, _ = await self.validate_extracted_data(result, ctx)
                self.update_statistics(True, processing_time, completeness=completeness)
            else:
                self.update_statistics(False, processing_time)
            
            return result
            
        except Exception as e:
            await self.log_error(f"Extractie fout: {e}", ctx, extra={"error": str(e)})
            await self.report_progress(100, 100, ctx)
            
            processing_time = time.time() - start_time
            self.update_statistics(False, processing_time)
            
            return None
    
    async def _extract_with_method(
        self,
        text: str,
        method: str,
        ctx: Optional[Context] = None
    ) -> Optional[CVData]:
        """Helper method voor extractie met specifieke methode."""
        
        try:
            prompt = self.get_extraction_prompt(text, method)
            
            await self.log_debug(f"Ollama aanroepen met {method} methode", ctx)
            
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
                await self.log_error("Geen JSON gevonden in response", ctx)
                return None
            
            # JSON parsen met reparatie
            parsed_data = self._parse_json_with_repair(json_str)
            
            if not parsed_data:
                return None
            
            # Valideren met Pydantic
            try:
                validated_data = CVData(**parsed_data)
                await self.log_info("CV data succesvol geëxtraheerd", ctx)
                return validated_data
            except ValidationError as e:
                await self.log_error(f"Pydantic validatie fout: {e}", ctx)
                return None
                
        except Exception as e:
            await self.log_error(f"Extractie fout: {e}", ctx)
            return None
    
    def _extract_json_from_response(self, response: str, method: str) -> Optional[str]:
        """Extract JSON from LLM response."""
        
        if method == "json_schema":
            return response
        
        # Prompt parsing: zoek JSON in response
        if "```json" in response:
            start_marker = "```json"
            end_marker = "```"
            start_idx = response.find(start_marker) + len(start_marker)
            end_idx = response.find(end_marker, start_idx)
            if start_idx != -1 and end_idx != -1:
                return response[start_idx:end_idx].strip()
        
        elif "```" in response:
            parts = response.split("```")
            if len(parts) >= 3:
                return parts[1].strip()
        
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            return response[json_start:json_end]
        
        return response.strip()
    
    def _parse_json_with_repair(self, json_str: str) -> Optional[Dict[str, Any]]:
        """Parse JSON met automatische reparatie van veelvoorkomende fouten."""
        
        try:
            return json_module.loads(json_str)
        except json_module.JSONDecodeError as e:
            logger.warning(f"JSON parsing fout: {e}, probeer reparatie...")
            
            repaired_json = json_str.strip()
            repaired_json = re.sub(r',\s*([}\]])', r'\1', repaired_json)
            
            open_braces = repaired_json.count('{')
            close_braces = repaired_json.count('}')
            open_brackets = repaired_json.count('[')
            close_brackets = repaired_json.count(']')
            
            if open_braces > close_braces:
                repaired_json += '}' * (open_braces - close_braces)
            if open_brackets > close_brackets:
                repaired_json += ']' * (open_brackets - close_brackets)
            
            repaired_json = re.sub(r',\s*([}\]])', r'\1', repaired_json)
            
            try:
                return json_module.loads(repaired_json)
            except json_module.JSONDecodeError:
                logger.error("JSON reparatie gefaald")
                return None
    
    # ==================== MERGING ====================
    
    async def merge_partial_results(
        self, 
        partial_results: List[BaseModel],
        ctx: Optional[Context] = None
    ) -> Optional[CVData]:
        """
        Merge partiële CV resultaten.
        
        Combineert werk ervaring, opleiding en skills.
        """
        await self.log_info(f"Mergen van {len(partial_results)} partiële resultaten", ctx)
        
        if not partial_results:
            await self.log_error("Geen partiële resultaten om te mergen", ctx)
            return None
        
        # Filter alleen CVData objecten
        cv_results = [r for r in partial_results if isinstance(r, CVData)]
        
        if not cv_results:
            await self.log_error("Geen CV data gevonden in resultaten", ctx)
            return None
        
        # Start met eerste resultaat
        merged = cv_results[0].model_copy()
        
        # Merge work experience
        all_experiences = []
        for result in cv_results:
            if result.work_experience:
                all_experiences.extend(result.work_experience)
        merged.work_experience = self._deduplicate_work_experience(all_experiences)
        
        # Merge education
        all_education = []
        for result in cv_results:
            if result.education:
                all_education.extend(result.education)
        merged.education = self._deduplicate_education(all_education)
        
        # Merge skills
        all_skills = []
        for result in cv_results:
            if result.skills:
                all_skills.extend(result.skills)
        merged.skills = self._deduplicate_skills(all_skills)
        
        # Voor andere velden: eerste niet-lege waarde
        for result in cv_results[1:]:
            if not merged.email and result.email:
                merged.email = result.email
            if not merged.phone_number and result.phone_number:
                merged.phone_number = result.phone_number
            if not merged.summary and result.summary:
                merged.summary = result.summary
        
        await self.log_info(
            f"Merge compleet: {len(merged.work_experience)} jobs, "
            f"{len(merged.education)} education, {len(merged.skills)} skills",
            ctx,
            extra={
                "work_experience_count": len(merged.work_experience),
                "education_count": len(merged.education),
                "skills_count": len(merged.skills)
            }
        )
        
        return merged
    
    def _deduplicate_work_experience(
        self, 
        experiences: List[WorkExperience], 
        threshold: int = 85
    ) -> List[WorkExperience]:
        """Ontdubbel work experience met fuzzy matching."""
        
        if not experiences:
            return []
        
        unique_experiences: List[WorkExperience] = []
        
        for exp in experiences:
            is_duplicate = False
            
            for unique_exp in unique_experiences:
                str1 = f"{exp.job_title} {exp.company}".lower()
                str2 = f"{unique_exp.job_title} {unique_exp.company}".lower()
                
                if fuzz.ratio(str1, str2) > threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_experiences.append(exp)
        
        return unique_experiences
    
    def _deduplicate_education(
        self, 
        education: List[Education], 
        threshold: int = 85
    ) -> List[Education]:
        """Ontdubbel education met fuzzy matching."""
        
        if not education:
            return []
        
        unique_education: List[Education] = []
        
        for edu in education:
            is_duplicate = False
            
            for unique_edu in unique_education:
                str1 = f"{edu.degree} {edu.institution}".lower()
                str2 = f"{unique_edu.degree} {unique_edu.institution}".lower()
                
                if fuzz.ratio(str1, str2) > threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_education.append(edu)
        
        return unique_education
    
    def _deduplicate_skills(
        self, 
        skills: List[str], 
        threshold: int = 85
    ) -> List[str]:
        """Ontdubbel skills met fuzzy matching."""
        
        if not skills:
            return []
        
        unique_skills: List[str] = []
        
        for skill in skills:
            is_duplicate = False
            
            for unique_skill in unique_skills:
                if fuzz.ratio(skill.lower(), unique_skill.lower()) > threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_skills.append(skill)
        
        return unique_skills
    
    # ==================== VALIDATIE ====================
    
    async def validate_extracted_data(
        self, 
        data: BaseModel,
        ctx: Optional[Context] = None
    ) -> Tuple[bool, float, List[str]]:
        """
        Valideer CV data en bereken completeness.
        """
        if not isinstance(data, CVData):
            return False, 0.0, ["Data is geen CVData object"]
        
        issues = []
        
        # Required fields check
        if not data.full_name:
            issues.append("full_name is leeg")
        if not data.summary:
            issues.append("summary is leeg")
        
        # Work experience check
        if not data.work_experience or len(data.work_experience) == 0:
            issues.append("Geen work experience gevonden")
        
        # Education check
        if not data.education or len(data.education) == 0:
            issues.append("Geen education gevonden")
        
        # Skills check
        if not data.skills or len(data.skills) == 0:
            issues.append("Geen skills gevonden")
        
        # Bereken completeness
        data_dict = data.model_dump()
        total_fields = 0
        filled_fields = 0
        
        for key, value in data_dict.items():
            if key in ["work_experience", "education", "skills"]:
                total_fields += 1
                if isinstance(value, list) and len(value) > 0:
                    filled_fields += 1
            else:
                total_fields += 1
                if value is not None and value != "":
                    filled_fields += 1
        
        completeness = (filled_fields / total_fields * 100) if total_fields > 0 else 0.0
        is_valid = len(issues) == 0
        
        if ctx:
            await self.log_info(
                f"Validatie: {completeness:.1f}% compleet, {len(issues)} issues",
                ctx,
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
        data: BaseModel,
        ctx: Optional[Context] = None
    ) -> Dict[str, Any]:
        """
        Generate CV-specific metrics.
        """
        if not isinstance(data, CVData):
            return {}
        
        # Bereken totaal jaren ervaring (simpele schatting)
        years_experience = len(data.work_experience) * 2  # Gemiddeld 2 jaar per job
        
        metrics = {
            "work_experience_count": len(data.work_experience) if data.work_experience else 0,
            "education_count": len(data.education) if data.education else 0,
            "skills_count": len(data.skills) if data.skills else 0,
            "has_email": bool(data.email),
            "has_phone": bool(data.phone_number),
            "estimated_years_experience": years_experience,
            "has_summary": bool(data.summary),
        }
        
        if ctx:
            await self.log_debug("Custom metrics gegenereerd", ctx, extra=metrics)
        
        return metrics

