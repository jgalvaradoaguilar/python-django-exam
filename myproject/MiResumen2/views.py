# Create your views here.

# Para poder usar el directorio del proyecto y las variables definidas en settings.py
import os.path
from django.conf import settings

# HttpResponseGone envia codigo 410: Ya no disponible, notallowed es 405 en caso de metodos no permitidos
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseGone, HttpResponseRedirect
# Para acceder a las bases de datos
from MiResumen2.models import Visitante, Micronota, Seleccion, Puntuacion, AuxMicronota

# Para las templates
from django.shortcuts import render_to_response
# Para las templates

# Necesario para obtener el rss de Identi.ca
import httplib

# Se importan las clases necesarias para que funcionen los parser
from xml.sax import make_parser
import ParserXML

# Para la generacion de valores de cookies
import random

# Para conocer el tiempo actual en formato datetime (para seleccionar una micronota)
from datetime import datetime




#***********************************************************************************************************************************
def idSesionAleatorio():
	while 1:
		try:
			# Se genera un numero aleatorio entero entre 1 y 999.999.999, por ejemplo
			aleatorio = random.randint(1,999999999)
			# Se comprueba que nadie mas tenga ese numero aleatorio
			Visitante.objects.get(sesion = aleatorio)
		except Visitante.DoesNotExist:
			#Salta la excepcion si no lo encuentra
			break
	return aleatorio



#***********************************************************************************************************************************
def compruebaCookie(request):
	if "sesion" in request.session:
		# Hay una cookie, ya hay un nombre de usuario y un css para ese visitante
		sesion = request.session["sesion"]
		nombre_visitante = Visitante.objects.get(sesion = sesion).nombre
		css_visitante = Visitante.objects.get(sesion = sesion).css
		dicc_navegador = request.COOKIES
		name = dicc_navegador["csrftoken"]
		value = dicc_navegador["sessionid"]
		record = Visitante.objects.get(sesion = sesion)
		record.name = str(name)
		record.value = str(value)
		record.save()
	else:
		# Hay que crear una cookie y crear un Visitante con su css por defecto
		sesion = idSesionAleatorio()
		nombre_visitante = "invitado"
		css_defecto = "/css/style.css"
		# Se lee el fichero css del visitante por defecto
		fichero_css = open(os.path.join(settings.PROJECT_PATH,'sfiles' + css_defecto),'r')
		css_visitante = fichero_css.read()
		request.session["sesion"] = sesion
		name = ""
		value = ""
		visita = Visitante (nombre = nombre_visitante, 
							sesion = sesion,
							name = name,
							value = value, 
							css = css_visitante)
		visita.save()
	# Se devolvera el nombre, el css y la sesion del visitante
	datos_usuario = [nombre_visitante, css_visitante, sesion]
	return datos_usuario



#************************************************************************************************************************************
def media(url):
	punt_media = 0.0
	try:
		puntuaciones = Puntuacion.objects.filter(url_micronota = url)
		for i in range(puntuaciones.count()):
			punt_media = punt_media + puntuaciones[i].puntos
		punt_media = punt_media/puntuaciones.count()
	except:
		pass
	# Se devuelve la puntuacion media (ya es un float)
	return punt_media



#************************************************************************************************************************************
def seleccionar(request, url):
	# Se comprueba si el usuario tiene cookie, porque entonces podria tener su propio css
	datos_usuario = compruebaCookie(request)
	usuario = datos_usuario[0]
	css = datos_usuario[1]
	sesion = datos_usuario[2]
	# Se comprueba cada metodo
	if request.method == 'POST':
		# esta_en_db = False
		# Se selecciona (aniade) la micronota a la BB.DD. "Seleccion" para ese usuario (sesion)
		# fecha_seleccion = None
		fecha_seleccion = datetime.now()
		micronota = Micronota.objects.get(url = url)
		fecha_publicacion = micronota.fecha_publicacion
		url_micronota = micronota.url
		p = Seleccion(sesion = sesion, fecha_seleccion = fecha_seleccion, micronota = micronota,
					fecha_publicacion = fecha_publicacion, url_micronota =url_micronota)
		p.save()
		mensaje = 'Micronota seleccionada correctamente'
		return render_to_response('mensaje.html', {
								'usuario': usuario, 
								'mensaje': mensaje, 
								'css': css})
	else:
		error = 'Solo el metodo POST se permite sobre este recurso'
        return render_to_response('error.html', {
								'usuario': usuario, 
								'error': error, 
								'css': css})



