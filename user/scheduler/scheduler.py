'''
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.core.management import call_command
import contextlib
import signal
def db_backup():
    try:
        call_command('dbbackup')
    except Exception as e:
        print(f"Error during database backup: {e}")
job_id = "weekly_backup_database_yes"
def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(),"default")
    scheduler.add_job(db_backup,'interval',minutes=5,jobstore="default",id=job_id)
    register_events(scheduler)
    scheduler.start()
     # Shut down the scheduler when the application is stopped
'''