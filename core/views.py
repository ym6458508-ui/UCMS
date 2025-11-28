from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Department, Professor, Student, Course, Enrollment, Material, Announcement
from .serializers import (
    DepartmentSerializer,
    ProfessorSerializer,
    StudentSerializer,
    CourseListSerializer,
    CourseDetailSerializer,
    EnrollmentSerializer,
    MaterialSerializer,
    AnnouncementSerializer,
)
from .permissions import (
    IsAdmin,
    IsProfessor,
    IsStudent,
    IsProfessorOfCourse,
    IsEnrolledStudent,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdmin]



class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().select_related('department').prefetch_related('professors')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def students(self, request, pk=None):
        course = self.get_object()

        if request.user.role == 'professor':
            if not course.professors.filter(user=request.user).exists():
                return Response({"detail": "Not allowed"}, status=403)

        enrollments = course.enrollments.filter(status='approved')
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)



class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all().select_related('student__user', 'course')
    serializer_class = EnrollmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), IsStudent()]
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsProfessor()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        return serializer.save(student=self.request.user.student)



class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all().select_related('course', 'uploaded_by')
    serializer_class = MaterialSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsProfessor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.role == 'student':
            student = self.request.user.student
            return qs.filter(course__enrollments__student=student, course__enrollments__status='approved')

        if self.request.user.role == 'professor':
            professor = self.request.user.professor
            return qs.filter(course__professors=professor)

        return qs

    def perform_create(self, serializer):
        professor = self.request.user.professor
        serializer.save(uploaded_by=professor)



class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all().select_related('course', 'posted_by')
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsProfessor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.role == 'student':
            student = self.request.user.student
            return qs.filter(course__enrollments__student=student, course__enrollments__status='approved')

        if self.request.user.role == 'professor':
            professor = self.request.user.professor
            return qs.filter(course__professors=professor)

        return qs

    def perform_create(self, serializer):
        professor = self.request.user.professor
        serializer.save(posted_by=professor)
