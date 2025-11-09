from django.db import models
from django.core.exceptions import ValidationError
from .managers import SiniestroManager, VictimaManager

# --- 1. MODELOS DE OPCIONES (Para listas largas) ---
# Implementamos "Borrado Lógico" (Soft Delete)

class TipoSiniestro(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    # --- CAMBIO 1: Borrado Lógico ---
    activo = models.BooleanField(
        default=True,
        help_text="Desmarcar para 'dar de baja' este tipo sin borrarlo"
    )

    class Meta:
        verbose_name = "Tipo de Siniestro"
        verbose_name_plural = "Tipos de Siniestros"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Causa(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    
    # --- CAMBIO 1: Borrado Lógico ---
    activo = models.BooleanField(
        default=True,
        help_text="Desmarcar para 'dar de baja' esta causa sin borrarla"
    )

    class Meta:
        verbose_name = "Causa Probable"
        verbose_name_plural = "Causas Probables"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# --- 2. MODELO PRINCIPAL (Siniestro) ---

class Siniestro(models.Model):
    # ... (campos fecha_hora, latitud, longitud, via) ...
    fecha_hora = models.DateTimeField(db_index=True, help_text="Fecha y hora del siniestro")
    latitud = models.FloatField(help_text="Latitud del siniestro")
    longitud = models.FloatField(help_text="Longitud del siniestro")
    via = models.CharField(max_length=200, blank=True, help_text="Tipo de vía donde ocurrió el siniestro")

    # (El campo Severidad se queda igual, con TextChoices, porque es crítico)
    class Severidad(models.TextChoices):
        CON_FALLECIDOS = 'CON_FALLECIDOS', 'con fallecidos en sitio'
        CON_LESIONADOS = 'CON_LESIONADOS', 'con lesionados'
        SOLO_DANOS = 'SOLO_DANOS', 'solo con danos materiales'
    grado_severidad = models.CharField(
        max_length=20, 
        choices=Severidad.choices,
    )

    # --- CAMBIO 2: Protección contra borrado ---
    tipo_siniestro = models.ForeignKey(
        TipoSiniestro,
        on_delete=models.PROTECT, # ¡PROHÍBE EL BORRADO!
        null=True, blank=True
    )
    causa_probable = models.ForeignKey(
        Causa, 
        on_delete=models.PROTECT, # ¡PROHÍBE EL BORRADO!
        null=True, blank=True 
    )

    objects = SiniestroManager()

    def __str__(self):
        return f"Siniestro el {self.fecha_hora.strftime('%Y-%m-%d')}"


# --- 3. MODELO RELACIONADO (Victima) ---
# (Este modelo se queda igual, con TextChoices, porque
# 'FALLECIDO' o 'LESIONADO' nunca deben ser 'dados de baja')

class Victima(models.Model):
    # ... (Igual que antes) ...
    siniestro = models.ForeignKey(Siniestro, related_name="victimas", on_delete=models.CASCADE)
    edad = models.PositiveIntegerField(null=True, blank=True, help_text="Edad de la víctima")

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
    
    def __str__(self):
        return f"Víctima ({self.condicion}) del siniestro {self.siniestro.id}"