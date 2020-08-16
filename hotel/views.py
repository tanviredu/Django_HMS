from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import ListView, FormView, View, DeleteView
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from .models import Room, Booking
from .forms import AvailabilityForm
from hotel.booking_functions.availability import check_availability
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import environ

import stripe
import json
stripe.api_key = settings.STRIPE_PRIVATE_KEY
# stripe.api_key = "sk_test_51HEuZ4DfnXAAr03AZc7MfpJTMagR5mDJmVnlcPLNMXgdF8fNVLULY1O9gQnC4zW2fFlDAh2uiLLs1KznVBolwzEZ000mnmElJi"

# stripe.Balance.retrieve()

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

environ.Env.read_env()


# Create your views here.


def RoomListView(request):
    room = Room.objects.all()[0]
    room_categories = dict(room.ROOM_CATEGORIES)
    room_values = room_categories.values()
    room_list = []
    print(stripe.apikey)
    print(stripe.Balance.retrieve())

    for room_category in room_categories:
        room = room_categories.get(room_category)
        room_url = reverse('hotel:RoomDetailView', kwargs={
                           'category': room_category})

        room_list.append((room, room_url))
    context = {
        "room_list": room_list,
    }
    return render(request, 'room_list_view.html', context)


class BookingListView(ListView):
    model = Booking
    template_name = "booking_list_view.html"

    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_staff:
            booking_list = Booking.objects.all()
            return booking_list
        else:
            booking_list = Booking.objects.filter(user=self.request.user)
            return booking_list

    # def get_context_data(self, **kwargs):
    #     room = Room.objects.all()[0]
    #     room_categories = dict(room.ROOM_CATEGORIES)
    #     context = super().get_context_data(**kwargs)
    #     context


class RoomDetailView(View):
    def get(self, request, *args, **kwargs):
        print(self.request.user)
        category = self.kwargs.get('category', None)
        form = AvailabilityForm()
        room_list = Room.objects.filter(category=category)

        if len(room_list) > 0:
            room = room_list[0]
            room_category = dict(room.ROOM_CATEGORIES).get(room.category, None)
            context = {
                'room_category': room_category,
                'form': form,
            }
            return render(request, 'room_detail_view.html', context)
        else:
            return HttpResponse('Category does not exist')

    def post(self, request, *args, **kwargs):
        category = self.kwargs.get('category', None)
        room_list = Room.objects.filter(category=category)
        form = AvailabilityForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

        available_rooms = []
        for room in room_list:
            if check_availability(room, data['check_in'], data['check_out']):
                available_rooms.append(room)

        if len(available_rooms) > 0:
            room = available_rooms[0]
            booking = Booking.objects.create(
                user=self.request.user,
                room=room,
                check_in=data['check_in'],
                check_out=data['check_out']
            )
            booking.save()
            message = Mail(
                from_email='dhabaledarshan@gmail.com',
                to_emails='dhabalekalpana@gmail.com',
                subject='Sending from hotelina',
                html_content='<strong>Sending from hotelina</strong>')
            try:
                sg = SendGridAPIClient(env.str('SG_KEY'))
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
                print('SENT!!!')
            except Exception as e:
                print(e)
            return HttpResponse(booking)
        else:
            return HttpResponse('All of this category of rooms are booked!! Try another one')


class CancelBookingView(DeleteView):
    model = Booking
    template_name = 'booking_cancel_view.html'
    success_url = reverse_lazy('hotel:BookingListView')


# class PaymentView(View):
#     def get(self, request, *args, **kwargs):
#         form = PaymentForm()

#         return render(request, 'payment.html', context)

#     def post(self, request, *args, **kwargs):
#         if user.is_authenticated:
#             stripe.Customer.retrieve(
#                 user.stripe_customer_id
#             )
#             intent = stripe.PaymentIntent.create(
#                 amount=786,
#                 currency='inr',
#                 payment_method_types=['card'],
#                 metadata={'integration_check': 'accept_a_payment'},
#             )
#             form = PaymentForm(request.POST)
#         if form.is_valid():

#         return render(request, 'payment.html', context)


def payment(request):

    print(request)
    intent = stripe.PaymentIntent.create(
        amount=786,
        currency='inr',
        payment_method_types=['card'],
        metadata={'integration_check': 'accept_a_payment'},
    )
    # print(intent)
    return render(request, 'payment_view.html', {"client_secret": intent['client_secret']})


@csrf_exempt
def paymentWebhook(request):
    if request.method == "POST":
        wh_sec = settings.STRIPE_PAYMENT_WEBHOOK_SECRET
        payload = request.body
        sig_header = request.headers['Stripe-Signature']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, wh_sec
            )
        except ValueError as e:
            # invalid payload
            return "Invalid payload", 400
        except stripe.error.SignatureVerificationError as e:
            # invalid signature
            return "Invalid signature", 400

        event_dict = event.to_dict()
        if event_dict['type'] == "payment_intent.succeeded":
            intent = event_dict['data']['object']
            print("Payment Succeeded: ", intent['id'])
            return redirect(reverse('success'))
            # Fulfill the customer's purchase
        elif event_dict['type'] == "payment_intent.payment_failed":
            intent = event_dict['data']['object']
            error_message = intent['last_payment_error']['message'] or None
            print("Payment Failed: ", intent['id'], error_message)
            # Notify the customer that payment failed
            return redirect(reverse('failure'))


def successMsg(request, *args, **kwargs):
    return render(request, 'success.html', {"amount": amount, "charge": charge})


def failure(request, *args, **kwargs):
    return render(request, 'failure.html')

# def charge(request):
#     amount = 5
#     if request.method == "POST":
#         print("Data:", request.POST)
#         token = request.POST['stripeToken']
#         customer = stripe.Customer.create(
#             name=request.POST['nickname'],
#             email=request.POST['email'],
#             source=token,
#         )
    # charge = stripe.Charge.create(
    #     amount=100,
    #     currency='inr',
    #     description='Example charge',
    #     customer=customer.id
    # )

    # return successMsg(request, kwargs={"charge": charge})
    # return JsonResponse({'client_secret': stripe.api_key})
