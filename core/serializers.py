from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Department, Professor, Student, Course, Enrollment, Material, Announcement

User = get_user_model()

class ReadOnlyUserSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email")
        read_only_fields = fields

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "code"]
        read_only_fields = ["id"]

class ProfessorCreateUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='professor'), write_only=True)
    user = ReadOnlyUserSmallSerializer(read_only=True)

    class Meta:
        model = Professor
        fields = ["id", "user", "user_id", "department", "office"]
        read_only_fields = ["id", "user"]

    def create(self, validated_data):
        user = validated_data.pop('user_id')
        return Professor.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('user_id', None)
        return super().update(instance, validated_data)

class ProfessorSerializer(ProfessorCreateUpdateSerializer):
    pass

class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='student'), write_only=True)
    user = ReadOnlyUserSmallSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ["id", "user", "user_id", "national_id", "department", "academic_year"]
        read_only_fields = ["id", "user"]

    def create(self, validated_data):
        user = validated_data.pop('user_id')
        return Student.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('user_id', None)
        return super().update(instance, validated_data)

class StudentSerializer(StudentCreateUpdateSerializer):
    pass

class CourseListSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    professor_ids = serializers.PrimaryKeyRelatedField(write_only=True, many=True, queryset=Professor.objects.all(), source='professors')
    professors = serializers.SerializerMethodField(read_only=True)
    seats_available = serializers.IntegerField(source='seats_available', read_only=True)

    class Meta:
        model = Course
        fields = ["id", "code", "title", "department", "professors", "professor_ids", "capacity", "credit_hours", "seats_available"]

    def get_professors(self, obj):
        return [{"id": p.id, "name": p.user.get_full_name() or p.user.username} for p in obj.professors.all()]

    def create(self, validated_data):
        profs = validated_data.pop('professors', [])
        course = Course.objects.create(**validated_data)
        if profs:
            course.professors.set(profs)
        return course

    def update(self, instance, validated_data):
        profs = validated_data.pop('professors', None)
        instance = super().update(instance, validated_data)
        if profs is not None:
            instance.professors.set(profs)
        return instance

class CourseDetailSerializer(CourseListSerializer):
    pass

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseListSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Course.objects.all(), source='course')

    class Meta:
        model = Enrollment
        fields = ["id", "student", "course", "course_id", "status", "created_at"]
        read_only_fields = ["id", "student", "course", "status", "created_at"]

    def validate(self, attrs):
        request = self.context.get('request')
        if request.user.role != 'student':
            raise serializers.ValidationError("Only students can enroll.")

        student = request.user.student
        course = attrs.get('course')

        if Enrollment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError("Already enrolled.")

        if course.seats_available() <= 0:
            raise serializers.ValidationError("Course capacity reached.")

        return attrs

    def create(self, validated_data):
        student = self.context['request'].user.student
        return Enrollment.objects.create(student=student, **validated_data)

class MaterialSerializer(serializers.ModelSerializer):
    uploaded_by = ProfessorSerializer(read_only=True)

    class Meta:
        model = Material
        fields = ["id", "course", "uploaded_by", "title", "file", "created_at"]
        read_only_fields = ["id", "uploaded_by", "created_at"]

    def validate(self, attrs):
        request = self.context['request']
        if request.user.role != 'professor':
            raise serializers.ValidationError("Only professors can upload.")

        prof = request.user.professor
        course = attrs.get('course')
        if course and not course.professors.filter(id=prof.id).exists():
            raise serializers.ValidationError("You are not assigned to this course.")

        return attrs

    def create(self, validated_data):
        prof = self.context['request'].user.professor
        return Material.objects.create(uploaded_by=prof, **validated_data)

class AnnouncementSerializer(serializers.ModelSerializer):
    posted_by = ProfessorSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = ["id", "course", "posted_by", "title", "body", "created_at"]
        read_only_fields = ["id", "posted_by", "created_at"]

    def validate(self, attrs):
        request = self.context['request']
        if request.user.role not in ("professor", "admin"):
            raise serializers.ValidationError("Only professors or admins can post.")

        if request.user.role == 'professor':
            prof = request.user.professor
            course = attrs.get('course')
            if course and not course.professors.filter(id=prof.id).exists():
                raise serializers.ValidationError("You are not assigned to this course.")

        return attrs

    def create(self, validated_data):
        if self.context['request'].user.role == 'professor':
            validated_data['posted_by'] = self.context['request'].user.professor
        return Announcement.objects.create(**validated_data)
