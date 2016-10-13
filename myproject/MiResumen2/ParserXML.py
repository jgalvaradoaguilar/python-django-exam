#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# Se importan las clases necesarias para que funcionen los parser
from xml.sax.handler import ContentHandler
# Se importan las bases de datos necesarias
from MiResumen2.models import AuxMicronota
from email.utils import parsedate
from datetime import datetime, timedelta



# Esta es mi clase que sirve para hacer el parser del RSS
class myContentHandler(ContentHandler):

    def __init__ (self):
		self.inItem = False
		self.inContent = False
		self.theContent = ""
		# Se declaran las variables para cada item
		self.titulo = ""
		self.enlace = ""
		self.rssDate = ""
		self.avatar = ""


    def startElement (self, name, attrs):
		if name == 'item':
			self.inItem = True
		elif self.inItem:
			if name == 'title':
				self.inContent = True
			elif name == 'link':
				self.inContent = True
			elif name =='description':
				self.inContent = True
			#elif name == 'dc:date':
			#	self.inContent = True
			elif name == 'statusnet:postIcon':	# para el avatar
				self.avatar = attrs['rdf:resource']
         
   
    def endElement (self, name):
		if name == 'item':
			self.inItem = False
		elif self.inItem:
			if name == 'title':
				#print "Title: " + self.theContent + "."
				self.titulo = self.theContent
				self.inContent = False
				self.theContent = ""
			elif name == 'link':
				#print " Link: " + self.theContent + "."
				self.enlace = self.theContent
				self.inContent = False
				self.theContent = ""
			elif name =='description':
				# En titulo viene nombre_micronotero: noticia
				# En enlace viene el link de la micronota
				# La fecha viene en description  (rssDate)
				self.rssDate = self.theContent.split(" on ")[1]
				self.inContent = False
				self.theContent = ""
				# Se le suman 2000 al year
				#print self.rssDate
				aux_year = int(self.rssDate.split(" ")[1].split("-")[2]) + 2000
				parte_inicial = self.rssDate.split(" ")[0]
				parte_year = self.rssDate.split(" ")[1]
				parte_hora = self.rssDate.split(" ")[2]
				parte_final = "UTC"
				self.rssDate = parte_inicial + " " + parte_year.split("-")[0] + "-" + parte_year.split("-")[1] + "-" + str(aux_year) + " " + parte_hora + " " + parte_final
				#print self.rssDate
				
			elif name == 'statusnet:postIcon':	#nuevo
				# Se mete el registro en la BB.DD. auxiliar
				micronotero = self.titulo.split(":")[0]
				campos = len(self.titulo.split(":"))
				noticia = ""
				for i in range(campos):
					if i != 0:
						if i != campos-1:
							noticia = noticia + self.titulo.split(":")[i] + ":"
						else:
							noticia = noticia + self.titulo.split(":")[i]
							
				#print noticia
				dbDate = datetime(*(parsedate(self.rssDate)[:6]))
				# Se le suman dos horas, para que no sea UTC sino hora de Spain(Europe).
				b = timedelta(hours = 2)
				dbDate = dbDate + b
				#print dbDate
				avatar_micronotero = self.avatar
				p = AuxMicronota(url = self.enlace, contenido = noticia, micronotero = micronotero, fecha_publicacion = dbDate, avatar = avatar_micronotero)
				p.save()

    def characters (self, chars):
        if self.inContent:
            self.theContent = self.theContent + chars
