from django.shortcuts import render, redirect, get_object_or_404
from .forms import TextoAnalizadoForm
from .models import TextoAnalizado, Ngrama

from collections import defaultdict, Counter
import re
from nltk.corpus import stopwords
import unicodedata
from nltk.util import ngrams

from django.shortcuts import render, get_object_or_404 
from django.http import JsonResponse

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

            # Guardar n-gramas en la BD
            for ngrama, freq in frecuencias.items():
                secuencia = " ".join(ngrama)
                Ngrama.objects.create(
                    texto=texto_obj,
                    n=n_value,
                    secuencia=secuencia,
                    frecuencia=freq
                )

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

# ======= Función auxiliar para calcular n-gramas =======
def calcular_ngrams(tokens, n=2):
    if n < 1:
        raise ValueError("El valor de n debe ser >= 1")

    ngramas = list(ngrams(tokens, n))   # <- lista de n-gramas
    frecuencias = Counter(ngramas)      # <- usamos la lista, no la función
    return ngramas, frecuencias



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

def calcular_mle(request, texto_id, n):
    texto = get_object_or_404(TextoAnalizado, id=texto_id)
    tokens = texto.texto_procesado.split() if texto.texto_procesado else []

    n = int(n)
    if n < 1:
        n = 1

    # n-gramas
    ngramas = list(ngrams(tokens, n))
    conteo_ngramas = Counter(ngrams(tokens, n))

    # Contador de contextos (n-1)-gramas
    if n > 1:
        contextos = [ng[:-1] for ng in ngramas]
        conteo_contextos = Counter(contextos)
    else:
        conteo_contextos = conteo_ngramas

    resultados = []
    for ngrama, conteo in conteo_ngramas.items():
        w1 = ngrama[:-1]  # contexto
        w2 = ngrama[-1]   # palabra
        conteo_c = conteo_contextos.get(w1, 0)
        prob = conteo / conteo_c if conteo_c > 0 else 0

        resultados.append({
            "contexto": " ".join(w1),
            "palabra": w2,
            "conteo_ngrama": conteo,
            "conteo_contexto": conteo_c,
            "probabilidad": round(prob, 4)
        })

    total_ngramas = sum(conteo_ngramas.values())
    total_contextos = sum(conteo_contextos.values())

    return render(request, "analisis/mle.html", {
        "texto": texto,
        "resultados": resultados,
        "tokens": tokens,
        "n": n,
        "total_ngramas": total_ngramas,
        "total_contextos": total_contextos
    })

def tokenizar_con_fronteras(texto):
    # Separa palabras y signos de puntuación
    tokens = re.findall(r"\w+|[.!?]", texto)

    resultado = []
    resultado.append("<s>")
    for tok in tokens:
        if tok in [".", "?", "!"]:
            resultado.append("</s>")
            resultado.append("<s>")
        else:
            resultado.append(tok)
    resultado.append("</s>")

    return resultado

def calcular_mle_fronteras(request, texto_id, n):
    texto = get_object_or_404(TextoAnalizado, id=texto_id)
    tokens = tokenizar_con_fronteras(texto.texto_procesado or "")


    n = int(n)
    if n < 1:
        n = 1

    ngramas = list(ngrams(tokens, n))
    conteo_ngramas = Counter(ngrams(tokens, n))

    # Contador de contextos (n-1)-gramas
    if n > 1:
        contextos = [ng[:-1] for ng in ngramas]
        conteo_contextos = Counter(contextos)
    else:
        conteo_contextos = conteo_ngramas

    resultados = []
    for ngrama, conteo in conteo_ngramas.items():
        w1 = ngrama[:-1]
        w2 = ngrama[-1]
        conteo_c = conteo_contextos.get(w1, 0)
        prob = conteo / conteo_c if conteo_c > 0 else 0

        resultados.append({
            "contexto": " ".join(w1),
            "palabra": w2,
            "conteo_ngrama": conteo,
            "conteo_contexto": conteo_c,
            "probabilidad": round(prob, 4)
        })

    total_ngramas = sum(conteo_ngramas.values())
    total_contextos = sum(conteo_contextos.values())

    return render(request, "analisis/mle_fronteras.html", {
        "texto": texto,
        "resultados": resultados,
        "tokens": tokens,
        "n": n,
        "total_ngramas": total_ngramas,
        "total_contextos": total_contextos
    })


def ver_ngrams(request, texto_id):
    texto = get_object_or_404(TextoAnalizado, pk=texto_id)

    # Obtenemos todos los valores únicos de n que existen para este texto
    valores_n = Ngrama.objects.filter(texto=texto).values_list("n", flat=True).distinct().order_by("n")

    # Creamos un diccionario {n: lista_de_ngramas}
    tablas = {}
    for n in valores_n:
        tablas[n] = Ngrama.objects.filter(texto=texto, n=n).order_by("-frecuencia")

    return render(request, 'analisis/ver_ngrams.html', {
        'texto': texto,
        'tablas': tablas
    })

