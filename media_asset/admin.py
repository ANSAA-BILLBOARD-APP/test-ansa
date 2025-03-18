from django.contrib import admin
from . models import Billboards, Zones, Dimensions, AmountPerSqFt
from django.forms import TextInput, Textarea, CharField
from django import forms
from django.db import models



class BillboardsAdmin(admin.ModelAdmin):
    search_fields = ('user','company_name','asset_lga','dimension', 'actual_size', 'unique_id', 'asin')
    list_filter = ('company_name', 'status','vacancy','business_type')
    ordering = ('-vacancy',)
    list_display = ('user','unique_id','company_name','price')

class ZonesAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    ordering = ('name',)

class DimensionsAdmin(admin.ModelAdmin):
    list_display = (f'id','name', 'category','min_width', 'max_width', 'zone','price')
    ordering = ('name',)
    
admin.site.register(Billboards, BillboardsAdmin)
admin.site.register(Zones, ZonesAdmin)
admin.site.register(Dimensions, DimensionsAdmin)
admin.site.register(AmountPerSqFt)
