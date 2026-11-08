from datetime import date, time, timedelta
from django.utils import timezone
from categories.models import Category
from timetable.models import Activity, ActivityInstanceLog
from tasks.models import Task, SubTask
from learning.models import LearningTopic, LearningResource, LearningMilestone, StudySession
from habits.models import Habit, HabitLog
from goals.models import Goal, GoalMilestone
from notes.models import Note
from notifications.models import Notification

def seed_user_data(user):
    """
    Seeds initial dynamic categories and records for a user.
    All data is stored in the database and 100% editable by the user.
    """
    # 1. Categories
    cat_work, _ = Category.objects.get_or_create(
        user=user, name="Deep Work & Projects",
        defaults={"color": "#7C6CFF", "icon": "briefcase", "type": "work"}
    )
    cat_learn, _ = Category.objects.get_or_create(
        user=user, name="Skill Mastery",
        defaults={"color": "#38BDF8", "icon": "book-open", "type": "study"}
    )
    cat_health, _ = Category.objects.get_or_create(
        user=user, name="Fitness & Wellness",
        defaults={"color": "#22C55E", "icon": "heart-pulse", "type": "health"}
    )
    cat_personal, _ = Category.objects.get_or_create(
        user=user, name="Personal & Life",
        defaults={"color": "#F59E0B", "icon": "user", "type": "personal"}
    )

    today = date.today()

    # 2. Timetable Activities
    if not Activity.objects.filter(user=user).exists():
        # Morning routine (Selected weekdays Mon-Fri)
        act1 = Activity.objects.create(
            user=user,
            title="Morning Routine & Exercise",
            description="Stretching, hydration, and light cardio workout",
            category=cat_health,
            date=today,
            start_time=time(7, 0),
            end_time=time(8, 0),
            priority="high",
            reminder_minutes=15,
            recurrence="selected_weekdays",
            selected_weekdays=[0, 1, 2, 3, 4], # Mon-Fri
            color="#22C55E"
        )
        # Mark completed today to test stats calculation
        ActivityInstanceLog.objects.create(
            activity=act1,
            user=user,
            date=today,
            status="completed"
        )

        # Deep work block (Daily)
        Activity.objects.create(
            user=user,
            title="Focus Work Block: Core Project",
            description="High-priority development and deep focus tasks",
            category=cat_work,
            date=today,
            start_time=time(9, 30),
            end_time=time(12, 0),
            priority="urgent",
            reminder_minutes=10,
            recurrence="daily",
            color="#7C6CFF"
        )

        # Afternoon Learning Session (Daily)
        Activity.objects.create(
            user=user,
            title="Focused Study & Skill Practice",
            description="Dedicated study session on active learning topic",
            category=cat_learn,
            date=today,
            start_time=time(15, 0),
            end_time=time(16, 30),
            priority="high",
            reminder_minutes=15,
            recurrence="daily",
            color="#38BDF8"
        )

        # Evening Review & Planning (Daily)
        Activity.objects.create(
            user=user,
            title="Daily Reflection & Next Day Planning",
            description="Review accomplishments, update tasks, and prepare for tomorrow",
            category=cat_personal,
            date=today,
            start_time=time(20, 0),
            end_time=time(20, 30),
            priority="medium",
            reminder_minutes=10,
            recurrence="daily",
            color="#F59E0B"
        )

    # 3. Tasks
    if not Task.objects.filter(user=user).exists():
        t1 = Task.objects.create(
            user=user,
            title="Review weekly progress and update productivity targets",
            description="Audit tasks completed vs planned and calibrate schedule",
            category=cat_personal,
            priority="high",
            status="todo",
            due_date=today,
            estimated_minutes=30,
            tags=["planning", "review"]
        )
        SubTask.objects.create(task=t1, title="Review completed timetable activities", is_completed=True, order=0)
        SubTask.objects.create(task=t1, title="Update active goal milestones", is_completed=False, order=1)
        SubTask.objects.create(task=t1, title="Set next week priorities", is_completed=False, order=2)

        t2 = Task.objects.create(
            user=user,
            title="Complete project technical architecture diagram",
            description="Document system design, data flow, and components",
            category=cat_work,
            priority="urgent",
            status="in_progress",
            due_date=today,
            estimated_minutes=90,
            tags=["work", "architecture"]
        )

        t3 = Task.objects.create(
            user=user,
            title="Finish module practice exercises",
            description="Work through exercises in the current learning track",
            category=cat_learn,
            priority="medium",
            status="completed",
            due_date=today,
            estimated_minutes=45,
            completed_at=timezone.now(),
            tags=["learning", "practice"]
        )

    # 4. Learning Topics
    if not LearningTopic.objects.filter(user=user).exists():
        topic1 = LearningTopic.objects.create(
            user=user,
            title="Advanced System Architecture",
            description="Designing scalable, resilient and maintainable systems",
            category=cat_learn,
            target_hours=40.0,
            logged_hours=14.5,
            color="#7C6CFF",
            icon="server",
            status="active"
        )
        LearningResource.objects.create(
            topic=topic1,
            title="Designing Data-Intensive Applications",
            type="book",
            is_completed=True
        )
        LearningResource.objects.create(
            topic=topic1,
            title="Distributed Systems Foundations",
            type="course",
            is_completed=False
        )
        LearningMilestone.objects.create(
            topic=topic1,
            title="Complete foundational architecture patterns review",
            target_date=today + timedelta(days=14),
            is_completed=True
        )
        LearningMilestone.objects.create(
            topic=topic1,
            title="Build resilient microservices prototype",
            target_date=today + timedelta(days=30),
            is_completed=False
        )

        # Add a study session
        StudySession.objects.create(
            user=user,
            topic=topic1,
            category=cat_learn,
            title="Microservices Patterns Study",
            session_type="pomodoro",
            duration_minutes=50,
            notes="Covered saga pattern and event sourcing concepts",
            rating=5
        )

    # 5. Habits & Routines
    if not Habit.objects.filter(user=user).exists():
        h1 = Habit.objects.create(
            user=user,
            title="Drink 2.5L Water Daily",
            description="Maintain proper hydration throughout the day",
            category=cat_health,
            frequency="daily",
            time_of_day="anytime",
            color="#38BDF8",
            icon="droplet",
            current_streak=5,
            best_streak=14
        )
        HabitLog.objects.create(habit=h1, user=user, date=today, completed=True)

        h2 = Habit.objects.create(
            user=user,
            title="30 Minutes Daily Reading / Study",
            description="Consistent daily learning habit",
            category=cat_learn,
            frequency="daily",
            time_of_day="evening",
            color="#7C6CFF",
            icon="book-open",
            current_streak=3,
            best_streak=9
        )
        HabitLog.objects.create(habit=h2, user=user, date=today, completed=True)

        h3 = Habit.objects.create(
            user=user,
            title="Morning Stretch & Physical Movement",
            description="Mobility exercises before work",
            category=cat_health,
            frequency="weekdays",
            time_of_day="morning",
            color="#22C55E",
            icon="activity",
            current_streak=4,
            best_streak=10
        )
        HabitLog.objects.create(habit=h3, user=user, date=today, completed=True)

    # 6. Goals
    if not Goal.objects.filter(user=user).exists():
        g1 = Goal.objects.create(
            user=user,
            title="Master Cloud Infrastructure & DevOps Pipeline",
            description="Achieve production proficiency in automated deployments and monitoring",
            category=cat_work,
            timeframe="medium_term",
            target_date=today + timedelta(days=60),
            target_value=100.0,
            current_value=45.0,
            unit="%",
            status="in_progress"
        )
        GoalMilestone.objects.create(goal=g1, title="Complete CI/CD automation pipeline", is_completed=True)
        GoalMilestone.objects.create(goal=g1, title="Implement automated test suite in pipeline", is_completed=False)

        g2 = Goal.objects.create(
            user=user,
            title="Read 12 Technical & Leadership Books This Year",
            description="Deepen broad domain expertise through regular reading",
            category=cat_learn,
            timeframe="long_term",
            target_date=today + timedelta(days=180),
            target_value=12.0,
            current_value=5.0,
            unit="books",
            status="in_progress"
        )

    # 7. Notes
    if not Note.objects.filter(user=user).exists():
        Note.objects.create(
            user=user,
            title="Weekly Objectives & Productivity Principles",
            content="""# My Productivity Manifesto
- Focus on high-leverage activities first.
- Maintain consistent routines over sporadic bursts.
- Protect deep work blocks from interruptions.
- Always review and plan the day ahead in the evening.
""",
            category=cat_personal,
            is_pinned=True,
            color="#151D2D",
            tags=["manifesto", "mindset", "productivity"]
        )

    # 8. Notifications
    if not Notification.objects.filter(user=user).exists():
        Notification.objects.create(
            user=user,
            title="Welcome to MyDaily!",
            message="Your dynamic daily productivity workspace is ready. You can customize categories, activities, goals, and habits at any time.",
            type="system",
            link="/settings"
        )
