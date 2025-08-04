from celery import shared_task
import pandas as pd
from .models import Customer
from loans.models import Loan
from datetime import datetime, timedelta

@shared_task
def ingest_customer_data(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        Customer.objects.update_or_create(
            phone_number=row['phone_number'],
            defaults={
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'age': row.get('age', 0),
                'monthly_salary': row['monthly_salary'],
                'approved_limit': row['approved_limit'],
            }
        )

@shared_task
def ingest_loan_data(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        try:
            customer = Customer.objects.get(phone_number=row['phone_number'])
            Loan.objects.create(
                customer=customer,
                loan_amount=row['loan_amount'],
                interest_rate=row['interest_rate'],
                tenure=row['tenure'],
                monthly_installment=row['monthly_installment'],
                emi_start_date=row.get('emi_start_date', datetime.today()),
                emi_end_date=row.get('emi_end_date', datetime.today() + timedelta(days=30 * int(row['tenure']))),
                is_approved=True,
                emis_paid_on_time=row.get('emis_paid_on_time', 0),
            )
        except Customer.DoesNotExist:
            print(f"Customer with phone {row['phone_number']} not found. Skipping loan record.")