#************************************************************************************************************************************
def deseleccionar(request, url):
	# Se comprueba si el usuario tiene cookie, porque entonces podria tener su propio css
	datos_usuario = compruebaCookie(request)
	usuario = datos_usuario[0]
	css = datos_usuario[1]
	sesion = datos_usuario[2]
	# Se comprueba cada metodo
	if request.method == 'POST':
		# Se deselecciona (borra) de la BB.DD. "Seleccion" para ese usuario
		seleccionada = Seleccion.objects.filter(sesion = sesion, url_micronota = url)
		seleccionada.delete()
		mensaje = 'Micronota deseleccionada correctamente'
		return render_to_response('mensaje.html', {
								'usuario': usuario, 
								'mensaje': mensaje, 
								'css': css})
	else:
		error = 'Solo el metodo POST se permite sobre este recurso'
        return render_to_response('error.html', {
								'usuario': usuario, 
								'error': error, 
								'css': css})



#************************************************************************************************************************************
def puntuar(request, url):
	# Se comprueba si el usuario tiene cookie, porque entonces podria tener su propio css
	datos_usuario = compruebaCookie(request)
	usuario = datos_usuario[0]
	css = datos_usuario[1]
	sesion = datos_usuario[2]
	# Se comprueba cada metodo
	if request.method == 'GET':
		# Se comprueba que no haya sido ya puntuada por el usuario
		esta_puntuada = False
		try:
			Puntuacion.objects.filter(sesion = sesion).get(url_micronota = url)
			esta_puntuada = True
		except:
			pass
		# Si ya fue puntuada previamente se envia un mensaje de error avisando al usuario
		if esta_puntuada:
			error = 'Usted ya ha puntuado esta micronota.'
			return render_to_response('error.html', {
								'usuario': usuario, 
								'error': error, 
								'css': css})
		else:
			# Se envia el formulario
			return render_to_response('puntuar.html', {
									'usuario': usuario, 
									'url_micronota': url,
									'css': css})
	elif request.method == 'POST':
		# Se aniade la puntuacion de la micronota a la BB.DD. "Puntuacion" para ese usuario (sesion)
		puntos = request.POST['puntaje']
		micronota = Micronota.objects.get(url = url)
		p = Puntuacion(sesion = sesion, puntos = puntos, url_micronota = micronota.url)
		p.save()
		mensaje = 'Micronota puntuada correctamente'
		return render_to_response('mensaje.html', {
								'usuario': usuario, 
								'mensaje': mensaje, 
								'css': css})
	else:
		error = 'Metodo no permitido sobre el recurso /puntuar'
        return render_to_response('error.html', {
								'usuario': usuario, 
								'error': error, 
								'css': css})



