
import os
import time 
from datetime import datetime
from django.core.management import BaseCommand, call_command
from django.core.files.storage import FileSystemStorage
from fuckyou.settings import BASE_DIR
from django_cron import CronJobBase, Schedule
from django.conf import settings
class BackupDatabase(CronJobBase):
    RUN_EVERY_MINS = 5  # run every 1 minute
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'yourapp.backup_database'  # a unique code for this task

    def do(self):
        try:
            # Create a timestamped backup file name
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            backup_filename = f'backup_{timestamp}.json'

            # Get the storage instance
            storage = FileSystemStorage(location=os.path.join(BASE_DIR, 'backup'))

            # Perform the database backup using Django's built-in 'dumpdata' management command
            with storage.open(backup_filename, 'w') as backup_file:
                call_command('dumpdata', '--exclude', 'auth.permission', '--exclude', 'contenttypes', stdout=backup_file)
            print('Database backup completed successfully.')

            # Run the development server after the backup only in DEBUG mode
            #if settings.DEBUG:
                #print('Starting Django development server...')
                #call_command('runserver')

        except Exception as e:
            # Log or print the error for debugging
            print(f"Error during backup or runserver: {e}")