from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import datetime
import os
from threading import Timer, Thread
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ai_learning_tracker import AILearningTracker
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Ensure instance folder for sqlite exists
os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

# Database URL with default to instance sqlite file
default_sqlite_path = os.path.join(app.root_path, 'instance', 'coursehub.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{default_sqlite_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'yourusername@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'password1234')

db = SQLAlchemy(app)
mail = Mail(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    usn = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    progress = db.relationship('StudentProgress', backref='student', lazy=True)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    regno = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phno = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    thumbnail = db.Column(db.String(200))
    total_chapters = db.Column(db.Integer, default=0)
    total_hours = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    chapters = db.relationship('Chapter', backref='course', lazy=True, cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    checkpoint = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    enrolled_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)

class StudentProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    time_spent = db.Column(db.Float, default=0)  # in hours

class OTPSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')  # info, success, warning, error
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    sender = db.Column(db.String(10), nullable=False)  # 'student' or 'admin'
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Email sending function
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_USERNAME']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# Auto-approval bot function
enrollment_timers = {}

def auto_approve_enrollment(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)
    if enrollment and enrollment.status == 'pending':
        enrollment.status = 'approved'
        enrollment.approved_at = datetime.datetime.utcnow()
        db.session.commit()
        
        # Create notification instead of sending email
        student = User.query.get(enrollment.student_id)
        course = Course.query.get(enrollment.course_id)
        notification = Notification(
            user_id=student.id,
            message=f"Your enrollment for {course.title} has been approved! You can now start learning.",
            type='success'
        )
        db.session.add(notification)
        db.session.commit()

def background_auto_approver_loop():
    from time import sleep
    # Ensure DB ops run inside app context when started by a thread/gunicorn
    with app.app_context():
        while True:
            try:
                cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
                pending = Enrollment.query.filter(Enrollment.status == 'pending', Enrollment.enrolled_at <= cutoff).all()
                for enrollment in pending:
                    enrollment.status = 'approved'
                    enrollment.approved_at = datetime.datetime.utcnow()
                    db.session.add(enrollment)
                    # notify
                    student = User.query.get(enrollment.student_id)
                    course = Course.query.get(enrollment.course_id)
                    if student and course:
                        note = Notification(
                            user_id=student.id,
                            message=f"Your enrollment for {course.title} has been auto-approved!",
                            type='success'
                        )
                        db.session.add(note)
                if pending:
                    db.session.commit()
            except Exception as e:
                print('Auto-approver error:', e)
                db.session.rollback()
            finally:
                sleep(60)

# Initialize DB and seed data at import time (works for gunicorn too)
with app.app_context():
    db.create_all()
    if Course.query.count() == 0:
        courses_data = [
            {'title': 'Java', 'description': 'Learn Java programming from basics to advanced', 'total_chapters': 10, 'total_hours': 40, 'thumbnail': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/java/java-original.svg'},
            {'title': 'Python', 'description': 'Master Python programming and applications', 'total_chapters': 12, 'total_hours': 50, 'thumbnail': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg'},
            {'title': 'C++', 'description': 'Comprehensive C++ programming course', 'total_chapters': 10, 'total_hours': 45, 'thumbnail': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/cplusplus/cplusplus-original.svg'},
            {'title': 'C', 'description': 'Fundamentals of C programming language', 'total_chapters': 8, 'total_hours': 35, 'thumbnail': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/c/c-original.svg'},
            {'title': 'Computer Networks', 'description': 'Learn networking concepts and protocols', 'total_chapters': 15, 'total_hours': 60, 'thumbnail': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/ubuntu/ubuntu-plain.svg'},
            {'title': 'Office Automation Tools', 'description': 'Master Microsoft Office and automation', 'total_chapters': 8, 'total_hours': 30, 'thumbnail': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/windows8/windows8-original.svg'},
            {'title': 'SQL', 'description': 'Database management and SQL queries', 'total_chapters': 10, 'total_hours': 40, 'thumbnail': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg'},
            {'title': 'Use of AI', 'description': 'Introduction to Artificial Intelligence and applications', 'total_chapters': 12, 'total_hours': 50, 'thumbnail': 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tensorflow/tensorflow-original.svg'}
        ]
        for course_data in courses_data:
            db.session.add(Course(**course_data))
        db.session.commit()

# Optionally start background approver in web process (single worker)
if os.environ.get('ENABLE_AUTO_APPROVER', '1') == '1':
    try:
        t = Thread(target=background_auto_approver_loop, daemon=True)
        t.start()
        print('Background auto-approver started')
    except Exception as e:
        print('Failed to start background auto-approver:', e)

# Routes
@app.route('/')
def landing():
    courses = Course.query.all()
    return render_template('landing.html', courses=courses)

@app.route('/get-started')
def get_started():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'student')
        
        if user_type == 'admin':
            admin = Admin.query.filter_by(email=email).first()
            if admin and check_password_hash(admin.password_hash, password):
                session['admin_id'] = admin.id
                session['admin_email'] = admin.email
                return redirect(url_for('admin_dashboard'))
            flash('Invalid admin credentials', 'error')
        else:
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_name'] = user.name
                return redirect(url_for('dashboard'))
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        usn = request.form.get('usn')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not usn or not email or not password:
            flash('Please fill in all fields', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(usn=usn).first():
            flash('USN already registered', 'error')
            return render_template('signup.html')
        
        # Create user account directly without OTP verification
        user = User(
            name=name,
            usn=usn,
            email=email,
            password_hash=generate_password_hash(password),
            email_verified=True  # Set as verified directly
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# OTP verification route removed - no longer needed

@app.route('/admin-signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        regno = request.form.get('regno')
        email = request.form.get('email')
        phno = request.form.get('phno')
        password = request.form.get('password')
        
        if Admin.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('admin_signup.html')
        
        if Admin.query.filter_by(regno=regno).first():
            flash('Registration number already exists', 'error')
            return render_template('admin_signup.html')
        
        admin = Admin(
            full_name=full_name,
            regno=regno,
            email=email,
            phno=phno,
            password_hash=generate_password_hash(password)
        )
        db.session.add(admin)
        db.session.commit()
        
        flash('Admin account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('admin_signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    enrollments = Enrollment.query.filter_by(student_id=user.id).all()
    courses = Course.query.all()
    
    enrolled_course_ids = [e.course_id for e in enrollments if e.status == 'approved']
    available_courses = [c for c in courses if c.id not in enrolled_course_ids]
    
    # Get unread notifications
    notifications = Notification.query.filter_by(
        user_id=user.id,
        read=False
    ).order_by(Notification.created_at.desc()).all()
    
    return render_template('dashboard.html', 
                         user=user, 
                         enrollments=enrollments,
                         available_courses=available_courses,
                         notifications=notifications)

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    total_students = User.query.count()
    total_courses = Course.query.count()
    total_enrollments = Enrollment.query.count()
    
    # Get monthly enrollment data
    enrollments = Enrollment.query.all()
    monthly_data = {}
    for enrollment in enrollments:
        month_key = enrollment.enrolled_at.strftime('%Y-%m')
        monthly_data[month_key] = monthly_data.get(month_key, 0) + 1
    
    # Get course-wise enrollment data
    course_data = {}
    for enrollment in enrollments:
        if enrollment.status == 'approved':
            course = Course.query.get(enrollment.course_id)
            if course:
                course_data[course.title] = course_data.get(course.title, 0) + 1
    
    courses = Course.query.all()
    
    return render_template('admin_dashboard.html',
                         total_students=total_students,
                         total_courses=total_courses,
                         total_enrollments=total_enrollments,
                         monthly_data=monthly_data,
                         course_data=course_data,
                         courses=courses)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    enrollments = Enrollment.query.filter_by(student_id=user.id).all()
    
    return render_template('profile.html', user=user, enrollments=enrollments)

@app.route('/admin-profile')
def admin_profile():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    admin = Admin.query.get(session['admin_id'])
    return render_template('admin_profile.html', admin=admin)

@app.route('/admin/delete-account', methods=['POST'])
def admin_delete_account():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    admin = Admin.query.get(session['admin_id'])
    if not admin:
        session.clear()
        return redirect(url_for('landing'))
    # Detach admin_id from chat messages to avoid FK issues
    ChatMessage.query.filter_by(admin_id=admin.id).update({ChatMessage.admin_id: None})
    db.session.delete(admin)
    db.session.commit()
    session.clear()
    flash('Your admin account has been deleted.', 'success')
    return redirect(url_for('landing'))

@app.route('/enroll/<int:course_id>')
def enroll(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if already enrolled
    existing = Enrollment.query.filter_by(
        student_id=session['user_id'],
        course_id=course_id
    ).first()
    
    if existing:
        flash('You are already enrolled in this course', 'info')
        return redirect(url_for('dashboard'))
    
    # Create enrollment
    enrollment = Enrollment(
        student_id=session['user_id'],
        course_id=course_id,
        status='pending'
    )
    db.session.add(enrollment)
    db.session.commit()
    
    # Schedule auto-approval after 5 minutes
    timer = Timer(300.0, auto_approve_enrollment, args=[enrollment.id])
    timer.start()
    enrollment_timers[enrollment.id] = timer
    
    flash('Enrollment request submitted. You will receive an email once approved.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/course/<int:course_id>')
def view_course(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(
        student_id=session['user_id'],
        course_id=course_id,
        status='approved'
    ).first()
    
    if not enrollment:
        flash('You must enroll and be approved to view this course', 'error')
        return redirect(url_for('dashboard'))
    
    chapters = Chapter.query.filter_by(course_id=course_id).order_by(Chapter.chapter_number).all()
    
    # Get progress
    progress = {}
    for chapter in chapters:
        student_progress = StudentProgress.query.filter_by(
            student_id=session['user_id'],
            chapter_id=chapter.id
        ).first()
        progress[chapter.id] = student_progress.completed if student_progress else False
    
    # Determine completion
    all_completed = all(progress.get(ch.id, False) for ch in chapters) if chapters else False
    return render_template('course_view.html', 
                         course=course, 
                         chapters=chapters,
                         progress=progress,
                         all_completed=all_completed)

@app.route('/chapter/<int:chapter_id>')
def view_chapter(chapter_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    course = chapter.course
    
    # Check enrollment
    enrollment = Enrollment.query.filter_by(
        student_id=session['user_id'],
        course_id=course.id,
        status='approved'
    ).first()
    
    if not enrollment:
        return redirect(url_for('dashboard'))
    
    # Get all chapters for navigation
    all_chapters = Chapter.query.filter_by(course_id=course.id).order_by(Chapter.chapter_number).all()
    current_index = next((i for i, ch in enumerate(all_chapters) if ch.id == chapter.id), 0)
    
    prev_chapter = all_chapters[current_index - 1] if current_index > 0 else None
    next_chapter = all_chapters[current_index + 1] if current_index < len(all_chapters) - 1 else None
    
    # Get progress
    student_progress = StudentProgress.query.filter_by(
        student_id=session['user_id'],
        chapter_id=chapter.id
    ).first()
    
    return render_template('chapter_view.html',
                         chapter=chapter,
                         course=course,
                         prev_chapter=prev_chapter,
                         next_chapter=next_chapter,
                         progress=student_progress)

@app.route('/certificate/<int:course_id>')
def certificate(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    course = Course.query.get_or_404(course_id)
    # Verify full completion
    chapters = Chapter.query.filter_by(course_id=course_id).all()
    if not chapters:
        flash('No chapters found for this course', 'error')
        return redirect(url_for('view_course', course_id=course_id))
    completed_count = StudentProgress.query.filter_by(student_id=user.id, course_id=course_id, completed=True).count()
    if completed_count < len(chapters):
        flash('Complete all chapters to download the certificate', 'error')
        return redirect(url_for('view_course', course_id=course_id))

    # Generate certificate PDF in memory
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Try to draw a background image if available
    import os
    bg_path = os.path.join(app.root_path, 'static', 'img', 'certificate_bg.png')
    try:
        if os.path.exists(bg_path):
            pdf.drawImage(ImageReader(bg_path), 0, 0, width=width, height=height)
    except Exception as e:
        print('Certificate background error:', e)

    # Title
    pdf.setFillColorRGB(0.82, 0.05, 0.05)  # accent-ish
    pdf.setFont('Helvetica-Bold', 28)
    pdf.drawCentredString(width/2, height-120, 'CERTIFICATE OF COMPLETION')

    # Presented to
    pdf.setFillColorRGB(1,1,1)
    pdf.setFont('Helvetica', 14)
    pdf.drawCentredString(width/2, height-160, f'is presented to')

    # Name
    pdf.setFillColorRGB(1,1,1)
    pdf.setFont('Helvetica-Bold', 24)
    pdf.drawCentredString(width/2, height-200, user.name)

    # Course
    pdf.setFont('Helvetica', 14)
    pdf.drawCentredString(width/2, height-230, f'for successfully completing {course.title}')

    # Date
    pdf.setFont('Helvetica-Oblique', 12)
    pdf.drawCentredString(width/2, height-260, datetime.datetime.utcnow().strftime('Dated: %d %B %Y (UTC)'))

    # Seal
    pdf.circle(width/2, 140, 28, stroke=1, fill=0)
    pdf.setFont('Helvetica', 10)
    pdf.drawCentredString(width/2, 120, 'CourseHub')

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    from flask import send_file
    filename = f'CourseHub-Certificate-{course.title}-{user.name}.pdf'
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

@app.route('/complete-checkpoint/<int:chapter_id>', methods=['POST'])
def complete_checkpoint(chapter_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    chapter = Chapter.query.get_or_404(chapter_id)
    
    # Check enrollment
    enrollment = Enrollment.query.filter_by(
        student_id=session['user_id'],
        course_id=chapter.course_id,
        status='approved'
    ).first()
    
    if not enrollment:
        return jsonify({'success': False, 'message': 'Not enrolled'})
    
    # Update or create progress
    student_progress = StudentProgress.query.filter_by(
        student_id=session['user_id'],
        chapter_id=chapter_id
    ).first()
    
    if not student_progress:
        student_progress = StudentProgress(
            student_id=session['user_id'],
            course_id=chapter.course_id,
            chapter_id=chapter_id,
            completed=True,
            completed_at=datetime.datetime.utcnow()
        )
        db.session.add(student_progress)
    else:
        student_progress.completed = True
        student_progress.completed_at = datetime.datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/admin/courses')
def admin_courses():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    courses = Course.query.all()
    return render_template('admin_courses.html', courses=courses)

@app.route('/admin/create-course', methods=['GET', 'POST'])
def admin_create_course():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        thumbnail = request.form.get('thumbnail')
        total_chapters = int(request.form.get('total_chapters', 0))
        total_hours = float(request.form.get('total_hours', 0))
        
        course = Course(
            title=title,
            description=description,
            thumbnail=thumbnail,
            total_chapters=total_chapters,
            total_hours=total_hours
        )
        db.session.add(course)
        db.session.commit()
        
        flash('Course created successfully', 'success')
        return redirect(url_for('admin_courses'))
    
    return render_template('admin_create_course.html')

@app.route('/admin/edit-course/<int:course_id>', methods=['GET', 'POST'])
def admin_edit_course(course_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.title = request.form.get('title')
        course.description = request.form.get('description')
        course.thumbnail = request.form.get('thumbnail')
        course.total_chapters = int(request.form.get('total_chapters', 0))
        course.total_hours = float(request.form.get('total_hours', 0))
        
        db.session.commit()
        flash('Course updated successfully', 'success')
        return redirect(url_for('admin_courses'))
    
    return render_template('admin_edit_course.html', course=course)

@app.route('/admin/enrollments')
def admin_enrollments():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    enrollments = Enrollment.query.order_by(Enrollment.enrolled_at.desc()).all()
    return render_template('admin_enrollments.html', enrollments=enrollments)

@app.route('/admin/enrollments/<int:enrollment_id>/approve', methods=['POST'])
def admin_approve_enrollment(enrollment_id):
    if 'admin_id' not in session:
        return jsonify({'success': False, 'error': 'Not authorized'})
    
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    if enrollment.status != 'pending':
        return jsonify({'success': False, 'error': 'Enrollment already processed'})
    
    # Cancel the auto-approval timer if it exists
    if enrollment_id in enrollment_timers:
        enrollment_timers[enrollment_id].cancel()
        del enrollment_timers[enrollment_id]
    
    # Approve the enrollment
    enrollment.status = 'approved'
    enrollment.approved_at = datetime.datetime.utcnow()
    db.session.commit()
    
    # Create notification for student
    student = User.query.get(enrollment.student_id)
    course = Course.query.get(enrollment.course_id)
    notification = Notification(
        user_id=student.id,
        message=f"Your enrollment for {course.title} has been approved by admin! You can now start learning.",
        type='success'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Enrollment approved successfully'})

@app.route('/admin/enrollments/<int:enrollment_id>/reject', methods=['POST'])
def admin_reject_enrollment(enrollment_id):
    if 'admin_id' not in session:
        return jsonify({'success': False, 'error': 'Not authorized'})
    
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    if enrollment.status != 'pending':
        return jsonify({'success': False, 'error': 'Enrollment already processed'})
    
    # Cancel the auto-approval timer if it exists
    if enrollment_id in enrollment_timers:
        enrollment_timers[enrollment_id].cancel()
        del enrollment_timers[enrollment_id]
    
    # Reject the enrollment
    enrollment.status = 'rejected'
    db.session.commit()
    
    # Create notification for student
    student = User.query.get(enrollment.student_id)
    course = Course.query.get(enrollment.course_id)
    notification = Notification(
        user_id=student.id,
        message=f"Your enrollment for {course.title} has been rejected. Please contact admin for more information.",
        type='error'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Enrollment rejected successfully'})

@app.route('/admin/students')
def admin_students():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    students = User.query.all()
    return render_template('admin_students.html', students=students)

# Chat - Student view
@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    student_id = session['user_id']
    messages = ChatMessage.query.filter_by(student_id=student_id).order_by(ChatMessage.created_at).all()
    return render_template('chat.html', messages=messages)

# Chat - Admin list and per-student view
@app.route('/admin/chats')
def admin_chats():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    # distinct students with messages
    student_ids = db.session.query(ChatMessage.student_id).distinct().all()
    students = User.query.filter(User.id.in_([sid for (sid,) in student_ids])).all()
    return render_template('admin_chats.html', students=students)

@app.route('/admin/group-chat')
def admin_group_chat():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    return render_template('admin_group_chat.html')

@app.route('/admin/student-group-chat')
def admin_student_group_chat():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    return render_template('admin_student_group_chat.html')

@app.route('/admin/chat/<int:student_id>')
def admin_chat(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    messages = ChatMessage.query.filter_by(student_id=student_id).order_by(ChatMessage.created_at).all()
    student = User.query.get_or_404(student_id)
    return render_template('admin_chat.html', messages=messages, student=student)

@app.route('/api/chat/send', methods=['POST'])
def api_chat_send():
    data = request.json or {}
    text = data.get('message', '').strip()
    student_id = data.get('student_id')
    if not text:
        return jsonify({'success': False})
    if 'user_id' in session:
        # student sending
        msg = ChatMessage(student_id=session['user_id'], admin_id=None, sender='student', message=text)
        db.session.add(msg)
        db.session.commit()
        return jsonify({'success': True, 'id': msg.id, 'time': msg.created_at.strftime('%H:%M')})
    elif 'admin_id' in session:
        if not student_id:
            return jsonify({'success': False})
        msg = ChatMessage(student_id=student_id, admin_id=session['admin_id'], sender='admin', message=text)
        db.session.add(msg)
        db.session.commit()
        return jsonify({'success': True, 'id': msg.id, 'time': msg.created_at.strftime('%H:%M')})
    return jsonify({'success': False})

@app.route('/api/chat/history/<int:student_id>')
def api_chat_history(student_id):
    if 'user_id' in session and session['user_id'] != student_id:
        return jsonify({'success': False})
    if 'admin_id' not in session and 'user_id' not in session:
        return jsonify({'success': False})
    messages = ChatMessage.query.filter_by(student_id=student_id).order_by(ChatMessage.created_at).all()
    out = [
        {
            'id': m.id,
            'sender': m.sender,
            'message': m.message,
            'time': m.created_at.strftime('%Y-%m-%d %H:%M')
        } for m in messages
    ]
    return jsonify({'success': True, 'messages': out})

@app.route('/api/chat/history-all')
def api_chat_history_all():
    if 'admin_id' not in session:
        return jsonify({'success': False})
    messages = ChatMessage.query.order_by(ChatMessage.created_at).all()
    # Build sender display
    def sender_of(m):
        return 'admin' if m.sender == 'admin' else (User.query.get(m.student_id).name if m.student_id else 'Student')
    out = [
        {
            'id': m.id,
            'sender': sender_of(m),
            'sender_type': 'admin' if m.sender == 'admin' else 'student',
            'message': m.message,
            'time': m.created_at.strftime('%Y-%m-%d %H:%M')
        } for m in messages
    ]
    return jsonify({'success': True, 'messages': out})

@app.route('/api/chat/history-students')
def api_chat_history_students():
    if 'admin_id' not in session:
        return jsonify({'success': False})
    messages = ChatMessage.query.filter(ChatMessage.sender == 'student').order_by(ChatMessage.created_at).all()
    out = [
        {
            'id': m.id,
            'sender': (User.query.get(m.student_id).name if m.student_id else 'Student'),
            'message': m.message,
            'time': m.created_at.strftime('%Y-%m-%d %H:%M')
        } for m in messages
    ]
    return jsonify({'success': True, 'messages': out})

@app.route('/api/chat/send-admin-broadcast', methods=['POST'])
def api_chat_send_admin_broadcast():
    if 'admin_id' not in session:
        return jsonify({'success': False})
    data = request.json or {}
    text = (data.get('message') or '').strip()
    if not text:
        return jsonify({'success': False})
    # Fan-out to all students (who exist). Could be optimized later.
    students = User.query.all()
    for s in students:
        msg = ChatMessage(student_id=s.id, admin_id=session['admin_id'], sender='admin', message=text)
        db.session.add(msg)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/student-progress/<int:student_id>')
def admin_student_progress(student_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    student = User.query.get_or_404(student_id)
    progress = StudentProgress.query.filter_by(student_id=student_id).all()
    
    return render_template('admin_student_progress.html', student=student, progress=progress)

@app.route('/admin/course/<int:course_id>/students')
def admin_course_students(course_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    course = Course.query.get_or_404(course_id)
    enrollments = Enrollment.query.filter_by(course_id=course_id, status='approved').all()
    
    return render_template('admin_course_students.html', course=course, enrollments=enrollments)

@app.route('/admin/add-chapter/<int:course_id>', methods=['GET', 'POST'])
def admin_add_chapter(course_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        chapter_number = int(request.form.get('chapter_number'))
        title = request.form.get('title')
        content = request.form.get('content')
        checkpoint = request.form.get('checkpoint')
        
        chapter = Chapter(
            course_id=course_id,
            chapter_number=chapter_number,
            title=title,
            content=content,
            checkpoint=checkpoint
        )
        db.session.add(chapter)
        db.session.commit()
        
        flash('Chapter added successfully', 'success')
        return redirect(url_for('admin_edit_course', course_id=course_id))
    
    # Get next chapter number
    last_chapter = Chapter.query.filter_by(course_id=course_id).order_by(Chapter.chapter_number.desc()).first()
    next_number = (last_chapter.chapter_number + 1) if last_chapter else 1
    
    return render_template('admin_add_chapter.html', course=course, next_number=next_number)

@app.route('/api/mark-notification-read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized'})
    
    notification.read = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/mark-all-notifications-read', methods=['POST'])
def mark_all_notifications_read():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    Notification.query.filter_by(user_id=session['user_id'], read=False).update({'read': True})
    db.session.commit()
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

@app.route('/api/track-progress', methods=['POST'])
def track_progress():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    data = request.json
    chapter_id = data.get('chapter_id')
    time_spent = data.get('time_spent', 0)
    
    progress = StudentProgress.query.filter_by(
        student_id=session['user_id'],
        chapter_id=chapter_id
    ).first()
    
    if progress:
        progress.time_spent += time_spent / 3600  # Convert seconds to hours
    else:
        chapter = Chapter.query.get(chapter_id)
        if chapter:
            progress = StudentProgress(
                student_id=session['user_id'],
                course_id=chapter.course_id,
                chapter_id=chapter_id,
                time_spent=time_spent / 3600
            )
            db.session.add(progress)
    
    db.session.commit()
    
    # Use AI learning tracker to track interaction
    tracker = AILearningTracker()
    tracker.track_chapter_interaction(session['user_id'], chapter_id, time_spent)
    
    return jsonify({'success': True})

@app.route('/api/ai-recommendations/<int:chapter_id>')
def ai_recommendations(chapter_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    chapter = Chapter.query.get_or_404(chapter_id)
    tracker = AILearningTracker()
    recommendations = tracker.get_recommended_content(
        session['user_id'],
        chapter.course_id,
        chapter_id
    )
    
    return jsonify(recommendations)

@app.route('/api/learning-report/<int:course_id>')
def learning_report(course_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    tracker = AILearningTracker()
    report = tracker.generate_learning_report(session['user_id'], course_id)
    
    if report:
        return jsonify(report)
    else:
        return jsonify({'error': 'No progress data found'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
