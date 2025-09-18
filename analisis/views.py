from django.shortcuts import render, redirect, get_object_or_404
from .forms import TextoAnalizadoForm
from .models import TextoAnalizado

from collections import defaultdict, Counter
import re
from nltk.corpus import stopwords
import unicodedata
from nltk.util import ngrams

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


# ======= Subir texto + cálculo de n-gramas =======
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

            # ==== NUEVO: cálculo de n-gramas ====
            try:
                n_raw = (request.POST.get("n") or "").strip()
                n_value = int(n_raw) if n_raw else 2
            except ValueError:
                n_value = 2

            if n_value < 2:   # aseguramos mínimo 2
                n_value = 2

            ngramas = list(ngrams(tokens_limpios, n_value))
            frecuencias = Counter(ngramas)

            return render(request, 'analisis/subir.html', {
                'form': TextoAnalizadoForm(),
                'texto_original': texto_obj.texto_original,
                'texto_procesado': texto_obj.texto_procesado,
                'tokens': tokens_limpios,
                'n': n_value,
                'ngramas': ngramas,
                'frecuencias': dict(frecuencias)
            })
    else:
        form = TextoAnalizadoForm()

    return render(request, 'analisis/subir.html', {'form': form})


# ======= Lista de textos =======
def lista_textos(request):
    textos = TextoAnalizado.objects.all().order_by('-fecha_subida')
    return render(request, 'analisis/lista.html', {'textos': textos})


# ======= Eliminar texto =======
def eliminar_texto(request, texto_id):
    texto = get_object_or_404(TextoAnalizado, pk=texto_id)
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

# ======= Cálculo MLE para bigramas =======
def calcular_mle(request, texto_id):
    texto = get_object_or_404(TextoAnalizado, id=texto_id)
    contenido = texto.texto_procesado or ""

    # 🔹 Tokenizador rápido sin NLTK
    tokens = re.findall(r'\w+', contenido.lower())  # quita puntuación y normaliza a minúsculas

    unigramas = Counter(tokens)
    bigramas = Counter(ngrams(tokens, 2))

    mle_resultados = []
    for (w1, w2), conteo_bigram in bigramas.items():
        prob = conteo_bigram / unigramas[w1]
        mle_resultados.append({
            'w1': w1,
            'w2': w2,
            'conteo_bigram': conteo_bigram,
            'conteo_unigrama': unigramas[w1],
            'probabilidad': round(prob, 4)
        })

    return render(request, 'analisis/mle.html', {
        'texto': texto,
        'tokens': tokens,
        'resultados': mle_resultados,
        'unigramas': dict(unigramas),
        'bigramas': dict(bigramas),
    })


# ======= Cálculo MLE con fronteras de oración =======
def calcular_mle_fronteras(request, texto_id):
    texto = get_object_or_404(TextoAnalizado, id=texto_id)
    contenido = texto.texto_procesado or ""

    # Dividir en oraciones
    oraciones = [o.strip() for o in contenido.split(".") if o.strip()]

    palabras = []
    for oracion in oraciones:
        tokens = re.findall(r'\w+', oracion.lower())
        if tokens:
            palabras.extend(["<s>"] + tokens + ["</s>"])

    unigramas = Counter(palabras)
    bigramas = Counter(ngrams(palabras, 2))

    mle_resultados = []
    for (w1, w2), conteo_bigram in bigramas.items():
        prob = conteo_bigram / unigramas[w1]
        mle_resultados.append({
            'w1': w1,
            'w2': w2,
            'conteo_bigram': conteo_bigram,
            'conteo_unigrama': unigramas[w1],
            'probabilidad': round(prob, 4)
        })

    return render(request, 'analisis/mle_fronteras.html', {
        'texto': texto,
        'tokens': palabras,
        'resultados': mle_resultados,
        'unigramas': dict(unigramas),
        'bigramas': dict(bigramas),
    })

