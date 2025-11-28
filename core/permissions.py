from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsProfessor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'professor'

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsProfessorOfCourse(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or request.user.role != 'professor':
            return False
        professor = request.user.professor

        if hasattr(obj, 'professors'):
            return obj.professors.filter(id=professor.id).exists()

        if hasattr(obj, 'course'):
            return obj.course.professors.filter(id=professor.id).exists()

        return False

class IsEnrolledStudent(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or request.user.role != 'student':
            return False

        student = request.user.student

        if hasattr(obj, 'enrollments'):
            return obj.enrollments.filter(student=student, status='approved').exists()

        if hasattr(obj, 'course'):
            course = obj.course
            return course.enrollments.filter(student=student, status='approved').exists()

        return False
