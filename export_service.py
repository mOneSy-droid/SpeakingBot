"""Export speech content to PDF/Word formats"""
import os
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas


EXPORTS_DIR = Path("exports")
EXPORTS_DIR.mkdir(exist_ok=True)


def create_speech_pdf(
    user_id: int,
    title: str,
    content: str,
    metadata: dict = None,
) -> str:
    """
    Create a PDF with corrected speech content
    
    Args:
        user_id: Telegram user ID
        title: Speech title
        content: Main content
        metadata: Additional info (date, score, etc.)
    
    Returns:
        Path to created PDF file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"speech_{user_id}_{timestamp}.pdf"
    filepath = EXPORTS_DIR / filename
    
    try:
        # Create PDF
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            alignment=1,  # Center
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=4,  # Justify
        )
        
        meta_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            spaceAfter=12,
        )
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Metadata
        if metadata:
            meta_text = f"Generated: {metadata.get('date', datetime.now().strftime('%Y-%m-%d %H:%M'))}"
            if 'score' in metadata:
                meta_text += f" | Quality Score: {metadata['score']}/100"
            story.append(Paragraph(meta_text, meta_style))
            story.append(Spacer(1, 0.1 * inch))
        
        # Main content - break into paragraphs
        for para in content.split('\n'):
            if para.strip():
                story.append(Paragraph(para.strip(), normal_style))
        
        # Build PDF
        doc.build(story)
        return str(filepath)
        
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return ""


def create_report_pdf(
    user_id: int,
    week_number: int,
    weekly_stats: dict,
    voice_recordings: list = None,
) -> str:
    """
    Create a weekly report PDF
    
    Args:
        user_id: Telegram user ID
        week_number: Week number in program
        weekly_stats: Stats dictionary with total_sessions, words_learned, improvement_score
        voice_recordings: List of recent recordings
    
    Returns:
        Path to created PDF
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"weekly_report_{user_id}_week{week_number}_{timestamp}.pdf"
    filepath = EXPORTS_DIR / filename
    
    try:
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            alignment=1,
            spaceAfter=12,
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2e5c3e'),
            spaceAfter=10,
        )
        
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
        )
        
        story = []
        
        # Title
        story.append(Paragraph(f"📊 Weekly Report - Week {week_number}", title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Statistics table
        stats_data = [
            ['Metric', 'Value'],
            ['Total Sessions', str(weekly_stats.get('total_sessions', 0))],
            ['Words Learned', str(weekly_stats.get('words_learned', 0))],
            ['Improvement Score', f"{weekly_stats.get('improvement_score', 0):.1f}%"],
            ['Date Generated', datetime.now().strftime('%Y-%m-%d %H:%M')],
        ]
        
        stats_table = Table(stats_data, colWidths=[2.5*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Voice recordings summary
        if voice_recordings:
            story.append(Paragraph("🎤 Voice Practice Summary", heading_style))
            rec_data = [['Question', 'WPM', 'Filler Words', 'Quality']]
            for rec in voice_recordings[:5]:
                rec_data.append([
                    rec.get('question', '')[:30],
                    str(rec.get('wpm', 0)),
                    str(rec.get('filler_count', 0)),
                    str(rec.get('quality_score', 0)),
                ])
            
            rec_table = Table(rec_data, colWidths=[2*inch, 0.8*inch, 1.2*inch, 0.8*inch])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c3e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ]))
            
            story.append(rec_table)
        
        doc.build(story)
        return str(filepath)
        
    except Exception as e:
        print(f"Error creating report PDF: {e}")
        return ""


def export_voice_history_pdf(user_id: int, recordings: list) -> str:
    """
    Export voice recording history as PDF
    
    Args:
        user_id: Telegram user ID
        recordings: List of recording dictionaries
    
    Returns:
        Path to created PDF
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"voice_history_{user_id}_{timestamp}.pdf"
    filepath = EXPORTS_DIR / filename
    
    try:
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            alignment=1,
            spaceAfter=12,
        )
        
        story = []
        story.append(Paragraph("🎤 Voice Practice History", title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Create table with all recordings
        table_data = [['#', 'Date', 'Question', 'WPM', 'Fillers', 'Score']]
        
        for i, rec in enumerate(recordings, 1):
            recorded_at = rec.get('recorded_at', '')[:10]
            table_data.append([
                str(i),
                recorded_at,
                rec.get('question', '')[:25],
                str(rec.get('wpm', 0)),
                str(rec.get('filler_count', 0)),
                f"{rec.get('quality_score', 0)}%",
            ])
        
        table = Table(table_data, colWidths=[0.4*inch, 0.8*inch, 2*inch, 0.6*inch, 0.6*inch, 0.6*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        
        story.append(table)
        doc.build(story)
        return str(filepath)
        
    except Exception as e:
        print(f"Error creating voice history PDF: {e}")
        return ""


def cleanup_old_exports(user_id: int, keep_count: int = 10):
    """Clean up old export files for a user"""
    try:
        user_files = sorted(
            EXPORTS_DIR.glob(f"*_{user_id}_*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        for old_file in user_files[keep_count:]:
            old_file.unlink()
    except Exception as e:
        print(f"Error cleaning up exports: {e}")
