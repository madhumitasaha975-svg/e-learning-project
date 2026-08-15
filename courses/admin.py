from django.contrib import admin
from .models import Course, Lesson, Enrollment, CourseProgress, LessonProgress, CourseRating


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'price', 'rating', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title',)
    readonly_fields = ('rating',)    # ← shows it but prevents editing


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course',)
    search_fields = ('title',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'progress', 'updated_at')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed', 'completed_at')


@admin.register(CourseRating)
class CourseRatingAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'stars', 'created_at')
    list_filter = ('stars', 'course')