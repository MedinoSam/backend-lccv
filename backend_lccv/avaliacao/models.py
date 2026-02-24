from django.db import models

# Create your models here.
class StatusAvaliacao(models.TextChoices):
    CRIADA = 'Criada', 'Criada'
    EM_ELABORACAO = 'Em elaboracao', 'Em elaboracao'
    EM_AVALIACAO = 'Em avaliacao', 'Em alvaiacao'
    CONCLUIDA = 'Concluida', 'Concluida'

class DimensaoItemAvaliacao(models.TextChoices):
    COMPORTAMENTO = 'Comportamento', 'Comportamento'
    ENTREGAS = 'Entregas', 'Entregas'
    TRABALHO_EM_EQUIPE = 'Trabalho em equipe', 'Trabalho em equipe'