#************************************************************************************************************************************
def ver_ultimas30(request):
	# Se comprueba si el usuario tiene cookie, porque entonces podria tener su propio css
	datos_usuario = compruebaCookie(request)
	usuario = datos_usuario[0]
	css = datos_usuario[1]
	sesion = datos_usuario[2]
	# Se comprueba cada metodo
	if request.method == 'GET':
		# Recoge las 30 ultimas micronotas del sitio en general
		micronotas_a_mostrar = []
		siguiente = 30		
		try:
			for i in range(30):
				# Se extrae la micronota
				# micronota = Micronota.objects.order_by('-fecha_publicacion')[i]
				micronota = Micronota.objects.all()[i]
				# Se comprueba si esta seleccionada la micronota por el usuario
				seleccionada = False
				fecha_seleccion = None
				try:
					seleccionadas = Seleccion.objects.filter(sesion = sesion)
					for j in range(seleccionadas.count()):
						if seleccionadas[j].micronota.url == micronota.url:
							seleccionada = True
							# Si esta seleccionada por el usuario se anota la fecha de seleccion
							fecha_seleccion = seleccionadas[j].fecha_seleccion
							break
				except:
					pass
				# Se cuenta el numero de visitantes que han seleccionado esta micronota
				try:
					veces_seleccionada = Seleccion.objects.filter(micronota = micronota).count()
				except:
					veces_seleccionada = 0
				# Se comprueba si ha sido puntuada por el usuario, y se recupera la nota puesta
				try:
					record = Puntuacion.objects.filter(sesion = sesion).get(url_micronota = micronota.url)
					puntuada = True
					mi_puntuacion = record.puntos
				except:
					puntuada = False
					mi_puntuacion = 0
				# Se cuenta el numero de puntuaciones que ha recibido esta micronota
				try:
					veces_puntuada = Puntuacion.objects.filter(url_micronota = micronota.url).count()
				except:
					veces_puntuada = 0
				# Se obtiene la nota media de la micronota
				punt_media = media(micronota.url)
				# LISTA DE DICCIONARIOS
				diccionario={}
				diccionario['seleccionada'] = seleccionada
				diccionario['fecha_seleccion'] = fecha_seleccion
				diccionario['veces_seleccionada'] = veces_seleccionada
				diccionario['puntuada'] = puntuada
				diccionario['mi_puntuacion'] = mi_puntuacion
				diccionario['punt_media'] = punt_media
				diccionario['veces_puntuada'] = veces_puntuada
				diccionario['url'] = micronota.url
				diccionario['contenido'] = micronota.contenido
				diccionario['micronotero'] = micronota.micronotero
				diccionario['fecha_publicacion'] = micronota.fecha_publicacion
				diccionario['avatar'] = micronota.avatar
				micronotas_a_mostrar.append(diccionario)
		except:
			pass
		return render_to_response('muestra_micronotas.html', {
								'usuario': usuario, 
								'micronotas_a_mostrar': micronotas_a_mostrar,
								'n_siguiente': siguiente,
								'css': css,})
	else:
		error = 'Solo el metodo GET se permite sobre este recurso'
        return render_to_response('error.html', {
								'usuario': usuario, 
								'error': error, 
								'css': css})



#*************************************************************************************************************************************
def ver_seleccion(request, nnn=0):
	# Se comprueba si el usuario tiene cookie, porque entonces podria tener su propio css
	datos_usuario = compruebaCookie(request)
	usuario = datos_usuario[0]
	css = datos_usuario[1]
	sesion = datos_usuario[2]
	# Se comprueba cada metodo
	if request.method == 'GET':
		# Recoge las 30 ultimas micronotas del sitio en general
		micronotas_a_mostrar = []
		siguiente = int(nnn) + 30
		try:
			for i in range(30):
				# Se extrae la micronota
				# micronota = Micronota.objects.order_by('-fecha_publicacion')[i + int(nnn)]
				micronota = Micronota.objects.all()[i + int(nnn)]
				# Se comprueba si esta seleccionada la micronota por el usuario
				seleccionada = False
				fecha_seleccion = None
				try:
					seleccionadas = Seleccion.objects.filter(sesion = sesion)
					for j in range(seleccionadas.count()):
						if seleccionadas[j].micronota.url == micronota.url:
							seleccionada = True
							# Si esta seleccionada por el usuario se anota la fecha de seleccion
							fecha_seleccion = seleccionadas[j].fecha_seleccion
							break
				except:
					pass			
				# Se cuenta el numero de visitantes que han seleccionado esta micronota
				try:
					veces_seleccionada = Seleccion.objects.filter(micronota = micronota).count()
				except:
					veces_seleccionada = 0
				# Se comprueba si ha sido puntuada por el usuario, y se recupera la nota puesta
				try:
					record = Puntuacion.objects.filter(sesion = sesion).get(url_micronota = micronota.url)
					puntuada = True
					mi_puntuacion = record.puntos
				except:
					puntuada = False
					mi_puntuacion = 0
				# Se cuenta el numero de puntuaciones que ha recibido esta micronota
				try:
					veces_puntuada = Puntuacion.objects.filter(url_micronota = micronota.url).count()
				except:
					veces_puntuada = 0
				# Se obtiene la nota media de la micronota
				punt_media = media(micronota.url)
				# LISTA DE DICCIONARIOS
				diccionario={}
				diccionario['seleccionada'] = seleccionada
				diccionario['fecha_seleccion'] = fecha_seleccion
				diccionario['veces_seleccionada'] = veces_seleccionada
				diccionario['puntuada'] = puntuada
				diccionario['mi_puntuacion'] = mi_puntuacion
				diccionario['punt_media'] = punt_media
				diccionario['veces_puntuada'] = veces_puntuada
				diccionario['url'] = micronota.url
				diccionario['contenido'] = micronota.contenido
				diccionario['micronotero'] = micronota.micronotero
				diccionario['fecha_publicacion'] = micronota.fecha_publicacion
				diccionario['avatar'] = micronota.avatar
				micronotas_a_mostrar.append(diccionario)
		except:
			pass
		return render_to_response('muestra_micronotas.html', {
								'usuario': usuario, 
								'micronotas_a_mostrar': micronotas_a_mostrar,
								'n_siguiente': siguiente,
								'css': css,})
	else:
		error = 'Solo el metodo GET se permite sobre este recurso'
        return render_to_response('error.html', {
								'usuario': usuario, 
								'error': error, 
								'css': css})



