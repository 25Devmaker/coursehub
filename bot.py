"""
Auto-enrollment approval bot for CourseHub
This bot automatically approves course enrollments after 5 minutes
"""
import sqlite3
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os

# Database path
DB_PATH = 'coursehub.db'

# Email configuration (same as app.py)
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your-app-password')

def send_email(to_email, subject, body):
    """Send email notification"""
    try:
        msg = MIMEMultipart()
        msg['From'] = MAIL_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def approve_enrollment(enrollment_id):
    """Approve an enrollment and send email notification"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get enrollment details
        cursor.execute("""
            SELECT e.student_id, e.course_id, u.name, u.email, c.title
            FROM enrollment e
            JOIN user u ON e.student_id = u.id
            JOIN course c ON e.course_id = c.id
            WHERE e.id = ? AND e.status = 'pending'
        """, (enrollment_id,))
        
        result = cursor.fetchone()
        if not result:
            print(f"Enrollment {enrollment_id} not found or already processed")
            return
        
        student_id, course_id, student_name, student_email, course_title = result
        
        # Update enrollment status
        cursor.execute("""
            UPDATE enrollment
            SET status = 'approved', approved_at = ?
            WHERE id = ?
        """, (datetime.utcnow(), enrollment_id))
        
        conn.commit()
        
        # Create notification instead of sending email
        cursor.execute("""
            INSERT INTO notification (user_id, message, type, read, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            student_id,
            f"Your enrollment for {course_title} has been approved! You can now start learning.",
            'success',
            False,
            datetime.utcnow()
        ))
        
        print(f"Enrollment {enrollment_id} approved and notification created for user {student_id}")
        
    except Exception as e:
        print(f"Error approving enrollment {enrollment_id}: {e}")
        conn.rollback()
    finally:
        conn.close()

def check_pending_enrollments():
    """Check for enrollments that are 5 minutes old and approve them"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get enrollments that are 5+ minutes old and still pending
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    
    cursor.execute("""
        SELECT id, enrolled_at
        FROM enrollment
        WHERE status = 'pending' AND enrolled_at <= ?
    """, (five_minutes_ago,))
    
    enrollments = cursor.fetchall()
    conn.close()
    
    for enrollment_id, enrolled_at in enrollments:
        print(f"Processing enrollment {enrollment_id} (enrolled at {enrolled_at})")
        approve_enrollment(enrollment_id)

def run_bot():
    """Main bot loop - runs every minute"""
    print("CourseHub Auto-Enrollment Bot Started")
    print("Checking for pending enrollments every minute...")
    
    while True:
        try:
            check_pending_enrollments()
        except Exception as e:
            print(f"Error in bot loop: {e}")
        
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    run_bot()

