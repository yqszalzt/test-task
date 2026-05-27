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


def build_department_tree(department: Department, depth: int, include_employees: bool) -> dict:
    """
    Рекурсивно строит дерево подразделений до указанной глубины.
    На каждом уровне - данные отдела, опционально сотрудники, опционально children
    """
    data = DepartmentSerializer(department).data

    if include_employees:
        employees = department.employees.order_by("full_name")
        data["employees"] = EmployeeSerializer(employees, many=True).data

    if depth > 1:
        children = department.children.all()
        data["children"] = [
            build_department_tree(child, depth - 1, include_employees)
            for child in children
        ]
    else:
        data["children"] = []

    return data