from django.urls import path
from . import views

urlpatterns = [
    path('subir/', views.subir_texto, name='subir_texto'),  # Para subir un texto
    path('', views.lista_textos, name='lista_textos'),      # Página inicial: lista de textos
    path('histograma/<int:texto_id>/', views.generar_histograma, name='generar_histograma'),  
    # path("normalizar/", views.normalizar_texto, name="normalizar"),  # (comentado)
    path('eliminar/<int:texto_id>/', views.eliminar_texto, name='eliminar_texto'),
 
]
