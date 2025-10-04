# 🔄 Refactoring Plan: Modulaire Document Processor Architectuur

## 📋 Doel

Transformeren van de huidige monolithische document processor naar een modulaire, uitbreidbare architectuur waarbij elk documenttype zijn eigen zelfstandige processor heeft.

## 🎯 Design Principes

1. **Single Responsibility**: Elke processor is verantwoordelijk voor één documenttype
2. **Open/Closed**: Uitbreidbaar zonder bestaande code te wijzigen
3. **Dependency Inversion**: Code hangt af van abstracties (interfaces), niet van concrete implementaties
4. **Plugin Architecture**: Nieuwe documenttypes toevoegen door nieuwe processor toe te voegen

## 🏗️ Architectuur Overzicht

### BaseDocumentProcessor (Abstract Base Class)

Definieert de interface die alle processors moeten implementeren.

**🔑 Kern Principes:**
- ✅ **Volledig Async**: Alle I/O operaties zijn async voor maximale performance
- ✅ **FastMCP Context**: Gebruik `Context` voor logging, progress, en status updates
- ✅ **Realtime Status**: Stream updates naar client tijdens verwerking
- ✅ **Centrale Logging**: Gestructureerde logging met metadata via Context
- ✅ **Statistics Tracking**: Automatische metrics en performance tracking

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Set, Type, Tuple, AsyncIterator
from pydantic import BaseModel
from fastmcp import Context
from enum import Enum


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
        from fastmcp import Annotations
        
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
            ),
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
        stats["processor_type"] = self.document_type
        stats["display_name"] = self.display_name
        
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
            "prompts": f"prompts://{doc_type}",
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
```

### ProcessorRegistry (Factory Pattern)

Centraal register van alle beschikbare processors met async classificatie.

```python
import asyncio
from typing import Dict, Optional, List, Tuple


