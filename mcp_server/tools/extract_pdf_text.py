"""
One-off utility: extract raw text from a resume PDF and save it as .txt,
so parse_resume.py has plain text to work with.

This is intentionally a separate, throwaway script rather than folded
into parse_resume.py itself — parsing a PDF and extracting structured
resume data are two different concerns, and keeping them separate
means each piece is easier to test and debug on its own.
"""

from pypdf import PdfReader

def extract_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text_parts = [page.extract_text() for page in reader.pages]
    return "\n".join(text_parts)

if __name__ == "__main__":
    text = extract_text("../../data/resume.pdf")
    with open("../../data/sample_resume.txt", "w") as f:
        f.write(text)
    print(f"Extracted {len(text)} characters to data/sample_resume.txt")
