from rest_framework import serializers
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    imagen = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Producto
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        imagen_field = instance.imagen
        if imagen_field:
            # Si es un path, construye la URL absoluta
            if hasattr(imagen_field, 'url'):
                url = imagen_field.url
            else:
                url = str(imagen_field)
            if request is not None:
                representation['imagen'] = request.build_absolute_uri(url)
            else:
                representation['imagen'] = url
        else:
            representation['imagen'] = None
        return representation