#***************************************************************************************************************************************
def update(request):
	# Recurso de actualizacion. Extrae ultimas 20 micronotas de Identi.ca y las almacena en la BB.DD. (si no estuvieran ya).
	# Ademas, muestra esas nuevas micronotas
	# Se comprueba si el usuario tiene cookie, porque entonces podria tener su propio css
	datos_usuario = compruebaCookie(request)
	usuario = datos_usuario[0]
	css = datos_usuario[1]
	sesion = datos_usuario[2]
	# Se comprueba cada metodo
	if request.method == 'GET':
		try:
			elemento = "/rss"
			conn = httplib.HTTPConnection("identi.ca")
			conn.request("GET", elemento)
			respuesta = conn.getresponse()
			# En data tenemos el contenido (rss) de la pagina web (Identi.ca)	
			data = respuesta.read()
			conn.close()
		except Exception:
			error = "No se puede contactar con Identi.ca"
			return render_to_response('error.html', {
									'usuario': usuario, 
									'error': error, 
									'css': css})


    	# Se guarda el canal rss en un archivo xml
		auxFile = open('MiIdentica.rss','w')
		auxFile.write(data)
		auxFile.close()

		# Se borran todos los objetos previos en la BB.DD. auxiliar
		objetos_previos = AuxMicronota.objects.all()
		objetos_previos.delete()
		
		# Load parser and driver
		theParser = make_parser()
		theHandler = ParserXML.myContentHandler()
		theParser.setContentHandler(theHandler)

		# Ready, set, go!
		xmlFile = open('MiIdentica.rss',"r")
		theParser.parse(xmlFile)

		# Se comprobara para las 20 ultimas de la BB.DD.auxiliar, si ya esta en la BB.DD. principal
		micronotas_a_mostrar = []
		for i in range(20):
			micronota = AuxMicronota.objects.all()[i]
			# Si no esta, se aniade a la BB.DD. principal
			try:
				# Se comprueba si esta ya en la BB.DD. principal
				Micronota.objects.get(url = micronota.url)
			except Micronota.DoesNotExist:
				# Excepcion si no lo encuentra (aniade la micronota a la BB.DD. Micronota)
				p = Micronota(url = micronota.url, contenido = micronota.contenido, micronotero = micronota.micronotero,
							fecha_publicacion = micronota.fecha_publicacion, avatar = micronota.avatar)
				p.save()
				# Se cuenta el numero de visitantes que han seleccionado esta micronota
				try:
					veces_seleccionada = Seleccion.objects.filter(micronota = micronota).count()
				except:
					veces_seleccionada = 0
				# Se comprueba si ha sido puntuada por el usuario, y se recupera la nota puesta
				try:
					record = Puntuacion.objects.filter(sesion = sesion).get(url_micronota = micronota.url)
					puntuada = True
					mi_puntuacion = record.puntos
				except:
					puntuada = False
					mi_puntuacion = 0
				# Se cuenta el numero de puntuaciones que ha recibido esta micronota
				try:
					veces_puntuada = Puntuacion.objects.filter(url_micronota = micronota.url).count()
				except:
					veces_puntuada = 0
				# Se obtiene la nota media de la micronota
				punt_media = media(micronota.url)
				# LISTA DE DICCIONARIOS
				diccionario={}
				diccionario['seleccionada'] = False
				diccionario['fecha_seleccion'] = None
				diccionario['veces_seleccionada'] = veces_seleccionada
				diccionario['puntuada'] = puntuada
				diccionario['mi_puntuacion'] = mi_puntuacion
				diccionario['punt_media'] = punt_media
				diccionario['veces_puntuada'] = veces_puntuada
				diccionario['url'] = micronota.url
				diccionario['contenido'] = micronota.contenido
				diccionario['micronotero'] = micronota.micronotero
				diccionario['fecha_publicacion'] = micronota.fecha_publicacion
				diccionario['avatar'] = micronota.avatar
				micronotas_a_mostrar.append(diccionario)
		# Por ultimo, se muestran las micronotas aniadidas a la BB.DD. principal
		return render_to_response('muestra_micronotas.html', {
								'usuario': usuario, 
								'micronotas_a_mostrar': micronotas_a_mostrar,
								'n_siguientes': None,	# Para poder distinguir cuando no hay que mostrar "Ver 30 micronotas siguientes"
								'css': css,})
	else:
		error = 'Solo el metodo GET se permite sobre el recurso /update'
		return render_to_response('error.html', {
								'usuario': usuario, 
								'error': error, 
								'css': css})	



