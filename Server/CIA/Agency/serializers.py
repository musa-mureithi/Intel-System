from rest_framework import serializers
from .models import Person, Operation, Report, OperationAssignment

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'

class OperationSerializer(serializers.ModelSerializer):
    Assigned_Personnel = serializers.PrimaryKeyRelatedField(
        queryset=Person.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Operation
        fields = '__all__'

class OperationAssignmentSerializers(serializers.ModelSerializer):
    class Meta:
        model= OperationAssignment
        field = "__all__"

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
        
                