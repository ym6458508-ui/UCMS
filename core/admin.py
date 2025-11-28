from django.contrib import admin
from .models import Department, Professor, Student, Course, Enrollment, Material, Announcement, User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email")



@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code")
    search_fields = ("name", "code")



@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "department", "office")
    list_filter = ("department",)
    search_fields = ("user__username", "user__first_name", "user__last_name")



@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "department", "academic_year", "national_id")
    list_filter = ("department", "academic_year")
    search_fields = ("user__username", "user__first_name", "user__last_name", "national_id")



@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "title", "department", "capacity", "credit_hours")
    list_filter = ("department",)
    search_fields = ("code", "title")
    filter_horizontal = ("professors",)



@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "course", "status", "created_at")
    list_filter = ("status", "course")
    search_fields = ("student__user__username", "course__title")



@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "uploaded_by", "created_at")
    list_filter = ("course",)
    search_fields = ("title", "course__title", "uploaded_by__user__username")



@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "posted_by", "created_at")
    list_filter = ("course",)
    search_fields = ("title", "course__title", "posted_by__user__username")

