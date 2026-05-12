from django.db import models
from address.models import AddressField
from django.utils.translation import gettext_lazy as _
from common.helpers import ModelModifer

class AGE_GROUP(models.TextChoices):
    INFANT = 'INF', _('Infant: 0 - 18 Months')
    TODDLER = 'TOD', _('Toddler: 18 Months - 3 Years')
    SCHOOLAGE = 'SA', _('School Age: 3 Years to 12 Years')
    TEEN = 'TEE', _('Teenager: 13+ Years')
    
class PROGRAM_TYPE(models.TextChoices):
    PRESCHOOL = 'PS', _('Preschool')
    HEADSTART = 'HD-ST', _('Headstart')
    PRECARE = 'PC', _('Precare')
    AFTERSCHOOL = 'AS', _('Afterschool')
    
class Site(ModelModifer, models.Model):
    name = models.CharField(max_length=265, unique=True)
    address1 = AddressField()
    address2 = AddressField(related_name='+', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
class Room(ModelModifer, models.Model):
    site= models.ForeignKey(Site, on_delete=models.CASCADE)
    name = models.CharField(max_length=375, null=False, blank=False)
    capacity = models.IntegerField()
    age_group = models.CharField(max_length=3, choices=AGE_GROUP.choices)
    is_active = models.BooleanField(default=True)

    def update_capacity(self, new_capacity:int):
        if isinstance(new_capacity, int):
            self.capacity = new_capacity
            self.save()
        else:
            raise ValueError(f"Capacity Must be of Type Int, got {type(new_capacity)}")
    
    def update_age_group(self, new_age_group):
        if new_age_group in AGE_GROUP.choices:
            self.age_group = new_age_group
            self.save()
        else:
            raise ValueError(f"Invalid Age Group: Got {new_age_group}")
        
class Program(ModelModifer,models.Model):
    site= models.ForeignKey(Site, on_delete=models.CASCADE)
    name = models.CharField(max_length=375, null=False, blank=False)
    program_type = models.CharField(max_length=14, choices=PROGRAM_TYPE.choices)
    is_active = models.BooleanField(default=True)
    
    def update_program_type(self, new_program_type):
        if new_program_type in PROGRAM_TYPE.choices:
            self.program_type = new_program_type
            self.save()
        else:
            raise ValueError(f"Invalid Program Type: Got {new_program_type}")
        