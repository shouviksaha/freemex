from django.contrib import admin
from stock.models import share
class shareAdmin(admin.ModelAdmin):
	pass
	
admin.site.register(share,shareAdmin)
