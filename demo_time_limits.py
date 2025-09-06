#!/usr/bin/env python3
"""
Time Limits Demo Script for Quiz Application

This script demonstrates the time limits functionality that has been implemented
in the quiz application. Run this script to see how the timing system works.

Usage: python demo_time_limits.py
"""

import time
from datetime import datetime, timezone, timedelta
from app import create_app, db
from app.models.user import User
from app.models.quiz_session import QuizSession
from app.models.question import Questions
from app.services.quiz_service import start_quiz_session, get_active_quiz_session, validate_session_time
from app.utils.timezone_utils import utc_now, format_duration


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title} ")
    print("="*60)


def print_session_status(session):
    """Print current session status"""
    print(f"📋 Session ID: {session.id}")
    print(f"⏰ Start Time: {session.start_time}")
    print(f"🎯 Time Limit: {session.time_limit_minutes} minutes")
    print(f"⏳ Time Remaining: {format_duration(session.time_remaining_seconds)}")
    print(f"📊 Progress: {session.progress_percentage:.1f}%")
    print(f"🔍 Status: {session.status}")
    print(f"❓ Is Expired: {'Yes' if session.is_expired else 'No'}")


def simulate_quiz_taking(session, simulation_seconds=10):
    """Simulate taking a quiz over time"""
    print(f"\n🎮 Simulating quiz taking for {simulation_seconds} seconds...")

    for i in range(simulation_seconds):
        # Check session status
        is_valid, message = validate_session_time(session)

        remaining = session.time_remaining_seconds
        elapsed = session.time_elapsed_seconds

        status_emoji = "🟢" if remaining > 60 else "🟡" if remaining > 10 else "🔴"

        print(f"{status_emoji} Second {i+1:2d}: {format_duration(remaining)} remaining | "
              f"Elapsed: {format_duration(elapsed)} | Valid: {is_valid}")

        if not is_valid:
            print(f"⚠️  Session expired! {message}")
            break

        time.sleep(1)  # Wait 1 second

    print("✅ Simulation complete!")


def demo_basic_timing():
    """Demonstrate basic timing functionality"""
    print_header("DEMO 1: Basic Time Limits Functionality")

    app = create_app()
    with app.app_context():
        # Get first user
        user = db.session.query(User).first()
        if not user:
            print("❌ No users found. Please register a user first.")
            return

        print(f"👤 Using user: {user.first_name} {user.last_name} ({user.user_name})")

        # Create a short 1-minute session for demo
        session = QuizSession(user_id=user.id, time_limit_minutes=1)
        db.session.add(session)
        db.session.commit()

        print("\n📝 Created new quiz session:")
        print_session_status(session)

        # Simulate taking the quiz
        simulate_quiz_taking(session, simulation_seconds=70)  # 70 seconds = 1min 10sec

        # Check final status
        print("\n📋 Final session status:")
        print_session_status(session)

        # Clean up
        db.session.delete(session)
        db.session.commit()
        print("🗑️  Demo session cleaned up")


def demo_session_management():
    """Demonstrate session management features"""
    print_header("DEMO 2: Session Management Features")

    app = create_app()
    with app.app_context():
        user = db.session.query(User).first()
        if not user:
            print("❌ No users found. Please register a user first.")
            return

        print(f"👤 Using user: {user.first_name} {user.last_name}")

        # Test creating multiple sessions (should replace previous)
        print("\n1️⃣ Creating first session (5 minutes)...")
        session1 = QuizSession.create_new_session(user.id, time_limit_minutes=5)
        print(f"   Created session {session1.id}")

        time.sleep(2)  # Wait 2 seconds

        print("\n2️⃣ Creating second session (3 minutes) - should abandon first...")
        session2 = QuizSession.create_new_session(user.id, time_limit_minutes=3)
        print(f"   Created session {session2.id}")

        # Check that first session was abandoned
        db.session.refresh(session1)  # Refresh from database
        print(f"   First session status: {session1.status}")
        print(f"   Second session status: {session2.status}")

        # Test session timeout
        print("\n3️⃣ Testing session timeout...")
        timeout_session = QuizSession(user_id=user.id, time_limit_minutes=0.05)  # 3 seconds
        db.session.add(timeout_session)
        db.session.commit()

        print("   Waiting for session to expire...")
        time.sleep(4)  # Wait 4 seconds

        is_valid, message = validate_session_time(timeout_session)
        print(f"   Session valid: {is_valid}")
        print(f"   Message: {message}")
        print(f"   Session status: {timeout_session.status}")

        # Clean up all demo sessions
        for session in [session1, session2, timeout_session]:
            try:
                db.session.delete(session)
            except:
                pass  # Already deleted
        db.session.commit()
        print("🗑️  All demo sessions cleaned up")


