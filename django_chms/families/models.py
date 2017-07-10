from django.core.urlresolvers import reverse
from django.db import models
import os

from django.contrib.auth.models import User
# Create your models here.

class Family(models.Model):
    def get_image_path(instance, filename):
        return os.path.join('photos', str(instance.id), filename)

    class Meta:
        verbose_name_plural = 'Families'
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    family_name = models.CharField(max_length=50)
    address1 = models.CharField(blank=True, max_length=255)
    address2 = models.CharField(blank=True, max_length=255)
    city = models.CharField(blank=True, max_length=50)
    postal_code = models.CharField(blank=True, max_length=10)
    state = models.CharField(blank=True, max_length=50)
    country = models.CharField(blank=True, max_length=70)
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to=get_image_path, blank=True, null=True)

    def __str__(self):
        return self.family_name

    def get_absolute_url(self):
        return reverse('families:detail', kwargs={
            'pk': self.id,
            })


class Member(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    class Meta:
        abstract = True
    family = models.ForeignKey(Family)
    title = models.CharField(blank=True, max_length=15)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(blank=True, max_length=255)
    last_name = models.CharField(max_length=50)
    suffix = models.CharField(blank=True, max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    birth_date = models.DateField(blank=True, null=True)
    date_joined = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)

    def save(self, *args, **kwargs):
        self.last_name = self.family.family_name
        super(Member, self).save(*args, **kwargs)

class Adult(Member):
    occupation = models.CharField(blank=True, max_length=255)
    workplace = models.CharField(blank=True, max_length=255)
    work_address = models.CharField(blank=True, max_length=255)
    marital_status = models.CharField(blank=True, max_length=20)

    class Meta:
        ordering = ['id',]

    def get_absolute_url(self):
        return reverse('families:member', kwargs={
            'family_pk': self.family_id,
            'member_type': 'a',
            'member_pk': self.id,
            })

class Child(Member):
    school = models.CharField(blank=True, max_length=255)

    class Meta:
        verbose_name_plural = 'Children'
        #    ordering = ['birth_date', 'id']

    def get_absolute_url(self):
        return reverse('families:member', kwargs={
            'family_pk': self.family_id,
            'member_type': 'd',
            'member_pk': self.id,
            })
    def age(self):
        from families.templatetags.family_extras import age_calc
        return '{} years'.format(age_calc(self.birth_date))



