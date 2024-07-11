from .models import *
from rest_framework import serializers

# Serializers des Contact pour l'envoye des invitations  
class ContactSerializes(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'email']
        
# Serializers des Données des messages
class MessageSerializes(serializers.Serializer):
    id = serializers.CharField(allow_blank=True, default='')
    subject = serializers.CharField(allow_blank=True, default='')
    sender = serializers.CharField(allow_blank=True, default='')
    snippets = serializers.CharField(allow_blank=True, default='')
    Date = serializers.CharField()

# Serializers du contenu des messages
class MailContentSerializes(serializers.Serializer):
    id = serializers.IntegerField()
    body = serializers.CharField() 
    subject = serializers.CharField(allow_blank=True, default='')
    sender = serializers.CharField(allow_blank=True, default='')
    snippets = serializers.CharField(allow_blank=True, default='')
    Date = serializers.CharField()
    
# serializers des creds    
class CredsSerializers(serializers.ModelSerializer):
    class Meta:
        model = CredsUsers
        fields = ['email', 'creds']
        
# Serializers des documents
class DocumentSerializes(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields = ['name', 'categories', 'genre', 'Date', 'link']
        
# serializers des informations des évents
class eventSerializers(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    link = serializers.CharField()
    location = serializers.CharField()
    start = serializers.CharField()
    end = serializers.CharField()

