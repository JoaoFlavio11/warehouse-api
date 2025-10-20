from rest_framework import serializers

class WarehouseSerializer(serializers.Serializer):
  uid = serializers.CharField(read_only=True)
  name = serializers.CharField(max_length=200)
  address = serializers.CharField(required=False, allow_blank=True)
  total_capacity = serializers.FloatField(default=0.0)
  created_at = serializers.DateTimeField(read_only=True)

class ZoneSerializer(serializers.Serializer):
  uid = serializers.CharField(read_only=True)
  name = serializers.CharField(max_length=100)
  zone_type = serializers.ChoiceField(choices=['receiving', 'storage', 'picking', 'shipping'])
  
class ProductSerializer(serializers.Serializer):
  uid = serializers.CharField(read_only=True)
  sku = serializers.CharField(max_length=50)
  name = serializers.CharField(max_length=200)
  quantity = serializers.IntegerField(default=0)
  unit = serializers.CharField(max_length=10, default='UN')
  location_code = serializers.CharField(required=False, allow_blank=True)
  
class BinSerializer(serializers.Serializer):
  uid = serializers.CharField(read_only=True)
  code = serializers.CharField(max_length=50)
  capacity = serializers.FloatField(default=100.0)
  occupied = serializers.FloatField(default=0.0)
  available = serializers.SerializerMethodField()
    
  def get_available(self, obj):
    return obj.capacity - obj.occupied