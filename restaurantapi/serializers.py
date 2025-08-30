from rest_framework import serializers
from restaurant.models import Menu, Booking

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):

    booking_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'