from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer, CustomerRegistrationSerializer

class RegisterCustomer(APIView):
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            approved_limit = round(36 * data['monthly_income'], -5)
            customer = Customer.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                age=data['age'],
                phone_number=data['phone_number'],
                monthly_salary=data['monthly_income'],
                approved_limit=approved_limit,
            )
            response_data = CustomerSerializer(customer).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
