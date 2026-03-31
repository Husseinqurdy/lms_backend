from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from core.models import Enrollment, User, CourseCategory, Module, Course





class CreateUserSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(required=True)
    middlename = serializers.CharField(required=False, allow_blank=True)
    surname = serializers.CharField(required=True)
    registration_number = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = [
            "id",
            "firstname",
            "middlename",
            "surname",
            "registration_number",
            "role",
            "username",
        ]
        read_only_fields = ["id", "username"]

    def create(self, validated_data):
        firstname = validated_data.get("firstname", "").strip()
        middlename = validated_data.get("middlename", "").strip()
        surname = validated_data.get("surname", "").strip()

        username_parts = [surname, firstname]
        if middlename:
            username_parts.append(middlename)
        username = ".".join(username_parts).lower()

        user = User.objects.create_user(
            username=username,
            firstname=firstname,
            middlename=middlename,
            surname=surname,
            registration_number=validated_data["registration_number"],
            role=validated_data["role"],
            password=surname,
            email=f"{validated_data['registration_number'].lower()}@placeholder.com"
        )
        return user
    


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']



class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id","title", "content"]

class CourseCreateSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True)

    class Meta:
        model = Course
        fields = ["title", "description", "category", "visibility", "modules"]

    def create(self, validated_data):
        modules_data = validated_data.pop("modules")
        course = Course.objects.create(**validated_data)
        for mod in modules_data:
            Module.objects.create(course=course, **mod)
        return course



class CourseWithModulesSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    category = CourseCategorySerializer(read_only=True)  
    enrolled_students = serializers.IntegerField(read_only=True)


    class Meta:
        model = Course
        fields = ["id", "title", "description", "category", "visibility", "status",  "created_at", "modules", "enrolled_students"
]



class ModuleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "title", "content"]

class CourseUpdateSerializer(serializers.ModelSerializer):
    modules = ModuleUpdateSerializer(many=True)

    class Meta:
        model = Course
        fields = ["title", "description", "category", "visibility", "modules"]

    def update(self, instance, validated_data):
        modules_data = validated_data.pop("modules", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Clear old modules and recreate
        instance.modules.all().delete()
        for mod in modules_data:
            Module.objects.create(course=instance, **mod)

        return instance
    
class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "firstname", "middlename", "surname", "registration_number"]

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentInfoSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "student", "enrolled_at"]




class AdminInstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "firstname", "middlename", "surname"]


class AdminCourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ["id", "name"]


class AdminModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "title", "content"]


class AdminCourseSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    instructor = AdminInstructorSerializer(source="created_by", read_only=True)
    modules = AdminModuleSerializer(many=True, read_only=True)
    enrolled_students = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "category",
            "visibility",
            "status",
            "modules",
            "enrolled_students",
            "instructor",
            "created_at",
            "updated_at",
        ]

    def get_category(self, obj):
        if obj.category:
            return {
                "id": obj.category.id,
                "name": obj.category.name
            }
        return None
    
class CategoryDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ["id", "name"]
        
        
class StudentCourseSerializer(serializers.ModelSerializer):
    category = CourseCategorySerializer()
    instructor = serializers.SerializerMethodField()
    enrolled_students = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id", "title", "description", "category",
            "visibility", "status", "enrolled_students",
            "instructor"
        ]

    def get_instructor(self, obj):
        return {
            "id": obj.created_by.id,
            "name": f"{obj.created_by.firstname} {obj.created_by.surname}"
        }


class StudentMyCourseSerializer(serializers.ModelSerializer):
    progress = serializers.IntegerField(source="enrollments__progress", read_only=True)
    status = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "title", "description", "progress", "status", "instructor"]

    def get_status(self, obj):
        progress = getattr(obj, "enrollments__progress", 0)
        if progress == 0:
            return "Not Started"
        elif progress < 100:
            return "In Progress"
        return "Completed"

    def get_instructor(self, obj):
        return f"{obj.created_by.firstname} {obj.created_by.surname}"



class CourseDetailSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "title", "description", "modules", "progress"]

    def get_progress(self, obj):
        enrollment = obj.enrollments.filter(student=self.context["request"].user).first()
        return enrollment.progress if enrollment else 0
