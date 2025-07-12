from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.utils.crypto import get_random_string
from .models import AnsaaUser
from django.contrib.auth.models import User
from .task import password_reset,  registration_notice
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _



class AnsaaUserAdmin(BaseUserAdmin):
    model = AnsaaUser
    list_display = ('email', 'fullname', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {
            'fields': ('fullname', 'phone_number', 'gender', 'picture')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'start_date'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'fullname', 'gender', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    search_fields = ('email', 'fullname')
    ordering = ('-start_date',)
    filter_horizontal = ('groups', 'user_permissions',)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        user = self.get_object(request, object_id)

        if user:
            extra_context = extra_context or {}
            extra_context['show_send_password_button'] = True
            extra_context['send_password_url'] = reverse('admin:admin_send_password', args=[user.id])

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-password/<int:user_id>/', self.admin_site.admin_view(self.send_raw_password), name='admin_send_password'),
        ]
        return custom_urls + urls

    def send_raw_password(self, request, user_id):
        user = AnsaaUser.objects.get(pk=user_id)
        
        if user:
            # When change is False, it's a new user
            password = get_random_string(length=8)
            user.set_password(password)
            user.save()

            # Send the registration email with the password
            email = user.email
            fullname = user.fullname
            password = password
            password_reset(email,password,fullname)
        else:
            pass

        # Ensure this function is defined correctly

        self.message_user(request, f"New password sent to {user.email}.")
        return redirect(reverse('admin:authentication_ansaauser_change', args=[user_id]))


    def save_model(self, request, obj, form, change):
        if not change:  # When change is False, it's a new user
            password = BaseUserManager().make_random_password()
            obj.set_password(password)
            obj.save()

            # Send the registration email with the password
            registration_notice(obj.email, password, obj.fullname)
        else:
            super().save_model(request, obj, form, change)

# Register your admin class
admin.site.register(AnsaaUser, AnsaaUserAdmin)
