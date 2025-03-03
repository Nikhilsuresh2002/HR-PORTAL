from django.shortcuts import render, redirect
from .models import Todo
from notification.models import Notification  # Import the Notification model

# View to list all to-dos, with filtering options
def todo_list(request, filter_type='all'):
    # Only show to-dos that belong to the logged-in user
    if filter_type == 'active':
        todos = Todo.objects.filter(user=request.user, is_completed=False)  # Filter by user
    elif filter_type == 'completed':
        todos = Todo.objects.filter(user=request.user, is_completed=True)  # Filter by user
    else:
        todos = Todo.objects.filter(user=request.user)  # Filter by user
    
    return render(request, 'todo.html', {'todos': todos})

# View to add a new to-do
def add_todo(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        new_todo = Todo.objects.create(title=title, user=request.user)  # Associate to-do with logged-in user
        
        # Add notification when a new To-Do is added
        Notification.objects.create(
            message=f"New To-Do '{new_todo.title}' added.",
            category='todo'
        )
        return redirect('todo_list')
    return redirect('todo_list')

# View to toggle completion status of a to-do
def toggle_complete(request, pk):
    todo = Todo.objects.get(pk=pk)
    
    # Ensure that the logged-in user can only toggle their own to-dos
    if todo.user == request.user:
        todo.is_completed = not todo.is_completed
        todo.save()

        # Add notification when a To-Do's completion status is toggled
        status = "completed" if todo.is_completed else "marked as active"
        Notification.objects.create(
            message=f"To-Do '{todo.title}' was {status}.",
            category='todo'
        )
    
    return redirect('todo_list')

# View to delete a to-do
def delete_todo(request, pk):
    todo = Todo.objects.get(pk=pk)
    
    # Ensure that the logged-in user can only delete their own to-dos
    if todo.user == request.user:
        title = todo.title
        todo.delete()

        # Add notification when a To-Do is deleted
        Notification.objects.create(
            message=f"To-Do '{title}' was deleted.",
            category='todo'
        )
    
    return redirect('todo_list')
