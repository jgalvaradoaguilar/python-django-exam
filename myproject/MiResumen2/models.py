from django.db import models

# Create your models here.
class Visitante(models.Model):
	nombre = models.CharField(max_length=100, default="")
	# sesion se usara en las cookies
	sesion = models.IntegerField(primary_key=True)
	# Para las cookies que pone realmente el navegador
	name = models.TextField()
	value = models.TextField()
	# Cada visitante tendra su propio css (aunque habra uno por defecto)
	css = models.TextField()
	

class Micronota(models.Model):
	url = models.CharField(max_length=255, primary_key=True)
	contenido = models.TextField()
	# micronotero = models.ForeignKey(Micronotero)    #obj_micronota.micronotero.micronotero
	micronotero = models.TextField()
	# Fecha de publicacion de la micronota en Identi.ca
	fecha_publicacion = models.DateTimeField()
	avatar = models.CharField(max_length=255)
	# La fecha en que la seleccionan los usuarios se mira con "Seleccion"
	# El numero de selecciones se hace contando los registros de "Seleccion" para esa micronota

	class Meta:
		ordering = ['-fecha_publicacion']


class Seleccion(models.Model):
	sesion = models.IntegerField()
	fecha_seleccion = models.DateTimeField()
	url_micronota = models.CharField(max_length=255)
	micronota = models.ForeignKey(Micronota)	#se podria quitar
	# Fecha de publicacion de la micronota en Identi.ca
	fecha_publicacion = models.DateTimeField()

	class Meta:
		ordering = ['-fecha_publicacion']
	

class Puntuacion(models.Model):
	sesion = models.IntegerField()
	puntos = models.IntegerField()
	url_micronota = models.CharField(max_length=255)


# Las auxiliares seran solo bases de datos intermedias...
class AuxMicronota(models.Model):
	url = models.CharField(max_length=255, primary_key=True)
	contenido = models.TextField()
	micronotero = models.TextField()
	# Fecha de publicacion de la micronota en Identi.ca
	fecha_publicacion = models.DateTimeField()
	avatar = models.CharField(max_length=255)
	
	class Meta:
		ordering = ['-fecha_publicacion']


