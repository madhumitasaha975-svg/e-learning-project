from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Course(models.Model):
    title       = models.CharField(max_length=200)
    description = models.TextField()
    instructor  = models.ForeignKey(User, on_delete=models.CASCADE)
    price       = models.DecimalField(max_digits=8, decimal_places=2)
    rating      = models.FloatField(default=0)
    thumbnail   = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def lesson_count(self):
        return self.lessons.count()

    def update_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            avg = sum(r.stars for r in ratings) / ratings.count()
            self.rating = round(avg, 1)
        else:
            self.rating = 0
        self.save()

    def rating_count(self):
        return self.ratings.count()

    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return None


class Lesson(models.Model):
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title      = models.CharField(max_length=200)
    content    = models.TextField()
    order      = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - Lesson {self.order}: {self.title}"


class Enrollment(models.Model):
    student    = models.ForeignKey(User, on_delete=models.CASCADE)
    course     = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        CourseProgress.objects.get_or_create(student=self.student, course=self.course)

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


class LessonProgress(models.Model):
    student    = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson     = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed  = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'lesson')


class CourseProgress(models.Model):
    student     = models.ForeignKey(User, on_delete=models.CASCADE)
    course      = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress    = models.IntegerField(default=0)
    last_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')

    def recalculate_progress(self):
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            self.progress = 0
        else:
            completed = LessonProgress.objects.filter(
                student=self.student, lesson__course=self.course, completed=True
            ).count()
            self.progress = round((completed / total_lessons) * 100)
        self.save()


class CourseRating(models.Model):
    STAR_CHOICES = [
        (1, '⭐ Poor'), (2, '⭐⭐ Fair'), (3, '⭐⭐⭐ Good'),
        (4, '⭐⭐⭐⭐ Very Good'), (5, '⭐⭐⭐⭐⭐ Excellent'),
    ]
    student    = models.ForeignKey(User, on_delete=models.CASCADE)
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ratings')
    stars      = models.IntegerField(choices=STAR_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    review     = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')