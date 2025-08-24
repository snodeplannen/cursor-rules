import pytest
import sys
import importlib.util
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

"""
Gedeelde fixtures en configuratie voor tests.
"""

# Voeg de src directory toe aan het Python pad
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def sample_cv_text() -> str:
    """Voorbeeld CV tekst voor testing."""
    return """
    Curriculum Vitae
    
    Naam: Jan Jansen
    Email: jan.jansen@email.com
    Telefoon: 06-12345678
    
    Samenvatting:
    Ervaren software ontwikkelaar met expertise in Python en web development.
    
    Werkervaring:
    - Software Engineer bij TechCorp (2020-2023)
    - Junior Developer bij StartupXYZ (2018-2020)
    
    Opleiding:
    - Bachelor Informatica, Universiteit van Amsterdam (2018)
    
    Vaardigheden:
    - Python, JavaScript, React
    - Docker, Kubernetes
    - Agile development
    """


@pytest.fixture(scope="session")
def sample_invoice_text() -> str:
    """Voorbeeld factuur tekst voor testing."""
    return """
    FACTUUR
    
    Factuurnummer: INV-2024-001
    Klant: Test Bedrijf BV
    Datum: 15-01-2024
    
    Artikel: Software Licentie
    Prijs: €500,00
    BTW: €105,00
    Totaal: €605,00
    """


@pytest.fixture(scope="session")
def uv_command() -> list[str]:
    """UV command voor het starten van de MCP server."""
    return [
        "C:\\ProgramData\\miniforge3\\Scripts\\uv.exe",
        "--directory",
        "C:\\py_cursor-rules\\cursor_ratsenbergertest\\",
        "run",
        "python",
        "-m",
        "mcp_invoice_processor.main"
    ]


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def src_directory(project_root: Path) -> Path:
    """Source directory."""
    return project_root / "src"


@pytest.fixture(scope="session")
def mcp_package_directory(src_directory: Path) -> Path:
    """MCP invoice processor package directory."""
    return src_directory / "mcp_invoice_processor"


@pytest.fixture(scope="session")
def processing_directory(mcp_package_directory: Path) -> Path:
    """Processing package directory."""
    return mcp_package_directory / "processing"


@pytest.fixture(scope="session")
def tests_directory(project_root: Path) -> Path:
    """Tests directory."""
    return project_root / "tests"


# Controleer of FastMCP beschikbaar is
@pytest.fixture(scope="session")
def fastmcp_available() -> bool:
    """Of FastMCP beschikbaar is."""
    try:
        fastmcp_spec = importlib.util.find_spec("fastmcp")
        return fastmcp_spec is not None
    except ImportError:
        return False


# Controleer of MCP library beschikbaar is
@pytest.fixture(scope="session")
def mcp_available() -> bool:
    """Of MCP library beschikbaar is."""
    try:
        mcp_spec = importlib.util.find_spec("mcp")
        return mcp_spec is not None
    except ImportError:
        return False


# Controleer of Ollama beschikbaar is
@pytest.fixture(scope="session")
def ollama_available() -> bool:
    """Of Ollama library beschikbaar is."""
    try:
        ollama_spec = importlib.util.find_spec("ollama")
        return ollama_spec is not None
    except ImportError:
        return False


@pytest.fixture(scope="session")
def mock_ollama_response() -> dict[str, Any]:
    """Mock Ollama response voor testing."""
    return {
        "model": "llama3",
        "created_at": "2024-01-01T00:00:00Z",
        "response": "Mock response",
        "done": True,
        "context": [],
        "total_duration": 1000000000,
        "load_duration": 500000000,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 200000000,
        "eval_count": 20,
        "eval_duration": 300000000
    }


@pytest.fixture(scope="session")
def mock_cv_data() -> dict[str, Any]:
    """Mock CV data voor testing."""
    return {
        "name": "Jan Jansen",
        "email": "jan.jansen@email.com",
        "phone": "06-12345678",
        "summary": "Ervaren software ontwikkelaar met expertise in Python en web development.",
        "work_experience": [
            {
                "company": "TechCorp",
                "position": "Software Engineer",
                "start_date": "2020",
                "end_date": "2023",
                "description": "Ontwikkeling van web applicaties"
            },
            {
                "company": "StartupXYZ",
                "position": "Junior Developer",
                "start_date": "2018",
                "end_date": "2020",
                "description": "Frontend ontwikkeling"
            }
        ],
        "education": [
            {
                "degree": "Bachelor Informatica",
                "institution": "Universiteit van Amsterdam",
                "graduation_year": "2018"
            }
        ],
        "skills": ["Python", "JavaScript", "React", "Docker", "Kubernetes", "Agile development"]
    }


@pytest.fixture(scope="session")
def mock_invoice_data() -> dict[str, Any]:
    """Mock factuur data voor testing."""
    return {
        "invoice_number": "INV-2024-001",
        "customer": "Test Bedrijf BV",
        "date": "15-01-2024",
        "items": [
            {
                "description": "Software Licentie",
                "price": 500.00,
                "vat": 105.00,
                "total": 605.00
            }
        ],
        "subtotal": 500.00,
        "vat_total": 105.00,
        "total_amount": 605.00
    }


@pytest.fixture(scope="session")
def mock_processing_result() -> dict[str, Any]:
    """Mock processing result voor testing."""
    return {
        "document_type": "cv",
        "data": {
            "name": "Jan Jansen",
            "email": "jan.jansen@email.com",
            "phone": "06-12345678"
        },
        "status": "success",
        "error_message": None
    }


@pytest.fixture(scope="session")
def mock_error_result() -> dict[str, Any]:
    """Mock error result voor testing."""
    return {
        "document_type": "unknown",
        "data": None,
        "status": "error",
        "error_message": "Test error message"
    }


# Test markers voor verschillende test types
def pytest_configure(config: Any) -> None:
    """Configureer pytest markers."""
    config.addinivalue_line(
        "markers", "fastmcp: mark test as requiring FastMCP"
    )
    config.addinivalue_line(
        "markers", "mcp: mark test as requiring MCP library"
    )
    config.addinivalue_line(
        "markers", "ollama: mark test as requiring Ollama"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "asyncio: mark test as async test"
    )


@pytest.fixture
def mock_context() -> Any:
    """Mock context voor MCP server testing."""
    class MockContext:
        def __init__(self) -> None:
            self.error_calls: list[str] = []
            self.warning_calls: list[str] = []
            self.info_calls: list[str] = []
        
        async def error(self, message: str) -> None:
            self.error_calls.append(message)
        
        async def warning(self, message: str) -> None:
            self.warning_calls.append(message)
        
        async def info(self, message: str) -> None:
            self.info_calls.append(message)
    
    return MockContext()
