from django.db import models
from authentication.models import AnsaaUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class Zones(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
        verbose_name = _('Sub zone')
        verbose_name_plural = _('Sub zones')

    def __str__(self):
        return self.name

class UserZone(models.Model):
    user = models.ForeignKey(AnsaaUser, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zones, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('User Zone')
        verbose_name_plural = _('User Zones')
        unique_together = ('user', 'zone')

    def __str__(self):
        return f"{self.user.fullname}'s Zone: {self.zone.name}"   


class Billboards(models.Model):

    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    
    STATUS_CHOICES = {
        STATUS_PENDING: _('Pending'),
        STATUS_COMPLETED: _('Completed'),
    }

    VACANCY_VACANT = 'vacant'
    VACANCY_OCCUPIED = 'occupied'

    VACANCY_CHOICES = {
        VACANCY_VACANT: _('Vacant'),
        VACANCY_OCCUPIED: _('Occupied'),
    }

    ELECTRONIC = 'electronic'
    STATIC = 'static'

    TYPE_CHOICES = {
        ELECTRONIC: _('Electronic'),
        STATIC: _('Static')
    }


    # Define constants for categories
    FREE_STANDING_SIGNS = 'free_standing_signs'
    PROJECTING_SIGNS = 'projecting_signs'
    WALL_SIGNS = 'wall_signs'
    BILLBOARD_DESIGNATION = 'billboard_designation'
    
    # Optional: Define a dictionary for lookup by key if needed
    CATEGORY_CHOICES = {
        FREE_STANDING_SIGNS: _('Free standing signs'),
        PROJECTING_SIGNS: _('Projecting signs'),
        WALL_SIGNS: _('Wall signs'),
        BILLBOARD_DESIGNATION: _('Billboard Designation')

    }

    ZONE_NORMAL = 'normal_zone'
    ZONE_RESTRICTED = 'restricted_zone'

    ZONE_CHOICES = {
        ZONE_NORMAL: _('Normal zone'),
        ZONE_RESTRICTED: _('Restricted zone')
    }


    PENDING = 'pending'
    PAID = 'paid'
    NOT_PAID = 'not_paid'
    PAYMENT_CHOICES = {
        PENDING: _('Pending'),
        PAID: _('Paid'),
        NOT_PAID: _('Not_paid'),
    }


    asset_name = models.CharField(max_length=10, editable=False)
    asset_type = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True)
    zone = models.CharField(max_length=50, choices=ZONE_CHOICES, blank=True)
    sub_zone = models.ForeignKey(Zones, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    vacancy = models.CharField(max_length=20, choices=VACANCY_CHOICES, default='vacant', blank=True)

    dimension = models.CharField(max_length=50, blank=True)
    actual_dimension = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES, default=PENDING
    )
    payment_date = models.DateTimeField(blank=True, null=True)
    main_image = models.URLField(max_length=200, blank=True, null=True)
    image_1 = models.URLField(max_length=200, blank=True, null=True)
    image_2 = models.URLField(max_length=200, blank=True, null=True)
    image_3 = models.URLField(max_length=200, blank=True, null=True)
    user = models.ForeignKey(AnsaaUser, on_delete=models.CASCADE)

    address = models.CharField(max_length=250, blank=True)
    city = models.CharField(max_length=150, blank=True)
    state = models.CharField(max_length=20, default="Anambra", editable=False)
    country = models.CharField(max_length=20, default="Nigeria", editable=False)

    company = models.CharField(max_length=150, blank=True)
    phone_number = PhoneNumberField(blank=True)

    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.asset_name:  # Generate asset_name ID only if not already set
            asset_name_prefix = 'BOARD '
            asset_name_suffix = uuid.uuid4().hex[:3]
            self.asset_name = f'{asset_name_prefix}{asset_name_suffix}'.upper()


        # Generate QR code
        qr_data = f'Asset Name: {self.asset_name}\n' \
                  f'Category: {self.category}\n' \
                  f'Zone: {self.zone}\n' \
                  f'Company: {self.company}\n' \
                  f'Price: {self.price}\n' \
                  f'City: {self.city}\n' \
                  f'Address: {self.address}\n' \
                  f'Sub Zone: {self.sub_zone}\n' \
                  f'Asset Type: {self.asset_type}\n' \
                  f'Address: {self.address}\n' \
                  f'Dimension: {self.dimension}\n' \
                  f'Actual Dimension: {self.actual_dimension}'
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        file_name = f'{self.asset_name}_qr.png'
        self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-status']
        verbose_name = _('Billboard')
        verbose_name_plural = _('Billboards')


    def __str__(self):
        return self.asset_name



class Dimensions(models.Model):
    # Define constants for categories
    FREE_STANDING_SIGNS = 'free_standing_signs'
    PROJECTING_SIGNS = 'projecting_signs'
    WALL_SIGNS = 'wall_signs'
    BILLBOARD_DESIGNATION = 'billboard_designation'
    
    # Define choices as a list of tuples
    CATEGORY_CHOICES = [
        (FREE_STANDING_SIGNS, _('Free standing signs')),
        (PROJECTING_SIGNS, _('Projecting signs')),
        (WALL_SIGNS, _('Wall signs')),
        (BILLBOARD_DESIGNATION, _('Billboard Designation'))
    ]

    ZONE_NORMAL = 'normal_zone'
    ZONE_RESTRICTED = 'restricted_zone'

    # Define zone choices as a list of tuples
    ZONE_CHOICES = [
        (ZONE_NORMAL, _('Normal zone')),
        (ZONE_RESTRICTED, _('Restricted zone'))
    ]

    name = models.CharField(max_length=100, help_text='Name or description of the dimension')
    min_width = models.FloatField(help_text='Width of the media asset in square meters')
    max_width = models.FloatField(help_text='Width of the media asset in square meters')
    unit = models.CharField(max_length=10)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True)
    zone = models.CharField(max_length=50, choices=ZONE_CHOICES, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price for this dimension')

    class Meta:
        verbose_name = 'Dimension'
        verbose_name_plural = 'Dimensions'

    def __str__(self):
        return f'{self.name} ({self.min_width}m² and {self.max_width}m²)'
