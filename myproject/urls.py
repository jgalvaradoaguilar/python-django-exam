from django.conf.urls.defaults import *
import django.contrib.auth.views
from django.views.generic.simple import direct_to_template

# Para la generacion de feeds
# from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^myproject/', include('myproject.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),

	# Para login y logout de usuarios
    #(r'^login$', 'django.contrib.auth.views.login'),
    #(r'^logout$', 'django.contrib.auth.views.logout'),

    # Para registrar nuevos usuarios
    #(r'^register$', 'myproject.MiResumen2.views.register',),

	# Microresumen de las ultimas 30 micronotas
    (r'^$', 'myproject.MiResumen2.views.ver_ultimas30',),
	# Microresumen de las micronotas entre la nnn y la nnn+29
	(r'^(?P<nnn>[\d]+)$', 'myproject.MiResumen2.views.ver_seleccion',),
	# Recurso de actualizacion
    (r'^update$', 'myproject.MiResumen2.views.update'),
	# Listado de todas las micronotas seleccionadas por el visitante
    (r'^selected$', 'myproject.MiResumen2.views.selected'),
	# Para seleccionar una micronota
    (r'^seleccionar/(?P<url>.*)$', 'myproject.MiResumen2.views.seleccionar'),
	# Para deseleccionar una micronota
    (r'^deseleccionar/(?P<url>.*)$', 'myproject.MiResumen2.views.deseleccionar'),
	# Para puntuar una micronota
    (r'^puntuar/(?P<url>.*)$', 'myproject.MiResumen2.views.puntuar'),	
	# Para el feed RSS
	(r'^feed$', 'myproject.MiResumen2.views.feed'),
	#(r'^feed$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
	# Para la configuracion del visitante
    (r'^conf$', 'myproject.MiResumen2.views.conf'),
	# Para la configuracion del skin (css)
    (r'^skin$', 'myproject.MiResumen2.views.skin'),
	# Muestra las cookies con sus visitantes
	(r'^cookies$', 'myproject.MiResumen2.views.cookies'),
    # Los ficheros estaticos no se deberian servir con Django... pero se pueden servir
    (r'^images/(?P<path>.*)$', 'django.views.static.serve',{'document_root': 'sfiles/images'}),
    # Los ficheros estaticos no se deberian servir con Django... pero se pueden servir
    #(r'^css/(?P<path>.*)$', 'django.views.static.serve',{'document_root': 'sfiles/css'}),
	# Por si no ha entrado a ninguna opcion valida anterior
    (r'^(.*)$', 'myproject.MiResumen2.views.Opcion_No_Valida'),
)

# Hay que proporcionar un diccionario con la correspondencia canal a objeto Feed:
#feeds = {
#	'latest': LatestEntriesRssFeed,
#}
