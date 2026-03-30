from weasyprint import HTML
from pathlib import Path

def export_html_to_pdf(html_content: str, output_path: str | Path):
    """
    Convert HTML content to a PDF file using WeasyPrint.
    """
    output_path = Path(output_path)
    HTML(string=html_content).write_pdf(output_path)
    return str(output_path)
