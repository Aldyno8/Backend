""" Fichier qui va gérer tout les fonctions nécessaire"""
import os.path, base64, datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from django.conf import settings
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.http import MediaInMemoryUpload
from .models import Documents

# Fonction qui va traiter la requete envoyer par l'utilisateur et extraire les données pour la création du meeting
def dataProcessing(requete, nlp):
    doc = nlp(requete)
        
    meeting_info = {
        "meeting_title": "",
        "meeting_description": "",
        "meeting_start": None ,
        "meeting_end": None
        }
        
    for ent in doc.ents:
        if ent.label_ == "EVENT":
            meeting_info['meeting_title'] = ent.text
        elif ent.label_ =='SUBJECT':
            meeting_info['meeting_description'] = ent.text
           
    return meeting_info
     
"""Verifie les tokens d'identification dans le fichier token.json si il est ivalide alors le raffraichir
si il n'éxiste pas alors permettre à l'utilisateur de se reconecté puis retourne une instance autorisé"""
def tokenCreate():
    SCOPES = ['https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/gmail.send', 
              'https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/drive.file']
    
    creds = None
    
    # Vérification des jetons d'accès
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # Si les jetons ne sont pas valides, permettre à l'utilisateur de se connecter.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Enregistrer les identifiants pour la prochaine exécution
        with open('token.json', 'w') as token:
            token.write(creds.to_json()) 
            
    return creds
    
