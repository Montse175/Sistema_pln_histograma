from django.urls import path
from . import views

urlpatterns = [
    path('subir/', views.subir_texto, name='subir_texto'),  # Para subir un texto
    path('', views.lista_textos, name='lista_textos'),      # Página inicial: lista de textos
    path('histograma/<int:texto_id>/', views.generar_histograma, name='generar_histograma'),  
    # path("normalizar/", views.normalizar_texto, name="normalizar"),  # (comentado)
    path('eliminar/<int:texto_id>/', views.eliminar_texto, name='eliminar_texto'),
    path('mle/<int:texto_id>/<int:n>/', views.calcular_mle, name='calcular_mle'),
    path('mle_fronteras/<int:texto_id>/<int:n>/', views.calcular_mle_fronteras, name='calcular_mle_fronteras'),
    path("ngramas/<int:texto_id>/", views.ver_ngrams, name="ver_ngrams"),
    path("ngramas/<int:texto_id>/generar/", views.generar_ngrams_view, name="generar_ngrams"),
    path("mle_fronteras/<int:texto_id>/<int:n_value>/", views.calcular_mle_fronteras, name="calcular_mle_fronteras"),
    path('mle/<int:texto_id>/', views.calcular_mle, {'n': 2}, name='calcular_mle_default'),
    path("autocompletar/<int:texto_id>/<int:n>/", views.autocompletar, name="autocompletar"),
    path("autocompletar/<int:texto_id>/", views.autocompletar, name="autocompletar_default"),


 
]
