from .models import Department
from .serializers import DepartmentSerializer, EmployeeSerializer

def is_in_subtree(node: Department, ancestor_id: int) -> bool:
    """Проверяет, является ли ancestor_id предком node (защита от циклов)."""
    current = node
    while current is not None:
        if current.id == ancestor_id:
            return True
        current = current.parent  # ForeignKey
    return False


def build_department_tree(department, depth, include_employees):
    data = DepartmentSerializer(department).data

    if include_employees:
        data["employees"] = EmployeeSerializer(
            department.employees.order_by("full_name"), many=True
        ).data
    else:
        data["employees"] = []

    if depth > 1:
        data["children"] = [
            build_department_tree(child, depth - 1, include_employees)
            for child in department.children.all()
        ]
    else:
        data["children"] = []

    return data