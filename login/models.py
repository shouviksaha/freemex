from django.db import models
from stock.models import share
from django.contrib.auth.models import User

class login(models.Model):
	user = models.ForeignKey(User)
	email = models.EmailField(blank=True)
	password = models.CharField(max_length=250,blank=True)
	money = models.FloatField()
	
	def __unicode__(self):
		return str(self.id)
	
class user_share(models.Model):
	user = models.ForeignKey(login)
	share = models.ForeignKey(share)
	quantity = models.IntegerField()
	


class notification(models.Model):
	user = models.ForeignKey(login)
	notification = models.TextField()
	time = models.DateTimeField(auto_now=True)
	
