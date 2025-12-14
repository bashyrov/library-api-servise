from rest_framework import serializers
from borrowings.models import Borrowing
from payments.serializers import PaymentSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book", "user", )
        read_only_fields = ("user", "actual_return_date", "borrow_date")

    def validate(self, data):
        book = data["book"]

        if book.inventory <= 0:
            raise serializers.ValidationError("We don't have enough inventory")

        return data


class BorrowingDetailSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(read_only=True, many=True)

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book", "user", "payments")

