from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Loan
from customers.models import Customer
from .serializers import (
    LoanEligibilityRequestSerializer,
    LoanEligibilityResponseSerializer,
    CreateLoanRequestSerializer,
    CreateLoanResponseSerializer,
    ViewLoanSerializer,
    ViewLoanByCustomerSerializer
)
from datetime import timedelta, date

class CheckEligibility(APIView):
    def post(self, request):
        serializer = LoanEligibilityRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            customer = Customer.objects.get(id=data['customer_id'])
            existing_debt = sum(loan.monthly_installment for loan in customer.loans.all())
            requested_installment = data['loan_amount'] * (1 + data['interest_rate'] / 100) / data['tenure']
            approval = requested_installment + existing_debt < customer.monthly_salary * 0.5
            return Response({
                "customer_id": customer.id,
                "approval": approval,
                "interest_rate": data['interest_rate'],
                "corrected_interest_rate": data['interest_rate'],
                "tenure": data['tenure'],
                "monthly_installment": requested_installment
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateLoan(APIView):
    def post(self, request):
        serializer = CreateLoanRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            customer = Customer.objects.get(id=data['customer_id'])
            requested_installment = data['loan_amount'] * (1 + data['interest_rate'] / 100) / data['tenure']
            existing_debt = sum(loan.monthly_installment for loan in customer.loans.all())
            approval = requested_installment + existing_debt < customer.monthly_salary * 0.5
            if approval:
                loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=data['loan_amount'],
                    interest_rate=data['interest_rate'],
                    tenure=data['tenure'],
                    monthly_installment=requested_installment,
                    is_approved=True,
                    end_date=date.today() + timedelta(weeks=4 * data['tenure'])
                )
                return Response({
                    "loan_id": loan.id,
                    "customer_id": customer.id,
                    "loan_approved": True,
                    "message": "Loan Approved",
                    "monthly_installment": requested_installment
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "loan_id": None,
                    "customer_id": customer.id,
                    "loan_approved": False,
                    "message": "Loan request exceeds eligible limit.",
                    "monthly_installment": requested_installment
                }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ViewLoan(APIView):
    def get(self, request, loan_id):
        loan = Loan.objects.get(id=loan_id)
        serializer = ViewLoanSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ViewLoansByCustomer(APIView):
    def get(self, request, customer_id):
        loans = Loan.objects.filter(customer__id=customer_id)
        serializer = ViewLoanByCustomerSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
