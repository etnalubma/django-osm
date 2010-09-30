from django.core.management.base import BaseCommand, CommandError
from djangoosm.utils.model import import_osm, set_streets, set_intersections, set_doors

class Command(BaseCommand):
    args = '<osm_file>'
    help = 'Toma un archivo .osm y lo importa al modelo django'

    def handle(self, osmfile=None, **options):
        self.stdout.write('Importing OSM File. This could take a while.')
        import_osm(osmfile)

        self.stdout.write("Setting Streets")
        set_streets()

        self.stdout.write("Setting Intersections")
        set_intersections()

        self.stdout.write("Setting Doors")
        set_doors()
