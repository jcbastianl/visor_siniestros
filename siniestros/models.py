from django.db import models
from .managers import SiniestroManager, VictimaManager


class TipoSiniestro(models.Model):
    """Catálogo de tipos de siniestro con borrado lógico."""
    nombre = models.CharField(max_length=100, unique=True)
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
    """Catálogo de causas probables con borrado lógico."""
    nombre = models.CharField(max_length=255, unique=True)
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


class Siniestro(models.Model):
    """
    Modelo principal de siniestros de tránsito.

    Almacena toda la información de un evento: ubicación, condiciones,
    vehículos involucrados, víctimas y daños. Los campos se mapean
    automáticamente desde los archivos Excel/CSV de la institución.
    """

    # --- Información básica ---
    fecha_hora = models.DateTimeField(db_index=True, help_text="Fecha y hora del siniestro")
    latitud = models.FloatField(help_text="Latitud del siniestro")
    longitud = models.FloatField(help_text="Longitud del siniestro")
    via = models.CharField(max_length=200, blank=True, help_text="Tipo de vía donde ocurrió el siniestro")

    class Severidad(models.TextChoices):
        CON_FALLECIDOS = 'CON_FALLECIDOS', 'Con fallecidos en sitio'
        CON_LESIONADOS = 'CON_LESIONADOS', 'Con lesionados'
        SOLO_DANOS = 'SOLO_DANOS', 'Solo con daños materiales'

    grado_severidad = models.CharField(max_length=20, choices=Severidad.choices)
    tipo_siniestro = models.ForeignKey(TipoSiniestro, on_delete=models.PROTECT, null=True, blank=True)
    causa_probable = models.ForeignKey(Causa, on_delete=models.PROTECT, null=True, blank=True)

    # --- Ubicación detallada ---
    zona = models.CharField(max_length=100, blank=True, help_text="Zona urbana/rural")
    barrio = models.CharField(max_length=100, blank=True, db_index=True, help_text="Barrio donde ocurrió")
    parroquia = models.CharField(max_length=100, blank=True, db_index=True, help_text="Parroquia urbana")
    parroquia_rural = models.CharField(max_length=100, blank=True, help_text="Parroquia rural")
    direccion_completa = models.TextField(blank=True, help_text="Dirección registrada completa")
    calle_principal = models.CharField(max_length=200, blank=True, help_text="Calle o avenida principal")
    calle_secundaria = models.CharField(max_length=200, blank=True, help_text="Calle o avenida secundaria")
    referencia = models.TextField(blank=True, help_text="Referencia del lugar")

    # --- Condiciones del evento ---
    condicion_calzada = models.CharField(max_length=50, blank=True, db_index=True, help_text="Estado de la calzada")
    condicion_atmosferica = models.CharField(max_length=50, blank=True, help_text="Condición climática")
    condicion_via = models.CharField(max_length=50, blank=True, help_text="Estado de la vía")
    luz_artificial = models.CharField(max_length=50, blank=True, help_text="Presencia de luz artificial")
    lugar_en_via = models.CharField(max_length=100, blank=True, help_text="Lugar específico en la vía")
    senalizacion_existente = models.CharField(max_length=100, blank=True, help_text="Señalización existente")

    # --- Vehículos ---
    num_vehiculos_involucrados = models.IntegerField(default=0, db_index=True, help_text="Número de vehículos involucrados")
    vehiculos_particular = models.IntegerField(default=0, help_text="Cantidad de vehículos particulares")
    vehiculos_publico = models.IntegerField(default=0, help_text="Cantidad de vehículos públicos")
    vehiculos_comercial = models.IntegerField(default=0, help_text="Cantidad de vehículos comerciales")
    tipos_vehiculos = models.TextField(blank=True, help_text="Tipos de vehículos separados por coma")

    # --- Contadores ---
    num_heridos = models.IntegerField(default=0, help_text="Número de personas heridas")
    num_fallecidos = models.IntegerField(default=0, help_text="Número de personas fallecidas")
    num_pruebas_alcohotest = models.IntegerField(default=0, help_text="Número de pruebas de alcohotest realizadas")
    num_personas_detenidas = models.IntegerField(default=0, help_text="Número de personas detenidas")
    vehiculos_retenidos = models.IntegerField(default=0, help_text="Número de vehículos retenidos")

    # --- Daños al bien público ---
    tiene_danos_bien_publico = models.BooleanField(default=False, help_text="¿Hubo daños al bien público?")
    descripcion_dano_bien_publico = models.TextField(blank=True, help_text="Descripción del daño al bien público")

    # --- Datos adicionales (campos extra del CSV que no tienen campo dedicado) ---
    datos_adicionales = models.JSONField(default=dict, blank=True, help_text="Datos adicionales del CSV original")

    objects = SiniestroManager()

    class Meta:
        verbose_name = "Siniestro"
        verbose_name_plural = "Siniestros"
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Siniestro el {self.fecha_hora.strftime('%Y-%m-%d')}"


class Victima(models.Model):
    """
    Víctima asociada a un siniestro.

    Usa TextChoices para condición, sexo y actor vial porque estos valores
    son fijos y no necesitan borrado lógico.
    """
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
