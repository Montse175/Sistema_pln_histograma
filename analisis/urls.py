from django.urls import path
from . import views

urlpatterns = [
    path('subir/', views.subir_texto, name='subir_texto'),
    path('', views.lista_textos, name='lista_textos'),
    path('histograma/<int:texto_id>/', views.generar_histograma, name='generar_histograma'),
]
