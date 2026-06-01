def split_into_paragraphs(text):
    """
    Splits page text into paragraphs.

    PyMuPDF often extracts text with line breaks, so this function
    tries to rebuild paragraph-like blocks.
    """
    raw_paragraphs = text.split("\n\n")

    paragraphs = []

    for paragraph in raw_paragraphs:
        cleaned = " ".join(paragraph.split())

        if cleaned:
            paragraphs.append(cleaned)

    return paragraphs


def create_overlap_text(text, overlap_size):
    """
    Creates character-based overlap from the end of a chunk.
    """
    if len(text) <= overlap_size:
        return text

    return text[-overlap_size:]


def chunk_text(text, target_size=1500, overlap=300, max_size=2500):
    """
    Paragraph-aware chunking strategy.

    Instead of cutting text every fixed number of characters,
    this groups paragraphs together into meaningful chunks.

    Args:
        text: Extracted page text.
        target_size: Preferred chunk size in characters.
        overlap: Number of characters repeated between chunks.
        max_size: Hard maximum chunk size in characters.

    Returns:
        List of text chunks.
    """
    paragraphs = split_into_paragraphs(text)

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        # If a single paragraph is very large, split it safely.
        if len(paragraph) > max_size:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""

            start = 0

            while start < len(paragraph):
                end = start + target_size
                piece = paragraph[start:end]

                if piece.strip():
                    chunks.append(piece.strip())

                start += target_size - overlap

            continue

        # If adding this paragraph would make the chunk too large,
        # save the current chunk and start a new one with overlap.
        if len(current_chunk) + len(paragraph) > target_size:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

                overlap_text = create_overlap_text(current_chunk, overlap)
                current_chunk = overlap_text + " " + paragraph
            else:
                current_chunk = paragraph
        else:
            current_chunk += " " + paragraph

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks
