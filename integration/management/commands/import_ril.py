import fileinput

from django.core.management.base import BaseCommand, CommandError
from integration.get_pocket import process_articles


class Command(BaseCommand):
    def handle(self, *args, **options):
        html = ''.join(x for x in fileinput.input(args))
        process_articles(html)
