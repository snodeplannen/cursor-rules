"""
Tekst chunking module voor grote documenten.
"""
from enum import Enum
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkingMethod(Enum):
    """Enum voor chunking methoden."""
    RECURSIVE = "recursive"
    # Toekomstige methoden zoals FIXED of SEMANTIC kunnen hier worden toegevoegd


def chunk_text(
    text: str,
    method: ChunkingMethod = ChunkingMethod.RECURSIVE,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> list[str]:
    """
    Verdeelt tekst in chunks met de gespecificeerde methode.

    Args:
        text: De tekst om te chunken
        method: De te gebruiken chunking methode
        chunk_size: De grootte van elke chunk in karakters
        chunk_overlap: De overlap tussen chunks in karakters

    Returns:
        list[str]: Lijst van tekst chunks

    Raises:
        NotImplementedError: Als de opgegeven methode niet geïmplementeerd is
    """
    if method == ChunkingMethod.RECURSIVE:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        return splitter.split_text(text)
    else:
        raise NotImplementedError(f"Chunking-methode {method} is niet geïmplementeerd.")
