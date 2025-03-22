import json
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from .models import Restaurant, Table, Reservation
from .serializers import RestaurantSerializer, TableSerializer, ReservationSerializer
from django.shortcuts import render
from .models import Table, Reservation
from datetime import datetime

from django.shortcuts import render, get_object_or_404
from .models import Restaurant, Table, Reservation
from datetime import datetime

def index(request):
    restaurants = Restaurant.objects.all()
    return render(request, "bookings/index.html", {"restaurants": restaurants})

def restaurant_tables(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    tables = restaurant.tables.all()
    
    table_data = []
    current_time = datetime.now().strftime("%H:%M")
    
    for table in tables:
        is_booked = Reservation.objects.filter(table=table, time_slot=current_time).exists()
        table_data.append({
            "id": table.id,
            "number": table.number,
            "is_booked": is_booked
        })

    return render(request, "bookings/tables.html", {"restaurant": restaurant, "tables": table_data})

def table_reservations(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    
    # Доступные таймслоты (например, с 12:00 до 22:00 каждый час)
    available_slots = [f"{hour}:00" for hour in range(12, 23)]
    
    # Убираем уже забронированные таймслоты
    booked_slots = Reservation.objects.filter(table=table).values_list("time_slot", flat=True)
    available_slots = [slot for slot in available_slots if slot not in booked_slots]

    return render(request, "bookings/reservations.html", {"table": table, "available_slots": available_slots})

def book_table(request):
    """API для бронирования столика."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            table_id = data.get("table_id")
            time_slot = data.get("time_slot")

            table = get_object_or_404(Table, id=table_id)

            # Проверяем, не занят ли столик на это время
            if Reservation.objects.filter(table=table, time_slot=time_slot).exists():
                return JsonResponse({"detail": "Этот столик уже забронирован на указанное время."}, status=400)

            # Создаем бронирование
            Reservation.objects.create(table=table, time_slot=time_slot)
            return JsonResponse({"message": "Столик успешно забронирован!"})

        except json.JSONDecodeError:
            return JsonResponse({"detail": "Ошибка обработки данных!"}, status=400)

    return JsonResponse({"detail": "Метод не разрешен!"}, status=405)

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    @extend_schema(
        summary="Получить список броней",
        responses={200: ReservationSerializer(many=True)}
    )
    def list(self, request):
        return super().list(request)

    @extend_schema(
        summary="Создать новую бронь",
        responses={201: ReservationSerializer}
    )
    def create(self, request):
        table_id = request.data.get("table_id")
        time_slot = request.data.get("time_slot")

        if not table_id or not time_slot:
            return Response({"error": "Не переданы все параметры"}, status=status.HTTP_400_BAD_REQUEST)

        table = Table.objects.filter(id=table_id).first()
        if not table:
            return Response({"error": "Столик не найден"}, status=status.HTTP_404_NOT_FOUND)

        if Reservation.objects.filter(table=table, time_slot=time_slot).exists():
            return Response({"error": "Этот столик уже забронирован на выбранное время"},
                            status=status.HTTP_400_BAD_REQUEST)

        reservation = Reservation.objects.create(table=table, time_slot=time_slot)
        return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Удалить бронь",
        responses={204: None}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