#***************************************************************************************************************************************
def selected(request):
	# Listado de todas las micronotas seleccionadas por el visitante actual
	# Se comprueba si el usuario tiene cookie, porque entonces podria tener su propio css
	datos_usuario = compruebaCookie(request)
	usuario = datos_usuario[0]
	css = datos_usuario[1]
	sesion = datos_usuario[2]
	# Se comprueba cada metodo
	if request.method == 'GET':
		micronotas_seleccionadas = []		# LISTA DE DICCIONARIOS
		try:
			# Filter devuelve una lista Query...
			seleccionadas = Seleccion.objects.filter(sesion = sesion).order_by('-fecha_publicacion')
			n_records = seleccionadas.count()	
			for i in range(n_records):				#len(seleccionadas)):
				# Obtengo cada micronota
				micronota = seleccionadas[i].micronota
				# Obtengo la fecha de seleccion de la micronota por parte del usuario
				fecha_seleccion = seleccionadas[i].fecha_seleccion
				# Se cuenta el numero de visitantes que han seleccionado esta micronota
				try:
					veces_seleccionada = Seleccion.objects.filter(micronota = micronota).count()
				except:
					veces_seleccionada = 0
				# Se comprueba si ha sido puntuada por el usuario, y se recupera la nota puesta
				try:
					record = Puntuacion.objects.filter(sesion = sesion).get(url_micronota = micronota.url)
					puntuada = True
					mi_puntuacion = record.puntos
				except:
					puntuada = False
					mi_puntuacion = 0
				# Se cuenta el numero de puntuaciones que ha recibido esta micronota
				try:
					veces_puntuada = Puntuacion.objects.filter(url_micronota = micronota.url).count()
				except:
					veces_puntuada = 0
				# Se obtiene la nota media de la micronota
				punt_media = media(micronota.url)
				# Se aniaden la micronotas seleccionadas (+ fecha_seleccion + veces_seleccionada) al diccionario
				diccionario={}
				diccionario['seleccionada'] = True
				diccionario['fecha_seleccion'] = fecha_seleccion
				diccionario['veces_seleccionada'] = veces_seleccionada
				diccionario['puntuada'] = puntuada
				diccionario['mi_puntuacion'] = mi_puntuacion
				diccionario['punt_media'] = punt_media
				diccionario['veces_puntuada'] = veces_puntuada
				diccionario['url'] = micronota.url
				diccionario['contenido'] = micronota.contenido
				diccionario['micronotero'] = micronota.micronotero
				diccionario['fecha_publicacion'] = micronota.fecha_publicacion
				diccionario['avatar'] = micronota.avatar
				# Se aniade el diccionario a la lista de micronotas seleccionadas
				micronotas_seleccionadas.append(diccionario)
		except:
			pass
		return render_to_response('muestra_micronotas.html', {
								'usuario': usuario, 
								'micronotas_a_mostrar': micronotas_seleccionadas,
								'n_siguientes': None,	# Para poder distinguir que no hay que mostrar 30 micronotas siguientes
								'css': css,})
	else:
		error = 'Solo el metodo GET se permite sobre este recurso'
		return render_to_response('error.html', {
								'usuario': usuario, 
								'error': error, 
								'css': css})



