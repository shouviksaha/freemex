from django.shortcuts import render_to_response
from login.models import login,user_share
from stock.models import share
from transaction.models import transactions
from freemex import settings
from django.template import RequestContext
from django.http import HttpResponse,HttpResponseRedirect


def marketwatch()
	shares = share.objects.all()
	sharelist=[]
	for s in shares:
			details={}
			details['name'] = s.name
			details['starting_price'] = s.day_value
			details['current_price'] = (transactions.objects.get(share=s).order_by('-id').[0]).price
			details['percentage']=((details['starting_price']-details['current_price'])/details['starting_price'])*100
			sharelist.append(details)
				
			return render_to_response('login.html', {'form':form,'sellShares':sellShares} , context_instance=RequestContext(request))
