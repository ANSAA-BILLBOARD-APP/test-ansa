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
        BILLBOARD_DESIGNATION: _('Billboard Designation'),

    }

    # Define constants for Signage Type
    FIRST_PARTY = 'first_party'
    THIRD_PARTY = 'third_party'

    SIGNAGE_TYPE = {
        FIRST_PARTY: _('First Party'),
        THIRD_PARTY: _('Third Party'),
    }

    # Define constants for Sign Type
    WALLDRAPES = 'walldrapes'
    PROJECTING_SIGNS = 'projecting_signs'
    WALL_CANOPY_ROOF_SIGNS = 'wall_canopy_roof_signs'
    NEON_SIGNS = 'neon_signs'
    _48_SHEETS = '48_sheets'
    _96_SHEETS = '96_sheets'
    BRIDGE_PANEL = 'bridge_panel'
    OVERHEAD_GANTRIES = 'overhead_gantries'
    LAMP_POSTS = 'lamp_posts'
    UNIPOLES = 'unipoles'
    LED_SCREENS_FILLING_STATIONS = 'led_screens_filling_stations'
    
    # Define constants for Sign Type
    SIGN_TYPE= {
        WALLDRAPES: _('Walldrapes'),
        PROJECTING_SIGNS: _('Projecting signs'),
        WALL_CANOPY_ROOF_SIGNS: _('Wall/Canopy/Roof Signs'),
        NEON_SIGNS: _('Neon signs'),
        _48_SHEETS: _('48 sheets'),
        _96_SHEETS: _('96 Sheets'),
        BRIDGE_PANEL: _('Bridge panel'),
        OVERHEAD_GANTRIES: _('Overhead Gantries'),
        LAMP_POSTS: _('Lamp posts'),
        UNIPOLES: _('Unipoles'),
        LED_SCREENS_FILLING_STATIONS: _('LED Screens (Filling stations)'),

    }

    # Define constants for Sign format
    PORTRAIT = 'portrait'
    LANDSCAPE = 'landscape'

    SIGN_FORMAT = {
        PORTRAIT: _('Portrait'),
        LANDSCAPE: _('Landscape'),
    }

    # Define constants for number of face
    SINGLE = 'single'
    DOUBLE = 'double'
    MULTIPLE = 'multiple'

    NO_OF_FACE = {
        SINGLE: _('Single'),
        DOUBLE: _('Double'),
        MULTIPLE: _('Multiple'),
    }

    # Define constants for illumination type
    NONE = 'none'
    EXTERNAL = 'external'
    INTERNAL = 'internal'

    ILLUMINATION_TYPE = {
        NONE: _('None'),
        EXTERNAL: _('External'),
        INTERNAL: _('Internal'),
    }

    # Define constants for business type
    COMMERCIAL_BUSINESS = 'commercial_business'

    BUSINESS_TYPE = {
        COMMERCIAL_BUSINESS: _('Commercial business'),
    }

    # Define constants for Sign Type
    OFFICE_OR_SHOPS = 'office_or_shops'
    HOTELS_OR_EATERIES = 'hotels_or_eateries'
    PARKS = 'parks'
    HOSTELS = 'hostels'
    COMMERCIAL_BANKS = 'commercial_banks'
    PRIVATE_MICROFINANCE_BANKS = 'private_microfinance_banks'

    
    # Define constants for Sign Type
    BUSINESS_CATEGORY= {
        OFFICE_OR_SHOPS: _('Office or shops'),
        HOTELS_OR_EATERIES: _('Hotels or Eateries'),
        PARKS: _('Parks'),
        HOSTELS: _('Hostels'),
        COMMERCIAL_BANKS: _('Commercial Banks'),
        PRIVATE_MICROFINANCE_BANKS: _('Private/Microfinance Banks'),
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

    unique_id = models.CharField(max_length=10, editable=False)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True)
    signage_type = models.CharField(max_length=50, choices=SIGNAGE_TYPE, blank=True)
    sign_type = models.CharField(max_length=50, choices=SIGN_TYPE, blank=True)
    zone = models.CharField(max_length=50, choices=ZONE_CHOICES, blank=True)
    sub_zone = models.ForeignKey(Zones, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    vacancy = models.CharField(max_length=20, choices=VACANCY_CHOICES, default='vacant', blank=True)

    sign_format = models.CharField(max_length=50, choices=SIGN_FORMAT)
    no_of_faces = models.CharField(max_length=50, choices=NO_OF_FACE)
    illumination_type = models.CharField(max_length=50, choices=ILLUMINATION_TYPE)
    length = models.CharField(max_length=150)
    breadth = models.CharField(max_length=150)
    dimension = models.CharField(max_length=50, blank=True)
    actual_size = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=30, decimal_places=2, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES, default=PENDING
    )
    payment_date = models.DateTimeField(blank=True, null=True)
    image1 = models.URLField(max_length=200, blank=True, null=True)
    image2 = models.URLField(max_length=200, blank=True, null=True)
    image3 = models.URLField(max_length=200, blank=True, null=True)
    user = models.ForeignKey(AnsaaUser, on_delete=models.CASCADE)

    asset_street_address = models.CharField(max_length=250, blank=True)
    asset_lga = models.CharField(max_length=150, blank=True)
    state = models.CharField(max_length=20, default="Anambra", editable=False)
    country = models.CharField(max_length=20, default="Nigeria", editable=False)

    company_name = models.CharField(max_length=150, blank=True)
    company_phone = PhoneNumberField(blank=True)
    asin = models.CharField(max_length=25)
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPE)
    business_category = models.CharField(max_length=50, choices=BUSINESS_CATEGORY)

    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.unique_id:  # Generate unique_id only if not already set
            unique_id_prefix = 'BOARD '
            unique_id_suffix = uuid.uuid4().hex[:3]
            self.unique_id = f'{unique_id_prefix}{unique_id_suffix}'.upper()


        # Generate QR code
        qr_data = f'Asset Name: {self.unique_id}\n' \
                  f'Sign Type: {self.sign_type}\n' \
                  f'Zone: {self.zone}\n' \
                  f'Company Name: {self.company_name}\n' \
                  f'Price: {self.price}\n' \
                  f'City: {self.asset_lga}\n' \
                  f'Address: {self.asset_street_address}\n' \
                  f'Sub Zone: {self.sub_zone}\n' \
                  f'Sign Format: {self.sign_format}\n' \
                  f'Number of Faces: {self.no_of_faces}\n' \
                  f'Dimension: {self.dimension}\n' \
                  f'Actual Dimension: {self.actual_size}'
        
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
        file_name = f'{self.unique_id}_qr.png'
        self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-status']
        verbose_name = _('Billboard')
        verbose_name_plural = _('Billboards')


    def __str__(self):
        return self.unique_id



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
