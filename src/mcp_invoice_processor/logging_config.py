"""
Uitgebreide logging configuratie voor de MCP Invoice Processor.
Inclusief file logging, JSON formatting en MCP-specifieke loggers.
"""
import logging.config
import warnings
from pathlib import Path
from datetime import datetime
from typing import Optional

# Onderdruk DeprecationWarnings van externe libraries
warnings.filterwarnings("ignore", category=DeprecationWarning, module="fitz")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="swigobject")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="swigvarlink")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sys")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="builtins")

# Onderdruk alle DeprecationWarnings globaal
warnings.filterwarnings("ignore", category=DeprecationWarning)

def setup_logging(log_level: str = "DEBUG", log_file: Optional[str] = None) -> logging.Logger:
    """Configureert uitgebreide logging voor de MCP applicatie."""
    
    # Maak logs directory als deze niet bestaat
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Standaard log bestand als geen specifiek bestand is opgegeven
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = logs_dir / f"mcp_invoice_processor_{timestamp}.log"
    else:
        log_file_path = Path(log_file)
    
    # Maak een custom formatter voor volledige output zonder truncatie
    class FullContentFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            # Zorg dat lange berichten niet worden afgekapt
            if hasattr(record, 'msg') and isinstance(record.msg, str):
                if len(record.msg) > 1000:
                    record.msg = f"{record.msg[:1000]}... [TRUNCATED - Totaal lengte: {len(record.msg)} karakters]"
            return super().format(record)
    
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "()": FullContentFormatter,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(funcName)s %(lineno)d",
            },
            "mcp_detailed": {
                "()": FullContentFormatter,
                "format": "%(asctime)s - MCP - %(levelname)s - %(name)s - %(message)s",
            },
            "mcp_clean": {
                "()": FullContentFormatter,
                "format": "%(asctime)s - MCP_SERVER - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "detailed",
                "stream": "ext://sys.stderr",
                "level": "INFO",
            },
            "file_detailed": {
                "class": "logging.FileHandler",
                "filename": str(log_file_path),
                "formatter": "detailed",
                "mode": "a",
                "encoding": "utf-8",
                "level": "DEBUG",
            },
            "file_json": {
                "class": "logging.FileHandler",
                "filename": str(logs_dir / "mcp_invoice_processor.json.log"),
                "formatter": "json",
                "mode": "a",
                "encoding": "utf-8",
                "level": "DEBUG",
            },
            "mcp_events": {
                "class": "logging.FileHandler",
                "filename": str(logs_dir / "mcp_events.log"),
                "formatter": "mcp_detailed",
                "mode": "a",
                "encoding": "utf-8",
                "level": "DEBUG",
            },
            "mcp_server": {
                "class": "logging.FileHandler",
                "filename": str(logs_dir / "mcp_server.log"),
                "formatter": "mcp_clean",
                "mode": "a",
                "encoding": "utf-8",
                "level": "INFO",
            },
        },
        "loggers": {
            # MCP specifieke loggers - Zorg dat deze niet als ERROR worden gelogd
            "mcp": {
                "handlers": ["mcp_server", "file_detailed", "file_json"],
                "level": "WARNING",  # Verhoog naar WARNING om DEBUG/INFO output te voorkomen
                "propagate": False,
            },
            "mcp.server": {
                "handlers": ["mcp_server", "file_detailed", "file_json"],
                "level": "WARNING",
                "propagate": False,
            },
            "mcp.server.lowlevel": {
                "handlers": ["mcp_server", "file_detailed", "file_json"],
                "level": "WARNING",
                "propagate": False,
            },
            "mcp.server.lowlevel.server": {
                "handlers": ["mcp_server", "file_detailed", "file_json"],
                "level": "WARNING",
                "propagate": False,
            },
            # FastMCP specifieke loggers
            "fastmcp": {
                "handlers": ["mcp_server", "file_detailed", "file_json"],
                "level": "WARNING",  # Verhoog naar WARNING om DEBUG/INFO output te voorkomen
                "propagate": False,
            },
            # Speciale MCP server logger voor Cursor integratie
            "mcp_server_integration": {
                "handlers": ["mcp_server", "file_detailed", "file_json"],
                "level": "INFO",
                "propagate": False,
            },
            # Onze applicatie loggers
            "invoice_processor": {
                "handlers": ["file_detailed", "file_json"],
                "level": log_level,
                "propagate": False,
            },
            "mcp_invoice_processor": {
                "handlers": ["file_detailed", "file_json"],
                "level": log_level,
                "propagate": False,
            },
            # HTTP en netwerk loggers
            "httpx": {
                "handlers": ["file_detailed", "file_json"],
                "level": "INFO",  # Verlaag naar INFO om te veel DEBUG output te voorkomen
                "propagate": False,
            },
            "httpcore": {
                "handlers": ["file_detailed", "file_json"],
                "level": "INFO",
                "propagate": False,
            },
            # Ollama integratie logger
            "ollama": {
                "handlers": ["file_detailed", "file_json"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["file_detailed"],
            "level": log_level,
        },
    }
    
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Log dat logging is opgezet (alleen naar file, niet naar console)
    logger = logging.getLogger(__name__)
    logger.info(f"Uitgebreide logging geconfigureerd - Level: {log_level}, File: {log_file_path}")
    logger.info(f"MCP events worden gelogd naar: {logs_dir / 'mcp_events.log'}")
    logger.info(f"JSON logs worden geschreven naar: {logs_dir / 'mcp_invoice_processor.json.log'}")
    
    # Test MCP logging (alleen naar file)
    mcp_logger = logging.getLogger("mcp")
    mcp_logger.info("MCP logging systeem geactiveerd")
    
    return logger
