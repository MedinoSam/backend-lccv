from rest_framework import serializers
from .models import Colaborador, TipoItemAvaliacaoDesempenho, AvaliacaoDesempenho, ItemAvaliacaoDesempenho, StatusAvaliacao


class ColaboradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colaborador
        fields = ['id', 'nome', 'cargo']

class TipoItemAvaliacaoDesempenhoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoItemAvaliacaoDesempenho
        fields = ['id', 'dimensao', 'tipo_item_avaliacao_desempenho', 'descricao']

class ItemAvaliacaoDesempenhoSerializer(serializers.ModelSerializer):
    tipo_item_avaliacao_desempenho_detail = TipoItemAvaliacaoDesempenhoSerializer(
        source='tipo_item_avaliacao_desempenho',
        read_only=True,
    )

    class Meta:
        model = ItemAvaliacaoDesempenho
        fields = ['id', 'tipo_item_avaliacao_desempenho', 'tipo_item_avaliacao_desempenho_detail', 'nota', 'observacoes']
    
    def validate_nota(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError('A nota deve ser entre 1 e 5')
        return value
    
#Serializer para listagem

class AvaliacaoDesempenhoListSerializer(serializers.ModelSerializer):
    colaborador_nome = serializers.CharField(source='colaborador.nome', read_only=True)
    supervisor_nome = serializers.CharField(source='supervisor.nome', read_only=True)
    status_avaliacao_display = serializers.CharField(
        source='get_status_avaliacao_display',
        read_only=True,
    )

    class Meta:
        model = AvaliacaoDesempenho
        fields = [
            'id',
            'colaborador',
            'colaborador_nome',
            'supervisor',
            'supervisor_nome',
            'mes_competencia',
            'status_avaliacao',
            'status_avaliacao_display',
            'nota',
        ]

class AvaliacaoDesempenhoDetailSerializer(serializers.ModelSerializer):
    colaborador_detail = ColaboradorSerializer(source='colaborador', read_only=True)
    supervisor_detail = ColaboradorSerializer(source='supervisor', read_only=True)
    itens = ItemAvaliacaoDesempenhoSerializer(many=True, read_only=True)
    status_avaliacao_display = serializers.CharField(
        source='get_status_avaliacao_display',
        read_only=True,
    )

    class Meta:
        model = AvaliacaoDesempenho
        fields = [
            'id',
            'colaborador',
            'colaborador_detail',
            'supervisor',
            'supervisor_detail',
            'mes_competencia',
            'status_avaliacao',
            'status_avaliacao_display',
            'nota',
            'sugestoes_supervisor',
            'observacoes_avaliado',
            'itens',
        ]
        read_only_fields = ['status_avaliacao', 'nota']
    
    def validate(self, data):
        colaborador = data.get('colaborador')
        supervisor = data.get('supervisor')
        if colaborador and supervisor and colaborador == supervisor:
            raise serializers.ValidationError(
                'Colaborador e Supervisor devem ser pessoas difenrtes'
            )
        return data
    
    def create(self, validated_data):
        avaliacao = AvaliacaoDesempenho.objects.create(**validated_data)
        tipos = TipoItemAvaliacaoDesempenho.objects.all()
        for tipo in tipos:
            ItemAvaliacaoDesempenho.objects.create(
                avaliacao_desempenho=avaliacao,
                tipo_item_avaliacao_desempenho=tipo,
            )
        return avaliacao
    
class AvaliacaoDesempenhoEditarSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvaliacaoDesempenho
        fields = ['sugestoes_supervisor', 'observacoes_avaliado']

    def validate(self, data):
        avaliacao = self.instance
        status_editaveis = [
            StatusAvaliacao.EM_ELABORACAO,
            StatusAvaliacao.EM_AVALIACAO,
        ]
        if avaliacao and avaliacao.status_avaliacao not in status_editaveis:
            raise serializers.ValidationError(
                'Nao eh possivel editar essa avalicacoa no momento'
            )
        return data