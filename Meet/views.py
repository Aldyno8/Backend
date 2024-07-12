from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from google.auth.transport import requests
from google.oauth2 import id_token
from django.conf import settings
from .models import *
from .serializers import *
from .utils import *
import spacy
        
# Charge le modèle pou le traitement des npl
nlp = spacy.load("./spacy_model")
# class qui va récupérer le informations de connexion de l'utilisateur
class UserAuth(APIView):
    def post(self, request):
        
        # a modifier pour q'il récupère les données de l'utilisateu et l'écris dans le fichier token.json
        token = request.data.get('token')
        email = request.data.get('email')
        # A ne pas oublier de modifier l'id de dans le settings

        if not token:
            print("token no recus ")
            return Response({"error": "le token n'est pas là"})
        else:
            tokenCreate()
            print(f"token recus avec succès: {token}")
            
                
            # Ecris le creds d'authorisation dans le fichier token.json ou le rafraichis  
            user, created = CredsUsers.objects.get_or_create(email=email, defaults={"creds":token})

            # refresh = RefreshToken.for_user(user)
            if created:
                return Response({"status": True})
            else:
                return Response({"status": False})
                               
# Class qui va gérer tout ce qui concerne les rendez vous   
class CreateMeetingView(APIView):
    def post(self, request, *args, **kwargs):
        
        # Traitement des donnés envoyée par l'user pour extraire les informations
        meeting_info = dataProcessing(request.data['requete'], nlp)
        event_duration = meeting_info['meeting_info']
        if not meeting_info['meeting_start']:
            start = randomDate("deadline", "event_priority","event_duration")
            meeting_details = createMeeting(
            meeting_info['meeting_title'], 
            meeting_info['meeting_description'], 
            start,
            start + event_duration,
            meeting_info['meeting_location']
        )
        else:
        # Création d'une réunion à partir des données qui ont été extrait de la requete User
            meeting_details = createMeeting(
            meeting_info['meeting_title'], 
            meeting_info['meeting_description'], 
            meeting_info['meeting_start'],
            meeting_info['meeting_end'],
            meeting_info['meeting_location']
        )
        
        # Vérifie si la réunion à bien été crée 
        if not meeting_details:
            return Response({"error": "Failed to create meeting"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Envoi du mail d'invitation 
        body = f"""Bonjour,
Je vous invite à une réunion en visioconférence pour {meeting_details['meeting_description']}.
Voici le lien pour rejoindre la réunion : {meeting_details["meeting_link"]}.
Merci de confirmer votre disponibilité.
Cordialement,
Bruel """
        
        Invitation = sendMail("bruel23.aps2a@gmail.com", 'Invitation à un meeting', body)
        if Invitation:
            print("mail envoyé")
        
        return Response({"message":"la réunion à bien été crée"}, status=status.HTTP_201_CREATED)

#class qui va gérer l'affichage de tout les évenements dans google agenda
class EventListView(APIView):
    def get(self, request):
        Event_list = getEventList()
        event_data = eventSerializers(Event_list)
        return Response(event_data.data)
    
# Class qui  va gérer les emails les récupérer et les affichés
class EmailGestionView(APIView):
    def get(self, request):
        email = getEmail(labelsId='IMPORTANT')
        list_message = detailsEmail(email)
        message = MessageSerializes(list_message, many=True)
        return Response(message.data)
   
  
# Class qui va gérer l'envoi des mails
class SendEmailView(APIView):
    def post(self, request):
        destinataire = request.data.get('destinataire')
        subject = request.data.get('subject')
        body = request.data.get('body')
        sendMail(destinataire, subject, body)
        return Response({})
        
# Class qui va gérer l'affichage des documents
class DocumentView(APIView):
    def get(self, request):
        messages = getEmail("IMPORTANT")
        getPj(messages)
        documents =  Documents.objects.all()   
        documents_data = DocumentSerializes(documents, many=True)
        return Response(documents_data.data)
                 