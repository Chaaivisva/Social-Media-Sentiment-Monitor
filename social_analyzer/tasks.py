from celery import shared_task
from django.core.management import call_command

@shared_task
def fetch_data_task():
    try:
        call_command('fetch_data')
    except Exception as e:
        print(f"Error running fetch_data command: {e}")

        