
from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'siniestros', views.SiniestroViewSet, basename='siniestro')
router.register(r'causas', views.CausaViewSet, basename='causa')
router.register(r'tipos-siniestro', views.TipoSiniestroViewSet, basename='tipo-siniestro')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/kpis/', views.KPIStatsView.as_view(), name='stats-kpis'),
    path('stats/por-mes/', views.SiniestrosPorMesView.as_view(), name='stats-por-mes'),
    path('stats/por-severidad/', views.SeveridadStatsView.as_view(), name='stats-por-severidad'),
    path('stats/por-hora/', views.SiniestrosPorHoraView.as_view(), name='stats-por-hora'),
    path('stats/por-dia-hora/', views.SiniestrosPorDiaHoraView.as_view(), name='stats-por-dia-hora'),
    # --- Rutas de Stats "Víctimas" ---
    path('stats/victimas/por-sexo/', views.VictimasPorSexoView.as_view(), name='stats-victimas-por-sexo'),
    path('stats/victimas/por-actor-vial/', views.VictimasPorActorVialView.as_view(), name='stats-victimas-por-actor-vial'),
    path('stats/victimas/por-edad-sexo/', views.VictimasPorEdadSexoView.as_view(), name='stats-victimas-por-edad-sexo'),
    path('stats/victimas/por-mes/', views.VictimasPorMesView.as_view(), name='stats-victimas-por-mes'),
    path('stats/victimas/por-hora/', views.VictimasPorHoraView.as_view(), name='stats-victimas-por-hora'),

]


# La forma como hice yo
# from django.urls import path
# from . import views

# urlpatterns = [
#     # Rutas para Siniestro
#     path('siniestros/', 
#          views.SiniestroViewSet.as_view({'get': 'list'}), 
#          name='siniestro-list'),
#     path('siniestros/<int:pk>/', 
#          views.SiniestroViewSet.as_view({'get': 'retrieve'}), 
#          name='siniestro-detail'),
         
#     # Rutas para Causa
#     path('causas/', 
#          views.CausaViewSet.as_view({'get': 'list'}), 
#          name='causa-list'),
#     path('causas/<int:pk>/', 
#          views.CausaViewSet.as_view({'get': 'retrieve'}), 
#          name='causa-detail'),

#     # Rutas para TipoSiniestro
#     path('tipos-siniestro/', 
#          views.TipoSiniestroViewSet.as_view({'get': 'list'}), 
#          name='tiposiniestro-list'),
#     path('tipos-siniestro/<int:pk>/', 
#          views.TipoSiniestroViewSet.as_view({'get': 'retrieve'}), 
#          name='tiposiniestro-detail'),
# ]