class ProcessorRegistry:
    """
    Registry voor document processors met async support.
    
    Beheert alle geregistreerde processors en voorziet in:
    - Processor registratie en lookup
    - Async document classificatie met confidence scoring
    - Aggregated statistics van alle processors
    - MCP tool metadata generatie
    """
    
    def __init__(self):
        """Initialiseer registry."""
        self._processors: Dict[str, BaseDocumentProcessor] = {}
    
    def register(self, processor: BaseDocumentProcessor) -> None:
        """
        Registreer een nieuwe processor.
        
        Args:
            processor: Document processor om te registreren
            
        Raises:
            ValueError: Als een processor met dit type al geregistreerd is
        """
        doc_type = processor.document_type
        
        if doc_type in self._processors:
            raise ValueError(
                f"Processor voor type '{doc_type}' is al geregistreerd. "
                f"Gebruik unregister() eerst om te vervangen."
            )
        
        self._processors[doc_type] = processor
        logger.info(
            f"✅ Processor geregistreerd: {processor.display_name} ({doc_type})",
            extra={
                "processor_type": doc_type,
                "tool_name": processor.tool_name
            }
        )
    
    def unregister(self, doc_type: str) -> bool:
        """
        Verwijder een processor.
        
        Args:
            doc_type: Document type om te verwijderen
            
        Returns:
            bool: True als verwijderd, False als niet gevonden
        """
        if doc_type in self._processors:
            processor = self._processors.pop(doc_type)
            logger.info(f"❌ Processor verwijderd: {processor.display_name}")
            return True
        return False
    
    def get_processor(self, doc_type: str) -> Optional[BaseDocumentProcessor]:
        """
        Haal processor op voor documenttype.
        
        Args:
            doc_type: Document type identifier
            
        Returns:
            Optional[BaseDocumentProcessor]: Processor of None als niet gevonden
        """
        return self._processors.get(doc_type)
    
    async def classify_document(
        self, 
        text: str,
        ctx: Optional[Context] = None
    ) -> Tuple[str, float, Optional[BaseDocumentProcessor]]:
        """
        Classificeer document door alle processors async te proberen.
        
        Alle processors worden parallel uitgevoerd voor snelheid.
        De processor met de hoogste confidence score wint.
        
        Args:
            text: Document tekst om te classificeren
            ctx: FastMCP context voor logging
            
        Returns:
            Tuple[str, float, Optional[BaseDocumentProcessor]]: 
                (documenttype, confidence_score, processor)
                
        Example:
            >>> registry = ProcessorRegistry()
            >>> doc_type, confidence, processor = await registry.classify_document(text, ctx)
            >>> print(f"Type: {doc_type}, Confidence: {confidence}%")
        """
        if not self._processors:
            logger.warning("Geen processors geregistreerd in registry")
            return "unknown", 0.0, None
        
        if ctx:
            await ctx.debug(
                f"Classificeren document met {len(self._processors)} processors...",
                extra={"processor_count": len(self._processors)}
            )
        
        # Voer alle classificaties parallel uit voor snelheid
        tasks = [
            processor.classify(text, ctx) 
            for processor in self._processors.values()
        ]
        
        try:
            scores = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Fout bij parallel classificeren: {e}")
            if ctx:
                await ctx.error(f"Classificatie fout: {e}")
            return "unknown", 0.0, None
        
        # Zoek beste score
        best_score = 0.0
        best_processor = None
        
        for processor, score in zip(self._processors.values(), scores):
            # Skip processors die een exception gaven
            if isinstance(score, Exception):
                logger.error(
                    f"Processor {processor.document_type} gaf fout: {score}",
                    extra={"processor": processor.document_type}
                )
                continue
            
            if ctx:
                await ctx.debug(
                    f"{processor.display_name}: {score:.1f}% confidence",
                    extra={
                        "processor": processor.document_type,
                        "confidence": score
                    }
                )
            
            if score > best_score:
                best_score = score
                best_processor = processor
        
        if best_processor:
            if ctx:
                await ctx.info(
                    f"📋 Beste match: {best_processor.display_name} ({best_score:.1f}% confidence)",
                    extra={
                        "document_type": best_processor.document_type,
                        "confidence": best_score
                    }
                )
            return best_processor.document_type, best_score, best_processor
        
        if ctx:
            await ctx.warning("Geen processor kon documenttype bepalen")
        
        return "unknown", 0.0, None
    
    def get_all_processors(self) -> List[BaseDocumentProcessor]:
        """
        Haal alle geregistreerde processors op.
        
        Returns:
            List[BaseDocumentProcessor]: Lijst van alle processors
        """
        return list(self._processors.values())
    
    def get_processor_types(self) -> List[str]:
        """
        Haal alle geregistreerde documenttypes op.
        
        Returns:
            List[str]: Lijst van document type identifiers
        """
        return list(self._processors.keys())
    
    def get_all_statistics(self) -> Dict[str, Any]:
        """
        Haal gecombineerde statistics van alle processors op.
        
        Returns:
            Dict: Aggregated statistics van alle processors
        """
        all_stats = {
            "total_processors": len(self._processors),
            "processor_types": self.get_processor_types(),
            "processors": {}
        }
        
        # Verzamel stats per processor
        total_processed = 0
        total_successful = 0
        total_failed = 0
        
        for doc_type, processor in self._processors.items():
            processor_stats = processor.get_statistics()
            all_stats["processors"][doc_type] = processor_stats
            
            total_processed += processor_stats["total_processed"]
            total_successful += processor_stats["total_successful"]
            total_failed += processor_stats["total_failed"]
        
        # Bereken globale statistieken
        all_stats["global"] = {
            "total_documents_processed": total_processed,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "global_success_rate": (
                (total_successful / total_processed * 100) 
                if total_processed > 0 else 0.0
            )
        }
        
        return all_stats
    
    def get_tool_metadata_list(self) -> List[Dict[str, Any]]:
        """
        Genereer MCP tool metadata voor alle processors.
        
        Gebruikt voor automatische MCP tool registratie.
        
        Returns:
            List[Dict]: Lijst van tool metadata voor elke processor
        """
        return [
            processor.tool_metadata 
            for processor in self._processors.values()
        ]


# Global singleton registry instance
_global_registry: Optional[ProcessorRegistry] = None