# Fonction qui va crée une réunion en et retourne les détails de celle_ci dans un dictionnaire nommé meeting_details
def createMeeting(meeting_title, meeting_description, meeting_start='2024-07-03T10:00:00-07:00', meeting_end='2024-07-03T10:30:00-07:00', meeting_location="Online"):

    # Récupère les données token 
    creds = tokenCreate()

    try:
        # Initialiser le client API Google Calendar
        service = build('calendar', 'v3', credentials=creds)

        # Détails de l'événement à créer
        event = {
            'summary': meeting_title,
            'description': meeting_description,
            'start': {
                'dateTime': meeting_start,
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': meeting_end,
                'timeZone': 'America/Los_Angeles',
            },
            "location": meeting_location, 
            'conferenceData': {
                'createRequest': {
                    'requestId': 'sample123',
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            }
        }
        # Créer l'événement
        event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
        meeting_link = event["conferenceData"]["entryPoints"][0]["uri"]
        
    except Exception as error:
        # Gestion des erreurs de l'API
        print(f'Une erreur est survenue : {error}')
        return {'error': str(error)}

    meeting_details = {
        "meeting_title": meeting_title,
        "meeting_description": meeting_description,
        "meeting_link": meeting_link,
        "meeting_start": meeting_start,
        "meeting_end": meeting_end,
        "meeting_location":meeting_location
    }
    
    return meeting_details

# fonction qui va retourner la liste des évenements récupérer dans le google agenda
def getEventList():
    creds = tokenCreate()
    service = build('calendar', 'v3', credentials=creds)
    time_now = datetime.datetime.utcnow().isoformat() +'Z'
    
    # Récupère les evenements dans le calendar
    results = service.events().list(calendarId='primary', timeMin= time_now, max_results=100, singleEvents=True, orderBy='startime').execute()
    
    events = results.get('items', [])
    
    if not events:
        print('Aucun evenements trouvé')
    
    for event in events:
        title = event.get('summary', 'Pas de titre')
        description = event.get('description')
        location =  event.get('location', "Meeting online")
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        
        link = 'Pas de réunion google meet'
        # Récupère les informations dans ConferenceData
        if "conferenceData" in event and "entryPoints" in event['conferenceData']:
            for entry_points in event['conferenceData']['entryPoints']:
                if entry_points[entry_points] == "video":
                    link = entry_points['uri']
        
    list_event = {
        "name": title,
        "description":description,
        "link": link,
        "location":location,
        "start":start,
        "end": end
    }
    
    return list_event
   
# fonction qui va génerer une time automatique
def randomDate(deadline, event_priority, event_duration):
    # Exemple de contraintes de disponibilité (jours ouvrables et heures de travail)
    working_days = [0, 1, 2, 3, 4]  # Lundi à vendredi
    star_work = datetime.time(8, 0)  # 8:00 AM
    end_work = datetime.time(17, 0)  # 5:00 PM

    current_datetime = datetime.datetime.now()
    datetimes_possible = []
    for i in range(7):
        next_day = current_datetime + datetime.timedelta(days=i)
        if next_day.weekday() > 0:
            if next_day.weekday() in working_days:
                # Ajouter toutes les heures de travail de la journée
                for hour in range(star_work.hour, end_work.hour):
                    possible_datetime = end_work.replace(hour=hour, minute=0, second=0, microsecond=0)
                    date_possible = datetime.datetime(current_datetime.year, current_datetime.month, next_day.day, possible_datetime.hour)
                    datetimes_possible.append(date_possible)
                    
    best_datetime = None
    best_score = float('inf')

    for possible_datetime in datetimes_possible:
        if possible_datetime <= deadline and possible_datetime >=current_datetime:
            # Calcul du score basé sur l'urgence et la proximité de la date limite
            time_difference = (deadline - possible_datetime).total_seconds() / 3600  # Différence en heures 
            if event_priority == 'very urgent':
                score = time_difference * 10  # Score élevé pour très urgent
            elif event_priority == 'urgent':
                score = time_difference * 5  # Score moyen pour urgent
            else:
                score = time_difference  # Score faible pour moins urgent

            # Ajustement du score en fonction de la durée estimée
            score *= event_duration

            if score < best_score:
                best_datetime = possible_datetime
                best_score = score

    return best_datetime        
    
# Fonction qui envoye les mails d'invitations à chaque participants pour le meeting
def sendMail( destinataire, subject, body, from_email='me'):
    
    creds = tokenCreate()
    try: 
        service = build('gmail', 'v1', credentials=creds)
        
        # Création du message a envoyer
        msg = MIMEText(body)
        msg['to'] = destinataire
        msg['From'] = from_email
        msg['subject'] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        message = service.users().messages().send(userId='me', body={'raw': raw}).execute()
        return message
    
    except Exception as error:
    # Gestion des erreurs de l'API
        print(f'Une erreur est survenue lors de l\'envoie : {error}')
        return {'error': str(error)}
       
# Fonction qui va uploader les fichiers dans drive afin de récup les liens de lecture
def uploadToDrive(service, file_data, filename):
    file_metadata = {'name': filename}
    media = MediaInMemoryUpload(file_data)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')

    permission = {
        'type': 'anyone',
        'role': 'reader',
    }
    service.permissions().create(fileId=file_id, body=permission).execute()
    print(' fichier uploader')

    link = f"https://drive.google.com/file/d/{file_id}/view"
    return link      
 
# Fonction qui va récupérer les emails importants dans la boite de réception et renvoie les informations concernant
def getEmail(labelsId):
    creds = tokenCreate()
    service = build('gmail', 'v1', credentials=creds)
    
    #Récupère les messages marqués comme important
    results = service.users().messages().list(userId='me', labelIds=labelsId).execute()
    messages = results.get('messages', [])
    
    return messages
    
# Fonction qui récupère le détails des évenements et les retournes
def detailsEmail(messages):
    creds = tokenCreate()
    service = build('gmail', 'v1', credentials=creds)
      
# Vérifie l'éxistence de message important
    if not messages:
        print(f"Aucun message important trouvé")
    
    else:
        print(f"{len(messages)} messages touvé")
        
        # Liste qui va contenit des dictionnaires contenant pour chacun des messages leurs détails
        list_details = []
                
        # Boucle qui va parcourir les messages et en extraire leurs information
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            identifiant = message['id']
            headers = msg['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
            sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
            sender_info = sender.split("<")
            if len(sender_info) == 2:
                print(sender_info)
                sender_name = sender_info[0]
                sender_email = sender_info[1]
            else:
                print(sender_info)
                sender_email = sender_info[0]
                                
            Date = next((header['value'] for header in headers if header['name']=='Date'), None)
            snippets = msg.get('snippet')
            
            # Dictionnaires des détails
            details = {
                "id":identifiant,
                "subject": subject,
                "sender": sender_name,
                "sender_mail":sender_email,
                'snippets': snippets,
                'Date': Date,
            }
            
            list_details.append(details)
        
        return list_details
    
# Fonction qui va récupérer le contenu d'un email et les retournes
def mailContent(id_message):
        creds = tokenCreate()
        service = build('gmail', 'v1', credentials=creds)
            
        # récupération des mails
        msg = service.users().messages().get(userId='me', id= id_message).execute()
        identifiant = id_message
        headers = msg['payload']['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
        Date = next((header['value'] for header in headers if header['name']=='Date'), None)
        body = None
        parts = msg['payload'].get('parts')
        
        if parts:
                for part in parts:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        body = part['body']['data']
                        body = base64.urlsafe_b64decode(body).decode('utf-8')
        else:
                body = msg['payload']['body']['data']
                body = base64.urlsafe_b64decode(body).decode('utf-8')
                        
        content = {
            "id": identifiant,
            "body": body,
            "subject":subject,
            "sender":sender,
            "Date":Date
            }
        return content
        
#  Fonction qui va récupérer pj pour les uploader dans drive avant d'insérer son lien dans la base de données 
def getPj(messages):
    creds = tokenCreate()
    service = build('gmail', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    for message in messages:
        headers = msg['payload']['headers']
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        Date = next((header['value'] for header in headers if header['name']=='Date'), None)
        parts = msg['payload'].get('parts')
        attachements = []
        if parts:
            for part in parts:
                if 'filename' in part and part['filename']:
                    if 'data' in part['body']:
                        attachement_data = part['body']['data']
                    else:
                        att_id = part['body']['attachmentId']
                        attachement = service.users().messages().attachments().get(userId='me', messageId=message['id'], id=att_id).execute()
                        attachement_data = attachement['data']
                        
                    file_data = base64.urlsafe_b64decode(attachement_data.encode('UTF-8'))
                    if file_data not in Documents.objects.all():
                        print("objects non existant dans la base de donnés")
                        file_categories = part['filename'].split(".")
                        file_categorie = file_categories[1]
                        file_name = file_categories[0]
                        if file_categorie == 'docx' or file_categorie == 'pdf':
                            link = uploadToDrive(drive_service, file_data, part['filename'])
                            print(f"fichier uploader avec succès")
                            attachements.append(link)
                            Documents.objects.create(name=file_name, categories=file_categorie, genre=file_categories[0], Date=Date, link = link)
                            