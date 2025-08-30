from rest_framework import serializers
from restaurant.models import Menu, Booking

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'



class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')  

    class Meta:
        model = Booking
        fields = ['id', 'user', 'first_name', 'reservation_date', 'reservation_slot']

    def validate_reservation_slot(self, value):
        if value < 10 or value > 20:
            raise serializers.ValidationError("Reservation slot must be between 10 and 20")
        return value

    def validate(self, attrs):
        # Use the incoming value, or fallback to model default
        reservation_slot = attrs.get('reservation_slot', 10)
        reservation_date = attrs.get('reservation_date')

        if reservation_date is None:
            raise serializers.ValidationError("Reservation date is required.")

        # Check if the slot is already taken
        if Booking.objects.filter(
            reservation_date=reservation_date,
            reservation_slot=reservation_slot
        ).exists():
            raise serializers.ValidationError(
                f"Slot {reservation_slot} is already taken on {reservation_date}."
            )

        # Set default if missing so serializer.save() has it
        attrs['reservation_slot'] = reservation_slot

        return attrs
        
