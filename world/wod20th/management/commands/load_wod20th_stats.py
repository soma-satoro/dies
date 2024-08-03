import json
from django.core.management.base import BaseCommand
from world.wod20th.models import Stat
from django.db import connection
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Load WoD20th stats from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing stats')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        
        try:
            with open(json_file, 'r') as file:
                stats_data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File {json_file} not found.'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Error decoding JSON from file {json_file}.'))
            return
        
        for stat_data in stats_data:
            name = stat_data.get('name')
            if not name:
                self.stdout.write(self.style.ERROR('Missing stat name in data. Skipping entry.'))
                continue
            
            description = stat_data.get('description', '')
            game_line = stat_data.get('game_line')
            category = stat_data.get('category')
            stat_type = stat_data.get('stat_type')
            values = stat_data.get('values', [])

            # Data validation
            if not game_line or not category or not stat_type:
                self.stdout.write(self.style.ERROR(f'Invalid data for stat {name}. Skipping entry.'))
                continue

            # Ensure values are a list of integers
            if not isinstance(values, list) or not all(isinstance(v, int) for v in values):
                self.stdout.write(self.style.ERROR(f'Invalid values for stat {name}. Values must be a list of integers. Skipping entry.'))
                continue

            # Check if stat already exists
            existing_stat = Stat.objects.filter(name=name, game_line=game_line, category=category, stat_type=stat_type).first()
            if existing_stat:
                self.stdout.write(self.style.WARNING(f'Stat {name} already exists. Skipping entry.'))
                continue
            
            # Create new stat
            stat = Stat(
                name=name,
                description=description,
                game_line=game_line,
                category=category,
                stat_type=stat_type,
                values=values
            )

            try:
                # Validate the model before saving
                stat.full_clean()
                stat.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully created stat: {stat.name}'))
            except ValidationError as e:
                self.stdout.write(self.style.ERROR(f'Validation error for stat {stat.name}: {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error saving stat {stat.name}: {e}'))
                self.stdout.write(self.style.ERROR(f'Stat object: {stat.__dict__}'))
                if connection.queries:
                    last_query = connection.queries[-1]
                    self.stdout.write(self.style.ERROR(f'SQL: {last_query.get("sql", "N/A")}'))
                    self.stdout.write(self.style.ERROR(f'SQL params: {last_query.get("params", "N/A")}'))
                else:
                    self.stdout.write(self.style.ERROR('No SQL queries recorded.'))

        self.stdout.write(self.style.SUCCESS('Finished processing all stats.'))