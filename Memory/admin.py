from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Contact)
admin.site.register(FAQS)


# from django_neomodel import admin as neo_admin

# from .models import Signups

# class SignupsAdmin(neo_admin.ModelAdmin):
#     list_display = ('username', 'email', 'dob')

# neo_admin.register(Signups, SignupsAdmin)
