from django.contrib import admin
from .models import Colaborador, TipoItemAvaliacaoDesempenho, AvaliacaoDesempenho, ItemAvaliacaoDesempenho

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'cargo']
    search_fields = ['nome', 'cargo']
    ordering = ['nome']

@admin.register(TipoItemAvaliacaoDesempenho)
class TipoItemAvaliacaoDesempenhoAdmin(admin.ModelAdmin):
    list_display = ['id', 'dimensao', 'tipo_item_avaliacao_desempenho', 'descricao']
    list_filter = ['dimensao']
    search_fields = ['tipo_item_avaliacao_desempenho', 'descricao']
    ordering = ['dimensao', 'tipo_item_avaliacao_desempenho']

class ItemAvaliacaoDesempenhoInline(admin.TabularInline):
    model = ItemAvaliacaoDesempenho
    extra = 0
    fields = ['tipo_item_avaliacao_desempenho', 'nota', 'observacoes']
    readonly_fields = ['tipo_item_avaliacao_desempenho']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False
    
@admin.register(AvaliacaoDesempenho)
class AvaliacaoDesempenhoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'colaborador',
        'supervisor',
        'mes_competencia',
        'status_avaliacao',
        'nota',
    ]

    list_filter = ['status_avaliacao', 'mes_competencia']
    search_fields = ['colaborador__nome', 'supervisor__nome']
    ordering = ['-mes_competencia', 'colaborador__nome']
    readonly_fields = ['nota', 'status_avaliacao']
    inlines = [ItemAvaliacaoDesempenhoInline]

    fieldsets = (
        ('Informacoeses gerais', {
            'fields': ('colaborador', 'supervisor', 'mes_competencia'),
        }),
        ('Status e nota', {
            'fields': ('status_avaliacao', 'nota'),
        }),
        ('Observacoes', {
            'fields': ('sugestoes_supervisor', 'observacoes_avaliado'),
            'classes': ('collapse',),
        }),
    )

    actions = ['acao_iniciar', 'acao_dar_feedback', 'acao_concluir']

    @admin.action(description='Iniciar avaliacoes selecionadas')
    def acao_iniciar(self, request, queryset):
        for avaliacao in queryset.filter(status_avaliacao='Criada'):
            avaliacao.iniciar()
        self.message_user(request, 'Avaliacoes iniciadas com sucesso')

    @admin.action(description='Dar feedback nas avaliacoes selecionadas')
    def acao_dar_feedback(self, request, queryset):
        for avaliacao in queryset.filter(status_avaliacao='Em elaboracao'):
            avaliacao.dar_feedback()
        self.message_user(request, 'Feedback registrado com sucesso')

    @admin.action(description='Concluir avaliacoes selecionadas')
    def acao_concluir(self, request, queryset):
        for avaliacao in queryset.filter(status_avaliacao='Em avaliacao'):
            avaliacao.concluir()
        self.message_user(request, 'Avaliações concluídas com sucesso.')

@admin.register(ItemAvaliacaoDesempenho)
class ItemAvaliacaoDesempenhoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'avaliacao_desempenho',
        'tipo_item_avaliacao_desempenho',
        'nota',
    ]
    list_filter = ['tipo_item_avaliacao_desempenho__dimensao']
    search_fields = [
        'avaliacao_desempenho__colaborador__nome',
        'tipo_item_avaliacao_desempenho__tipo_item_avaliacao_desempenho',
    ]
    ordering = ['avaliacao_desempenho', 'tipo_item_avaliacao_desempenho__dimensao']