#***************************************************************************************************************************************
def feed(request):
	# Devuelve un canal RSS con las 10 micronotas mas recientes seleccionadas por el visitante actual
	# Se comprueba si el usuario tiene cookie, porque entonces podria tener su propio css
	datos_usuario = compruebaCookie(request)
	usuario = datos_usuario[0]
	css = datos_usuario[1]
	sesion = datos_usuario[2]
	# Se comprueba cada metodo
	if request.method == 'GET':
		micronotas_feed = []
		try:
			# Filter devuelve una lista Query...
			seleccionadas = Seleccion.objects.filter(sesion = sesion).order_by('-fecha_publicacion')
			for i in range(10):
				# Obtengo cada micronota
				micronota = seleccionadas[i].micronota
				# Se aniaden las 10 ultimas micronotas seleccionadas a la lista "micronotas_feed"
				micronotas_feed.append(micronota)
		except:
			pass
		return render_to_response('rss.html', {
								'usuario': usuario, 
								'micronotas': micronotas_feed,})
	else:
		error = 'Solo el metodo GET se permite sobre el recurso /feed'
		return render_to_response('error.html', {
								'usuario': usuario, 
								'error': error, 
								'css': css})



#***************************************************************************************************************************************
def conf(request):
	# Incluye campos para editar el nombre del visitante
	# Se comprueba si el usuario tiene cookie, porque entonces podria tener su propio css
	datos_usuario = compruebaCookie(request)
	usuario = datos_usuario[0]
	css = datos_usuario[1]
	sesion = datos_usuario[2]
	# Se inicializan variables de control (en plantillas)
	nombre_repetido = False	#False es None
	nombre_cambiado = False
	# Se comprueba cada metodo
	if request.method == 'GET':
		# Aqui se envia el formulario
		return render_to_response('conf.html', {
								'usuario': usuario, 
								'nombre_repetido': nombre_repetido, 
								'nombre_cambiado': nombre_cambiado,
								'css': css})
	elif request.method == 'POST':
		# Aqui se recogen los datos del formulario
		nuevo_nombre = request.POST['nombre']
		nombre_repetido = False
		mismo_nombre = False
		# Se comprueba que nadie mas tenga ese nombre (si es distinto de invitado)
		# El nombre 'invitado' no se considera como repetido
		if nuevo_nombre != 'invitado':
			try:
				Visitante.objects.get(nombre = nuevo_nombre)
				nombre_repetido = True
			except Visitante.DoesNotExist:
				pass
		# Si no es nombre_repetido, entonces se cambia en la BB.DD.
		if nombre_repetido == False:
			record = Visitante.objects.get(sesion = sesion)
			record.nombre = nuevo_nombre
			record.save()
			nombre_cambiado = True
		# Por ultimo, se comprueba si el nombre elegido ha sido el que ya tenia!!!
		if nuevo_nombre == usuario:
			nombre_repetido = False
			nombre_cambiado = False
			mismo_nombre = True
		# Se envia la respuesta
		nombre_actual = Visitante.objects.get(sesion = sesion).nombre
		return render_to_response('conf.html', {
								'usuario': nombre_actual, 
								'nombre_repetido': nombre_repetido, 
								'nombre_cambiado': nombre_cambiado,
								'mismo_nombre': mismo_nombre,
								'css': css})
	else:
		# Cualquier otro metodo no es aceptado para /conf
		error = 'Metodo no soportado para /conf'
		return render_to_response('error.html', {
								'usuario': usuario, 
								'error': error, 
								'css': css})



