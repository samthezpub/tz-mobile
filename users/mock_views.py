from rest_framework.response import Response
from rest_framework.views import APIView

from users.services import check_access_permission


PRODUCTS = [
    {"id": 1, "name": "Phone", "price": 799},
    {"id": 2, "name": "Laptop", "price": 1499},
    {"id": 3, "name": "Headphones", "price": 199},
]

STORES = [
    {"id": 1, "name": "Central Store", "city": "Moscow"},
    {"id": 2, "name": "North Store", "city": "Saint Petersburg"},
]

ORDERS = [
    {"id": 1, "number": "ORD-1001", "status": "new"},
    {"id": 2, "number": "ORD-1002", "status": "processing"},
]


class ProductsListView(APIView):
    def get(self, request):
        check_access_permission(request.user, "products", "read")
        return Response({"items": PRODUCTS})


class StoresListView(APIView):
    def get(self, request):
        check_access_permission(request.user, "stores", "read")
        return Response({"items": STORES})


class OrdersListView(APIView):
    def get(self, request):
        check_access_permission(request.user, "orders", "read")
        return Response({"items": ORDERS})
