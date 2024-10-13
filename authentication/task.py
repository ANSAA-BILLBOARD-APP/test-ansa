import threading, random, string
from django.utils import timezone
from django.conf import settings
from . models import OTP
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.template import loader
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string



class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        self.email_message.reply_to = ['noreply@ansaa.com']
        self.email_message.from_email = 'Ansaa <noreply@example.com>'
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()




    


