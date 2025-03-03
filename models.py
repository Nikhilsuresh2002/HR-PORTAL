from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User



# Client model to represent clients in the system
class Client(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)  # Use hashed passwords in production!
    tasks = models.TextField(blank=True, null=True)
    client_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile', null=True, blank=True)

    def __str__(self):
        return self.name


# Project model to represent client projects
class Project(models.Model):
    name = models.CharField(max_length=200)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="projects", null=True, blank=True)  # Allow null
    employee_name = models.CharField(max_length=100,null=True,blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField(default=timezone.now)  # Set default to current time
    progress = models.IntegerField(default=0)  # Add this field to store progress percentage
    payment_status = models.CharField(max_length=50, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid')  # Added payment status field
    file_path = models.FileField(upload_to='project_files/', null=True, blank=True)

    def __str__(self):
        return self.name


# Payment model to track client payments
class Payment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('completed', 'Completed'), ('pending', 'Pending')], default='pending')

    def __str__(self):
        return f"Payment of {self.amount} for {self.client.name}"
    
    
# Ticket model to manage client tickets
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')  # User who created the ticket
    client = models.ForeignKey(Client, on_delete=models.CASCADE,default=1)  # Client associated with the ticket
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')  # Employee assigned to the ticket
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title