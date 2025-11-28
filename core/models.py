from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("professor", "Professor"),
        ("student", "Student"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"

class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Professor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    office = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return f"Prof. {self.user.get_full_name() or self.user.username}"

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    national_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    academic_year = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.academic_year}"

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    professors = models.ManyToManyField(Professor, blank=True, related_name='courses')
    capacity = models.PositiveIntegerField(default=30)
    credit_hours = models.PositiveSmallIntegerField(default=3)

    def __str__(self):
        return f"{self.code} - {self.title}"

    def seats_available(self):
        enrolled = self.enrollments.filter(status='approved').count()
        return max(0, self.capacity - enrolled)

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )
    student = models.ForeignKey(Student, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='approved')

    class Meta:
        unique_together = (('student', 'course'),)

    def clean(self):
        if self.status == 'approved' and self.course.seats_available() <= 0:
            raise ValidationError('Course capacity reached')

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} -> {self.course} ({self.status})"

class Material(models.Model):
    course = models.ForeignKey(Course, related_name='materials', on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='materials/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course.code})"

class Announcement(models.Model):
    course = models.ForeignKey(Course, related_name='announcements', on_delete=models.CASCADE)
    posted_by = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Announcement: {self.title} - {self.course.code}"
