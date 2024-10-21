from django.urls import path

from .views import (
    GenerateOTPView,
    VerifyOTPView,
    VerifyTokenView,
    ProfileView,
    KYCUploadView,
    MutualFundListView,
    PlaceOrderView,
    PlaceCancelOrderView,
    ListTransactionsView,
)

urlpatterns = [
    path("generate_otp_for_username", GenerateOTPView.as_view(), name="generate_otp"),
    path("verify_otp_for_username", VerifyOTPView.as_view(), name="verify_otp"),
    path("verify_token", VerifyTokenView.as_view(), name="verify_token"),
    path("profile", ProfileView.as_view(), name="profile"),
    path("upload_kyc_details", KYCUploadView.as_view(), name="upload_kyc_details"),
    path("get_mutual_funds", MutualFundListView.as_view(), name="get_mutual_funds"),
    path("place_order", PlaceOrderView.as_view(), name="place_order"),
    path(
        "place_order/cancel", PlaceCancelOrderView.as_view(), name="place_cancel_order"
    ),
    path(
        "list_orders", ListTransactionsView.as_view(), name="list_orders"
    ),
]