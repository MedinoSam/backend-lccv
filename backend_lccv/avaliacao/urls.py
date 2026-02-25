from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
from django.urls import path, include

from .views import (
    ColaboradorViewSet,
    TipoItemAvaliacaoDesempenhoViewSet,
    AvaliacaoDesempenhoViewSet,
    ItemAvaliacaoDesempenhoViewSet,
)

router = DefaultRouter()

router.register('colaboradores', ColaboradorViewSet, basename='colaborador')

router.register('tipos-item-avaliacao', TipoItemAvaliacaoDesempenhoViewSet, basename='tipo-item-avaliacao')

router.register('avaliacoes', AvaliacaoDesempenhoViewSet, basename='avaliacao')

#rota aninhada
avaliacoes_router = nested_routers.NestedDefaultRouter(router, 'avaliacoes', lookup='avaliacao')
avaliacoes_router.register('itens', ItemAvaliacaoDesempenhoViewSet, basename='avaliacao-itens')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(avaliacoes_router.urls)),
]