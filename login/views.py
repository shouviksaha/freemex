from django.shortcuts import render_to_response
from login.models import login,user_share,notification
from stock.models import share
from freemex import settings
from django.template import RequestContext
from django.http import HttpResponse,HttpResponseRedirect
from transaction.models import transactions,bid,offer
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
#from transaction.views import chectransaction
import decimal,random
from django import forms
from django.db import connection

def eod(request):
	if request.method == 'POST':
		if request.POST['password'] == "bowchikawowwow":
			shares = share.objects.all()
			dummy = login.objects.get(email='dummy@dummy.com')
				
			cursor = connection.cursor()
			cursor.execute("TRUNCATE TABLE `transaction_bid`")
			cursor.execute("TRUNCATE TABLE `transaction_offer`")
			
			for shareId in shares:
					try:
						current_price = round(((transactions.objects.filter(share=shareId).order_by('-id'))[0]).price,2)
					except:
						current_price = shareId.day_value
					shareId.day_value = current_price
					shareId.save()
					
					
					start = shareId.day_value
					stopbid = shareId.day_value - shareId.day_value * 0.01
					stopoffer = shareId.day_value + shareId.day_value * 0.01
					step = 0.001
					f = .001
					
					dummyquantity = round(40000/current_price)
					
					for i in range(3):
						b = bid(bidder=dummy, share=shareId, quantity=dummyquantity, quote=round((random.randrange(round(stopbid/f),round(start/f),round(step/f))*f),2))
						s = offer(seller=dummy, share=shareId, quantity=dummyquantity, quote=round((random.randrange(round(start/f),round(stopoffer/f),round(step/f))*f),2))
						b.save()
						s.save()
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
		else:
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
			
def eodpage(request):
	return render_to_response('eod.html', {} , context_instance=RequestContext(request))
	
def mailtest(request):
			email_body = 'bal'
			email_subject = 'Congratulations! Your password has been successfully changed'
			email_from = 'cricketkeeda@sportskeeda.com'
			email_to = 'svksaha91@gmail.com'
			email_bcc = 'saurav.singhi@gmail.com'
			email = EmailMultiAlternatives(subject=email_subject, body=email_body, from_email=email_from, to=[email_to], bcc=[email_bcc])
			email.attach_alternative(email_body, "text/html")
			email.send()
			return HttpResponse('baal')
 
def faq(request):
	return render_to_response('faq.html', {} , context_instance=RequestContext(request))

def logout(request):
	del request.session['login_id']
	return HttpResponseRedirect(request.META['HTTP_REFERER'])
		
def buyShareList():
	shares = share.objects.all()
	sharelist = []
	for i in shares:
		sharelist.append((i.id,i.name))		
	return sharelist

def sellShareList(request):
	login_id = login.objects.get(pk=request.session['login_id'])
	shares=[]
	shares.extend(user_share.objects.filter(user=login_id))
	sharelist = []
	for i in shares:
		if i.quantity == 0:
			continue
		details = {}
		
		stock = share.objects.get(pk=i.share_id)
		details['shareid']=stock.id
		details['name']=stock.name
		details['quantity']=i.quantity
		details['min'] = round(stock.day_value*0.9,2)
		details['max'] = round(stock.day_value*1.1,2)
		sharelist.append((details))
		
	
	return sharelist

class BidForm(forms.Form):
	quantity = forms.IntegerField()
	price = forms.DecimalField(decimal_places=2,max_digits=15)
	share = forms.ChoiceField(choices=buyShareList())

def marketWatch():
	shares = share.objects.all()
	sharelist=[]

	for s in shares:
			details={}
			details['shareid'] = int(s.id)
			details['name'] = s.name
			details['starting_price'] = s.day_value
			details['min'] = round(details['starting_price']*0.9,2)
			details['max'] = round(details['starting_price']*1.1,2)
			try:
				details['current_price'] = round(((transactions.objects.filter(share=s).order_by('-id'))[0]).price,2)
				details['percentage']=((details['current_price']-details['starting_price'])/details['starting_price'])*100
			except:
				details['current_price'] = details['starting_price']
				details['percentage'] = 0
			sharelist.append(details)


	return sharelist
	
