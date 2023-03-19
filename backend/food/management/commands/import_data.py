import os

from backend.settings import BASE_DIR
from django.core.management.base import BaseCommand

from food.models import Ingredient

DATA_FILES_DIR = os.path.join(BASE_DIR, 'data/')


class Command(BaseCommand):
    """Command class. See help attribute for further info."""
    help = '''Take all .csv files inside "data" folder of
        root django project and populate "ingredient" table.'''

    def _correct_files(self):
        """Only .csv files allowed to proceed."""
        files = os.listdir(DATA_FILES_DIR)
        for file in os.listdir(DATA_FILES_DIR):
            if not file.endswith('.csv'):
                files.remove(file)

        return files

    def _populate_table(self, file, model):
        """Create table entries row by row."""
        path = os.path.join(DATA_FILES_DIR, file)
        with open(path, 'r', encoding='utf8') as csv_file:
            for line in csv_file:
                somedict = dict()
                somedict['name'], somedict['measurement_unit'] = line.replace(
                    '\n', ''
                ).replace('"', '').rsplit(',', 1)
                Ingredient.objects.create(**somedict)

    def handle(self, *args, **options):
        for file in self._correct_files():
            self._populate_table(file, Ingredient)
