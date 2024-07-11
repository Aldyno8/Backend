from django.contrib import admin
from django.contrib.auth.models import User
from .models import *

# Register your models here.
class ContactAdmin(admin.ModelAdmin):
    model = Contact
    list_display = ('name', 'email')
    
class DocumentAdmin(admin.ModelAdmin):
    model = Documents
    list_display = ('name', 'categories', 'genre', 'Date', 'link')
    
class CredsAdmin(admin.ModelAdmin):
    model = CredsUsers
    list_display = ('email', 'creds') 
    
admin.site.register(Contact, ContactAdmin)
admin.site.register(CredsUsers, CredsAdmin)
admin.site.register(Documents, DocumentAdmin)
admin.site.unregister(User)
