"""
Tekst chunking module voor grote documenten.
"""
import logging
from enum import Enum
from typing import Optional, Union
from langchain_text_splitters import RecursiveCharacterTextSplitter
import ollama
from ..config import settings

logger = logging.getLogger(__name__)


class ChunkingMethod(Enum):
    """Enum voor chunking methoden."""
    RECURSIVE = "recursive"
    SMART = "smart"
    AUTO = "auto"  # Automatische chunk size gebaseerd op Ollama model context
    # Toekomstige methoden zoals FIXED of SEMANTIC kunnen hier worden toegevoegd


def get_ollama_model_context_size(model_name: str = None) -> int:
    """
    Haal de maximale context size op van het Ollama model.
    
    Args:
        model_name: Naam van het model (default: uit configuratie)
        
    Returns:
        int: Maximale context size in tokens
        
    Raises:
        ValueError: Als model niet gevonden wordt of context size niet bepaald kan worden
    """
    if model_name is None:
        model_name = settings.ollama.MODEL
    
    try:
        # Haal model informatie op
        model_info = ollama.show(model_name)
        
        # Zoek naar context size in verschillende velden
        context_size = None
        
        # Probeer verschillende velden waar context size kan staan
        if 'details' in model_info:
            details = model_info['details']
            if 'parameter_size' in details:
                # Sommige modellen hebben parameter_size
                param_size = details['parameter_size']
                # Schat context size gebaseerd op parameter size
                if '7B' in param_size or '7b' in param_size:
                    context_size = 8192
                elif '8B' in param_size or '8b' in param_size:
                    context_size = 8192
                elif '13B' in param_size or '13b' in param_size:
                    context_size = 8192
                elif '70B' in param_size or '70b' in param_size:
                    context_size = 8192
                elif '3B' in param_size or '3b' in param_size:
                    context_size = 2048
        
        # Fallback: probeer context size direct
        if context_size is None:
            # Bekende context sizes voor populaire modellen
            model_context_map = {
                'llama3.2': 128000,
                'llama3.2:3b': 128000,
                'llama3.2:1b': 128000,
                'llama3.1': 128000,
                'llama3.1:8b': 128000,
                'llama3.1:70b': 128000,
                'llama3': 8192,
                'llama3:8b': 8192,
                'llama3:70b': 8192,
                'mistral': 32768,
                'mistral:7b': 32768,
                'codellama': 16384,
                'codellama:7b': 16384,
                'codellama:13b': 16384,
                'phi3': 128000,
                'phi3:mini': 128000,
                'gemma2': 8192,
                'gemma2:2b': 8192,
                'gemma2:9b': 8192,
            }
            
            # Zoek exacte match
            if model_name in model_context_map:
                context_size = model_context_map[model_name]
            else:
                # Zoek gedeeltelijke match
                for key, size in model_context_map.items():
                    if key in model_name or model_name in key:
                        context_size = size
                        break
        
        if context_size is None:
            # Ultimate fallback
            logger.warning(f"Kon context size niet bepalen voor model {model_name}, gebruik default 8192")
            context_size = 8192
        
        logger.info(f"Model {model_name} heeft context size: {context_size} tokens")
        return context_size
        
    except Exception as e:
        logger.error(f"Fout bij ophalen model info voor {model_name}: {e}")
        # Fallback naar bekende default
        logger.warning("Gebruik fallback context size: 8192 tokens")
        return 8192


