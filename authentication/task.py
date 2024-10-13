import threading, random, string
from django.utils import timezone
from django.conf import settings
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


# def generate_otp():
#         # Generate a 4-digit OTP
#         otp = ''.join(random.choices(string.digits, k=4))
#         return otp

# def send_otp_email(email, otp_code):
#     # Send OTP email
#     email_subject = '[Ansaa OTP] Verification Code'
#     template = loader.get_template('mail_template.txt')
#     parameters = {'otp': otp_code}
#     email_content = template.render(parameters)

#     email_message = EmailMultiAlternatives(
#         email_subject,
#         email_content,
#         settings.EMAIL_HOST_USER,
#         [email]
#     )
#     email_message.content_subtype = 'html'
#     EmailThread(email_message).start()


def registration_notice(email, password, fullname):
    # Send account creation mail
    email_subject = 'You have a new Ansa account'
    template = loader.get_template('registration.txt')
    parameters = {'password':password, "name": fullname}
    email_content = template.render(parameters)

    email_message = EmailMultiAlternatives(
        email_subject,
        email_content,
        settings.EMAIL_HOST_USER,
        [email]
    )
    email_message.content_subtype = 'html'
    EmailThread(email_message).start()

def password_reset(email, password, fullname):
    # Send password reset mail
    email_subject = 'Password reset notification'
    template = loader.get_template('change_password.txt')
    parameters = {'password':password, "name": fullname}
    email_content = template.render(parameters)

    email_message = EmailMultiAlternatives(
        email_subject,
        email_content,
        settings.EMAIL_HOST_USER,
        [email]
    )
    email_message.content_subtype = 'html'
    EmailThread(email_message).start()