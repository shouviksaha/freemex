from django.db import models
from stock.models import share
from login.models import login,user_share

class bid(models.Model):
	bidder = models.ForeignKey(login)
	share = models.ForeignKey(share)
	quantity = models.IntegerField()
	quote = models.FloatField()


	def __unicode__(self):
		return self.seller		
	
	

class offer(models.Model):
	seller = models.ForeignKey(login)
	share = models.ForeignKey(share)
	quantity = models.IntegerField()
	quote = models.FloatField()
	

	def __unicode__(self):
		return self.seller		

class transactions(models.Model):
	buyer = models.ForeignKey(login,related_name='transaction_buyer')
	seller = models.ForeignKey(login,related_name='transaction_seller')
	share = models.ForeignKey(share)
	quantity = models.IntegerField()
	price = models.FloatField()
	time = models.DateTimeField(auto_now=True)
	
