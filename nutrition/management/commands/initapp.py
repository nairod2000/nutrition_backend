from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Run multiple commands sequentially'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to run multiple commands...'))

        # List of commands to run
        commands_to_run = ['flush', 'import_units', 'import_nutrients','finalimporter3','createsuperuser','runserver']

        for command in commands_to_run:
            try:
                self.stdout.write(self.style.NOTICE(f'Running command: {command}'))
                call_command(command)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error occurred in command {command}: {e}'))

        self.stdout.write(self.style.SUCCESS('All commands finished.'))