def calculate_auto_chunk_size(model_name: str = None, chunk_overlap: int = None) -> int:
    """
    Bereken optimale chunk size gebaseerd op Ollama model context.
    
    Args:
        model_name: Naam van het model
        chunk_overlap: Overlap tussen chunks (default uit configuratie)
        
    Returns:
        int: Aanbevolen chunk size in karakters
    """
    if not settings.chunking.AUTO_MODE_ENABLED:
        logger.info("Auto mode uitgeschakeld, gebruik default chunk size")
        return settings.chunking.DEFAULT_CHUNK_SIZE
    
    # Gebruik default overlap als niet opgegeven
    if chunk_overlap is None:
        chunk_overlap = settings.chunking.DEFAULT_CHUNK_OVERLAP
    
    try:
        # Haal context size op
        context_size_tokens = get_ollama_model_context_size(model_name)
        
        # Converteer tokens naar karakters (rough estimate: 1 token ≈ 4 karakters)
        # Dit is een conservatieve schatting
        chars_per_token = 4
        max_chars = context_size_tokens * chars_per_token
        
        # Pas safety factor toe
        safe_chars = int(max_chars * settings.chunking.AUTO_MODE_SAFETY_FACTOR)
        
        # Trek overlap af van beschikbare ruimte
        # Bij chunking wordt overlap gebruikt tussen chunks, dus we moeten dit reserveren
        available_chars = safe_chars - chunk_overlap
        
        # Zorg dat het binnen de geldige range valt
        chunk_size = max(settings.chunking.MIN_CHUNK_SIZE, 
                        min(available_chars, settings.chunking.MAX_CHUNK_SIZE))
        
        logger.info(f"Auto chunk size berekend: {chunk_size} karakters "
                   f"(context: {context_size_tokens} tokens, safety: {settings.chunking.AUTO_MODE_SAFETY_FACTOR}, "
                   f"overlap: {chunk_overlap}, available: {available_chars})")
        
        return chunk_size
        
    except Exception as e:
        logger.error(f"Fout bij berekenen auto chunk size: {e}")
        logger.warning("Gebruik default chunk size als fallback")
        return settings.chunking.DEFAULT_CHUNK_SIZE


def chunk_text(
    text: str,
    method: ChunkingMethod = ChunkingMethod.RECURSIVE,
    chunk_size: Union[int, str, None] = None,
    chunk_overlap: int = None
) -> list[str]:
    """
    Verdeelt tekst in chunks met de gespecificeerde methode.

    Args:
        text: De tekst om te chunken
        method: De te gebruiken chunking methode
        chunk_size: De grootte van elke chunk in karakters (default uit config)
                   Kan ook "auto" zijn voor automatische berekening
        chunk_overlap: De overlap tussen chunks in karakters (default uit config)

    Returns:
        list[str]: Lijst van tekst chunks

    Raises:
        NotImplementedError: Als de opgegeven methode niet geïmplementeerd is
        ValueError: Als chunk_size buiten geldige range valt
    """
    # Gebruik configuratie defaults als niet opgegeven
    if chunk_overlap is None:
        chunk_overlap = settings.chunking.DEFAULT_CHUNK_OVERLAP
    
    if chunk_size is None:
        chunk_size = settings.chunking.DEFAULT_CHUNK_SIZE
    elif chunk_size == "auto":
        chunk_size = calculate_auto_chunk_size(chunk_overlap=chunk_overlap)
    
    # Valideer chunk_size
    if chunk_size < settings.chunking.MIN_CHUNK_SIZE:
        raise ValueError(f"chunk_size ({chunk_size}) moet minimaal {settings.chunking.MIN_CHUNK_SIZE} zijn")
    if chunk_size > settings.chunking.MAX_CHUNK_SIZE:
        raise ValueError(f"chunk_size ({chunk_size}) mag maximaal {settings.chunking.MAX_CHUNK_SIZE} zijn")
    
    # Valideer chunk_overlap
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap moet kleiner zijn dan chunk_size")
    
    # Auto mode: gebruik berekende chunk size
    if method == ChunkingMethod.AUTO:
        auto_chunk_size = calculate_auto_chunk_size(chunk_overlap=chunk_overlap)
        chunk_size = min(chunk_size, auto_chunk_size)  # Gebruik kleinste van beide
        logger.info(f"Auto mode: gebruik chunk size {chunk_size} met overlap {chunk_overlap}")
    
    if method in [ChunkingMethod.RECURSIVE, ChunkingMethod.AUTO]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        return splitter.split_text(text)
    elif method == ChunkingMethod.SMART:
        # SMART methode: probeer op natuurlijke grenzen te splitsen
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        return splitter.split_text(text)
    else:
        raise NotImplementedError(f"Chunking-methode {method} is niet geïmplementeerd.")
