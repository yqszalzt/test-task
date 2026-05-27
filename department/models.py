from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Department(BaseModel):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True,
        blank=True, 
        related_name='children',
    )

    def __str__(self):
        return f"Department(id={self.id}, name='{self.name}', parent_id={self.parent_id_id})"
    
    def save(self, *args, **kwargs):
        if self.parent_id and self.parent_id_id == self.id:
            raise ValueError("A department cannot be its own parent.")
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'


class Employee(BaseModel):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    hired_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Employee(id={self.id}, full_name='{self.full_name}', position='{self.position}', department_id={self.department_id})"
    
    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'