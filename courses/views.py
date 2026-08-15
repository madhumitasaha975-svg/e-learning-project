# courses/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Course, Lesson, Enrollment, CourseProgress, LessonProgress, CourseRating
from .forms import CourseForm, LessonForm


# ─────────────────────────────────────────────
# COURSE LIST
# ─────────────────────────────────────────────

def course_list(request):
    courses = Course.objects.all()

    query = request.GET.get('q', '').strip()
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(instructor__username__icontains=query)
        )

    price_filter = request.GET.get('price', '')
    if price_filter == 'free':
        courses = courses.filter(price=0)
    elif price_filter == 'paid':
        courses = courses.filter(price__gt=0)

    context = {
        'courses': courses,
        'query': query,
        'price_filter': price_filter,
        'total_results': courses.count(),
    }

    return render(request, 'courses/course_list.html', context)


# ─────────────────────────────────────────────
# COURSE DETAIL
# ─────────────────────────────────────────────

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    lessons = course.lessons.all()
    is_enrolled = False
    user_rating = None

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=course
        ).exists()
        user_rating = CourseRating.objects.filter(
            student=request.user, course=course
        ).first()

    all_ratings = CourseRating.objects.filter(
        course=course
    ).select_related('student').order_by('-created_at')

    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'user_rating': user_rating,
        'all_ratings': all_ratings,
        'star_range': range(1, 6),
    }

    return render(request, 'courses/course_detail.html', context)


# ─────────────────────────────────────────────
# ENROLL
# ─────────────────────────────────────────────

@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.user == course.instructor:
        return redirect('course_detail', pk=pk)

    Enrollment.objects.get_or_create(student=request.user, course=course)
    return redirect('course_detail', pk=pk)


# ─────────────────────────────────────────────
# LESSON DETAIL
# ─────────────────────────────────────────────

@login_required
def lesson_detail(request, course_pk, lesson_pk):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, course=course)

    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=course
    ).exists()

    if not is_enrolled:
        return redirect('course_detail', pk=course_pk)

    all_lessons = course.lessons.all()

    progress, _ = CourseProgress.objects.get_or_create(
        student=request.user, course=course
    )
    progress.last_lesson = lesson
    progress.save()

    lesson_progress, _ = LessonProgress.objects.get_or_create(
        student=request.user, lesson=lesson
    )

    completed_lesson_ids = LessonProgress.objects.filter(
        student=request.user,
        lesson__course=course,
        completed=True
    ).values_list('lesson_id', flat=True)

    prev_lesson = all_lessons.filter(order__lt=lesson.order).last()
    next_lesson = all_lessons.filter(order__gt=lesson.order).first()

    context = {
        'course': course,
        'lesson': lesson,
        'all_lessons': all_lessons,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'lesson_progress': lesson_progress,
        'completed_lesson_ids': completed_lesson_ids,
    }

    return render(request, 'courses/lesson_detail.html', context)


# ─────────────────────────────────────────────
# MARK LESSON COMPLETE
# ─────────────────────────────────────────────

@login_required
def mark_lesson_complete(request, course_pk, lesson_pk):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, course=course)

    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=course
    ).exists()

    if not is_enrolled:
        return redirect('course_detail', pk=course_pk)

    lesson_progress, _ = LessonProgress.objects.get_or_create(
        student=request.user, lesson=lesson
    )
    lesson_progress.completed = True
    lesson_progress.save()

    course_progress, _ = CourseProgress.objects.get_or_create(
        student=request.user, course=course
    )
    course_progress.recalculate_progress()

    return redirect('lesson_detail', course_pk=course_pk, lesson_pk=lesson_pk)


# ─────────────────────────────────────────────
# RATE COURSE
# ─────────────────────────────────────────────