def get_registry() -> ProcessorRegistry:
    """
    Haal de globale processor registry op (singleton pattern).
    
    Returns:
        ProcessorRegistry: De globale registry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ProcessorRegistry()
    return _global_registry


def register_processor(processor: BaseDocumentProcessor) -> None:
    """
    Convenience functie om processor bij globale registry te registreren.
    
    Args:
        processor: Processor om te registreren
    """
    registry = get_registry()
    registry.register(processor)


# ==================== MCP RESOURCE REGISTRATION ====================

def register_processor_resources(mcp: FastMCP, processor: BaseDocumentProcessor) -> None:
    """
    Registreer alle MCP resources voor een processor.
    
    Dit maakt processor data beschikbaar via MCP Resources protocol:
    - stats://{doc_type} - Processor statistics
    - schema://{doc_type} - JSON schema van data model
    - keywords://{doc_type} - Classificatie keywords
    
    Args:
        mcp: FastMCP server instance
        processor: Processor om resources voor te registreren
        
    References:
        - https://gofastmcp.com/servers/resources
    
    Example:
        >>> mcp = FastMCP("DocumentProcessor")
        >>> invoice_processor = InvoiceProcessor()
        >>> register_processor_resources(mcp, invoice_processor)
    """
    from fastmcp import Annotations
    
    doc_type = processor.document_type
    display_name = processor.display_name
    
    # Resource 1: Statistics
    @mcp.resource(
        uri=f"stats://{doc_type}",
        name=f"{display_name} Statistics",
        description=f"Processor statistics voor {display_name} documenten",
        mime_type="application/json",
        annotations=Annotations(
            readOnlyHint=True,
            idempotentHint=True
        ),
        meta={
            "processor_type": doc_type,
            "resource_type": "statistics"
        }
    )
    async def get_stats(ctx: Context) -> Dict[str, Any]:
        return await processor.get_statistics_resource(ctx)
    
    # Resource 2: JSON Schema
    @mcp.resource(
        uri=f"schema://{doc_type}",
        name=f"{display_name} Schema",
        description=f"JSON schema voor {display_name} data extractie",
        mime_type="application/json",
        annotations=Annotations(
            readOnlyHint=True,
            idempotentHint=True
        ),
        meta={
            "processor_type": doc_type,
            "resource_type": "schema"
        }
    )
    async def get_schema(ctx: Context) -> Dict[str, Any]:
        return await processor.get_schema_resource(ctx)
    
    # Resource 3: Keywords
    @mcp.resource(
        uri=f"keywords://{doc_type}",
        name=f"{display_name} Keywords",
        description=f"Classificatie keywords voor {display_name} detectie",
        mime_type="application/json",
        annotations=Annotations(
            readOnlyHint=True,
            idempotentHint=True
        ),
        meta={
            "processor_type": doc_type,
            "resource_type": "keywords"
        }
    )
    async def get_keywords(ctx: Context) -> Dict[str, Any]:
        return await processor.get_keywords_resource(ctx)
    
    logger.info(
        f"✅ MCP Resources geregistreerd voor {display_name}",
        extra={
            "processor_type": doc_type,
            "resources": ["stats", "schema", "keywords"]
        }
    )


def register_all_processor_resources(mcp: FastMCP) -> None:
    """
    Registreer MCP resources voor alle processors in de registry.
    
    Args:
        mcp: FastMCP server instance
        
    Example:
        >>> mcp = FastMCP("DocumentProcessor")
        >>> register_processor(InvoiceProcessor())
        >>> register_processor(CVProcessor())
        >>> register_all_processor_resources(mcp)
    """
    registry = get_registry()
    
    for processor in registry.get_all_processors():
        register_processor_resources(mcp, processor)
    
    # Registreer ook een global statistics resource
    @mcp.resource(
        uri="stats://all",
        name="All Processors Statistics",
        description="Gecombineerde statistics van alle document processors",
        mime_type="application/json",
        annotations=Annotations(
            readOnlyHint=True,
            idempotentHint=True
        ),
        meta={
            "resource_type": "global_statistics"
        }
    )
    async def get_all_stats(ctx: Context) -> Dict[str, Any]:
        await ctx.debug("Ophalen global statistics")
        return registry.get_all_statistics()
```

## 🎯 FastMCP Best Practices Implementatie

### Context Usage

Volgens [FastMCP Context documentatie](https://gofastmcp.com/servers/context):

```python
from fastmcp import Context

async def extract(self, text: str, ctx: Optional[Context] = None, method: str = "hybrid"):
    """Alle processor methods accepteren optionele Context parameter."""
    
    # 1. Structured Logging met extra metadata
    if ctx:
        await ctx.info(
            "Starting extraction",
            extra={
                "processor": self.document_type,
                "method": method,
                "text_length": len(text)
            }
        )
    
    # 2. Progress reporting
    if ctx:
        await ctx.report_progress(progress=25.0, total=100.0)
    
    # 3. Error handling met context
    try:
        result = await self._do_extraction(text)
    except Exception as e:
        if ctx:
            await ctx.error(f"Extraction failed: {e}", extra={"error_type": type(e).__name__})
        raise
    
    return result
```

### Resources met Annotations

Volgens [FastMCP Resources documentatie](https://gofastmcp.com/servers/resources):

```python
from fastmcp import FastMCP, Context, Annotations

@mcp.resource(
    uri=f"stats://invoice",
    name="Invoice Statistics",
    description="Statistics voor invoice processing",
    mime_type="application/json",
    annotations=Annotations(
        readOnlyHint=True,      # Resource wijzigt geen data
        idempotentHint=True     # Herhaald lezen heeft geen side effects
    ),
    meta={
        "processor_type": "invoice",
        "version": "1.0.0"
    }
)
async def get_invoice_stats(ctx: Context) -> dict:
    """Async resource met Context parameter."""
    await ctx.debug("Fetching invoice statistics")
    return processor.get_statistics()
```

### Tools met Annotations

Volgens [FastMCP Tools documentatie](https://gofastmcp.com/servers/tools):

```python
@mcp.tool(
    annotations=Annotations(
        readOnlyHint=True,      # Tool wijzigt geen externe state
        idempotentHint=True     # Herhaalde calls met zelfde input → zelfde output
    )
)
async def process_invoice(text: str, ctx: Context, method: str = "hybrid") -> dict:
    """
    Process een invoice document.
    
    Args:
        text: De invoice tekst
        ctx: FastMCP context voor logging en progress
        method: Extractie methode (json_schema, prompt_parsing, hybrid)
        
    Returns:
        dict: Geëxtraheerde invoice data
    """
    await ctx.info("Processing invoice document")
    
    # Gebruik registry om processor op te halen
    registry = get_registry()
    doc_type, confidence, processor = await registry.classify_document(text, ctx)
    
    if processor:
        result = await processor.extract(text, ctx, method)
        return result.model_dump() if result else {"error": "Extraction failed"}
    
    return {"error": "No suitable processor found"}
```

### Progress Reporting

Volgens [FastMCP Progress documentatie](https://gofastmcp.com/servers/progress):

```python
async def extract_with_progress(self, text: str, ctx: Context):
    """Multi-stage processing met progress updates."""
    
    # Stage 1: Classification (0-20%)
    await ctx.report_progress(progress=0, total=100)
    await ctx.info("Classificeren document...")
    doc_type = await self.classify(text, ctx)
    await ctx.report_progress(progress=20, total=100)
    
    # Stage 2: Extraction (20-80%)
    await ctx.info("Extractie starten...")
    await ctx.report_progress(progress=20, total=100)
    
    result = await self._extract_data(text, ctx)
    
    await ctx.report_progress(progress=80, total=100)
    
    # Stage 3: Validation (80-100%)
    await ctx.info("Valideren resultaat...")
    is_valid, completeness, issues = await self.validate_extracted_data(result, ctx)
    await ctx.report_progress(progress=100, total=100)
    
    return result
```

### Server Setup met Alle Best Practices

Complete FastMCP server setup:

```python
from fastmcp import FastMCP, Context
from processors import get_registry, register_processor, register_all_processor_resources
from processors.invoice import InvoiceProcessor
from processors.cv import CVProcessor

# Initialiseer FastMCP server
mcp = FastMCP(
    name="DocumentProcessor",
    version="2.0.0",
    dependencies=["ollama", "pydantic", "pymupdf"]
)

# === PROCESSOR REGISTRATION ===

# Registreer processors bij registry
register_processor(InvoiceProcessor())
register_processor(CVProcessor())

# Registreer alle MCP resources (stats://, schema://, keywords://)
register_all_processor_resources(mcp)

# === TOOLS REGISTRATION ===

@mcp.tool(
    annotations=Annotations(readOnlyHint=True, idempotentHint=True)
)
async def process_document(
    text: str, 
    ctx: Context,
    method: str = "hybrid"
) -> dict:
    """
    Verwerk een document met automatische type detectie.
    
    Args:
        text: Document tekst om te verwerken
        ctx: FastMCP context voor logging en progress
        method: Extractie methode (json_schema, prompt_parsing, hybrid)
        
    Returns:
        dict: Geëxtraheerde gestructureerde data
    """
    registry = get_registry()
    
    # Classificeer document (parallel over alle processors)
    doc_type, confidence, processor = await registry.classify_document(text, ctx)
    
    if not processor:
        await ctx.warning("Geen geschikt processor gevonden")
        return {"error": "Unknown document type"}
    
    await ctx.info(
        f"Document type: {processor.display_name} ({confidence:.1f}% confidence)",
        extra={
            "document_type": doc_type,
            "confidence": confidence,
            "processor": processor.tool_name
        }
    )
    
    # Extraheer data
    result = await processor.extract(text, ctx, method)
    
    if result:
        # Update statistics
        processor.update_statistics(
            success=True,
            processing_time=0.0,  # Zou van timer moeten komen
            confidence=confidence,
            completeness=100.0  # Zou van validation moeten komen
        )
        
        return result.model_dump()
    
    return {"error": "Extraction failed"}


@mcp.tool(
    annotations=Annotations(readOnlyHint=True, idempotentHint=True)
)
async def classify_document(text: str, ctx: Context) -> dict:
    """
    Classificeer document type zonder volledige verwerking.
    
    Args:
        text: Document tekst
        ctx: FastMCP context
        
    Returns:
        dict: Classification result met confidence scores
    """
    registry = get_registry()
    
    doc_type, confidence, processor = await registry.classify_document(text, ctx)
    
    return {
        "document_type": doc_type,
        "confidence": confidence,
        "processor": processor.tool_name if processor else None,
        "display_name": processor.display_name if processor else None
    }


# === PROMPTS REGISTRATION (Optioneel) ===

@mcp.prompt()
def invoice_extraction_tips(ctx: Context) -> str:
    """Tips voor betere invoice extractie."""
    return """
    Bij het verwerken van facturen, let op:
    - Factuurnummer vaak bovenaan document
    - BTW informatie meestal onderaan
    - Line items in tabel formaat
    - Totalen in meerdere kolommen (subtotaal, BTW, totaal)
    """

@mcp.prompt()
def cv_extraction_tips(ctx: Context) -> str:
    """Tips voor betere CV extractie."""
    return """
    Bij het verwerken van CV's, let op:
    - Contactinformatie meestal bovenaan
    - Chronologische volgorde werkervaring
    - Opleidingen met datum en instelling
    - Skills vaak in lijst of tabel
    """


if __name__ == "__main__":
    mcp.run()
```

### Resource URI Schema

Alle processor resources zijn beschikbaar via:

```
stats://{document_type}      # Processor statistics
schema://{document_type}     # JSON schema van data model
keywords://{document_type}   # Classificatie keywords
stats://all                  # Global statistics van alle processors
```

Voorbeelden:
- `stats://invoice` → Invoice processor statistics
- `stats://cv` → CV processor statistics  
- `schema://invoice` → InvoiceData JSON schema
- `keywords://cv` → CV classificatie keywords
- `stats://all` → Alle processors combined

## 📁 Nieuwe Directory Structuur

```
src/mcp_invoice_processor/
├── processors/
│   ├── __init__.py              # Exporteert registry & base
│   ├── base.py                  # BaseDocumentProcessor (interface)
│   ├── registry.py              # ProcessorRegistry (factory)
│   │
│   ├── invoice/
│   │   ├── __init__.py          # Exporteert InvoiceProcessor
│   │   ├── processor.py         # InvoiceProcessor implementatie
│   │   ├── models.py            # InvoiceData, InvoiceLineItem
│   │   ├── prompts.py           # Invoice-specifieke prompts
│   │   └── tools.py             # MCP tool functies voor invoices
│   │
│   └── cv/
│       ├── __init__.py          # Exporteert CVProcessor
│       ├── processor.py         # CVProcessor implementatie
│       ├── models.py            # CVData, WorkExperience, Education
│       ├── prompts.py           # CV-specifieke prompts
│       └── tools.py             # MCP tool functies voor CVs
│
├── processing/                   # Hergebruikbare utilities
│   ├── __init__.py
│   ├── chunking.py              # Text chunking (blijft generiek)
│   ├── text_extractor.py        # PDF text extraction (blijft generiek)
│   └── ollama_client.py         # Ollama API wrapper (nieuw, herbruikbaar)
│
├── fastmcp_server.py            # Gebruikt ProcessorRegistry
├── tools.py                     # Generieke MCP tools (gedelegeerd naar processors)
└── ...
```

## 🔄 Migratie Stappen

### Stap 1: Maak Base Infrastructuur
- [ ] `processors/base.py` - BaseDocumentProcessor interface
- [ ] `processors/registry.py` - ProcessorRegistry
- [ ] `processing/ollama_client.py` - Extract Ollama logica uit pipeline.py

### Stap 2: Implementeer InvoiceProcessor
- [ ] `processors/invoice/models.py` - Verplaats InvoiceData & InvoiceLineItem
- [ ] `processors/invoice/prompts.py` - Extract invoice prompts uit pipeline.py
- [ ] `processors/invoice/processor.py` - Implementeer InvoiceProcessor
- [ ] Test invoice processor standalone

### Stap 3: Implementeer CVProcessor
- [ ] `processors/cv/models.py` - Verplaats CVData, WorkExperience, Education
- [ ] `processors/cv/prompts.py` - Extract CV prompts uit pipeline.py
- [ ] `processors/cv/processor.py` - Implementeer CVProcessor
- [ ] Test CV processor standalone

### Stap 4: Refactor Centrale Code
- [ ] Update `tools.py` om ProcessorRegistry te gebruiken
- [ ] Update `fastmcp_server.py` om processors te registreren
- [ ] Update `processing/pipeline.py` om registry te gebruiken (of verwijderen)
- [ ] Verwijder oude `processing/classification.py`

### Stap 5: Update Tests
- [ ] Maak processor-specifieke test bestanden
- [ ] Update bestaande tests om nieuwe architectuur te gebruiken
- [ ] Voeg integration tests toe voor registry

### Stap 6: Documentatie
- [ ] Update `MCP_TOOLS_DOCUMENTATION.md`
- [ ] Maak `ADDING_NEW_DOCUMENT_TYPE.md` guide
- [ ] Update README met nieuwe architectuur

### Stap 7: Cleanup
- [ ] Verwijder oude bestanden
- [ ] Verwijder deprecated code
- [ ] Run linters en type checkers

## 🎨 Voorbeeld: Nieuwe DocumentType Toevoegen

Om een nieuw documenttype (bijv. "Receipt") toe te voegen:

1. Maak nieuwe directory: `processors/receipt/`
2. Implementeer `ReceiptProcessor` in `processor.py`
3. Definieer `ReceiptData` model in `models.py`
4. Definieer prompts in `prompts.py`
5. Registreer processor in `fastmcp_server.py`:

```python
from processors.receipt import ReceiptProcessor

# In setup
registry.register(ReceiptProcessor())
```

Dat is alles! Geen wijzigingen in bestaande code nodig.

## ✅ Voordelen van Nieuwe Architectuur

### 🎯 Modularity & Extensibility

1. **Modulariteit**: Elk documenttype is volledig zelfstandig
2. **Uitbreidbaarheid**: Nieuwe types toevoegen zonder bestaande code te wijzigen
3. **Testbaarheid**: Processors kunnen isolated worden getest
4. **Onderhoud**: Bug fixes blijven lokaal in één processor
5. **Duidelijkheid**: Alle code voor één type op één plek
6. **Herbruikbaarheid**: Generieke utilities (chunking, PDF extractie) blijven herbruikbaar

### ⚡ Performance & Async

1. **Parallelle Classificatie**: Alle processors classificeren tegelijkertijd via `asyncio.gather()`
2. **Non-blocking I/O**: Ollama requests blokkeren niet de event loop
3. **Concurrent Processing**: Meerdere documenten tegelijk verwerken
4. **Scalability**: Async design schaalt beter met meer processors

**Performance Impact:**
```python
# Oude sync manier (sequential)
for processor in processors:
    score = processor.classify(text)  # Wacht op elke processor
# Totaal: N * avg_time

# Nieuwe async manier (parallel)
scores = await asyncio.gather(*[
    processor.classify(text) for processor in processors
])
# Totaal: max(all_times) - veel sneller!
```

### 📊 Realtime Status & Logging

1. **Structured Logging**: Alle logs via FastMCP Context met metadata
   ```python
   await ctx.info("Processing invoice", extra={
       "processor": "invoice",
       "confidence": 95.5,
       "method": "hybrid"
   })
   ```

2. **Progress Reporting**: Client ziet realtime voortgang
   ```python
   await ctx.report_progress(progress=50.0, total=100.0)
   ```

3. **Status Streaming**: Stream updates tijdens verwerking
   ```python
   async for status, data in processor.extract_with_status_stream(text, ctx):
       print(f"{status.stage}: {status.progress}%")
   ```

4. **Centrale Logging**: Geen manuele logger setup per module - Context handled alles

### 📈 Statistics & Monitoring

1. **Per-Processor Statistics**: Elk processor type tracked eigen metrics
   - Success rate
   - Avg processing time
   - Avg confidence scores
   - Avg completeness scores

2. **Aggregated Statistics**: Registry verzamelt stats van alle processors
   - Global success rate
   - Total documents processed
   - Per-type breakdown

3. **Custom Metrics**: Elke processor kan eigen domain-specifieke metrics toevoegen
   - Invoice: total_amount, line_items_count, has_vat
   - CV: years_experience, education_level, skills_count

4. **Real-time Monitoring**: Statistics zijn altijd up-to-date tijdens verwerking

### 🎨 Developer Experience

1. **Type Safety**: Volledig typed met Pydantic en type hints
2. **Auto-completion**: IDE's kunnen alle methods suggesteren
3. **Clear Interface**: Base class documenteert exact wat geïmplementeerd moet worden
4. **Easy Testing**: Mock Context parameter voor unit tests
5. **Hot Reload**: Nieuwe processors registreren zonder server restart

### 🚀 FastMCP Integration

1. **Context Everywhere**: Optionele `Context` parameter in alle methods
   - Structured logging met `extra` metadata
   - Progress reporting via `ctx.report_progress()`
   - Geen manuele logger setup nodig

2. **Resources**: Automatische registratie van processor data
   - `stats://{doc_type}` - Realtime statistics
   - `schema://{doc_type}` - JSON schemas voor LLMs
   - `keywords://{doc_type}` - Classificatie keywords
   - `stats://all` - Global statistics

3. **Annotations**: Hints voor LLMs over tool/resource gedrag
   - `readOnlyHint=True` - Tools wijzigen geen data
   - `idempotentHint=True` - Herhaalde calls → zelfde resultaat
   - Helpt LLMs betere beslissingen maken

4. **Meta Data**: Custom metadata voor processors
   - Version tracking
   - Category classification
   - Custom processor-specific info

5. **Best Practices Compliant**: 
   - Async everywhere voor performance
   - Context voor visibility
   - Resources voor data exposure
   - Annotations voor LLM hints
   - Progress voor user feedback

**MCP Protocol Voordelen:**
- LLMs kunnen processor statistics opvragen via Resources
- LLMs zien realtime progress tijdens verwerking
- Structured logging maakt debugging makkelijker
- Annotations helpen LLMs correcte tools kiezen

## 🚀 Implementatie Approach

Ik stel voor om dit incrementeel te doen:

1. **Fase 1**: Maak base infrastructuur en InvoiceProcessor (backward compatible)
2. **Fase 2**: Voeg CVProcessor toe (parallel aan oude code)
3. **Fase 3**: Switch alle code naar nieuwe architectuur
4. **Fase 4**: Cleanup oude code

Dit minimaliseert risico en zorgt dat de applicatie blijft werken tijdens refactoring.

