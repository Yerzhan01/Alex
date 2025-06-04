import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re

def generate_pdf_report(user_data, report_content, session_id):
    """
    Generate PDF report from the health report content
    """
    # Create temporary file for PDF
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, f'health_report_{session_id}.pdf')
    
    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor='#2C3E50'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor='#34495E'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        leading=14
    )
    
    # Build PDF content
    story = []
    
    # Title
    story.append(Paragraph("AI Health Report", title_style))
    story.append(Paragraph(f"Персонализированный отчет о здоровье", normal_style))
    story.append(Spacer(1, 20))
    
    # User info section
    user_info = f"""
    <b>Данные пользователя:</b><br/>
    Возраст: {user_data.get('age', 'Не указан')}<br/>
    Пол: {user_data.get('gender', 'Не указан')}<br/>
    Рост: {user_data.get('height', 'Не указан')} см<br/>
    Вес: {user_data.get('weight', 'Не указан')} кг<br/>
    """
    story.append(Paragraph(user_info, normal_style))
    story.append(Spacer(1, 20))
    
    # Process report content
    # Split content by sections and format for PDF
    sections = parse_report_sections(report_content)
    
    for section_title, section_content in sections:
        story.append(Paragraph(section_title, heading_style))
        
        # Split content into paragraphs
        paragraphs = section_content.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                # Clean up formatting for PDF
                clean_paragraph = clean_text_for_pdf(paragraph)
                story.append(Paragraph(clean_paragraph, normal_style))
                story.append(Spacer(1, 8))
    
    # Build PDF
    doc.build(story)
    
    return pdf_path

def parse_report_sections(content):
    """
    Parse report content into sections based on headers
    """
    sections = []
    
    # Split by emoji headers (🧠, 📊, ⚠️, 🛠️, 🥊, 🔥)
    header_pattern = r'([🧠📊⚠️🛠️🥊🔥]\s*\*\*[^*]+\*\*)'
    parts = re.split(header_pattern, content)
    
    current_title = None
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # Check if it's a header
        if re.match(header_pattern, part):
            current_title = part
        else:
            if current_title:
                sections.append((current_title, part))
                current_title = None
    
    # If no sections were found, treat entire content as one section
    if not sections:
        sections.append(("Отчет о здоровье", content))
    
    return sections

def clean_text_for_pdf(text):
    """
    Clean text for PDF generation - remove markdown and format properly
    """
    # Remove markdown bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # Remove markdown italic
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    
    # Convert bullet points
    text = re.sub(r'^- ', '• ', text, flags=re.MULTILINE)
    
    # Handle line breaks
    text = text.replace('\n', '<br/>')
    
    return text
