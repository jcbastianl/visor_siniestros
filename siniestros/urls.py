from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiniestroViewSet, VictimaViewSet, CausaViewSet, TipoSiniestroViewSet

# Router único - automáticamente genera todas las URLs
router = DefaultRouter()
router.register(r'siniestros', SiniestroViewSet, basename='siniestro')
router.register(r'victimas', VictimaViewSet, basename='victima')
router.register(r'causas', CausaViewSet, basename='causa')
router.register(r'tipos-siniestro', TipoSiniestroViewSet, basename='tipo-siniestro')




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