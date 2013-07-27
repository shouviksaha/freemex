from django.db import models


class share(models.Model):
	name = models.CharField(max_length=250)
	face_value = models.FloatField()
	day_value = models.FloatField()
	total_quantity = models.IntegerField()

	def __unicode__(self):
		return self.name	
