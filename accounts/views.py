from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegisterForm, ProfileUpdateForm


def home_view(request):
    from courses.models import Course, Enrollment, CourseRating
    from django.db.models import Avg

    total_courses     = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    total_students    = User.objects.filter(is_superuser=False).count()
    # instructors = anyone who has created at least one course
    total_instructors = Course.objects.values('instructor').distinct().count()
    # learners = users who have at least one enrollment
    total_learners    = Enrollment.objects.values('student').distinct().count()

    print(f"DEBUG STATS — courses:{total_courses} enrollments:{total_enrollments} students:{total_students} instructors:{total_instructors} learners:{total_learners}")

    # Avg satisfaction from all ratings (0-5 stars to percentage)
    avg = CourseRating.objects.aggregate(a=Avg('stars'))['a']
    satisfaction = round((avg / 5) * 100) if avg else 98

    # Top 3 courses by rating
    courses = Course.objects.all().order_by('-rating')[:3]

    context = {
        'courses':           courses,
        'total_courses':     total_courses,
        'total_students':    total_students,
        'total_enrollments': total_enrollments,
        'total_learners':    total_learners,
        'total_instructors': total_instructors,
        'satisfaction':      satisfaction,
    }
    return render(request, 'home.html', context)


@login_required
def student_dashboard(request):
    from courses.models import Enrollment, CourseProgress

    enrollments   = Enrollment.objects.filter(student=request.user).select_related('course')
    progress_data = []
    for enrollment in enrollments:
        try:
            cp = CourseProgress.objects.get(student=request.user, course=enrollment.course)
            progress = cp.progress
            last_lesson = cp.last_lesson
        except CourseProgress.DoesNotExist:
            progress = 0
            last_lesson = None
        progress_data.append({
            'course':      enrollment.course,
            'progress':    progress,
            'last_lesson': last_lesson,
        })

    enrolled_count   = enrollments.count()
    highest_progress = max((p['progress'] for p in progress_data), default=0)
    average_progress = round(
        sum(p['progress'] for p in progress_data) / enrolled_count
    ) if enrolled_count else 0

    return render(request, 'student_dashboard.html', {
        'enrollments':       enrollments,
        'progress_data':     progress_data,
        'enrolled_count':    enrolled_count,
        'highest_progress':  highest_progress,
        'average_progress':  average_progress,
    })


@login_required
def profile_view(request):
    from courses.models import Enrollment, CourseProgress

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    enrolled_count = enrollments.count()

    progress_data = []
    for enrollment in enrollments:
        try:
            cp = CourseProgress.objects.get(student=request.user, course=enrollment.course)
            progress = cp.progress
        except CourseProgress.DoesNotExist:
            progress = 0
        progress_data.append({'course': enrollment.course, 'progress': progress})

    average_progress = round(
        sum(p['progress'] for p in progress_data) / enrolled_count
    ) if enrolled_count else 0

    return render(request, 'accounts/profile.html', {
        'form':             form,
        'enrolled_count':   enrolled_count,
        'average_progress': average_progress,
        'progress_data':    progress_data,
    })


@login_required
def instructor_dashboard(request):
    from courses.models import Course, Enrollment, CourseRating
    from django.db.models import Avg, Count

    courses = Course.objects.filter(instructor=request.user)

    course_stats = []
    for course in courses:
        student_count = Enrollment.objects.filter(course=course).count()
        lesson_count  = course.lessons.count()
        rating_data   = CourseRating.objects.filter(course=course).aggregate(
            avg=Avg('stars'), count=Count('id')
        )
        course_stats.append({
            'course':        course,
            'student_count': student_count,
            'lesson_count':  lesson_count,
            'avg_rating':    round(rating_data['avg'], 1) if rating_data['avg'] else 0,
            'rating_count':  rating_data['count'],
        })

    total_students    = sum(s['student_count'] for s in course_stats)
    overall_avg       = CourseRating.objects.filter(
        course__instructor=request.user
    ).aggregate(a=Avg('stars'))['a']
    overall_avg_rating = round(overall_avg, 1) if overall_avg else 0
    recent_enrollments = Enrollment.objects.filter(
        course__instructor=request.user
    ).select_related('student', 'course').order_by('-enrolled_at')[:8]

    return render(request, 'accounts/instructor_dashboard.html', {
        'course_stats':       course_stats,
        'total_courses':      courses.count(),
        'total_students':     total_students,
        'overall_avg_rating': overall_avg_rating,
        'recent_enrollments': recent_enrollments,
    })


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})