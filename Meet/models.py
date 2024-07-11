from django.db import models
    
# models qui va gérer les contacts où envoyer les emails
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    
    def __str__(self):
        return self.name
    
# models qui va contenir les fichiers
class Documents(models.Model):
    name = models.CharField(max_length=100)
    categories = models.CharField(max_length=20)
    genre = models.CharField(max_length=10) 
    Date = models.CharField(max_length=75)
    link = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name
    
# models qui va gérer les creds des utilisateurs
class CredsUsers(models.Model):
    email = models.EmailField()
    creds = models.CharField(max_length=200)
    
    def __str__(self):
        return self.email
 
    