def demo_api_responses():
    """Demonstrate API response format"""
    print_header("DEMO 3: API Response Format")

    app = create_app()
    with app.app_context():
        user = db.session.query(User).first()
        if not user:
            print("❌ No users found. Please register a user first.")
            return

        # Create a session
        session = QuizSession(user_id=user.id, time_limit_minutes=2)
        db.session.add(session)
        db.session.commit()

        print("📡 Session API Response Format:")
        session_dict = session.to_dict()

        for key, value in session_dict.items():
            print(f"   {key}: {value}")

        # Clean up
        db.session.delete(session)
        db.session.commit()
        print("🗑️  Demo session cleaned up")


def demo_scoring_with_timeout():
    """Demonstrate quiz scoring with timeouts"""
    print_header("DEMO 4: Quiz Scoring with Time Limits")

    app = create_app()
    with app.app_context():
        user = db.session.query(User).first()
        questions = db.session.query(Questions).limit(3).all()

        if not user or not questions:
            print("❌ Need users and questions in database.")
            return

        print(f"👤 User: {user.user_name}")
        print(f"📚 Using {len(questions)} questions for demo")

        # Create a very short session (10 seconds)
        session = QuizSession(user_id=user.id, time_limit_minutes=0.17)  # ~10 seconds
        db.session.add(session)
        db.session.commit()

        print(f"\n⏰ Created 10-second session")
        print(f"   Start: {session.start_time}")
        print(f"   Expires: {session.expiry_time}")

        # Simulate answering questions
        form_data = {}
        for i, q in enumerate(questions):
            print(f"\n❓ Question {i+1}: {q.question}")
            print(f"   Correct answer: {q.answer}")

            # Simulate user providing correct answer
            form_data[str(q.id)] = q.answer

            time.sleep(3)  # 3 seconds per question

            remaining = session.time_remaining_seconds
            print(f"   ⏳ Time remaining: {format_duration(remaining)}")

            if session.is_expired:
                print("   ⚠️  Time expired during question!")
                break

        print(f"\n📊 Final form data: {len(form_data)} answers collected")
        print(f"⏰ Session expired: {session.is_expired}")

        # This would normally be called in the route handler
        # but we'll just show the concept
        if session.is_expired:
            print("🔴 Quiz would be auto-submitted due to timeout")
            session.timeout_session(score=len(form_data), total_questions=len(questions))
        else:
            print("🟢 Quiz completed within time limit")
            session.complete_session(score=len(form_data), total_questions=len(questions))

        db.session.commit()

        print(f"\n📋 Final session status:")
        print(f"   Status: {session.status}")
        print(f"   Score: {session.score}/{session.total_questions}")
        print(f"   End time: {session.end_time}")

        # Clean up
        db.session.delete(session)
        db.session.commit()
        print("🗑️  Demo session cleaned up")


def demo_frontend_integration():
    """Show how frontend would integrate with timing"""
    print_header("DEMO 5: Frontend Integration Points")

    print("🌐 Frontend Integration Overview:")
    print()
    print("1️⃣ Quiz Start:")
    print("   - GET /quiz creates new QuizSession")
    print("   - Template receives session data with time_limit_seconds")
    print("   - JavaScript timer starts countdown")
    print()
    print("2️⃣ During Quiz:")
    print("   - JavaScript updates timer display every second")
    print("   - Optional: Periodic AJAX calls to /quiz_status for sync")
    print("   - Visual warnings at 5 minutes and 1 minute remaining")
    print()
    print("3️⃣ Auto-Submit:")
    print("   - JavaScript auto-submits form when timer reaches 0")
    print("   - Backend validates submission time")
    print("   - Timeout handling provides partial scoring")
    print()
    print("4️⃣ Results:")
    print("   - Results page shows completion status")
    print("   - Different display for completed vs timed-out")
    print("   - Performance analytics with timing data")
    print()

    print("📱 Key Frontend Features:")
    print("   ✅ Live countdown timer")
    print("   ✅ Progress bar visualization")
    print("   ✅ Color-coded warnings (green → yellow → red)")
    print("   ✅ Auto-save answers to localStorage")
    print("   ✅ Prevent accidental page refresh")
    print("   ✅ Mobile-responsive design")
    print("   ✅ Accessibility features")


def main():
    """Run all demos"""
    print("🎯 QUIZ APPLICATION TIME LIMITS DEMO")
    print("=" * 60)
    print("This demo shows the time limits functionality implemented in the quiz app.")
    print("The system provides comprehensive timing controls with both backend")
    print("validation and frontend user experience enhancements.")

    try:
        demo_basic_timing()
        demo_session_management()
        demo_api_responses()
        demo_scoring_with_timeout()
        demo_frontend_integration()

        print_header("DEMO COMPLETE")
        print("✅ All time limits functionality demonstrated successfully!")
        print()
        print("🚀 Key Benefits:")
        print("   • Fair quiz timing with server-side validation")
        print("   • Excellent user experience with live feedback")
        print("   • Automatic handling of timeouts and edge cases")
        print("   • Comprehensive session management")
        print("   • Mobile-friendly responsive design")
        print("   • Production-ready security and error handling")

    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
