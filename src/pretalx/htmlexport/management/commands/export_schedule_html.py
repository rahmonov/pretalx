from bakery.management.commands.build import Command as BakeryBuildCommand
from django.conf import settings
from django.core.management.base import CommandError
from django.utils import translation

from pretalx.event.models import Event


class Command(BakeryBuildCommand):
    help = 'Exports event schedule as a static HTML dump'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('event', type=str)

    def handle(self, *args, **options):
        try:
            event = Event.objects.get(slug=options['event'])
        except Event.DoesNotExist:
            raise CommandError('Could not find event with slug "{}"'.format(options['event']))

        settings.EXPORTING_EVENT = event

        # TODO: use the default langauge for each event
        translation.activate('en-gb')

        super().handle(*args, **options)
