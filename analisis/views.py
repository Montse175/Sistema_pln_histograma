from django.shortcuts import render, redirect, get_object_or_404
from .forms import TextoAnalizadoForm
from .models import TextoAnalizado

from collections import defaultdict
import string
import re
from nltk.corpus import stopwords
import unicodedata

# ======= Función de limpieza / normalización =======
def limpiar_texto(texto, opciones):
    texto_procesado = texto

    # Convertir a minúsculas
    if "minusculas" in opciones:
        texto_procesado = texto_procesado.lower()

    # Quitar puntuación
    if "puntuacion" in opciones:
        texto_procesado = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]', '', texto_procesado)

      # Quitar acentos
    if "acentos" in opciones:
        texto_procesado = ''.join(
            c for c in unicodedata.normalize('NFD', texto_procesado)
            if unicodedata.category(c) != 'Mn'
        )
        
    # Tokenizar
    tokens = texto_procesado.split()

    # Eliminar stopwords
    if "stopwords" in opciones:
        try:
            stop_es = set(stopwords.words("spanish"))
        except LookupError:
            stop_es = set()
        tokens = [t for t in tokens if t not in stop_es]

    return " ".join(tokens), tokens


# ======= Subir texto =======
def subir_texto(request):
    if request.method == 'POST':
        form = TextoAnalizadoForm(request.POST, request.FILES)
        if form.is_valid():
            texto_obj = form.save(commit=False)

            # Leer archivo
            archivo = request.FILES["archivo"].read().decode("utf-8", errors="ignore")
            opciones = request.POST.getlist("opciones")

            # Guardar original
            texto_obj.texto_original = archivo

            # Procesar
            texto_procesado, tokens_limpios = limpiar_texto(archivo, opciones)
            texto_obj.texto_procesado = texto_procesado
            texto_obj.save()

            return render(request, 'analisis/subir.html', {
                'form': TextoAnalizadoForm(),
                'texto_original': texto_obj.texto_original,
                'texto_procesado': texto_obj.texto_procesado,
                'tokens': tokens_limpios
            })
    else:
        form = TextoAnalizadoForm()

    return render(request, 'analisis/subir.html', {'form': form})


# ======= Lista de textos =======
def lista_textos(request):
    textos = TextoAnalizado.objects.all().order_by('-fecha_subida')
    return render(request, 'analisis/lista.html', {'textos': textos})


# ======= Eliminar texto =======
def eliminar_texto(request, pk):
    texto = get_object_or_404(TextoAnalizado, pk=pk)
    texto.delete()
    return redirect('lista_textos')


# ======= Histograma =======
def generar_histograma(request, texto_id):
    texto = get_object_or_404(TextoAnalizado, id=texto_id)

    # Usamos el texto procesado en lugar del archivo crudo
    contenido = texto.texto_procesado or ""

    palabras = contenido.split()

    conteo_dic = defaultdict(int)
    for palabra in palabras:
        conteo_dic[palabra] += 1

    # Ordenar por frecuencia
    conteo = dict(sorted(conteo_dic.items(), key=lambda x: x[1], reverse=True))

    return render(request, 'analisis/histograma.html', {
        'texto': texto,
        'conteo': conteo
    })
def eliminar_texto(request, texto_id):
    texto = get_object_or_404(TextoAnalizado, id=texto_id)
    texto.delete()
    return redirect('lista_textos')