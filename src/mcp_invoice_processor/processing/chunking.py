"""
Tekst chunking module voor grote documenten.
"""
from enum import Enum
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..config import settings


class ChunkingMethod(Enum):
    """Enum voor chunking methoden."""
    RECURSIVE = "recursive"
    SMART = "smart"
    # Toekomstige methoden zoals FIXED of SEMANTIC kunnen hier worden toegevoegd


def chunk_text(
    text: str,
    method: ChunkingMethod = ChunkingMethod.RECURSIVE,
    chunk_size: int = None,
    chunk_overlap: int = None
) -> list[str]:
    """
    Verdeelt tekst in chunks met de gespecificeerde methode.

    Args:
        text: De tekst om te chunken
        method: De te gebruiken chunking methode
        chunk_size: De grootte van elke chunk in karakters (default uit config)
        chunk_overlap: De overlap tussen chunks in karakters (default uit config)

    Returns:
        list[str]: Lijst van tekst chunks

    Raises:
        NotImplementedError: Als de opgegeven methode niet geïmplementeerd is
        ValueError: Als chunk_size buiten geldige range valt
    """
    # Gebruik configuratie defaults als niet opgegeven
    if chunk_size is None:
        chunk_size = settings.chunking.DEFAULT_CHUNK_SIZE
    if chunk_overlap is None:
        chunk_overlap = settings.chunking.DEFAULT_CHUNK_OVERLAP
    
    # Valideer chunk_size
    if chunk_size < settings.chunking.MIN_CHUNK_SIZE:
        raise ValueError(f"chunk_size ({chunk_size}) moet minimaal {settings.chunking.MIN_CHUNK_SIZE} zijn")
    if chunk_size > settings.chunking.MAX_CHUNK_SIZE:
        raise ValueError(f"chunk_size ({chunk_size}) mag maximaal {settings.chunking.MAX_CHUNK_SIZE} zijn")
    
    # Valideer chunk_overlap
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap moet kleiner zijn dan chunk_size")
    
    if method == ChunkingMethod.RECURSIVE:
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
