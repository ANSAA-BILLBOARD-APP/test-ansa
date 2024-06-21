from django.contrib import admin
from .models import Target

class TargetAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'year', 'target', 'target_count')
    list_filter = ('month', 'year')
    search_fields = ('user__fullname',)
    readonly_fields = ('target_count', 'date')

admin.site.register(Target, TargetAdmin)