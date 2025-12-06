from datetime import date
from django.db import models

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.CharField(max_length=100, default="Test")  #TODO: Change to User model

    def set_actual_return_date(self):
        self.actual_return_date = date.today()
        self.save()