#geberar n-gramas
def generar_ngrams_view(request, texto_id):
    texto = get_object_or_404(TextoAnalizado, id=texto_id)

    if request.method == "POST":
        n_value = int(request.POST.get("n"))

        # Tokenizar el texto procesado
        tokens = texto.texto_procesado.split()

        # Usar la función auxiliar
        ngramas, frecuencias = calcular_ngrams(tokens, n_value)


            # Eliminar n-gramas previos del mismo texto y valor de n
        Ngrama.objects.filter(texto=texto, n=n_value).delete()

        # Guardar los nuevos
        for ngrama, freq in frecuencias.items():
            secuencia = " ".join(ngrama)
            Ngrama.objects.create(
                texto=texto,
                n=n_value,
                secuencia=secuencia,
                frecuencia=freq
            )

        return redirect("ver_ngrams", texto_id=texto.id)

    return render(request, "analisis/generar_ngrams.html", {"texto": texto})


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from collections import Counter
from nltk.util import ngrams

def autocompletar(request, texto_id, n=2):
    texto = get_object_or_404(TextoAnalizado, id=texto_id)

    # Valor por defecto para el formulario (si venimos por GET con ?fronteras=1)
    usar_fronteras_default = request.GET.get("fronteras") == "1"
    usar_fronteras = usar_fronteras_default

    n = int(n) if n else 2
    if n < 1:
        n = 1

    if request.method == "POST":
        entrada = request.POST.get("entrada", "").strip().lower()
        palabras = [p for p in entrada.split() if p.strip()]

        # si el formulario envía un n diferente, lo respetamos
        try:
            n = int(request.POST.get("n", n))
        except (TypeError, ValueError):
            pass

        # leemos la opción de fronteras del POST
        usar_fronteras = request.POST.get("fronteras") == "1"

        # tokens: con o sin fronteras
        if usar_fronteras:
            tokens = tokenizar_con_fronteras(texto.texto_procesado or "")
        else:
            tokens = (texto.texto_procesado or "").split()

        # normalizamos y quitamos tokens vacíos
        tokens = [t.lower() for t in tokens if t and t.strip()]

        # UNIGRAMAS
        if n == 1:
            conteo_uni = Counter([t for t in tokens if t not in ("<s>", "</s>")])
            if not conteo_uni:
                return JsonResponse({"error": "No hay tokens para sugerir."})
            total = sum(conteo_uni.values())
            top = conteo_uni.most_common(3)
            sugerencia = top[0][0] if top else ""
            top3 = [{"palabra": w, "probabilidad": round(freq/total,4)} for w,freq in top]
            return JsonResponse({"sugerencia": sugerencia, "top3": top3, "usar_fronteras": usar_fronteras})

        # BIGRAMAS / TRIGRAMAS
        if n > 1 and len(palabras) < (n - 1):
            return JsonResponse({"error": f"Necesitas al menos {n-1} palabra(s) de contexto para usar {n}-gramas."})

        contexto = tuple(palabras[-(n-1):])
        ngramas_corpus = list(ngrams(tokens, n))
        conteo_ngramas = Counter(ngramas_corpus)
        conteo_contextos = Counter([ng[:-1] for ng in ngramas_corpus])

        # seguridad: si el contexto no aparece, devolvemos mensaje claro
        contexto_count = conteo_contextos.get(contexto, 0)
        if contexto_count == 0:
            return JsonResponse({"mensaje": f"No se encontraron sugerencias para el contexto: {' '.join(contexto)}"})

        candidatos = []
        for ng, freq in conteo_ngramas.items():
            if ng[:-1] == contexto:
                palabra_cand = ng[-1]
                if palabra_cand in ("<s>", "</s>"):
                    continue
                prob = freq / contexto_count if contexto_count > 0 else 0
                candidatos.append((palabra_cand, prob))

        candidatos.sort(key=lambda x: x[1], reverse=True)

        if candidatos:
            sugerencia = candidatos[0][0]
            top3 = [{"palabra": w, "probabilidad": round(p,4)} for w,p in candidatos[:3]]
            return JsonResponse({"sugerencia": sugerencia, "top3": top3, "usar_fronteras": usar_fronteras})

        return JsonResponse({"mensaje": "No se han encontrado candidatos."})

    # GET → render del formulario (pasamos el flag para que el checkbox quede chequeado si venimos con ?fronteras=1)
    return render(request, "analisis/autocompletar.html", {
        "texto": texto,
        "n": int(n),
        "usar_fronteras": usar_fronteras_default
    })