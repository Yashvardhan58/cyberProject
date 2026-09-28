"""
Django Management Command to Seed the UEBA Database.
Run via: `python manage.py seed_ueba_database`
"""

from django.core.management.base import BaseCommand
from pathlib import Path
import sys

# Import direct seeder function
backend_dir = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))
from ml.data.seed_sqlite_db import seed_database


class Command(BaseCommand):
    help = "Seed database with sample UEBA user vectors, alerts, SHAP values, and experiments."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting UEBA database seeding..."))
        try:
            counts = seed_database()
            self.stdout.write(self.style.SUCCESS(
                f"Successfully seeded {counts['users']} users, {counts['alerts']} alerts, and {counts['risk_scores']} risk score records."
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Seeding failed: {str(e)}"))
