from django.contrib import admin
from login.models import login,user_share

class loginAdmin(admin.ModelAdmin):
	pass

class user_shareAdmin(admin.ModelAdmin):
	pass
		
admin.site.register(user_share,user_shareAdmin)
admin.site.register(login,loginAdmin)