from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import (Colaborador,TipoItemAvaliacaoDesempenho,AvaliacaoDesempenho,ItemAvaliacaoDesempenho,StatusAvaliacao)

from .serializers import (
    ColaboradorSerializer,
    TipoItemAvaliacaoDesempenhoSerializer,
    AvaliacaoDesempenhoListSerializer,
    AvaliacaoDesempenhoDetailSerializer,
    AvaliacaoDesempenhoEditarSerializer,
    ItemAvaliacaoDesempenhoSerializer,
)

@extend_schema_view(
    list=extend_schema(summary='Listar colaboradores'),
    retrieve=extend_schema(summary='Consultar colaborador'),
    create=extend_schema(summary='Cadastrar colaborador'),
    update=extend_schema(summary='Editar colaborador'),
    partial_update=extend_schema(summary='Editar colaborador parcialmente'),
)
class ColaboradorViewSet(viewsets.ModelViewSet):
    queryset = Colaborador.objects.all()
    serializer_class = ColaboradorSerializer
    http_method_names = ['get', 'post', 'patch', 'put']

@extend_schema_view(
    list=extend_schema(summary='Listar tipos de itens de avaliação'),
    retrieve=extend_schema(summary='Consultar tipo de item de avaliação'),
    create=extend_schema(summary='Cadastrar tipo de item de avaliação'),
    update=extend_schema(summary='Editar tipo de item de avaliação'),
    partial_update=extend_schema(summary='Editar tipo de item de avaliação parcialmente'),
)
class TipoItemAvaliacaoDesempenhoViewSet(viewsets.ModelViewSet):

    """gerenciar  tipos de itens de avaliação"""

    queryset = TipoItemAvaliacaoDesempenho.objects.all()
    serializer_class = TipoItemAvaliacaoDesempenhoSerializer
    http_method_names = ['get', 'post', 'patch', 'put']

@extend_schema_view(
    list=extend_schema(summary='Listar avaliações de desempenho'),
    retrieve=extend_schema(summary='Consultar avaliação de desempenho'),
    create=extend_schema(summary='Cadastrar avaliação de desempenho'),
    update=extend_schema(summary='Editar avaliação de desempenho'),
    partial_update=extend_schema(summary='Editar avaliação de desempenho parcialmente'),
)
class AvaliacaoDesempenhoViewSet(viewsets.ModelViewSet):
    queryset = AvaliacaoDesempenho.objects.select_related(
        'colaborador', 'supervisor'
        ).prefetch_related('itens__tipo_item_avaliacao_desempenho')
    http_method_names = ['get', 'post', 'patch', 'put']

    def get_serializer_class(self):
        if self.action == 'list':
            return AvaliacaoDesempenhoListSerializer
        if self.action in ['update', 'partial_update']:
            return AvaliacaoDesempenhoEditarSerializer
        return AvaliacaoDesempenhoDetailSerializer
    
    @extend_schema(
        summary='Iniciar avaliação',
        description='Transição de estado de criada para Em elaboração',
        responses={200: AvaliacaoDesempenhoDetailSerializer},
    )
    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        avaliacao = self.get_object()
        if avaliacao.status_avaliacao != StatusAvaliacao.CRIADA:
            return response(
                {'detail': 'A avaliacao deve ter o status de "criada" para poder ser iniciada'},
                status= status.HTTP_400_BAD_REQUEST,
            )
        avaliacao.iniciar()
        serializer = AvaliacaoDesempenhoDetailSerializer(avaliacao)
        return response(serializer.data)
    
    @extend_schema(
        summary='Dar feedback',
        description='Transição de estado de  "Em elaboração"  para  "Em avaliação"',
        responses={200: AvaliacaoDesempenhoDetailSerializer},
    )
    @action(detail=True, methods=['post'], url_path='dar-feedback')
    def dar_feedback(self, request, pk=None):
        avaliacao = self.get_object()
        if avaliacao.status_avaliacao != StatusAvaliacao.EM_ELABORACAO:
            return Response(
                {'detail': 'A avaliacao precisa estar "Em elaboração" para receber feedback'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        avaliacao.dar_feedback()
        serializer = AvaliacaoDesempenhoDetailSerializer(avaliacao)
        return Response(serializer.data)
    
    @extend_schema(
        summary='Concluir avaliacao',
        description='Transicao de estado de  "Em avaliação" para  "Concluída"',
        responses={200: AvaliacaoDesempenhoDetailSerializer},
    )
    @action(detail=True, methods=['post'])
    def concluir(self, request, pk=None):
        avaliacao = self.get_object()
        if avaliacao.status_avaliacao != StatusAvaliacao.EM_AVALIACAO:
            return Response(
                {'detail': 'A avaliacao precisa estar "Em avaliação" para ser concluida'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        avaliacao.concluir()
        serializer = AvaliacaoDesempenhoDetailSerializer(avaliacao)
        return Response(serializer.data)

@extend_schema_view(
    list=extend_schema(summary='Listar itens de uma avaliacao'),
    retrieve=extend_schema(summary='Consultar item de avaliacao'),
    update=extend_schema(summary='Editar item de avaliacao'),
    partial_update=extend_schema(summary='Editar item de uma avaliacao parcialmente'),
)
class ItemAvaliacaoDesempenhoViewSet(viewsets.GenericViewSet,
                                     viewsets.mixins.ListModelMixin,
                                     viewsets.mixins.RetrieveModelMixin,
                                     viewsets.mixins.UpdateModelMixin):
    """
    ViewSet para gerenciamento de itens de avaliação
    Itens são criados automaticamente ao cadastrar a avaliação
    Tem listagem, consulta e edição
    """
    serializer_class = ItemAvaliacaoDesempenhoSerializer
    http_method_names = ['get', 'patch', 'put']

    def get_queryset(self):
        return ItemAvaliacaoDesempenho.objects.filter(
            avaliacao_desempenho_id=self.kwargs['avaliacao_pk']
        ).select_related('tipo_item_avaliacao_desempenho')

    def validate_status_editavel(self, avaliacao):
        status_editaveis = [StatusAvaliacao.EM_ELABORACAO, StatusAvaliacao.EM_AVALIACAO]
        if avaliacao.status_avaliacao not in status_editaveis:
            return Response(
                {'detail': 'Os itens não podem ser editados no status atual da avaliacao'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    def update(self, request, *args, **kwargs):
        item = self.get_object()
        erro = self.validate_status_editavel(item.avaliacao_desempenho)
        if erro:
            return erro
        response = super().update(request, *args, **kwargs)
        return response