import logging
from fpdf import FPDF
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)

class PDFExporter:
    """Export notes, summaries, and exams to PDF."""

    def __init__(self):
        """Initialize PDF exporter."""
        pass

    def generate_transcript_pdf(self, transcript_text: str) -> bytes:
        buffer = BytesIO()

        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        story = []

        for line in transcript_text.split("\n"):
            story.append(Paragraph(line, styles["Normal"]))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def export_transcript_bytes(self, title: str, transcript: str) -> bytes:
        return self.generate_transcript_pdf(transcript)

    def export_notes_bytes(self, title: str, content: str, metadata: dict = None) -> bytes:
        """
        Export notes to PDF bytes.

        Args:
            title: Document title
            content: Notes content
            metadata: Optional dict with author, date, etc.

        Returns:
            PDF bytes
        """
        try:
            logger.info(f"Exporting notes to PDF: {title}")

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=16, style='B')
            pdf.cell(200, 10, txt=title, ln=True, align='C')
            pdf.ln(10)

            if metadata:
                pdf.set_font("Arial", size=10)
                pdf.cell(200, 10, txt=f"Generated: {metadata.get('date', datetime.now().strftime('%Y-%m-%d %H:%M'))}", ln=True)
                if metadata.get('duration'):
                    pdf.cell(200, 10, txt=f"Duration: {metadata['duration']}", ln=True)
                if metadata.get('author'):
                    pdf.cell(200, 10, txt=f"Author: {metadata['author']}", ln=True)
                pdf.ln(10)

            pdf.set_font("Arial", size=12)
            for line in content.split('\n'):
                pdf.multi_cell(0, 8, line)

            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            logger.info("✓ Notes PDF generated in memory")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Error exporting notes to PDF: {e}")
            raise

    def export_exam_bytes(self, title: str, questions: list, exam_type: str = "mixed") -> bytes:
        """
        Export exam questions to PDF bytes.

        Args:
            title: Exam title
            questions: List of question dicts
            exam_type: Type of exam

        Returns:
            PDF bytes
        """
        try:
            logger.info(f"Exporting exam to PDF: {title}")

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=16, style='B')
            pdf.cell(200, 10, txt=title, ln=True, align='C')
            pdf.ln(10)

            pdf.set_font("Arial", size=10)
            pdf.cell(200, 10, txt=f"Instructions: {len(questions)} questions | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
            pdf.ln(10)

            pdf.set_font("Arial", size=12)
            for i, q in enumerate(questions, 1):
                pdf.set_font("Arial", size=12, style='B')
                pdf.cell(200, 10, txt=f"Question {i}:", ln=True)
                pdf.set_font("Arial", size=12)

                if isinstance(q, dict):
                    if 'question' in q:
                        pdf.multi_cell(0, 10, txt=q['question'])
                    elif 'text' in q:
                        pdf.multi_cell(0, 10, txt=q['text'])
                    elif 'statement' in q:
                        pdf.multi_cell(0, 10, txt=f"T/F: {q['statement']}")

                    # Options for MCQ
                    if 'options' in q and q['options']:
                        for opt in q['options']:
                            pdf.cell(200, 10, txt=f"- {opt}", ln=True)
                else:
                    pdf.multi_cell(0, 10, txt=str(q))

                pdf.ln(5)

            pdf_bytes = pdf.output(dest='S')
            logger.info("✓ Exam PDF generated in memory")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Error exporting exam to PDF: {e}")
            raise
