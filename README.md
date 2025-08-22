# Sistema PLN con Django

Este proyecto es un sistema en **Django** para **subir archivos de texto**, generar un **histograma de palabras** y mostrarlo en forma de tabla.  

---

## Requisitos
- Python 3.10 o superior (probado en Python 3.13.2)  
- [Pipenv](https://pipenv.pypa.io/en/latest/) instalado   
- Git para clonar el repositorio  

---

##  Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/Montse175/Sistema_pln_histograma.git
   cd Sistema_pln_histograma
2. Instalar dependencias y crear entorno virtual con Pipenv:
-pipenv install
-pipenv shell

3. Aplicar migraciones:
-python manage.py migrate

4. Crear superusuario para acceder al panel de administración:
-python manage.py createsuperuser

5. Iniciar el servidor:
python manage.py runserver

## Uso del sistema

Subir un archivo:
👉 http://127.0.0.1:8000/subir/

Ver lista de archivos subidos:
👉 http://127.0.0.1:8000/

Generar histograma en tabla:
👉 Desde la lista, hacer clic en "Generar histograma" junto al archivo deseado.

Panel de administración:
👉 http://127.0.0.1:8000/admin/

(usar el superusuario creado).




