from django.urls import path
from .views import index, restaurant_tables, table_reservations
from .views import RestaurantViewSet, TableViewSet, ReservationViewSet

urlpatterns = [
    path("", index, name="index"),  # Главная страница со списком ресторанов
    path("restaurant/<int:restaurant_id>/", restaurant_tables, name="restaurant_tables"),  # Столики ресторана
    path("table/<int:table_id>/", table_reservations, name="table_reservations"),  # Таймслоты для бронирования

    # Исправленный API бронирования
    path("reservations/", ReservationViewSet.as_view({"get": "list", "post": "create"}), name="reservations"),
    path("reservations/<int:pk>/", ReservationViewSet.as_view({"delete": "destroy"}), name="reservation-detail"),
]
