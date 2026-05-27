from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.exceptions import NotFound, ValidationError

from .responses import SuccessResponse, ErrorResponse
from .models import Department, Employee
from .serializers import DepartmentSerializer, EmployeeSerializer, DepartmentDetailSerializer
from .utils import build_department_tree, is_in_subtree


class DepartmentAddView(APIView):
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        summary="Создать подразделение",
        request=DepartmentSerializer,
        responses={201: DepartmentSerializer},
        tags=["departments"],
    )
    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            department = serializer.save()
            return SuccessResponse(
                data=DepartmentSerializer(department).data,
                status=status.HTTP_201_CREATED,
            )
        return ErrorResponse(error=serializer.errors)

class DepartmentView(APIView):
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        summary="Получить подразделение (детали + сотрудники + поддерево)",
        parameters=[
            OpenApiParameter("depth", OpenApiTypes.INT, description="Глубина вложенности (1–5)", default=1),
            OpenApiParameter("include_employees", OpenApiTypes.BOOL, description="Включить сотрудников", default=True),
        ],
        responses={200: DepartmentDetailSerializer},
        tags=["departments"],
    )
    def get(self, request, department_id):
        if department_id is None:
            return ErrorResponse(error="department_id is required.", status=status.HTTP_400_BAD_REQUEST)

        department = get_object_or_404(Department, id=department_id)

        depth = int(request.query_params.get("depth", 1))
        depth = max(1, min(depth, 5))
        include_employees = request.query_params.get("include_employees", "true").lower() == "true"

        data = build_department_tree(department, depth, include_employees)
        return SuccessResponse(data=data)

    @extend_schema(
        summary="Обновить подразделение (переименовать / переместить)",
        request=DepartmentSerializer,
        responses={200: DepartmentSerializer},
        tags=["departments"],
    )
    def patch(self, request, department_id):
        if department_id is None:
            return ErrorResponse(error="department_id is required.", status=status.HTTP_400_BAD_REQUEST)
        department = get_object_or_404(Department, id=department_id)
        serializer = DepartmentSerializer(department, data=request.data, partial=True)

        if serializer.is_valid():
            new_parent_id = request.data.get("parent_id")
            if new_parent_id is not None:
                new_parent_id = int(new_parent_id)

                if new_parent_id == department.id:
                    raise ValidationError("A department cannot be its own parent.")

                if is_in_subtree(get_object_or_404(Department, pk=new_parent_id), department.id):
                    return ErrorResponse(
                        error="Cannot move a department into its own subtree.",
                        status=status.HTTP_409_CONFLICT,
                    )

            department = serializer.save()
            return SuccessResponse(data=DepartmentSerializer(department).data)

        return ErrorResponse(error=serializer.errors)

    @extend_schema(
        summary="Удалить подразделение",
        parameters=[
            OpenApiParameter("mode", OpenApiTypes.STR, description="cascade | reassign"),
            OpenApiParameter("reassign_to_department_id", OpenApiTypes.INT, description="Куда перевести сотрудников (для mode=reassign)"),
        ],
        responses={204: None},
        tags=["departments"],
    )
    def delete(self, request, department_id):
        if department_id is None:
            return ErrorResponse(error="department_id is required.", status=status.HTTP_400_BAD_REQUEST)
        department = get_object_or_404(Department, id=department_id)
        mode = request.query_params.get("mode", "cascade")

        if mode == "cascade":
            department.delete()
            return SuccessResponse(data=None, status=status.HTTP_204_NO_CONTENT)

        elif mode == "reassign":
            reassign_to_id = request.query_params.get("reassign_to_department_id")
            if not reassign_to_id:
                raise ValidationError("reassign_to_department_id is required for mode=reassign.")

            target = get_object_or_404(Department, id=reassign_to_id)
            Employee.objects.filter(department=department).update(department=target)
            department.delete()
            return SuccessResponse(data=None, status=status.HTTP_204_NO_CONTENT)

        return ErrorResponse(error="mode must be 'cascade' or 'reassign'.", status=status.HTTP_400_BAD_REQUEST)

class EmployeeView(APIView):
    throttle_classes = [AnonRateThrottle]

    @extend_schema(
        summary="Создать сотрудника в подразделении",
        request=EmployeeSerializer,
        responses={201: EmployeeSerializer},
        tags=["employees"],
    )
    def post(self, request, department_id=None):
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return ErrorResponse(error="Department not found", status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeSerializer(data=request.data)

        if serializer.is_valid():
            employee = serializer.save(department=department)
            return SuccessResponse(data=EmployeeSerializer(employee).data, status=status.HTTP_201_CREATED)
        return ErrorResponse(error=serializer.errors, status=status.HTTP_400_BAD_REQUEST)