def pendingBid(request):
	bidlist=[]
	try:
		bidOrders=bid.objects.filter(bidder_id=request.session['login_id'])	
			

		for s in bidOrders:
				details={}
				details['transaction_id'] = s.id
				details['share_id'] = s.share_id
				details['share_name'] = (share.objects.get(pk=s.share_id)).name
				starting_price = (share.objects.get(pk=s.share_id)).day_value
				details['min'] = round(starting_price*0.9,2)
				details['max'] = round(starting_price*1.1,2)
				details['price'] = s.quote
				details['quantity'] = s.quantity
				bidlist.append(details)
	except:
		pass

	return bidlist
	
def pendingOffer(request):	
	offerlist=[]
	
	try:
		offerOrders=offer.objects.filter(seller_id=request.session['login_id'])	
		for s in offerOrders:
			details={}
			details['transaction_id'] = s.id
			details['share_id'] = s.share_id
			details['share_name'] = (share.objects.get(pk=s.share_id)).name
			usershare = user_share.objects.get(user=request.session['login_id'],share=s.share)
			details['max_share'] = usershare.quantity
			starting_price = (share.objects.get(pk=s.share_id)).day_value
			details['min'] = round(starting_price*0.9,2)
			details['max'] = round(starting_price*1.1,2)
			details['price'] = s.quote
			details['quantity'] = s.quantity
			offerlist.append(details)
	except:
		pass

	return offerlist	

def currentHolding(request):
	sharelist=[]
	try:
		userShares = user_share.objects.filter(user_id=request.session['login_id'])
	
	
		for s in userShares:
			if s.quantity ==0:
				continue
			details={}
			details['share_id']=s.share_id
			details['share_name']=(share.objects.get(pk=s.share_id)).name
			details['quantity']=s.quantity
			try:
				details['current_price'] = round(((transactions.objects.filter(share=s.share).order_by('-id'))[0]).price,2)
				sharesBought = transactions.objects.filter(share=s.share,buyer_id=request.session['login_id'])
				totalShare=0
				totalMoney=0
				for i in sharesBought:
					totalShare += i.quantity
					totalMoney += i.price*i.quantity
				details['buying_price']=totalMoney/totalShare
				details['profit']=(details['current_price']-details['buying_price'])*details['quantity']
			except:
				details['current_price']=share.objects.get(pk=s.share_id).day_value
				details['buying_price']=share.objects.get(pk=s.share_id).face_value
				details['profit']=(details['current_price']-details['buying_price'])*details['quantity']
				
			sharelist.append(details)
	except:
		pass
	return sharelist

def transactionhistory(request):
	transactionlist=[]
	try:
		userTransactions = transactions.objects.filter(Q(buyer_id=request.session['login_id']) | Q(seller_id=request.session['login_id'])).order_by('-id')[0:15]
		for ut in userTransactions:
			if ut.buyer_id == ut.seller_id:
				continue
			details={}
			details['share_name']=(share.objects.get(pk=ut.share_id)).name
			details['quantity']=ut.quantity
			details['price']=ut.price
			if ut.buyer_id == request.session['login_id']:
				details['type'] = "bought"
			else:
				details['type'] = "sold"
			transactionlist.append(details)
	except:
		pass
	return transactionlist

def marqueecontent(baal):
	shares = share.objects.all()
	sharelist=[]

	for s in shares:
			details={}
			details['shareid'] = int(s.id)
			details['name'] = s.name
			details['starting_price'] = s.day_value
			try:
				details['current_price'] = round(((transactions.objects.filter(share=s).order_by('-id'))[0]).price,2)
				details['difference']=((details['current_price']-details['starting_price']))
			except:
				details['current_price'] = details['starting_price']
				details['difference'] = 0
			sharelist.append(details)
	content = ''' '''
	for s in sharelist:
		content = content + '''<span class="stockbox"><a href="/analysis?q=''' + str(s['shareid']) + '''">''' + str(s['name']) + '''</a>&nbsp;''' + '''&nbsp;<span style="color: #'''
		if s['difference']>0:
			content += '''009900;">'''+str(s['current_price'])+'''&nbsp;&uarr;&nbsp'''+str(s['difference'])+'''</span></span>'''
		elif s['difference']<0:
			content += '''ff0000;">''' +str(s['current_price'])+'''&nbsp;&darr;&nbsp'''+str(s['difference'])+'''</span></span>'''
		else:
			content +='''ffff00;">'''+ str(s['current_price'])+'''&nbsp;-&nbsp'''+str(s['difference'])+'''</span></span>'''
	
	return HttpResponse(content)
		
		
