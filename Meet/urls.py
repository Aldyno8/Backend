from django.urls import path
from .views import *

urlpatterns = [
    path('new/', CreateMeetingView.as_view(), name="create_meet"),
    path('Email/', EmailGestionView.as_view(), name='Email'),
    path('EmailContent/', EmailContentView.as_view(), name='content'),
    path('Documents/', DocumentView.as_view(), name='Documents'),
    path('SendEmail/', SendEmailView.as_view(), name= 'SendEmail'),
    path('Auth/', UserAuth.as_view(), name="auth"),
    path('EventList/', EventListView.as_view(), name='Event_list')
]
