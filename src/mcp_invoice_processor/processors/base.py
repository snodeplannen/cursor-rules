"""
Base interface voor document processors.

Definieert de abstracte interface die alle document processors moeten implementeren.
Volgt FastMCP best practices voor Context, Resources, Annotations en Progress.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Set, Type, Tuple, AsyncIterator
from enum import Enum

from pydantic import BaseModel
from fastmcp import Context

logger = logging.getLogger(__name__)


class ProcessingStage(str, Enum):
    """Stages van document processing voor status updates."""
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    VALIDATION = "validation"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStatus:
    """Realtime status van document processing."""
    
    def __init__(self):
        self.stage: ProcessingStage = ProcessingStage.CLASSIFICATION
        self.progress: float = 0.0  # 0-100
        self.message: str = ""
        self.items_processed: int = 0
        self.items_total: int = 0
        self.start_time: float = 0.0
        self.errors: List[str] = []


class BaseDocumentProcessor(ABC):
    """
    Basis interface voor document processors.
    
    Elke processor implementeert alle functionaliteit voor één specifiek documenttype:
    - Classificatie met confidence scores
    - Data extractie met alle methoden (json_schema, prompt_parsing, hybrid)
    - Realtime status updates via FastMCP Context
    - Gestructureerde logging met metadata
    - Performance metrics en statistics
    - MCP tool metadata en documentatie
    
    References:
        - https://gofastmcp.com/servers/context
        - https://gofastmcp.com/servers/resources
        - https://gofastmcp.com/servers/tools
        - https://gofastmcp.com/servers/progress
    """
    
    def __init__(self):
        """Initialiseer processor met statistics tracking."""
        self._stats = {
            "total_processed": 0,
            "total_successful": 0,
            "total_failed": 0,
            "total_processing_time": 0.0,
            "avg_confidence": 0.0,
            "avg_completeness": 0.0
        }
    
    # ==================== METADATA ====================
    
    @property
    @abstractmethod
    def document_type(self) -> str:
        """
        Het documenttype dat deze processor verwerkt.
        
        Returns:
            str: Document type identifier (bijv. "invoice", "cv", "receipt")
        """
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        Menselijke leesbare naam voor dit documenttype.
        
        Returns:
            str: Display naam (bijv. "Factuur", "Curriculum Vitae", "Kassabon")
        """
        pass
    
    @property
    @abstractmethod
    def tool_name(self) -> str:
        """
        Naam van de MCP tool voor dit documenttype.
        
        Returns:
            str: Tool naam (bijv. "process_invoice", "process_cv")
        """
        pass
    
    @property
    @abstractmethod
    def tool_description(self) -> str:
        """
        Beschrijving voor MCP tool (gebruikt door LLM voor tool selectie).
        
        Returns:
            str: Gedetailleerde beschrijving van wat deze tool doet
        """
        pass
    
    @property
    def tool_metadata(self) -> Dict[str, Any]:
        """
        Volledige MCP tool metadata volgens FastMCP best practices.
        
        Bevat annotations voor hints aan de LLM over tool gedrag.
        
        Returns:
            Dict: Complete tool metadata voor MCP registratie
            
        References:
            - https://gofastmcp.com/servers/tools
            - https://gofastmcp.com/servers/context
        """
        from fastmcp.utilities.types import Annotations
        
        return {
            "name": self.tool_name,
            "description": self.tool_description,
            "document_type": self.document_type,
            "display_name": self.display_name,
            "supported_methods": ["json_schema", "prompt_parsing", "hybrid"],
            "supported_formats": [".txt", ".pdf"],
            "annotations": Annotations(
                readOnlyHint=True,  # Tools lezen documenten, wijzigen ze niet
                idempotentHint=True  # Herhaald aanroepen heeft zelfde effect
            ),  # type: ignore[call-arg]
            "meta": {
                "category": "document_processing",
                "processor_type": self.document_type,
                "version": "1.0.0"
            }
        }
    
    # ==================== CLASSIFICATIE ====================
    
    @property
    @abstractmethod
    def classification_keywords(self) -> Set[str]:
        """
        Keywords voor auto-detectie van dit documenttype.
        
        Returns:
            Set[str]: Set van keywords (lowercase) die indiceren dit documenttype
        """
        pass
    
    @abstractmethod
    async def classify(
        self, 
        text: str, 
        ctx: Optional[Context] = None
    ) -> float:
        """
        Bereken confidence score (0-100) dat deze tekst dit documenttype is.
        
        Deze methode analyseert de tekst en retourneert een confidence score.
        Hogere score = meer zekerheid dat dit het juiste documenttype is.
        
        Args:
            text: Document tekst om te classificeren
            ctx: FastMCP context voor logging (optioneel)
            
        Returns:
            float: Confidence score 0-100
            
        Example:
            >>> processor = InvoiceProcessor()
            >>> score = await processor.classify("Factuur #123...", ctx)
            >>> print(f"Confidence: {score}%")
        """
        pass
    
    # ==================== DATA MODELLEN ====================
    
    @property
    @abstractmethod
    def data_model(self) -> Type[BaseModel]:
        """
        Het Pydantic model voor geëxtraheerde data van dit documenttype.
        
        Returns:
            Type[BaseModel]: Pydantic model class
        """
        pass
    
    @abstractmethod
    def get_json_schema(self) -> Dict[str, Any]:
        """
        Genereer JSON schema voor Ollama structured output.
        
        Returns:
            Dict: JSON schema compatible met Ollama format parameter
        """
        pass
    
    # ==================== PROMPTS ====================
    
    @abstractmethod
    def get_extraction_prompt(
        self, 
        text: str, 
        method: str  # "json_schema", "prompt_parsing", "hybrid"
    ) -> str:
        """
        Genereer LLM prompt voor data extractie.
        
        Args:
            text: Document tekst om te verwerken
            method: Extractie methode ("json_schema", "prompt_parsing", "hybrid")
            
        Returns:
            str: Complete prompt voor LLM
        """
        pass
    
    # ==================== EXTRACTIE (ASYNC) ====================
    
    @abstractmethod
    async def extract(
        self,
        text: str,
        ctx: Optional[Context] = None,
        method: str = "hybrid"
    ) -> Optional[BaseModel]:
        """
        Extraheer gestructureerde data uit tekst met realtime status updates.
        
        Deze methode:
        1. Logt start via ctx.info() met structured logging
        2. Stuurt progress updates via ctx.report_progress()
        3. Extraheert data via Ollama
        4. Valideert resultaat
        5. Logt completion met metrics
        
        Args:
            text: Document tekst om te verwerken
            ctx: FastMCP context voor logging en progress (optioneel maar aanbevolen)
            method: Extractie methode ("json_schema", "prompt_parsing", "hybrid")
            
        Returns:
            Optional[BaseModel]: Geëxtraheerde en gevalideerde data, of None bij fout
            
        Example:
            >>> processor = InvoiceProcessor()
            >>> data = await processor.extract(text, ctx, method="hybrid")
            >>> if data:
            ...     print(f"Extracted: {data.model_dump()}")
        """
        pass
    
    async def extract_with_status_stream(
        self,
        text: str,
        ctx: Optional[Context] = None,
        method: str = "hybrid"
    ) -> AsyncIterator[Tuple[ProcessingStatus, Optional[BaseModel]]]:
        """
        Extraheer data met realtime status streaming.
        
        Yields status updates tijdens processing, eindigt met final result.
        
        Args:
            text: Document tekst
            ctx: FastMCP context voor logging
            method: Extractie methode
            
        Yields:
            Tuple[ProcessingStatus, Optional[BaseModel]]: (status, data)
            - Tijdens processing: (status, None)
            - Bij completion: (status, extracted_data)
            
        Example:
            >>> async for status, data in processor.extract_with_status_stream(text, ctx):
            ...     print(f"{status.stage}: {status.progress}%")
            ...     if data:
            ...         print(f"Completed: {data}")
        """
        status = ProcessingStatus()
        status.start_time = time.time()
        
        try:
            # Stage 1: Classificatie
            status.stage = ProcessingStage.CLASSIFICATION
            status.progress = 10.0
            status.message = "Classificeren documenttype..."
            yield (status, None)
            
            # Stage 2: Extractie
            status.stage = ProcessingStage.EXTRACTION
            status.progress = 30.0
            status.message = "Extraheren gestructureerde data..."
            yield (status, None)
            
            # Voer extractie uit
            data = await self.extract(text, ctx, method)
            
            if data:
                # Stage 3: Validatie
                status.stage = ProcessingStage.VALIDATION
                status.progress = 80.0
                status.message = "Valideren geëxtraheerde data..."
                yield (status, None)
                
                # Valideer
                is_valid, completeness, issues = await self.validate_extracted_data(data, ctx)
                
                # Stage 4: Completed
                status.stage = ProcessingStage.COMPLETED
                status.progress = 100.0
                status.message = f"Verwerking voltooid ({completeness:.1f}% compleet)"
                status.items_processed = 1
                status.items_total = 1
                yield (status, data)
            else:
                # Failed
                status.stage = ProcessingStage.FAILED
                status.progress = 100.0
                status.message = "Extractie mislukt"
                status.errors.append("Geen data geëxtraheerd")
                yield (status, None)
                
        except Exception as e:
            status.stage = ProcessingStage.FAILED
            status.progress = 100.0
            status.message = f"Fout: {str(e)}"
            status.errors.append(str(e))
            yield (status, None)
    
    # ==================== MERGING (ASYNC) ====================
    
    @abstractmethod
    async def merge_partial_results(
        self, 
        partial_results: List[BaseModel],
        ctx: Optional[Context] = None
    ) -> Optional[BaseModel]:
        """
        Voeg partiële extractie resultaten samen (voor gechunkte documenten).
        
        Args:
            partial_results: List van partiële data extracties
            ctx: FastMCP context voor logging
            
        Returns:
            Optional[BaseModel]: Samengevoegd resultaat
        """
        pass
    
    # ==================== VALIDATIE (ASYNC) ====================
    
    @abstractmethod
    async def validate_extracted_data(
        self, 
        data: BaseModel,
        ctx: Optional[Context] = None
    ) -> Tuple[bool, float, List[str]]:
        """
        Valideer en beoordeel kwaliteit van geëxtraheerde data.
        
        Args:
            data: Geëxtraheerde data om te valideren
            ctx: FastMCP context voor logging
            
        Returns:
            Tuple[bool, float, List[str]]: 
                - is_valid: Of de data valide is
                - completeness_score: Percentage compleetheid (0-100)
                - issues: List van gevonden problemen/waarschuwingen
        """
        pass
    
    # ==================== LOGGING HELPERS (ASYNC) ====================
    
    async def log_info(
        self, 
        message: str, 
        ctx: Optional[Context] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log informatie bericht met structured data.
        
        Args:
            message: Log bericht
            ctx: FastMCP context
            extra: Extra structured data voor logging
        """
        if ctx:
            log_extra = {
                "processor": self.document_type,
                "tool": self.tool_name,
                **(extra or {})
            }
            await ctx.info(message, extra=log_extra)
    
    async def log_debug(
        self, 
        message: str, 
        ctx: Optional[Context] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log debug bericht."""
        if ctx:
            log_extra = {
                "processor": self.document_type,
                "tool": self.tool_name,
                **(extra or {})
            }
            await ctx.debug(message, extra=log_extra)
    
    async def log_warning(
        self, 
        message: str, 
        ctx: Optional[Context] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log waarschuwing."""
        if ctx:
            log_extra = {
                "processor": self.document_type,
                "tool": self.tool_name,
                **(extra or {})
            }
            await ctx.warning(message, extra=log_extra)
    
    async def log_error(
        self, 
        message: str, 
        ctx: Optional[Context] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log error bericht."""
        if ctx:
            log_extra = {
                "processor": self.document_type,
                "tool": self.tool_name,
                **(extra or {})
            }
            await ctx.error(message, extra=log_extra)
    
    async def report_progress(
        self,
        progress: float,
        total: Optional[float] = None,
        ctx: Optional[Context] = None
    ) -> None:
        """
        Rapporteer progress naar client volgens FastMCP best practices.
        
        Progress wordt gebruikt door clients om voortgang te tonen.
        Gebruik dit voor langlopende operaties.
        
        Args:
            progress: Huidige progress waarde
            total: Totale waarde (optioneel, default 100 voor percentage)
            ctx: FastMCP context
            
        References:
            - https://gofastmcp.com/servers/progress
        """
        if ctx:
            # FastMCP report_progress voor realtime updates
            await ctx.report_progress(progress=progress, total=total or 100.0)
    
    # ==================== METRICS & STATISTICS ====================
    
    def update_statistics(
        self,
        success: bool,
        processing_time: float,
        confidence: Optional[float] = None,
        completeness: Optional[float] = None
    ) -> None:
        """
        Update processor statistics na verwerking.
        
        Args:
            success: Of verwerking succesvol was
            processing_time: Verwerkingstijd in seconden
            confidence: Classificatie confidence score
            completeness: Data completeness score
        """
        self._stats["total_processed"] += 1
        
        if success:
            self._stats["total_successful"] += 1
        else:
            self._stats["total_failed"] += 1
        
        self._stats["total_processing_time"] += processing_time
        
        if confidence is not None:
            # Rolling average van confidence
            n = self._stats["total_processed"]
            current_avg = self._stats["avg_confidence"]
            self._stats["avg_confidence"] = (current_avg * (n - 1) + confidence) / n
        
        if completeness is not None:
            # Rolling average van completeness
            n = self._stats["total_successful"]
            if n > 0:
                current_avg = self._stats["avg_completeness"]
                self._stats["avg_completeness"] = (current_avg * (n - 1) + completeness) / n
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Haal processor statistics op.
        
        Returns:
            Dict: Statistics van deze processor
        """
        stats = self._stats.copy()
        
        # Bereken afgeleide statistieken
        if stats["total_processed"] > 0:
            stats["success_rate"] = (
                stats["total_successful"] / stats["total_processed"] * 100
            )
            stats["avg_processing_time"] = (
                stats["total_processing_time"] / stats["total_processed"]
            )
        else:
            stats["success_rate"] = 0.0
            stats["avg_processing_time"] = 0.0
        
        # Voeg metadata toe
        stats["processor_type"] = self.document_type  # type: ignore[assignment]
        stats["display_name"] = self.display_name  # type: ignore[assignment]
        
        return stats
    
    @abstractmethod
    async def get_custom_metrics(
        self, 
        data: BaseModel,
        ctx: Optional[Context] = None
    ) -> Dict[str, Any]:
        """
        Genereer processor-specifieke metrics.
        
        Args:
            data: Geëxtraheerde data
            ctx: FastMCP context voor logging
            
        Returns:
            Dict: Custom metrics specifiek voor dit documenttype
            
        Example (Invoice):
            {
                "total_amount": 1234.56,
                "line_items_count": 5,
                "has_vat": True,
                "currency": "EUR"
            }
        """
        pass
    
    # ==================== MCP RESOURCES ====================
    
    def get_resource_uris(self) -> Dict[str, str]:
        """
        Definieer MCP Resources URIs voor dit processor type.
        
        Resources exposen processor data/statistics via MCP protocol.
        
        Returns:
            Dict[str, str]: Mapping van resource naam naar URI
            
        References:
            - https://gofastmcp.com/servers/resources
        """
        doc_type = self.document_type
        return {
            "statistics": f"stats://{doc_type}",
            "schema": f"schema://{doc_type}",
            "keywords": f"keywords://{doc_type}"
        }
    
    async def get_statistics_resource(self, ctx: Optional[Context] = None) -> Dict[str, Any]:
        """
        Resource: Haal processor statistics op.
        
        Deze methode wordt aangeroepen als MCP resource voor stats://{document_type}
        
        Args:
            ctx: FastMCP context
            
        Returns:
            Dict: Processor statistics
        """
        if ctx:
            await ctx.debug(f"Ophalen statistics voor {self.display_name}")
        
        return self.get_statistics()
    
    async def get_schema_resource(self, ctx: Optional[Context] = None) -> Dict[str, Any]:
        """
        Resource: Haal JSON schema op voor dit documenttype.
        
        Deze methode wordt aangeroepen als MCP resource voor schema://{document_type}
        
        Args:
            ctx: FastMCP context
            
        Returns:
            Dict: JSON schema van data model
        """
        if ctx:
            await ctx.debug(f"Ophalen schema voor {self.display_name}")
        
        return self.get_json_schema()
    
    async def get_keywords_resource(self, ctx: Optional[Context] = None) -> Dict[str, Any]:
        """
        Resource: Haal classificatie keywords op.
        
        Deze methode wordt aangeroepen als MCP resource voor keywords://{document_type}
        
        Args:
            ctx: FastMCP context
            
        Returns:
            Dict: Keywords voor classificatie
        """
        if ctx:
            await ctx.debug(f"Ophalen keywords voor {self.display_name}")
        
        return {
            "document_type": self.document_type,
            "display_name": self.display_name,
            "keywords": sorted(list(self.classification_keywords))
        }

