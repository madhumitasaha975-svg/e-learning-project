from django import forms
from .models import Course, Lesson


class CourseForm(forms.ModelForm):
    class Meta:
        model  = Course
        fields = ['title', 'description', 'price', 'thumbnail']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Python for Beginners'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe what students will learn...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0 for free',
                'min': '0',
            }),
            'thumbnail': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model  = Lesson
        fields = ['title', 'content', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Introduction to Variables'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Write the lesson content here...'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 1, 2, 3...',
                'min': '1',
            }),
        }