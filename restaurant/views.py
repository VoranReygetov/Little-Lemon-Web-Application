# from django.http import HttpResponse
from django.shortcuts import render
from .forms import BookingForm
from .models import Menu
from django.core import serializers
from .models import Booking
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.
def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def reservations(request):
    booking_json = {"bookings":"No bookings"}

    if request.user.is_authenticated:
        bookings = Booking.objects.filter(user=request.user)
        booking_json = serializers.serialize('json', bookings)
        
    return render(request, 'bookings.html',{"bookings":booking_json})

@login_required
def book(request):
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form':form}
    return render(request, 'book.html', context)

# Add your code here to create new views
def menu(request):
    menu_data = Menu.objects.all()
    main_data = {"menu": menu_data}
    return render(request, 'menu.html', {"menu": main_data})


def display_menu_item(request, pk=None): 
    if pk: 
        menu_item = Menu.objects.get(pk=pk) 
    else: 
        menu_item = "" 
    return render(request, 'menu_item.html', {"menu_item": menu_item}) 

@csrf_exempt
@login_required
def bookings(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Check if the user already has a booking for the same day
        booking, created = Booking.objects.update_or_create(
            user=request.user,
            reservation_date=data['reservation_date'],
            defaults={
                'first_name': data['first_name'],
                'reservation_slot': data['reservation_slot'],
            }
        )
        # Return info if it was updated or created
        return JsonResponse({
            "success": 1,
            "updated": not created,
            "reservation_slot": booking.reservation_slot
        })

    # GET request
    date = request.GET.get('date')
    if not date:
        date = datetime.today().date()
    else:
        # Convert string to date if necessary
        date = datetime.strptime(date, '%Y-%m-%d').date()
        
    bookings = Booking.objects.filter(reservation_date=date, user=request.user)
    booking_json = serializers.serialize('json', bookings)

    return HttpResponse(booking_json, content_type='application/json')