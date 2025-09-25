from django.db import models

# Create your models here

from django.db import models

class TextoAnalizado(models.Model):
    titulo = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='textos/')
    texto_original = models.TextField(blank=True, null=True)
    texto_procesado = models.TextField(blank=True, null=True)  
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Texto {self.id} - {self.fecha_subida}"

class Ngrama(models.Model):
    texto = models.ForeignKey(TextoAnalizado, on_delete=models.CASCADE, related_name="ngramas")
    n = models.IntegerField()  # si es bigrama (2), trigramas (3), etc.
    secuencia = models.TextField(default="")
 
    frecuencia = models.IntegerField(default=0)
    class Meta:
        ordering = ['-frecuencia', 'secuencia']  # Primero por frecuencia descendente, luego alfabéticamente

    def __str__(self):
        return f"{self.secuencia} ({self.frecuencia})"
