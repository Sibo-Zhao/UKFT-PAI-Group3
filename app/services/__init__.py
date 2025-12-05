"""
Service Layer Package.

This package contains business logic services that implement the core
functionality of the University Wellbeing API. Services are separated
from controllers to follow the Single Responsibility Principle and
improve testability.

Services:
    StudentAnalyticsService: Student performance and wellbeing analytics
    AttendanceService: Attendance tracking and reporting
    GradingService: Assignment grading and submission management
    WellbeingService: Student wellbeing data analysis
    CourseService: Course and module management

Architecture:
    Controllers -> Services -> Models
    
    Controllers handle HTTP requests/responses
    Services contain business logic
    Models handle data persistence

Usage:
    from app.services.student_analytics_service import StudentAnalyticsService
    
    service = StudentAnalyticsService()
    analytics = service.get_comprehensive_analytics(student_id)
"""