from django.urls import path

from users.mock_views import OrdersListView, ProductsListView, StoresListView


urlpatterns = [
    path("products/", ProductsListView.as_view(), name="products-list"),
    path("stores/", StoresListView.as_view(), name="stores-list"),
    path("orders/", OrdersListView.as_view(), name="orders-list"),
]
