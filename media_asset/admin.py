from django.contrib import admin
from . models import Billboards, Zones, UserZone, Dimensions
from django.forms import TextInput, Textarea, CharField
from django import forms
from django.db import models



class BillboardsAdmin(admin.ModelAdmin):
    search_fields = ('user','company','city','dimension', 'actual_dimension', 'asset_name')
    list_filter = ('company', 'status','vacancy','city')
    ordering = ('-vacancy',)
    list_display = ('user','asset_name','company','price')

class ZonesAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    ordering = ('name',)

class DimensionsAdmin(admin.ModelAdmin):
    list_display = (f'id','name', 'category','min_width', 'max_width', 'zone','price')
    ordering = ('name',)
    
admin.site.register(Billboards, BillboardsAdmin)
admin.site.register(Zones, ZonesAdmin)
admin.site.register(UserZone)
admin.site.register(Dimensions, DimensionsAdmin)
