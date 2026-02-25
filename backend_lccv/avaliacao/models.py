from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class StatusAvaliacao(models.TextChoices):
    CRIADA = 'Criada', 'Criada'
    EM_ELABORACAO = 'Em elaboracao', 'Em elaboracao'
    EM_AVALIACAO = 'Em avaliacao', 'Em alvaiacao'
    CONCLUIDA = 'Concluida', 'Concluida'

class DimensaoItemAvaliacao(models.TextChoices):
    COMPORTAMENTO = 'Comportamento', 'Comportamento'
    ENTREGAS = 'Entregas', 'Entregas'
    TRABALHO_EM_EQUIPE = 'Trabalho em equipe', 'Trabalho em equipe'

class Colaborador(models.Model):
    nome = models.CharField(max_length=255, verbose_name='Nome')
    cargo = models.CharField(max_length=255, verbose_name='Cargo')

    class Meta:
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'
        ordering = ['nome']
    
    def __str__(self):
        return f'{self.nome} | {self.cargo}'
    

class TipoItemAvaliacaoDesempenho(models.Model):
    dimensao = models.CharField(
        max_length=40,
        choices=DimensaoItemAvaliacao.choices,
        verbose_name='Dimensao',
    )
    tipo_item_avaliacao_desempenho = models.CharField(max_length=255,verbose_name='Tipo de item')
    descricao = models.TextField(verbose_name='Descricao')

    class Meta:
        verbose_name = 'Tipo de item de avaliacao'
        verbose_name_plural = 'Tipos de itens de avaliacoes'
        ordering = ['dimensao', 'tipo_item_avaliacao_desempenho']

    def __str__(self):
        return f'{self.dimensao} | {self.tipo_item_avaliacao_desempenho}'
    
class AvaliacaoDesempenho(models.Model):
    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.PROTECT,
        related_name='avaliacoes',
        verbose_name='Colaborador',
    )
    supervisor = models.ForeignKey(
        Colaborador,
        on_delete=models.PROTECT,
        related_name='avaliacoes_supervisonadas',
        verbose_name='Supervisor',
    )
    mes_competencia = models.DateField(verbose_name='Mes de competencia')
    status_avaliacao = models.CharField(
        max_length=30,
        choices=StatusAvaliacao.choices,
        default=StatusAvaliacao.CRIADA,
        verbose_name='Status',
    )
    sugestoes_supervisor = models.TextField(
        blank=True,
        null=True,
        verbose_name='Sugestoes do supervisor',
    )
    observacoes_avaliado = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observacoes do avaliado'
    )

    class Meta:
        verbose_name = 'Avaliacao de desempenho'
        verbose_name_plural = 'Avaliacao de desempenhos'
        ordering = ['-mes_competencia', 'colaborador__nome']
        constraints = [
            models.UniqueConstraint(
                fields=['colaborador', 'mes_competencia'],
                name='unique_colaborador_mes_competencia',
            )
        ]

    def __str__(self):
        return (
            f'Avaliacao de {self.colaborador.nome} no mes {self.mes_competencia.strftime("%m/%Y")}'
        )
    
    @property
    def nota(self):
        total_itens = TipoItemAvaliacaoDesempenho.objects.count()
        if total_itens == 0:
            return 0
        soma = sum(
            item.nota for item in self.itens.all() if item.nota is not None
        )
        return (soma / (total_itens * 5)) * 100
    
    def iniciar(self):
        self.status_avaliacao = StatusAvaliacao.EM_ELABORACAO
        self.save(update_fields=['status_avaliacao'])

    def dar_feedback(self):
        self.status_avaliacao = StatusAvaliacao.EM_AVALIACAO
        self.save(update_fields=['status_avaliacao'])

    def concluir(self):
        self.status_avaliacao = StatusAvaliacao.CONCLUIDA
        self.save(update_fields=['status_avaliacao'])

class ItemAvaliacaoDesempenho(models.Model):
    avaliacao_desempenho = models.ForeignKey(
        AvaliacaoDesempenho,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Avaliacao de desempenho',
    )
    tipo_item_avaliacao_desempenho = models.ForeignKey(
        TipoItemAvaliacaoDesempenho,
        on_delete=models.PROTECT,
        verbose_name='Tipo de item',
    )
    nota = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Nota',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    observacoes = models.TextField(
        null=True,
        blank=True,
        verbose_name='Observacoes'
    )

    class Meta:
        verbose_name = 'Item de avaliacao'
        verbose_name_plural = 'Itens de avaliacao'
        ordering = ['tipo_item_avaliacao_desempenho__dimensao']
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(nota__isnull=True)
                    | (models.Q(nota__gte=1) & models.Q(nota__lte=5))
                ),
                name='nota_item_entre_1_e_5'
            )
        ]

    def __str__(self):
        return (
            f'{self.tipo_item_avaliacao_desempenho} | Nota: {self.nota or "sem avaliacao"}'
        )