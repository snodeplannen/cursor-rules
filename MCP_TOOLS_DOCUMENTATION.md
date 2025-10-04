# MCP Invoice Processor - Gedetailleerde Tools Documentatie

## 📋 Overzicht

De MCP Invoice Processor biedt geavanceerde document verwerking met AI-powered extractie via het Model Context Protocol (MCP). De server gebruikt Ollama LLM voor intelligente data extractie uit CV's en facturen.

## 🚀 Server Informatie

- **Naam**: MCP Invoice Processor
- **Versie**: 1.0.0
- **Transport**: STDIO (voor Cursor integratie)
- **AI Model**: Ollama LLM (standaard: llama3:8b)
- **Ondersteunde Formaten**: TXT, PDF

## 🔧 Beschikbare MCP Tools

### 1. `process_document_text`

**Beschrijving**: Verwerkt document tekst en extraheert gestructureerde data met AI.

**Parameters**:
- `text` (string, verplicht): De tekst inhoud van het document
- `ctx` (Context, verplicht): FastMCP context voor logging en progress
- `extraction_method` (string, optioneel): Extractie methode - "hybrid" (default), "json_schema" of "prompt_parsing"

**Return Type**: `Dict[str, Any]`

**Return Data Structure**:
```json
{
  "document_type": "cv|invoice",
  "processing_time": 2.45,
  "full_name": "Jan Jansen",           // CV velden
  "email": "jan@email.com",
  "phone_number": "06-12345678",
  "summary": "Software ontwikkelaar",
  "work_experience": [...],
  "education": [...],
  "skills": [...],
  "invoice_id": "INV-001",             // Invoice velden
  "invoice_number": "INV-001",
  "invoice_date": "2025-01-01",
  "due_date": "2025-02-01",
  "supplier_name": "Test Supplier",
  "customer_name": "Test Customer",
  "subtotal": 100.0,
  "vat_amount": 21.0,
  "total_amount": 121.0,
  "line_items": [...],
  "payment_terms": "30 days",
  "payment_method": "Bank transfer",
  "notes": "Test invoice",
  "reference": "REF-001"
}
```

**Gebruik Voorbeeld**:
```python
result = await process_document_text(
    text="Dit is een CV van Jan Jansen...",
    ctx=context,
    extraction_method="hybrid"
)
```

### 2. `process_document_file`

**Beschrijving**: Verwerkt een document bestand (PDF, TXT) en extraheert gestructureerde data.

**Parameters**:
- `file_path` (string, verplicht): Pad naar het document bestand
- `ctx` (Context, verplicht): FastMCP context voor logging en progress
- `extraction_method` (string, optioneel): Extractie methode - "json_schema" (default) of "prompt_parsing"

**Return Type**: `Dict[str, Any]`

**Ondersteunde Bestandstypen**:
- `.txt` - Plain text bestanden
- `.pdf` - PDF documenten (tekst extractie via PyMuPDF)

**Gebruik Voorbeeld**:
```python
result = await process_document_file(
    file_path="/path/to/document.pdf",
    ctx=context,
    extraction_method="json_schema"
)
```

### 3. `classify_document_type`

**Beschrijving**: Classificeert alleen het document type zonder volledige verwerking.

**Parameters**:
- `text` (string, verplicht): De tekst inhoud van het document
- `ctx` (Context, verplicht): FastMCP context voor logging

**Return Type**: `Dict[str, Any]`

**Return Data Structure**:
```json
{
  "document_type": "cv|invoice|unknown",
  "confidence": "high|low"
}
```

**Classificatie Logica**:
- **CV Trefwoorden**: ervaring, opleiding, vaardigheden, curriculum vitae, werkervaring, education, experience, skills, competenties, diploma, werkgever, employer, functie, position, carrière, career
- **Invoice Trefwoorden**: factuur, invoice, totaal, total, bedrag, amount, btw, vat, klant, customer, leverancier, supplier, artikel, item, prijs, price, kosten, costs, betaling, payment, factuurnummer, nummer, datum, date, €, eur, euro, subtotaal, subtotal, vervaldatum, due

**Gebruik Voorbeeld**:
```python
result = await classify_document_type(
    text="Dit is een factuur met nummer INV-001...",
    ctx=context
)
```

### 4. `get_metrics`

**Beschrijving**: Haalt huidige metrics op van de document processor.

**Parameters**:
- `ctx` (Context, verplicht): FastMCP context voor logging

**Return Type**: `Dict[str, Any]`

**Return Data Structure**:
```json
{
  "timestamp": "2025-01-01T12:00:00",
  "system": {
    "uptime": "02:15:30",
    "memory_usage_mb": 153.83,
    "cpu_usage_percent": 27.22,
    "active_connections": 0,
    "total_connections": 0
  },
  "processing": {
    "total_documents": 25,
    "successful_documents": 23,
    "failed_documents": 2,
    "success_rate_percent": 92.0,
    "average_processing_time": 2.45,
    "p95_processing_time": 4.2,
    "p99_processing_time": 6.8,
    "document_types": {
      "cv": 12,
      "invoice": 11,
      "unknown": 2
    },
    "error_breakdown": {
      "extraction_failed": 1,
      "validation_error": 1
    }
  },
  "ollama": {
    "total_requests": 25,
    "successful_requests": 23,
    "failed_requests": 2,
    "success_rate_percent": 92.0,
    "average_response_time": 1.8,
    "p95_response_time": 3.2,
    "model_usage": {
      "llama3:8b": 25
    },
    "error_breakdown": {
      "timeout": 1,
      "model_error": 1
    }
  }
}
```