def leaderboard():
	users = login.objects.all()
	dummy = login.objects.get(email='dummy@dummy.com')

	leaderList = []
	for i in users:
		if i==dummy:
			continue
		details={}
		details['email']=User.objects.get(pk=i.user_id).username
		userShares = user_share.objects.filter(user_id=i.id)
		totalValue = 0
		for userShare in userShares:
			try:
				price = ((transactions.objects.filter(share=userShare.share).order_by('-id'))[0]).price
			except:
				continue
			shareValue = userShare.quantity*price
			totalValue = totalValue + shareValue
		details['assets']= i.money + totalValue
		leaderList.append(details)
	leaderList = sorted(leaderList, key=lambda k: int(k['assets'])) 
	leaderList.reverse()
	return leaderList
		
def pricevariations():
	shares=share.objects.all()
	finalList = {}
	for shareId in shares:
		shareTransactions = transactions.objects.filter(share=shareId)
		
		list=[]
		for st in shareTransactions:
			details={}
			timeTuple = (st.time).timetuple()
			details['date']=(timeTuple[0],timeTuple[1],timeTuple[2],timeTuple[3],timeTuple[4],0,0)
			details['val']=st.price
			list.append(details)
		finalList[shareId.id]=list
		
	return finalList
	
		
def analysis(request):
		shareTransactions = transactions.objects.filter(share=request.GET['q'])		
		list=[]
		for st in shareTransactions:
			details={}
			timeTuple = (st.time).timetuple()
			details['date']=(timeTuple[0],timeTuple[1],timeTuple[2],timeTuple[3],timeTuple[4],0,0)
			details['val']=st.price
			list.append(details)
		temp = settings.STATIC_URL	
		name = share.objects.get(pk=request.GET['q']).name
		return render_to_response('analysis.html', {'temp':temp,'list':list,'name':name} , context_instance=RequestContext(request))
		
def main(request):
	if request.user.is_authenticated():
		try:
			Login = login.objects.get(user=request.user)
		except:
			Login = login(user=request.user,money=100000)
			Login.save()
		request.session['login_id'] = Login.id
		
	temp = settings.STATIC_URL
	return render_to_response('home.html', {'temp':temp} , context_instance=RequestContext(request))
		

def portfolio(request):
	pendingBids = pendingBid(request)
	pendingOffers = pendingOffer(request)
	currentHoldings = currentHolding(request)
	userMoney = login.objects.get(pk=request.session['login_id']).money
	temp = settings.STATIC_URL
	return render_to_response('portfolio.html', {'temp':temp,'pendingBids':pendingBids,'pendingOffers':pendingOffers,'currentHoldings':currentHoldings,'userMoney':userMoney} , context_instance=RequestContext(request))
	
def marketwatch(request):
	market = marketWatch()
	try:
		usershares=sellShareList(request)
	except:
		usershares=[]
	variations=pricevariations()
	temp = settings.STATIC_URL

	return render_to_response('marketwatch.html', {'temp':temp,'market':market,'usershares':usershares,'variations':variations} , context_instance=RequestContext(request))
	
	
def history(request):
	userTransaction = transactionhistory(request)
	temp = settings.STATIC_URL
	return render_to_response('transactions.html', {'temp':temp,'list':userTransaction} , context_instance=RequestContext(request))
	
	
	
def leader(request):
	board = leaderboard()
	temp = settings.STATIC_URL
	return render_to_response('leaderboard.html', {'temp':temp,'leaderboard':board} , context_instance=RequestContext(request))
	
def notify(request):
		try:
			note = notification.objects.filter(user_id=request.session['login_id']).order_by('-id')[0:5]
			content = ""
			for i in note:
				content = content +"<li><a href='#'>"+i.notification+"</a></li>"
			return HttpResponse(content)
		except:
			return HttpResponse("<li>"+"</li>")
		
	

		

	