#***************************************************************************************************************************************
def skin(request):
	# Aqui el visitante podra ver (y editar) el fichero CSS que codificara su estilo
	# Se comprueba si el usuario tiene cookie, porque entonces podria tener su propio css
	datos_usuario = compruebaCookie(request)
	usuario = datos_usuario[0]
	css = datos_usuario[1]
	sesion = datos_usuario[2]
	# Se inicializan variables de control (en plantillas)
	css_cambiado = False
	# Se comprueba cada metodo
	if request.method == 'GET':
		#Aqui se envia el formulario (con el css editable)
		texto_css = css
		return render_to_response('skin.html', {
								'usuario': usuario,
								'css_cambiado': css_cambiado,
								'texto_css': texto_css,
								'css': css})
	elif request.method == 'POST':
		# Aqui se recogen los datos del formulario (nuevo_css)
		texto_nuevo_css = request.POST['nuevo_css']
		# Se cambia el texto del css del visitante en la BB.DD.
		record = Visitante.objects.get(sesion = sesion)
		record.css = texto_nuevo_css
		record.save()
		css_cambiado = True
		# Ahora se pone el texto del nuevo css en la ruta correspondiente
		#auxFile = open(os.path.join(settings.PROJECT_PATH,'sfiles' + ruta_nuevo_css),'w')
		#auxFile.write(texto_nuevo_css)
		#auxFile.close()
		# Se envia la respuesta
		return render_to_response('skin.html', {
								'usuario': usuario,
								'css_cambiado': css_cambiado,
								'texto_css': texto_nuevo_css,
								'css': texto_nuevo_css})
	else:
		# Cualquier otro metodo no es aceptado para /skin
		error = 'Metodo no soportado para /skin'
		return render_to_response('error.html', {
								'usuario': usuario, 
								'error': error, 
								'css': css})



#***************************************************************************************************************************************
def cookies(request):
	# Devuelve una pagina HTML que incluye un listado de las cookies que se estan usando para cada "visitante conocido"
	# Se comprueba si el usuario tiene cookie, porque entonces podria tener su propio css
	datos_usuario = compruebaCookie(request)
	usuario = datos_usuario[0]
	css = datos_usuario[1]
	sesion = datos_usuario[2]
	# Se comprueba cada metodo
	if request.method == 'GET':
		visitantes = []
		# Se recogen todas las cookies de la BB.DD. Visitante
		records = Visitante.objects.all()
		for i in range(len(records)):
			record = Visitante.objects.all()[i]
			if record.value != "":
				visitantes.append(record)
		# Se envian todas las cookies en un formato listo para ser usado en un editor de cookies
		return render_to_response('cookies.html', {
								'usuario': usuario,
								'visitantes': visitantes,
								'css': css})
	else:
		error = 'Solo el metodo GET se permite sobre este recurso'
		return render_to_response('error.html', {
								'usuario': usuario, 
								'error': error, 
								'css': css})


#***************************************************************************************************************************************
def Opcion_No_Valida(request, recurso):
	# Se comprueba si el usuario tiene cookie, porque entonces podria tener su propio css
	datos_usuario = compruebaCookie(request)
	usuario = datos_usuario[0]
	css = datos_usuario[1]
	sesion = datos_usuario[2]
	# Se le comunica que esa opcion no es valida
	error = 'El recurso "' + recurso + '" seleccionado no se implementa!!!'
	return render_to_response('error.html', {
							'usuario': usuario, 
							'error': error, 
							'css': css})



