from rest_framework import serializers
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    imagen = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = '__all__'

    def get_imagen(self, obj):
        request = self.context.get('request')
        if obj.imagen:
            if hasattr(obj.imagen, 'url'):
                url = obj.imagen.url
            else:
                url = str(obj.imagen)
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None
