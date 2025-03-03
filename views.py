from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect ,  get_object_or_404
from django.contrib import messages
from .models import Client
from .models import Project , Payment
import paypalrestsdk
from django.urls import reverse
from django.conf import settings
from .forms import TicketForm
from .models import Ticket 
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
import os




# PayPal SDK Configuration
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # 'sandbox' for dummy, 'live' for real
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})



# Client Login View
def client_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        login(request, user)
        print(user)
        # Validate credentials
        try:
            client = Client.objects.get(username=username, password=password)
            request.session['client_id'] = client.id  # Store client ID in session
            return redirect('client_home')  # Redirect to client home page
        except Client.DoesNotExist:
            messages.error(request, 'Invalid username or password')

    return render(request, 'client_login.html')  # Corrected templ



# Client Home View
def client_home(request):
    client_id = request.session.get('client_id')
    if not client_id:
        return redirect('client_login')  # Redirect to login if no session exists

    client = Client.objects.get(id=client_id)
    project = Project.objects.filter(client=client).first()  # Get the first project associated with the client
    return render(request, 'client_home.html', {'client': client, 'project': project})




# Client Logout View
def client_logout(request):
    if 'client_id' in request.session:
        del request.session['client_id']
    return redirect('client_login')  # Redirect to login after logout


def project_details(request):
        projects = Project.objects.all()
        return render(request, 'project_details.html', {'projects': projects})


def download_file(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
        file_path = project.file_path.path  # Get the full file path
        file_name = os.path.basename(file_path)  # Extract the file name
        
        # Serve the file as a response
        response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)
        return response
    except Project.DoesNotExist:
        raise Http404("Project not found.")
    except Exception as e:
        raise Http404(f"Error: {str(e)}")



# View to show the payment confirmation page
def show_payment_page(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'paypal_payment.html', {'project': project})



# View to create and redirect to PayPal
def create_paypal_payment(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Create a PayPal Payment object dynamically
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('payment_success', args=[project_id])),
            "cancel_url": request.build_absolute_uri(f"/client/payment_cancel/{project_id}/"),
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": project.name,  # Project name dynamically
                    "sku": f"project_{project.id}",  # Unique project ID
                    "price": str(project.cost),  # Use `project.cost` dynamically
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {"total": str(project.cost), "currency": "USD"},
            "description": f"Payment for project: {project.name}"
        }]
    })

    # Redirect to PayPal approval URL
    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)  # Redirect to PayPal for approval
    else:
        messages.error(request, "Error creating PayPal payment. Try again later.")
        return redirect('client_home')


# Payment Success View

def payment_success(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Retrieve PayPal parameters from the GET request
    payment_id = request.GET.get('paymentId')
    token = request.GET.get('token')
    payer_id = request.GET.get('PayerID')
    
    return render(request, 'payment_success.html', {'project': project})



# Payment Cancel View
def payment_cancel(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        return render(request, 'paypal_payment.html', {
            'project': project,
            'payment_failed': True
        })
    except Project.DoesNotExist:
        messages.error(request, "Project not found.")
        return redirect('client_home')
    

@login_required
def manage_tickets(request):
    
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            return redirect('manage_tickets')
    else:
        form = TicketForm()

    completed_tickets = Ticket.objects.filter(created_by=request.user, status='Completed')
    return render(request, 'manage_tickets.html', {'form': form, 'completed_tickets': completed_tickets})