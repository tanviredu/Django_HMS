from django.urls import path
from .views import RoomListView, BookingListView, RoomDetailView, CancelBookingView,  successMsg, payment, paymentWebhook, failure
app_name = 'hotel'

urlpatterns = [
    path('', RoomListView, name='RoomListView'),
    path('booking_list/', BookingListView.as_view(), name='BookingListView'),
    path('room/<category>', RoomDetailView.as_view(), name='RoomDetailView'),
    path('booking/cancel/<pk>', CancelBookingView.as_view(),
         name='CancelBookingView'),
    path('success/', successMsg,
         name='success'),
    path('failure/', failure,
         name='failure'),
    path('payment/', payment,
         name='payment'),
    path('payment-webhook/', paymentWebhook,
         name='paymentWebhook'),

]
