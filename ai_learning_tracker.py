"""
AI Learning Tracker for CourseHub
Tracks student learning patterns and adapts course content
"""
import sqlite3
from datetime import datetime, timedelta
import json

DB_PATH = 'coursehub.db'

class AILearningTracker:
    def __init__(self):
        self.db_path = DB_PATH
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def calculate_learning_speed(self, student_id, course_id):
        """Calculate how fast a student is learning"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all progress for this course
        cursor.execute("""
            SELECT sp.time_spent, sp.completed, sp.completed_at, c.total_hours
            FROM student_progress sp
            JOIN chapter c ON sp.chapter_id = c.id
            WHERE sp.student_id = ? AND sp.course_id = ?
        """, (student_id, course_id))
        
        progress_data = cursor.fetchall()
        conn.close()
        
        if not progress_data:
            return "normal"  # Default speed
        
        total_time = sum(row[0] for row in progress_data if row[0])
        completed_chapters = sum(1 for row in progress_data if row[1])
        total_chapters = len(progress_data)
        
        if total_chapters == 0:
            return "normal"
        
        completion_rate = completed_chapters / total_chapters
        
        # Calculate average time per chapter
        avg_time_per_chapter = total_time / completed_chapters if completed_chapters > 0 else 0
        
        # Determine learning speed
        if completion_rate > 0.8 and avg_time_per_chapter < 1.5:
            return "fast"
        elif completion_rate < 0.5 or avg_time_per_chapter > 3:
            return "slow"
        else:
            return "normal"
    
    def get_recommended_content(self, student_id, course_id, chapter_id):
        """Get recommended content based on learning pattern"""
        learning_speed = self.calculate_learning_speed(student_id, course_id)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current chapter
        cursor.execute("""
            SELECT content, checkpoint
            FROM chapter
            WHERE id = ?
        """, (chapter_id,))
        
        chapter = cursor.fetchone()
        
        # Get student progress on this chapter
        cursor.execute("""
            SELECT completed, time_spent
            FROM student_progress
            WHERE student_id = ? AND chapter_id = ?
        """, (student_id, chapter_id))
        
        progress = cursor.fetchone()
        conn.close()
        
        recommendations = {
            "learning_speed": learning_speed,
            "content_focus": [],
            "suggested_time": 2.0,  # hours
            "difficulty_adjustment": "normal"
        }
        
        if learning_speed == "fast":
            recommendations["content_focus"] = ["advanced", "practicals", "challenges"]
            recommendations["suggested_time"] = 1.5
            recommendations["difficulty_adjustment"] = "increase"
        elif learning_speed == "slow":
            recommendations["content_focus"] = ["basics", "examples", "step-by-step"]
            recommendations["suggested_time"] = 3.0
            recommendations["difficulty_adjustment"] = "decrease"
        else:
            recommendations["content_focus"] = ["balanced", "examples", "practice"]
            recommendations["suggested_time"] = 2.0
        
        # Check if student is struggling with current chapter
        if progress and progress[0] == False and progress[1] and progress[1] > 2.5:
            recommendations["content_focus"].append("review")
            recommendations["difficulty_adjustment"] = "decrease"
        
        return recommendations
    
    def track_chapter_interaction(self, student_id, chapter_id, time_spent):
        """Track how much time student spends on a chapter"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Update or create progress record
        cursor.execute("""
            SELECT id FROM student_progress
            WHERE student_id = ? AND chapter_id = ?
        """, (student_id, chapter_id))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE student_progress
                SET time_spent = time_spent + ?
                WHERE id = ?
            """, (time_spent / 3600, existing[0]))  # Convert seconds to hours
        else:
            # Get course_id from chapter
            cursor.execute("SELECT course_id FROM chapter WHERE id = ?", (chapter_id,))
            course_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO student_progress (student_id, course_id, chapter_id, time_spent)
                VALUES (?, ?, ?, ?)
            """, (student_id, course_id, chapter_id, time_spent / 3600))
        
        conn.commit()
        conn.close()
    
    def get_next_chapter_recommendation(self, student_id, course_id):
        """Recommend next chapter based on learning pattern"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all chapters and their completion status
        cursor.execute("""
            SELECT c.id, c.chapter_number, c.title,
                   CASE WHEN sp.completed = 1 THEN 1 ELSE 0 END as completed
            FROM chapter c
            LEFT JOIN student_progress sp ON c.id = sp.chapter_id AND sp.student_id = ?
            WHERE c.course_id = ?
            ORDER BY c.chapter_number
        """, (student_id, course_id))
        
        chapters = cursor.fetchall()
        conn.close()
        
        # Find first incomplete chapter
        for chapter in chapters:
            if chapter[3] == 0:  # Not completed
                return {
                    "recommended": chapter[0],  # chapter_id
                    "reason": "next_incomplete"
                }
        
        # All chapters completed
        return {
            "recommended": None,
            "reason": "all_completed",
            "message": "Congratulations! You've completed all chapters."
        }
    
    def generate_learning_report(self, student_id, course_id):
        """Generate a learning analytics report"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get course details
        cursor.execute("SELECT title, total_chapters, total_hours FROM course WHERE id = ?", (course_id,))
        course = cursor.fetchone()
        
        # Get progress statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_chapters,
                SUM(CASE WHEN sp.completed = 1 THEN 1 ELSE 0 END) as completed_chapters,
                SUM(sp.time_spent) as total_time_spent,
                AVG(sp.time_spent) as avg_time_per_chapter
            FROM chapter c
            LEFT JOIN student_progress sp ON c.id = sp.chapter_id AND sp.student_id = ?
            WHERE c.course_id = ?
        """, (student_id, course_id))
        
        stats = cursor.fetchone()
        conn.close()
        
        if not stats or not stats[0]:
            return None
        
        total_chapters, completed_chapters, total_time, avg_time = stats
        
        completion_percentage = (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0
        estimated_remaining_time = (total_chapters - completed_chapters) * (avg_time or 2.0)
        
        learning_speed = self.calculate_learning_speed(student_id, course_id)
        
        return {
            "course_title": course[0],
            "total_chapters": total_chapters,
            "completed_chapters": completed_chapters or 0,
            "completion_percentage": round(completion_percentage, 1),
            "total_time_spent": round(total_time or 0, 2),
            "avg_time_per_chapter": round(avg_time or 0, 2),
            "estimated_remaining_time": round(estimated_remaining_time, 2),
            "learning_speed": learning_speed,
            "recommendations": self._get_overall_recommendations(completion_percentage, learning_speed)
        }
    
    def _get_overall_recommendations(self, completion_rate, learning_speed):
        """Generate overall learning recommendations"""
        recommendations = []
        
        if completion_rate < 30:
            recommendations.append("Focus on completing the basics before moving to advanced topics")
        elif completion_rate < 70:
            recommendations.append("Great progress! Keep up the momentum")
        else:
            recommendations.append("You're almost done! Finish strong")
        
        if learning_speed == "slow":
            recommendations.append("Take your time to understand concepts fully")
            recommendations.append("Review previous chapters if needed")
        elif learning_speed == "fast":
            recommendations.append("Consider exploring advanced topics and additional resources")
        
        return recommendations

# API endpoint integration (to be used in Flask app)
def get_learning_recommendations(student_id, course_id, chapter_id):
    """Get AI-generated learning recommendations"""
    tracker = AILearningTracker()
    return tracker.get_recommended_content(student_id, course_id, chapter_id)

def get_learning_report(student_id, course_id):
    """Get learning analytics report"""
    tracker = AILearningTracker()
    return tracker.generate_learning_report(student_id, course_id)

