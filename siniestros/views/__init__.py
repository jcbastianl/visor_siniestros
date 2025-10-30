from .api_datos import CausaViewSet, SiniestroViewSet, TipoSiniestroViewSet
from .api_stats_siniestros import (
    KPIStatsView,
    SeveridadStatsView,
    SiniestrosPorDiaHoraView,
    SiniestrosPorHoraView,
    SiniestrosPorMesView,
)
from .api_stats_victimas import (
    VictimasPorActorVialView,
    VictimasPorDiaHoraView,
    VictimasPorEdadSexoView,
    VictimasPorHoraView,
    VictimasPorMesView,
    VictimasPorSexoView,
)

__all__ = [
    'CausaViewSet',
    'SiniestroViewSet',
    'TipoSiniestroViewSet',
    'KPIStatsView',
    'SeveridadStatsView',
    'SiniestrosPorDiaHoraView',
    'SiniestrosPorHoraView',
    'SiniestrosPorMesView',
    'VictimasPorActorVialView',
    'VictimasPorDiaHoraView',
    'VictimasPorEdadSexoView',
    'VictimasPorHoraView',
    'VictimasPorMesView',
    'VictimasPorSexoView',
]
