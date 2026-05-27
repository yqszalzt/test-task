from django.urls import path

from .views import DepartmentView, EmployeeView, DepartmentAddView


urlpatterns = [
    path("", DepartmentAddView.as_view()),
    path("<int:department_id>/", DepartmentView.as_view()),
    path("<int:department_id>/employees/", EmployeeView.as_view())
]