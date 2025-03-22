from rest_framework import serializers
from .models import Restaurant, Table, Reservation

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'

class TableSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)

    class Meta:
        model = Table
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    table = TableSerializer(read_only=True)
    table_id = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all(), source='table', write_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'table', 'table_id', 'time_slot']

    def validate(self, data):
        """Проверяем, что столик не забронирован на этот таймслот"""
        table = data['table']
        time_slot = data['time_slot']
        if Reservation.objects.filter(table=table, time_slot=time_slot).exists():
            raise serializers.ValidationError("Этот столик уже забронирован на данный таймслот.")
        return data
