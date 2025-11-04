# How to See the Bot Working

The CourseHub system has **two ways** to automatically approve enrollments:

## Method 1: Built-in Timer (in app.py)
When a student enrolls, a Timer automatically approves after 5 minutes.

**How to see it working:**
1. Login as a student and enroll in a course
2. Check your dashboard - enrollment shows "Pending Approval"
3. Wait 5 minutes (300 seconds)
4. Refresh your dashboard - status changes to "Approved" ✅
5. Check your email for approval notification

## Method 2: Separate Bot Script (bot.py)
A standalone bot that checks for pending enrollments every minute.

### How to Run the Bot:

**Step 1:** Open a new terminal/command prompt (separate from Flask app)

**Step 2:** Navigate to project directory:
```bash
cd C:\Users\Administrator\Videos\coursehub
```

**Step 3:** Run the bot:
```bash
python bot.py
```

**Step 4:** You'll see output like:
```
CourseHub Auto-Enrollment Bot Started
Checking for pending enrollments every minute...
Processing enrollment 1 (enrolled at 2025-01-01 12:00:00)
Enrollment 1 approved and email sent to student@example.com
```

### Where to See Bot Activity:

1. **Terminal Output** - The bot prints messages when it processes enrollments
   - "Processing enrollment X"
   - "Enrollment X approved and email sent to..."
   
2. **Student Dashboard** - Status changes from "Pending" to "Approved"
   - URL: `http://localhost:5000/dashboard`
   - Check "My Enrolled Courses" section

3. **Admin Dashboard** - View all enrollments and their status
   - URL: `http://localhost:5000/admin/enrollments`
   - Shows enrollment date/time and approval date/time

4. **Email Notifications** - Students receive confirmation email
   - Subject: "Course Enrollment Approved - CourseHub"

5. **Student Profile** - Enrollment history with timestamps
   - URL: `http://localhost:5000/profile`

### Testing the Bot:

**Quick Test (Method 1 - Built-in Timer):**
1. Enroll in a course
2. Note the time
3. Wait 5 minutes
4. Refresh dashboard - should be approved

**Quick Test (Method 2 - Separate Bot):**
1. Run `python bot.py` in a separate terminal
2. Enroll in a course
3. Wait 5+ minutes
4. Check bot terminal - you'll see it processing
5. Check dashboard - enrollment approved

### Notes:
- The built-in Timer works automatically when Flask app is running
- The separate bot.py needs to be run separately
- Both methods approve enrollments after 5 minutes
- Email notifications require email configuration in app.py/bot.py

