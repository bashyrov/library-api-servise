from django.urls import path
from rest_framework.routers import DefaultRouter
from payments.views import PaymentViewSet, StripePaymentCancelAPIView, StripePaymentSuccessAPIView

app_name = 'payments'

router = DefaultRouter()
router.register("", PaymentViewSet, basename="payments")

urlpatterns = [
    path('success/', StripePaymentSuccessAPIView.as_view(), name='stripe-success'),
    path('cancel/', StripePaymentCancelAPIView.as_view(), name='stripe-cancel'),
] + router.urls