**Gebruik Voorbeeld**:
```python
metrics = await get_metrics(ctx=context)
print(f"Success rate: {metrics['processing']['success_rate_percent']}%")
```

### 5. `health_check`

**Beschrijving**: Voert een health check uit van de service.

**Parameters**:
- `ctx` (Context, verplicht): FastMCP context voor logging

**Return Type**: `Dict[str, Any]`

**Return Data Structure**:
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2025-01-01T12:00:00",
  "ollama_status": "healthy|unhealthy: error message",
  "available_models": ["llama3:8b", "mistral:7b"],
  "uptime": "02:15:30",
  "total_documents_processed": 25,
  "total_ollama_requests": 25
}
```

**Health Check Componenten**:
- **Ollama Service**: Controleert connectie naar Ollama API
- **Model Beschikbaarheid**: Verificeert beschikbare LLM modellen
- **Document Processor**: Test basis functionaliteit
- **Metrics Collector**: Controleert metrics systeem

**Gebruik Voorbeeld**:
```python
health = await health_check(ctx=context)
if health['status'] == 'healthy':
    print("✅ Alle services zijn operationeel")
```

## 📊 Extractie Methodes

### Hybrid (Aanbevolen)
- **Waarde**: `"hybrid"`
- **Beschrijving**: Combineert precisie van JSON schema met flexibiliteit van prompts
- **Wanneer gebruiken**: Voor de meeste documenten
- **Voordelen**: Beste van beide werelden, automatische fallback

### JSON Schema
- **Waarde**: `"json_schema"`
- **Beschrijving**: Gestructureerde extractie met JSON schema validatie
- **Wanneer gebruiken**: Voor gestructureerde documenten met vaste formaten
- **Voordelen**: Hoge precisie, consistente output, type safety

### Prompt Parsing
- **Waarde**: `"prompt_parsing"`
- **Beschrijving**: Flexibele extractie met prompt engineering
- **Wanneer gebruiken**: Voor complexe of ongestructureerde documenten
- **Voordelen**: Flexibel, kan complexe patronen herkennen

## 📋 Data Modellen

### CVData Model
```python
{
  "full_name": str,                    # Verplicht: Volledige naam
  "email": Optional[str],             # E-mailadres
  "phone_number": Optional[str],       # Telefoonnummer
  "summary": str,                      # Verplicht: Professionele samenvatting
  "work_experience": List[WorkExperience],  # Werkervaringen
  "education": List[Education],       # Opleidingen
  "skills": List[str]                 # Vaardigheden
}
```

### WorkExperience Model
```python
{
  "job_title": str,                   # Verplicht: Functietitel
  "company": str,                     # Verplicht: Bedrijfsnaam
  "start_date": Optional[str],        # Startdatum
  "end_date": Optional[str],          # Einddatum
  "description": str                  # Verplicht: Werkzaamheden beschrijving
}
```

### Education Model
```python
{
  "degree": str,                      # Verplicht: Graad/diploma
  "institution": str,                # Verplicht: Onderwijsinstelling
  "graduation_date": Optional[str]    # Afstudeerdatum
}
```

### InvoiceData Model
```python
{
  "invoice_id": str,                  # Verplicht: Unieke identificatie
  "invoice_number": Optional[str],    # Factuurnummer
  "invoice_date": Optional[str],      # Factuurdatum
  "due_date": Optional[str],          # Vervaldatum
  
  # Bedrijfsinformatie
  "supplier_name": str,               # Verplicht: Leverancier naam
  "supplier_address": Optional[str], # Leverancier adres
  "supplier_vat_number": Optional[str], # Leverancier BTW-nummer
  "customer_name": str,               # Verplicht: Klant naam
  "customer_address": Optional[str],  # Klant adres
  "customer_vat_number": Optional[str], # Klant BTW-nummer
  
  # Financiële informatie
  "subtotal": float,                  # Verplicht: Subtotaal exclusief BTW
  "vat_amount": float,                # Verplicht: BTW-bedrag
  "total_amount": float,              # Verplicht: Totaal inclusief BTW
  "currency": str,                    # Valuta (default: "EUR")
  
  # Factuurregels
  "line_items": List[InvoiceLineItem], # Factuurregels
  
  # Betalingsinformatie
  "payment_terms": Optional[str],     # Betalingsvoorwaarden
  "payment_method": Optional[str],   # Betalingsmethode
  
  # Extra informatie
  "notes": Optional[str],             # Opmerkingen
  "reference": Optional[str]         # Referentie/ordernummer
}
```

### InvoiceLineItem Model
```python
{
  "description": str,                 # Verplicht: Product/dienst beschrijving
  "quantity": float,                  # Verplicht: Aantal/hoeveelheid
  "unit_price": float,                # Verplicht: Eenheidsprijs exclusief BTW
  "unit": Optional[str],              # Eenheid (stuks, uren, etc.)
  "line_total": float,                # Verplicht: Regeltotaal exclusief BTW
  "vat_rate": Optional[float],         # BTW-tarief percentage
  "vat_amount": Optional[float]       # BTW-bedrag voor deze regel
}
```

## ⚙️ Configuratie

### Omgevingsvariabelen
```bash
# Ollama configuratie
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3:8b
OLLAMA_TIMEOUT=120

