from datetime import date
from django.contrib.auth import get_user_model
from django.db import models

from books.models import Book


user_model = get_user_model()


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(user_model, on_delete=models.CASCADE, related_name="borrowings")

    def set_actual_return_date(self):
        self.actual_return_date = date.today()
        self.save()

