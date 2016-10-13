from django.contrib import admin
from myproject.MiResumen2.models import Visitante
#from myproject.MiResumen2.models import Micronotero
from myproject.MiResumen2.models import Micronota
from myproject.MiResumen2.models import Seleccion
#from myproject.MiResumen2.models import MeGusta

admin.site.register(Visitante)
#admin.site.register(Micronotero)
admin.site.register(Micronota)
admin.site.register(Seleccion)
#admin.site.register(MeGusta)
