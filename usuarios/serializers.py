from rest_framework import serializers
from .models import Producto, MaestroPedido, DetallePedido
import base64
import re

class ProductoSerializer(serializers.ModelSerializer):
    imagen = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Producto
        fields = '__all__'

    def validate_imagen(self, value):
        if value in (None, ""):  # Permitir vacío
            return value
        # Validar prefijo
        if not (value.startswith("data:image/png;base64,") or value.startswith("data:image/jpeg;base64,") or value.startswith("data:image/jpg;base64,")):
            raise serializers.ValidationError("La imagen debe estar en formato base64 PNG o JPG.")
        # Validar base64 con corrección de padding
        try:
            base64_data = value.split(",", 1)[1]
            # Corregir padding si es necesario
            missing_padding = len(base64_data) % 4
            if missing_padding:
                base64_data += '=' * (4 - missing_padding)
            base64.b64decode(base64_data, validate=True)
        except Exception:
            raise serializers.ValidationError("La imagen no es una cadena base64 válida.")
        return value

class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'precio']

class MaestroPedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True)
    class Meta:
        model = MaestroPedido
        fields = ['id', 'fecha_registro', 'codigo_cliente', 'nombre_cliente', 'total', 'numero_celular', 'detalles']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        maestro = MaestroPedido.objects.create(**validated_data)
        for detalle_data in detalles_data:
            DetallePedido.objects.create(maestro=maestro, **detalle_data)
        return maestro
