from rest_framework.serializers import ModelSerializer, SerializerMethodField, DictField, CharField, ValidationError, IntegerField

from department.models import Department, Employee


class DepartmentSerializer(ModelSerializer):
    name = CharField(max_length=200)
    parent_id = IntegerField(required=False, allow_null=True, write_only=False)

    class Meta:
        model = Department
        fields = ['id', 'name', 'parent_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        return value.strip()

    def validate(self, attrs):
        name = attrs.get('name', getattr(self.instance, 'name', None))
        parent_id = attrs.get('parent_id', getattr(self.instance, 'parent_id', None))
        qs = Department.objects.filter(name=name, parent_id=parent_id)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Department with this name already exists under the same parent.")
        return attrs


class EmployeeSerializer(ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'position', 'hired_at', 'department_id', 'created_at']
        read_only_fields = ['id', 'department_id', 'created_at']


class DepartmentDetailSerializer(ModelSerializer):
    employees = SerializerMethodField()
    children = SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'parent_id', 'created_at', 'employees', 'children']

    def get_employees(self, obj):
        employees = obj.employees.order_by('full_name')
        return EmployeeSerializer(employees, many=True).data

    def get_children(self, obj):
        # рекурсия живёт в build_department_tree
        return DepartmentSerializer(obj.children.all(), many=True).data