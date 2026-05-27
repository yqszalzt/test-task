import pytest
from rest_framework.test import APIClient
from department.models import Department, Employee


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def dept(db):
    return Department.objects.create(name="Engineering")


@pytest.fixture
def child_dept(db, dept):
    return Department.objects.create(name="Backend", parent=dept)


@pytest.fixture
def employee(db, dept):
    return Employee.objects.create(
        department=dept,
        full_name="John Doe",
        position="Developer",
    )


@pytest.mark.django_db
def test_create_department(client):
    res = client.post("/api/v1/departments/", {"name": "HR"}, format="json")
    assert res.status_code == 201
    assert res.data["data"]["name"] == "HR"


@pytest.mark.django_db
def test_create_department_with_parent(client, dept):
    res = client.post("/api/v1/departments/", {"name": "Frontend", "parent_id": dept.id}, format="json")
    assert res.status_code == 201
    assert res.data["data"]["parent_id"] == dept.id


@pytest.mark.django_db
def test_create_department_duplicate_name_same_parent(client, dept):
    Department.objects.create(name="Backend", parent=dept)
    res = client.post("/api/v1/departments/", {"name": "Backend", "parent_id": dept.id}, format="json")
    assert res.status_code == 400


@pytest.mark.django_db
def test_create_department_trims_name(client):
    res = client.post("/api/v1/departments/", {"name": "  DevOps  "}, format="json")
    assert res.status_code == 201
    assert res.data["data"]["name"] == "DevOps"


@pytest.mark.django_db
def test_create_department_empty_name(client):
    res = client.post("/api/v1/departments/", {"name": ""}, format="json")
    assert res.status_code == 400


@pytest.mark.django_db
def test_get_department(client, dept):
    res = client.get(f"/api/v1/departments/{dept.id}/")
    assert res.status_code == 200
    assert res.data["data"]["name"] == "Engineering"


@pytest.mark.django_db
def test_get_department_not_found(client):
    res = client.get("/api/v1/departments/99999/")
    assert res.status_code == 404


@pytest.mark.django_db
def test_get_department_includes_employees(client, dept, employee):
    res = client.get(f"/api/v1/departments/{dept.id}/?include_employees=true")
    assert res.status_code == 200
    assert len(res.data["data"]["employees"]) == 1
    assert res.data["data"]["employees"][0]["full_name"] == "John Doe"


@pytest.mark.django_db
def test_get_department_excludes_employees(client, dept, employee):
    res = client.get(f"/api/v1/departments/{dept.id}/?include_employees=false")
    assert res.status_code == 200
    assert res.data["data"]["employees"] == []


@pytest.mark.django_db
def test_get_department_children_depth(client, dept, child_dept):
    res = client.get(f"/api/v1/departments/{dept.id}/?depth=2")
    assert res.status_code == 200
    children = res.data["data"]["children"]
    assert len(children) == 1
    assert children[0]["name"] == "Backend"


@pytest.mark.django_db
def test_patch_department_rename(client, dept):
    res = client.patch(f"/api/v1/departments/{dept.id}/", {"name": "Tech"}, format="json")
    assert res.status_code == 200
    assert res.data["data"]["name"] == "Tech"


@pytest.mark.django_db
def test_patch_department_self_parent(client, dept):
    res = client.patch(f"/api/v1/departments/{dept.id}/", {"parent_id": dept.id}, format="json")
    assert res.status_code == 400


@pytest.mark.django_db
def test_patch_department_cycle(client, dept, child_dept):
    # пытаемся сделать родителя дочерним элементом своего же ребёнка
    res = client.patch(f"/api/v1/departments/{dept.id}/", {"parent_id": child_dept.id}, format="json")
    assert res.status_code in (400, 409)


@pytest.mark.django_db
def test_patch_department_not_found(client):
    res = client.patch("/api/v1/departments/99999/", {"name": "Ghost"}, format="json")
    assert res.status_code == 404


@pytest.mark.django_db
def test_delete_department_cascade(client, dept, employee):
    dept_id = dept.id
    res = client.delete(f"/api/v1/departments/{dept_id}/?mode=cascade")
    assert res.status_code == 204
    assert not Department.objects.filter(id=dept_id).exists()
    assert not Employee.objects.filter(id=employee.id).exists()


@pytest.mark.django_db
def test_delete_department_reassign(client, dept, employee):
    target = Department.objects.create(name="Target")
    res = client.delete(
        f"/api/v1/departments/{dept.id}/?mode=reassign&reassign_to_department_id={target.id}"
    )
    assert res.status_code == 204
    assert not Department.objects.filter(id=dept.id).exists()
    employee.refresh_from_db()
    assert employee.department_id == target.id


@pytest.mark.django_db
def test_delete_department_reassign_missing_target(client, dept):
    res = client.delete(f"/api/v1/departments/{dept.id}/?mode=reassign")
    assert res.status_code == 400


@pytest.mark.django_db
def test_delete_department_invalid_mode(client, dept):
    res = client.delete(f"/api/v1/departments/{dept.id}/?mode=invalid")
    assert res.status_code == 400


@pytest.mark.django_db
def test_create_employee(client, dept):
    res = client.post(
        f"/api/v1/departments/{dept.id}/employees/",
        {"full_name": "Jane Smith", "position": "Designer"},
        format="json",
    )
    assert res.status_code == 201
    assert res.data["data"]["full_name"] == "Jane Smith"


@pytest.mark.django_db
def test_create_employee_nonexistent_department(client):
    res = client.post(
        "/api/v1/departments/99999/employees/",
        {"full_name": "Ghost", "position": "Nobody"},
        format="json",
    )
    assert res.status_code == 404


@pytest.mark.django_db
def test_create_employee_missing_fields(client, dept):
    res = client.post(
        f"/api/v1/departments/{dept.id}/employees/",
        {"full_name": "No Position"},
        format="json",
    )
    assert res.status_code == 400


@pytest.mark.django_db
def test_create_employee_with_hired_at(client, dept):
    res = client.post(
        f"/api/v1/departments/{dept.id}/employees/",
        {"full_name": "Alice", "position": "PM", "hired_at": "2024-01-15"},
        format="json",
    )
    assert res.status_code == 201
    assert res.data["data"]["hired_at"] == "2024-01-15"