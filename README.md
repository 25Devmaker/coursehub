# CourseHub - Online Course Registration Platform

A modern, dark-themed online course registration system built with Flask, featuring student enrollment, admin management, automated enrollment approval, and AI-powered learning tracking.

## Features

### Student Features
- **Registration & Authentication**
  - Email-based signup with OTP verification
  - Password creation during signup
  - USN number and personal/college email registration
  - Secure login system

- **Course Management**
  - Browse available courses
  - Enroll in courses (auto-approved after 5 minutes)
  - View enrolled courses
  - Track learning progress

- **Learning Experience**
  - Interactive course viewer with chapters
  - Checkpoint system with completion tracking
  - Code editor for practice
  - Navigation between chapters (Previous/Next)
  - Progress tracking

### Admin Features
- **Account Management**
  - Admin registration with full details
  - Admin login (email: admin@branch.edu.nitte.in, password: admin@2027)
  - Profile management

- **Course Management**
  - Create new courses
  - Edit existing courses
  - Add chapters with content and checkpoints
  - Course thumbnail support
  - Set total chapters and hours

- **Student Management**
  - View all enrolled students
  - View student progress per course
  - Enrollment statistics and analytics
  - Bar charts for monthly enrollments
  - Pie charts for course-wise enrollments

### Automation Features
- **Auto-Enrollment Bot**
  - Python bot that automatically approves enrollments after 5 minutes
  - Email notifications to students upon approval
  - Can run as a separate service

- **AI Learning Tracker**
  - Tracks student learning patterns
  - Adapts course content based on learning speed
  - Provides learning recommendations
  - Generates learning analytics reports

## Courses Included

1. Java
2. Python
3. C++
4. C
5. Computer Networks
6. Office Automation Tools
7. SQL
8. Use of AI

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Database**: SQLite
- **Visualization**: Chart.js
- **Code Editor**: CodeMirror

## Installation

1. **Clone the repository**
   ```bash
   cd coursehub
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up email configuration**
   - Set environment variables for email:
     ```bash
     export MAIL_USERNAME="your-email@gmail.com"
     export MAIL_PASSWORD="your-app-password"
     ```
   - Or edit `app.py` directly with your email credentials

4. **Initialize the database**
   ```bash
   python app.py
   ```
   The database will be created automatically with initial courses.

## Running the Application

1. **Start the Flask application**
   ```bash
   python app.py
   ```

2. **Start the auto-enrollment bot (optional, separate terminal)**
   ```bash
   python bot.py
   ```

3. **Access the application**
   - Open browser: `http://localhost:5000`
   - Landing page: `http://localhost:5000/`
   - Login page: `http://localhost:5000/login`

## Admin Login

After creating an admin account:
- Email: `admin@(branch).edu.nitte.in` (format you set during registration)
- Password: `admin@2027` (password you set during registration)

## Project Structure

```
coursehub/
├── app.py                  # Main Flask application
├── bot.py                  # Auto-enrollment approval bot
├── ai_learning_tracker.py  # AI learning tracking system
├── requirements.txt        # Python dependencies
├── coursehub.db            # SQLite database (created on first run)
├── templates/             # HTML templates
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   ├── signup.html
│   ├── verify_otp.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── course_view.html
│   ├── chapter_view.html
│   └── admin_*.html         # Admin templates
└── static/
    └── css/
        └── style.css       # Dark theme styles
```

## Theme

The website uses a dark "Nothing OS" theme with:
- Background: Very dark gray (hsl(0 0% 8%))
- Surface/Cards: Dark gray (hsl(0 0% 12%))
- Text: Almost pure white (hsl(0 0% 98%))
- Accent: Vibrant red (hsl(0 72.2% 50.6%))
- Borders: Subtle gray (hsl(0 0% 14.9%))

## API Endpoints

### Student Endpoints
- `POST /signup` - Student registration
- `POST /verify-otp` - OTP verification
- `POST /login` - User login
- `GET /dashboard` - Student dashboard
- `GET /profile` - Student profile
- `GET /enroll/<course_id>` - Enroll in a course
- `GET /course/<course_id>` - View course
- `GET /chapter/<chapter_id>` - View chapter content
- `POST /complete-checkpoint/<chapter_id>` - Complete checkpoint
- `POST /api/track-progress` - Track learning progress
- `GET /api/ai-recommendations/<chapter_id>` - Get AI recommendations
- `GET /api/learning-report/<course_id>` - Get learning report

### Admin Endpoints
- `POST /admin-signup` - Admin registration
- `GET /admin-dashboard` - Admin dashboard
- `GET /admin/courses` - Manage courses
- `POST /admin/create-course` - Create course
- `POST /admin/edit-course/<course_id>` - Edit course
- `POST /admin/add-chapter/<course_id>` - Add chapter
- `GET /admin/enrollments` - View all enrollments
- `GET /admin/students` - View all students
- `GET /admin/student-progress/<student_id>` - View student progress
- `GET /admin/course/<course_id>/students` - View course students

## Email Configuration

To enable email functionality (OTP and enrollment notifications), configure:

1. **Gmail** (recommended for development):
   - Enable "Less secure app access" or use App Password
   - Set `MAIL_USERNAME` and `MAIL_PASSWORD` environment variables

2. **Other SMTP servers**:
   - Update SMTP settings in `app.py` and `bot.py`

## Database Schema

### Tables
- `user` - Student accounts
- `admin` - Admin accounts
- `course` - Course information
- `chapter` - Course chapters
- `enrollment` - Student course enrollments
- `student_progress` - Learning progress tracking
- `otp_session` - Email OTP verification

## Development

### Adding New Courses
Courses can be added through the admin panel or directly in the database.

### Customizing AI Learning Tracker
Edit `ai_learning_tracker.py` to adjust learning speed calculations and recommendations.

### Running in Production
- Use a production WSGI server (e.g., Gunicorn)
- Set up proper database (PostgreSQL recommended)
- Configure environment variables
- Enable HTTPS
- Set up proper email service

## License

This project is for educational purposes.

## Contributing

Feel free to submit issues and enhancement requests!

