from django.conf import settings
#from django.core.urlresolvers import reverse
from django.urls import reverse_lazy
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from model_utils.managers import InheritanceManager
import os

from django.contrib.auth.models import User
from cities_local.models import Country, Region, City
# Create your models here.



class Family(models.Model):
    def get_image_path(instance, filename):
        return os.path.join('photos', str(instance.id), filename)

    #def user_directory_path(instance, filename):
    #    filename = os.path.split(filename)[1]
    #    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    #    return 'photos_{0}/{1}'.format(instance.id, filename)

    class Meta:
        verbose_name_plural = 'Families'
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.PROTECT)
    family_name = models.CharField(max_length=50)
    address1 = models.CharField(blank=True, max_length=255)
    address2 = models.CharField(blank=True, max_length=255)
    postal_code = models.CharField(blank=True, max_length=15)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.PROTECT)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.PROTECT)

    membership_status = models.CharField(max_length=2, choices=settings.MEMBERSHIP_TYPES, default='FM')
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    image_sm = ImageSpecField(source='image',
                                    processors=[ResizeToFill(300, 200)],
                                    format='JPEG',
                                    options={'quality': 60})

    def get_adults(self):
        #return [member for member in self.member_set.all() if hasattr(member, 'adult')]
        return [member for member in self.member_set.all().order_by('-gender') if member.fam_member_type == 'a']

    def get_children(self):
        return [member for member in self.member_set.all().order_by('birth_date') if member.fam_member_type == 'c']
    
    def get_children_names(self):
        return [member.first_name for member in self.member_set.all() if member.fam_member_type == 'c']
   
    def __str__(self):
        return self.family_name

    def get_absolute_url(self):
        return reverse_lazy('families:family_detail', kwargs={
            'pk': self.id,
            })

class Member(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    FMEMBER_TYPE_CHOICES = (
        ('c', 'Child'),
        ('a', 'Adult')
    )
    MARITAL_STATUS_CHOICES = (
        ('s', 'Single'),
        ('m', 'Married'),
        ('d', 'Divorced'),
        ('w', 'Widowed'),
    )
    #class Meta:
    #    abstract = True
    family = models.ForeignKey(Family, on_delete=models.PROTECT) 
    objects = InheritanceManager()
    title = models.CharField(blank=True, max_length=15)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(blank=True, max_length=255)
    last_name = models.CharField(max_length=50)
    suffix = models.CharField(blank=True, max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    birth_date = models.DateField(blank=True, null=True)
    membership_status = models.CharField(max_length=2, choices=settings.MEMBERSHIP_TYPES, default='FM')
    date_joined = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    fam_member_type = models.CharField(max_length=1, default='a', choices=FMEMBER_TYPE_CHOICES)
    occupation = models.CharField(blank=True, max_length=255)
    workplace = models.CharField(blank=True, max_length=255)
    work_address = models.CharField(blank=True, max_length=255)
    marital_status = models.CharField(blank=True, max_length=1, default='s', choices=MARITAL_STATUS_CHOICES)
    school = models.CharField(blank=True, max_length=255)
    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)

    def get_absolute_url(self):
        return reverse_lazy('families:member_detail', kwargs={
            'family_pk': self.family_id,
            'member_pk': self.id,
            })
    #def save(self, *args, **kwargs):
    #    self.last_name = self.family.family_name
    #    super(Member, self).save(*args, **kwargs)

    class Meta:
        ordering = ['fam_member_type',]


    def age(self):
        from families.templatetags.family_extras import age_calc
        if self.birth_date:
            return '{} years'.format(age_calc(self.birth_date))
        else:
            return



