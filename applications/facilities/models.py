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
    """
    Represents a physical facility location within the organization. 

    A site groups rooms, programs, and related resources under a single addressable location.
    """
    name = models.CharField(max_length=265, unique=True)
    address1 = AddressField()
    address2 = AddressField(related_name='+', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self) -> str:
        return f"{self.name}"
class Room(ModelModifer, models.Model):
    """
    Represents an individual room within a site where children are assigned. 

    Rooms define capacity limits and targeted age groups for program enrollment.
    """
    site= models.ForeignKey(Site, on_delete=models.CASCADE)
    name = models.CharField(max_length=375, null=False, blank=False)
    capacity = models.IntegerField()
    age_group = models.CharField(max_length=3, choices=AGE_GROUP.choices)
    is_active = models.BooleanField(default=True)
    def __str__(self) -> str:
        return f"{self.name} ({self.site}:{self.capacity})"
    
    def update_capacity(self, new_capacity:int):
        """Updates the room's capacity to a new integer value. 

        This method validates the provided capacity and persists the change to the database.

        Args:
            new_capacity (int): The new maximum number of children allowed in the room.

        Raises:
            ValueError: If the provided capacity is not an integer.
        """
        if not isinstance(new_capacity, int):
            raise ValueError(f"Capacity Must be of Type Int, got {type(new_capacity)}")
        self.capacity = new_capacity
        self.save()
    
    def update_age_group(self, new_age_group):
        """Updates the room's designated age group. 

        This method validates the new age group choice and saves the updated value to the database.

        Args:
            new_age_group: The new age group value to assign to the room.

        Raises:
            ValueError: If the provided age group is not a valid choice.
        """
        if new_age_group not in AGE_GROUP.choices:
            raise ValueError(f"Invalid Age Group: Got {new_age_group}")
        self.age_group = new_age_group
        self.save()
        
class Program(ModelModifer,models.Model):
    """
    Represents a distinct childcare or educational program offered at a site. 

    Programs categorize services by type and can be activated or deactivated for enrollment and scheduling.
    """
    site= models.ForeignKey(Site, on_delete=models.CASCADE)
    name = models.CharField(max_length=375, null=False, blank=False)
    program_type = models.CharField(max_length=14, choices=PROGRAM_TYPE.choices)
    is_active = models.BooleanField(default=True)
    def __str__(self) -> str:
        return f"{self.name} ({self.get_program_type_display()}: {self.site})"
    def update_program_type(self, new_program_type):
        """
        Updates the program's type classification. 

        This method validates the new program type choice and saves the updated value to the database.

        Args:
            new_program_type: The new program type value to assign to the program.

        Raises:
            ValueError: If the provided program type is not a valid choice.
        """
        if new_program_type not in PROGRAM_TYPE.choices:
            raise ValueError(f"Invalid Program Type: Got {new_program_type}")
        self.program_type = new_program_type
        self.save()
        