@login_required
def rate_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    is_enrolled = Enrollment.objects.filter(
        student=request.user, course=course
    ).exists()

    if not is_enrolled:
        messages.error(request, "You must be enrolled to rate this course.")
        return redirect('course_detail', pk=pk)

    if request.method == 'POST':
        stars = request.POST.get('stars')
        review = request.POST.get('review', '').strip()

        if not stars or not stars.isdigit() or int(stars) not in range(1, 6):
            messages.error(request, "Please select a valid star rating (1–5).")
            return redirect('course_detail', pk=pk)

        rating, created = CourseRating.objects.update_or_create(
            student=request.user,
            course=course,
            defaults={'stars': int(stars), 'review': review}
        )
        course.update_rating()

        if created:
            messages.success(request, "Thanks for your rating! ⭐")
        else:
            messages.success(request, "Your rating has been updated! ⭐")

    return redirect('course_detail', pk=pk)


# ─────────────────────────────────────────────
# CREATE COURSE
# ─────────────────────────────────────────────

@login_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, "Course created successfully! Now add some lessons.")
            return redirect('manage_course', pk=course.pk)
    else:
        form = CourseForm()

    return render(request, 'courses/create_course.html', {'form': form})


# ─────────────────────────────────────────────
# MANAGE COURSE (edit course + add lessons)
# ─────────────────────────────────────────────

@login_required
def manage_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    # Only the instructor of this course can manage it
    if request.user != course.instructor:
        messages.error(request, "You don't have permission to manage this course.")
        return redirect('course_detail', pk=pk)

    course_form = CourseForm(instance=course)
    lesson_form = LessonForm()
    lessons = course.lessons.all()

    # Handle course update
    if request.method == 'POST':
        if 'update_course' in request.POST:
            course_form = CourseForm(request.POST, request.FILES, instance=course)
            if course_form.is_valid():
                course_form.save()
                messages.success(request, "Course updated successfully!")
                return redirect('manage_course', pk=pk)

        # Handle add lesson
        elif 'add_lesson' in request.POST:
            lesson_form = LessonForm(request.POST)
            if lesson_form.is_valid():
                lesson = lesson_form.save(commit=False)
                lesson.course = course
                lesson.save()
                messages.success(request, f"Lesson '{lesson.title}' added!")
                return redirect('manage_course', pk=pk)

    context = {
        'course': course,
        'course_form': course_form,
        'lesson_form': lesson_form,
        'lessons': lessons,
    }

    return render(request, 'courses/manage_course.html', context)


# ─────────────────────────────────────────────
# DELETE COURSE
# ─────────────────────────────────────────────

@login_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.user != course.instructor:
        messages.error(request, "You don't have permission to delete this course.")
        return redirect('course_detail', pk=pk)

    if request.method == 'POST':
        course.delete()
        messages.success(request, "Course deleted successfully.")
        return redirect('instructor_dashboard')

    return render(request, 'courses/delete_course.html', {'course': course})


# ─────────────────────────────────────────────
# DELETE LESSON
# ─────────────────────────────────────────────

@login_required
def delete_lesson(request, course_pk, lesson_pk):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, course=course)

    if request.user != course.instructor:
        messages.error(request, "You don't have permission to delete this lesson.")
        return redirect('course_detail', pk=course_pk)

    if request.method == 'POST':
        lesson.delete()
        messages.success(request, f"Lesson '{lesson.title}' deleted.")
        return redirect('manage_course', pk=course_pk)

    return redirect('manage_course', pk=course_pk)

# ─────────────────────────────────────────────
# CERTIFICATE
# ─────────────────────────────────────────────
@login_required
def course_certificate(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)

    try:
        cp = CourseProgress.objects.get(student=request.user, course=course)
    except CourseProgress.DoesNotExist:
        messages.error(request, "Complete the course first!")
        return redirect('course_detail', pk=pk)

    if cp.progress < 100:
        messages.error(request, f"You need 100% to get a certificate. You're at {cp.progress}%.")
        return redirect('course_detail', pk=pk)

    return render(request, 'courses/certificate.html', {
        'course':       course,
        'student':      request.user,
        'enrolled_at':  enrollment.enrolled_at,
        'completed_at': cp.updated_at,
    })