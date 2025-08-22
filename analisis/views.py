from django.shortcuts import render, redirect, get_object_or_404
from .forms import TextoAnalizadoForm
from .models import TextoAnalizado

from collections import defaultdict
import os


def subir_texto(request):
    if request.method == 'POST':
        form = TextoAnalizadoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_textos')
    else:
        form = TextoAnalizadoForm()
    return render(request, 'analisis/subir.html', {'form': form})


def lista_textos(request):
    textos = TextoAnalizado.objects.all().order_by('-fecha_subida')
    return render(request, 'analisis/lista.html', {'textos': textos})


def generar_histograma(request, texto_id):
    texto = get_object_or_404(TextoAnalizado, id=texto_id)
    archivo_path = texto.archivo.path

    # Leer archivo
    with open(archivo_path, "r", encoding="utf-8") as f:
        contenido = f.read().lower()

    for ch in [",", ".", ";", ":", "?", "!", "\n", "\t"]:
        contenido = contenido.replace(ch, " ")
    palabras = contenido.split()

    # Contar palabras en una sola pasada
    conteo_dic = defaultdict(int)
    for palabra in palabras:
        conteo_dic[palabra] += 1

    # Ordenar por frecuencia
    conteo = dict(sorted(conteo_dic.items(), key=lambda x: x[1], reverse=True))

    return render(request, 'analisis/histograma.html', {
        'texto': texto,
        'conteo': conteo
    })