# Applicatie configuratie
LOG_LEVEL=INFO
```

### Configuratiebestand (.env)
```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3:8b
OLLAMA_TIMEOUT=120
LOG_LEVEL=INFO
```

## 🔍 Document Types

### CV/Resume Detectie
**Trefwoorden**: ervaring, opleiding, vaardigheden, curriculum vitae, werkervaring, education, experience, skills, competenties, diploma, werkgever, employer, functie, position, carrière, career

**Geëxtraheerde velden**:
- Persoonlijke informatie (naam, email, telefoon)
- Professionele samenvatting
- Werkervaring (functie, bedrijf, datums, beschrijving)
- Opleiding (graad, instelling, afstudeerdatum)
- Vaardigheden en technologieën

### Invoice/Factuur Detectie
**Trefwoorden**: factuur, invoice, totaal, total, bedrag, amount, btw, vat, klant, customer, leverancier, supplier, artikel, item, prijs, price, kosten, costs, betaling, payment, factuurnummer, nummer, datum, date, €, eur, euro, subtotaal, subtotal, vervaldatum, due

**Geëxtraheerde velden**:
- Factuur identificatie (nummer, datum, vervaldatum)
- Bedrijfsinformatie (leverancier en klant)
- Financiële informatie (bedragen, BTW)
- Factuurregels (producten/diensten met prijzen)
- Betalingsinformatie

## 🚨 Error Handling

### Veelvoorkomende Errors
- **`extraction_failed`**: AI extractie mislukt
- **`validation_error`**: Data validatie gefaald
- **`json_decode_error`**: JSON parsing probleem
- **`ollama_error`**: Ollama service fout
- **`timeout`**: Request timeout
- **`model_error`**: LLM model fout
- **`connection_error`**: Netwerk connectie probleem

### Error Response Format
```json
{
  "error": "Beschrijving van de fout",
  "document_type": "cv|invoice|unknown",
  "processing_time": 2.45
}
```

## 💡 Best Practices

### 1. Extractie Methode Keuze
- **Start altijd met "hybrid"** voor beste resultaten
- **Gebruik "json_schema"** voor gestructureerde facturen
- **Gebruik "prompt_parsing"** voor complexe CV's

### 2. Document Voorbereiding
- **CV's**: Zorg voor duidelijke secties en consistente datumformaten
- **Facturen**: Include duidelijk factuurnummer en bedragen
- **PDF's**: Zorg voor goede tekst extractie kwaliteit

### 3. Performance Optimalisatie
- **Controleer health_check** voor Ollama connectie
- **Monitor metrics** voor performance trends
- **Gebruik kleinere documenten** voor snellere verwerking

### 4. Error Handling
- **Implementeer retry logica** voor tijdelijke fouten
- **Valideer resultaten** voordat verdere verwerking
- **Log errors** voor troubleshooting

## 🔧 Troubleshooting

### Ollama Connectie Problemen
1. Controleer of Ollama draait: `ollama serve`
2. Verificeer host configuratie: `curl http://localhost:11434/api/tags`
3. Controleer model beschikbaarheid: `ollama list`

### Extractie Kwaliteit Problemen
1. Probeer verschillende extractie methodes
2. Controleer document kwaliteit en structuur
3. Test met verschillende Ollama modellen

### Performance Problemen
1. Monitor metrics voor bottlenecks
2. Optimaliseer Ollama configuratie
3. Gebruik kleinere batch sizes

## 📚 Resources

### MCP Resources
- `mcp://document-types` - Voorbeelden van ondersteunde document types
- `mcp://extraction-methods` - Gids voor extractie methodes
- `mcp://server-config` - Server configuratie informatie

### Prompts
- `document-processing-guide` - Gids voor document verwerking
- `troubleshooting-guide` - Troubleshooting gids

## 🚀 Quick Start

```python
# 1. Health check
health = await health_check(ctx=context)
if health['status'] != 'healthy':
    print("❌ Server niet gezond")

# 2. Document classificatie
doc_type = await classify_document_type(text, ctx=context)
print(f"Document type: {doc_type['document_type']}")

# 3. Volledige verwerking
result = await process_document_text(
    text=document_text,
    ctx=context,
    extraction_method="hybrid"
)

# 4. Metrics bekijken
metrics = await get_metrics(ctx=context)
print(f"Success rate: {metrics['processing']['success_rate_percent']}%")
```

---

**Versie**: 1.0.0  
**Laatste update**: 2025-01-01  
**Compatibiliteit**: MCP 1.13.1, FastMCP, Ollama LLM

