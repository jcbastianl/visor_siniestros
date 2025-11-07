from django.db import models
from django.core.exceptions import ValidationError
from .managers import SiniestroManager, VictimaManager


# --- MODELOS DE OPCIONES (con Soft Delete) ---

class TipoSiniestro(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Siniestro"
        verbose_name_plural = "Tipos de Siniestros"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Causa(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Causa Probable"
        verbose_name_plural = "Causas Probables"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# --- MODELOS PRINCIPALES ---

class Siniestro(models.Model):
    """Evento de siniestro vial."""
    
    fecha_hora = models.DateTimeField(db_index=True)
    latitud = models.FloatField()
    longitud = models.FloatField()
    via = models.CharField(max_length=200, blank=True)

    class Severidad(models.TextChoices):
        CON_FALLECIDOS = 'CON_FALLECIDOS', 'con fallecidos en sitio'
        CON_LESIONADOS = 'CON_LESIONADOS', 'con lesionados'
        SOLO_DANOS = 'SOLO_DANOS', 'solo con danos materiales'

    grado_severidad = models.CharField(max_length=20, choices=Severidad.choices)
    tipo_siniestro = models.ForeignKey(TipoSiniestro, on_delete=models.PROTECT, null=True, blank=True)
    causa_probable = models.ForeignKey(Causa, on_delete=models.PROTECT, null=True, blank=True)

    objects = SiniestroManager()

    class Meta:
        ordering = ['-fecha_hora']
        indexes = [models.Index(fields=['-fecha_hora']), models.Index(fields=['grado_severidad'])]

    def __str__(self):
        return f"Siniestro {self.id} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"


class Victima(models.Model):
    """Víctima de un siniestro vial."""
    
    siniestro = models.ForeignKey(Siniestro, related_name="victimas", on_delete=models.CASCADE)
    edad = models.PositiveIntegerField(null=True, blank=True)

    class Condicion(models.TextChoices):
        FALLECIDO = 'FALLECIDO', 'Fallecido'
        LESIONADO = 'LESIONADO', 'Lesionado'
        ILESO = 'ILESO', 'Ileso'

    condicion = models.CharField(max_length=20, choices=Condicion.choices, db_index=True)

    class Sexo(models.TextChoices):
        HOMBRE = 'HOMBRE', 'Hombre'
        MUJER = 'MUJER', 'Mujer'
        NO_REGISTRA = 'NO_REGISTRA', 'No registra'

    sexo = models.CharField(max_length=20, choices=Sexo.choices, default=Sexo.NO_REGISTRA)

    class ActorVial(models.TextChoices):
        PEATON = 'PEATON', 'Peatón'
        MOTOCICLETA = 'MOTOCICLETA', 'Ocupante Motocicleta'
        VEH_LIVIANO = 'VEH_LIVIANO', 'Ocupante Veh. Liviano'
        CICLISTA = 'CICLISTA', 'Ciclista'
        SCOOTER = 'SCOOTER', 'Ocupante Scooter'
        OTRO = 'OTRO', 'Otro'

    actor_vial = models.CharField(max_length=20, choices=ActorVial.choices, default=ActorVial.OTRO)

    objects = VictimaManager()

    class Meta:
        ordering = ['-siniestro__fecha_hora']
        indexes = [models.Index(fields=['condicion']), models.Index(fields=['sexo'])]

    def __str__(self):
        return f"Víctima {self.id} - {self.condicion}"
