from django.db import models

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="tables")
    number = models.IntegerField()
    capacity = models.IntegerField()

    def __str__(self):
        return f"Table {self.number} in {self.restaurant.name}"

class Reservation(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="reservations")
    time_slot = models.TimeField()

    class Meta:
        unique_together = ('table', 'time_slot')  # Нельзя дважды забронировать один столик на один таймслот

    def __str__(self):
        return f"Reservation for Table {self.table.number} at {self.time_slot}"
