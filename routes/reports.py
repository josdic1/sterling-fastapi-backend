# routes/reports.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from database import get_db
from models.user import User
from models.reservation import Reservation
from models.dining_room import DiningRoom
from models.reservation_attendee import ReservationAttendee
from utils.admin_auth import get_admin_user

router = APIRouter()

def create_daily_report_pdf(target_date: date, db: Session) -> BytesIO:
    """Generate daily operations PDF for restaurant"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.5*inch
    )
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#121212'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#757575'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#eb5638'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    # ==================== HEADER ====================
    elements.append(Paragraph("STERLING CATERING", title_style))
    elements.append(Paragraph("DAILY OPERATIONS REPORT", title_style))
    
    date_str = target_date.strftime("%A, %B %d, %Y")
    elements.append(Paragraph(date_str, subtitle_style))
    elements.append(Paragraph(
        "Contact: (555) 123-4567 | reservations@sterlingcatering.com",
        subtitle_style
    ))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # ==================== GET DATA ====================
    
    # Get all reservations for the day
    reservations = db.query(Reservation).filter(
        Reservation.date == target_date,
        Reservation.status == "confirmed" # Only show confirmed
    ).order_by(Reservation.start_time).all()
    
    # Get all rooms
    rooms = db.query(DiningRoom).order_by(DiningRoom.id).all()
    
    # Calculate stats
    total_reservations = len(reservations)
    total_guests = sum([
        db.query(ReservationAttendee).filter_by(reservation_id=r.id).count()
        for r in reservations
    ])
    
    # ==================== SUMMARY STATS ====================
    elements.append(Paragraph("TODAY'S SUMMARY", header_style))
    
    stats_data = [
        ['Total Reservations', 'Total Guests', 'Active Rooms', 'Operating Hours'],
        [
            str(total_reservations),
            str(total_guests),
            str(sum(1 for r in rooms if r.is_active)),
            '11:00 AM - 9:00 PM'
        ]
    ]
    
    stats_table = Table(stats_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch, 2.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#121212')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 16),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f8f8'))
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # ==================== TIMELINE SCHEDULE ====================
    elements.append(Paragraph("RESERVATION SCHEDULE", header_style))
    
    # Create time slots (11:00 AM - 9:00 PM in 1-hour increments)
    time_slots = []
    for hour in range(11, 22):
        # Convert to AM/PM
        if hour == 12:
            time_str = "12:00 PM"
        elif hour > 12:
            time_str = f"{hour-12}:00 PM"
        else:
            time_str = f"{hour}:00 AM"
        time_slots.append((hour, time_str))
    
    # Build schedule table
    # Header row: TIME | Room1 | Room2 | Room3 | ...
    header_row = ['TIME'] + [room.name for room in rooms]
    schedule_data = [header_row]
    
    # For each time slot, find reservations
    for hour, time_str in time_slots:
        row = [time_str]
        
        for room in rooms:
            cell_content = ""
            
            # Check if room is inactive
            if not room.is_active:
                cell_content = "CLOSED"
            else:
                # Find ALL reservations for this room at this time
                found_reservations = []
                for res in reservations:
                    if res.dining_room_id == room.id:
                        # Check if time slot falls within reservation window
                        if isinstance(res.start_time, str):
                            start_hour = int(res.start_time.split(':')[0])
                        else:
                            start_hour = res.start_time.hour
                        
                        if hour == start_hour:
                            # Get user info
                            user = db.query(User).filter_by(id=res.created_by_id).first()
                            if not user:
                                continue
                            
                            attendee_count = db.query(ReservationAttendee).filter_by(
                                reservation_id=res.id
                            ).count()
                            
                            # Add to list instead of overwriting
                            found_reservations.append(f"• {user.name} ({attendee_count})")
                
                # Join all found reservations with newlines
                if found_reservations:
                    cell_content = "\n".join(found_reservations)
            
            row.append(cell_content)
        
        schedule_data.append(row)
    
    # Calculate column widths dynamically
    num_rooms = len(rooms)
    room_col_width = (9 * inch) / num_rooms
    col_widths = [1.5*inch] + [room_col_width] * num_rooms
    
    schedule_table = Table(schedule_data, colWidths=col_widths, repeatRows=1)
    
    # Style the schedule table
    table_style = [
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#121212')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f8f8')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]
    
    # Highlight closed rooms
    for row_idx in range(1, len(schedule_data)):
        for col_idx, room in enumerate(rooms, start=1):
            if not room.is_active:
                table_style.append(
                    ('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), colors.HexColor('#e0e0e0'))
                )
                table_style.append(
                    ('TEXTCOLOR', (col_idx, row_idx), (col_idx, row_idx), colors.HexColor('#757575'))
                )
    
    # Highlight reservation cells
    for row_idx in range(1, len(schedule_data)):
        for col_idx in range(1, len(schedule_data[row_idx])):
            cell = schedule_data[row_idx][col_idx]
            # Check for the bullet point we added
            if cell and cell != "CLOSED" and "•" in cell:
                table_style.append(
                    ('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), colors.HexColor('#fff5f3'))
                )
                table_style.append(
                    ('TEXTCOLOR', (col_idx, row_idx), (col_idx, row_idx), colors.HexColor('#121212'))
                )
                table_style.append(
                    ('FONTNAME', (col_idx, row_idx), (col_idx, row_idx), 'Helvetica-Bold')
                )
    
    schedule_table.setStyle(TableStyle(table_style))
    elements.append(schedule_table)
    
    # ==================== FOOTER ====================
    elements.append(Spacer(1, 0.3*inch))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#757575'),
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')} | Sterling Catering Operations",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer 



@router.get("/daily-pdf")
@router.get("/daily-pdf/")
def get_daily_report_pdf(
    date: str | None = None,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Generate and download daily operations PDF
    
    Query params:
    - date: Date in YYYY-MM-DD format (defaults to today)
    """
    
    # Parse date or use today
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        target_date = datetime.now().date()
    
    # Generate PDF
    pdf_buffer = create_daily_report_pdf(target_date, db)
    
    # Return as downloadable file
    filename = f"sterling_daily_report_{target_date.strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )