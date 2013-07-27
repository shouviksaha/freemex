from django.shortcuts import render_to_response
from login.models import login,user_share,notification
from stock.models import share
from freemex import settings
from django.template import RequestContext
from django.http import HttpResponse,HttpResponseRedirect
from transaction.models import bid,offer,transactions
from login.views import buyShareList,BidForm
import random,decimal,math
from django.db.models import Q
from datetime import datetime

def randrange_float(start, stop, step):
	rand = random.randint(0, round((stop - start) / step)) * step + start
	rand = round(20*rand)/20
	return rand
	
def dummy(shareId,request):
	dummy = login.objects.get(email='dummy@dummy.com')
	#change dummy money here
	try:
		bidMoney = bid.objects.filter(bidder_id=request.session['login_id'],share=shareId).order_by('-id')[0].quote
		bidQuantity = bid.objects.filter(bidder_id=request.session['login_id'],share=shareId).order_by('-id')[0].quantity
		totalBidValue = bidMoney*bidQuantity
	except:
		totalBidValue = 0
	try:
		offerMoney = offer.objects.filter(seller_id=request.session['login_id'],share=shareId).order_by('-id')[0].quote
		offerQuantity = offer.objects.filter(seller_id=request.session['login_id'],share=shareId).order_by('-id')[0].quantity
		totalOfferValue = offerMoney*offerQuantity
	except:
		totalOfferValue = 0
	try:
		current_price = ((transactions.objects.filter(share=shareId).order_by('-id'))[0]).price
	except:
		current_price = shareId.day_value
	totalValue=max(totalBidValue, totalOfferValue)
	
	dummyquantity = totalValue * 0.4 / current_price
	if dummyquantity<1:
		dummyquantity = 10
	start = shareId.day_value
	stopbid = shareId.day_value - shareId.day_value * 0.01
	stopoffer = shareId.day_value + shareId.day_value * 0.01
	step = 0.001
	f = .001
	
	for i in range(3):
		b = bid(bidder=dummy, share=shareId, quantity=dummyquantity, quote=round((random.randrange(round(stopbid/f),round(start/f),round(step/f))*f),2))
		s = offer(seller=dummy, share=shareId, quantity=dummyquantity, quote=round((random.randrange(round(start/f),round(stopoffer/f),round(step/f))*f),2))
		b.save()
		checktransaction(shareId, "bid", request)
		s.save()
		checktransaction(shareId, "sell", request)
		
def deletebid(request):
	date = datetime.now()
	hour = (date.time()).hour
	if hour < 21:
		message = notification(user_id=request.session['login_id'],notification = "Order cannot be processed. Market Closed")
		message.save()
		return HttpResponseRedirect('/marketwatch/')
	if request.method == 'POST':
		b = bid.objects.get(pk=request.POST['transaction_id'])
		b.delete()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

def deleteoffer(request):
	date = datetime.now()
	hour = (date.time()).hour
	if hour < 21:
		message = notification(user_id=request.session['login_id'],notification = "Order cannot be processed. Market Closed")
		message.save()
		return HttpResponseRedirect('/marketwatch/')
	if request.method == 'POST':
		s = offer.objects.get(pk=request.POST['transaction_id'])
		s.delete()
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
		
def bidmodify(request):
	date = datetime.now()
	hour = (date.time()).hour
	if hour < 21:
		message = notification(user_id=request.session['login_id'],notification = "Order cannot be processed. Market Closed")
		message.save()
		return HttpResponseRedirect('/marketwatch/')
	if request.method == 'POST':
		try:
			b = bid.objects.get(pk=request.POST['transaction_id'])
		except:
			return HttpResponseRedirect('/portfolio/')
		b.quantity=request.POST['quantity']
		b.quote = request.POST['quote']
		shareId = b.share
		min = round(shareId.day_value * 0.9, 2) 
		max = round(shareId.day_value * 1.1, 2)
		quote = round(decimal.Decimal(b.quote), 2)
		if quote < min or quote > max:
			message = notification(user_id=request.session['login_id'],notification="Quote unsuccessful. Quote price out of bounds")
			message.save()
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
		b.save()
		
		data = "bid"
		checktransaction(shareId,data,request)
		dummy(shareId,request)
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

def offermodify(request):
	date = datetime.now()
	hour = (date.time()).hour
	if hour < 21:
		message = notification(user_id=request.session['login_id'],notification = "Order cannot be processed. Market Closed")
		message.save()
		return HttpResponseRedirect('/marketwatch/')
	if request.method == 'POST':
		try:
			o = offer.objects.get(pk=request.POST['transaction_id'])
		except:
			return HttpResponseRedirect('/portfolio/')
		shareId = o.share
		o.quantity=request.POST['quantity']
		o.quote = request.POST['quote']

		userShare = user_share.objects.get(user_id=request.session['login_id'],share=shareId)
		min = round(shareId.day_value * 0.9, 2) 
		max = round(shareId.day_value * 1.1, 2)
		quote = round(decimal.Decimal(o.quote), 2)
		if quote < min or quote > max:
			message = notification(user_id=request.session['login_id'],notification="Quote unsuccessful. Quote price out of bounds")
			message.save()
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
		if int(o.quantity) > userShare.quantity:
			message = notification(user_id=request.session['login_id'],notification="Quote unsuccessful. Not enough stocks to sell")
			message.save()
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
		
		o.save()
		data = "sell"
		checktransaction(shareId,data,request)
		dummy(shareId,request)
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

def bidcheck(request):
	date = datetime.now()
	hour = (date.time()).hour

	if hour < 21:
		message = notification(user_id=request.session['login_id'],notification = "Order cannot be processed. Market Closed")
		message.save()
		return HttpResponseRedirect('/marketwatch/')
	if request.method == 'POST':
		shareId = share.objects.get(pk=request.POST['share'])
		bidderId = login.objects.get(pk=request.session['login_id'])
		b = bid(bidder = bidderId, share = shareId, quantity=request.POST['quantity'], quote=request.POST['price'])
		min = round(shareId.day_value * 0.9, 2)
		max = round(shareId.day_value * 1.1, 2)
		quote = round(decimal.Decimal(b.quote), 2)
		if quote < min or quote > max:
			message = notification(user_id=request.session['login_id'],notification = "Quote unsuccessful. Quote price out of bounds")
			message.save()
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
		b.save()
		data = "bid"
		checktransaction(shareId,data,request)
		dummy(shareId,request)
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
			
def offercheck(request):
	date = datetime.now()
	hour = (date.time()).hour
	if hour < 21:
		message = notification(user_id=request.session['login_id'],notification = "Order cannot be processed. Market Closed")
		message.save()
		return HttpResponseRedirect('/marketwatch/')
	if request.method == 'POST':
		shareId = share.objects.get(pk=request.POST['share'])
		sellerId = login.objects.get(pk=request.session['login_id'])
		s = offer(seller = sellerId ,share = shareId , quantity=request.POST['quantity'],quote=request.POST['price'])
		userShare = user_share.objects.get(user_id=request.session['login_id'],share=shareId)
		min = round(shareId.day_value * 0.9, 2) 
		max = round(shareId.day_value * 1.1, 2)
		quote = round(decimal.Decimal(s.quote), 2)
		if quote < min or quote > max:
			message = notification(user_id=request.session['login_id'],notification="Quote unsuccessful. Quote price out of bounds")
			message.save()
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
		if int(s.quantity) > userShare.quantity:
			message = notification(user_id=request.session['login_id'],notification="Quote unsuccessful. Not enough stocks to sell")
			message.save()
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
			
		
		s.save()
		data = "sell"
		checktransaction(shareId,data,request)
		dummy(shareId,request)
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
		
		

def checktransaction(shareId,data,request):
	shareBids = bid.objects.filter(share=shareId).order_by('-quote')
	shareOffers = offer.objects.filter(share=shareId).order_by('quote')
	shareName = shareId.name
	dummy = login.objects.get(email='dummy@dummy.com')
	if(data == "bid"):
			for i in shareOffers:
				try:
					if (i.quote < shareBids[0].quote) or (i.quote == shareBids[0].quote):
						if i.quantity < shareBids[0].quantity:


							userId=login.objects.get(pk=shareBids[0].bidder_id)
							transactionPrice = i.quote +(shareBids[0].quote - i.quote)/2
							transactionTotal = i.quantity*transactionPrice
							if userId != dummy:
								if userId.money < transactionTotal:
									shareBids[0].delete()
									for shareBid in shareBids:
										shareBid.save()
									note = notification(user=userId,notification="Your Bid for "+shareName+" got deleted due to lack of money")
									note.save()
									break
								
							temp = shareBids[0]
							temp.quantity = temp.quantity - i.quantity
							temp.save()	
							try:
								t=transactions(buyer=shareBids[0].bidder,seller = i.seller , share = shareId , quantity = i.quantity , price = transactionPrice)
								noteBuyer = notification(user=t.buyer,notification=str(t.quantity)+" shares of "+shareId.name+" bought at "+str(t.price))
								noteSeller = notification(user=t.seller,notification=str(t.quantity)+" shares of "+shareId.name+" sold at "+str(t.price))
								noteBuyer.save()
								noteSeller.save()
							except IndexError:
								break
							buyer = t.buyer
							seller = t.seller
							if (buyer!=seller):
								if buyer != dummy:
									buyer.money = buyer.money - transactionTotal
								if (user_share.objects.filter(user=buyer,share=shareId)):
									bs = user_share.objects.get(user=buyer,share=shareId)
									bs.quantity = bs.quantity + t.quantity
								else:
									bs = user_share(user=buyer,share=shareId,quantity=t.quantity)
								bs.save()
								ss=user_share.objects.get(user=seller,share=shareId)
								if seller != dummy:
									ss.quantity = ss.quantity - t.quantity
								ss.save()
								seller = i.seller
								seller.money = seller.money + transactionTotal
								buyer.save()
								seller.save()
							t.save()						

							i.delete()
						else:

							transactionPrice =i.quote + (shareBids[0].quote - i.quote)/2
							transactionTotal = shareBids[0].quantity*transactionPrice

							userId=login.objects.get(pk=shareBids[0].bidder_id)
							money = userId.money
							if userId != dummy:
								if userId.money < transactionTotal:
									i.delete()
									for shareBid in shareBids:
										shareBid.save()
									note = notification(user=userId,notification="Your Bid for "+shareName+" got deleted due to lack of money")
									note.save()
									break
								
							i.quantity = i.quantity - shareBids[0].quantity 	
							try:
								t=transactions(buyer=shareBids[0].bidder,seller = i.seller , share = shareId , quantity = shareBids[0].quantity , price = transactionPrice)
								noteBuyer = notification(user=t.buyer,notification=str(t.quantity)+" shares of "+shareId.name+" bought at "+str(t.price))
								noteSeller = notification(user=t.seller,notification=str(t.quantity)+" shares of "+shareId.name+" sold at "+str(t.price))
								noteBuyer.save()
								noteSeller.save()
							except IndexError:
								break
							
							buyer = t.buyer
							seller = t.seller
							if (buyer!=seller):
								if buyer != dummy:
									buyer.money = buyer.money - transactionTotal
								if (user_share.objects.filter(user=buyer,share=shareId)):
									bs = user_share.objects.get(user=buyer,share=shareId)
									bs.quantity = bs.quantity + t.quantity
								else:
									bs = user_share(user=buyer,share=shareId,quantity=t.quantity)
								bs.save()
								
								ss=user_share.objects.get(user=seller,share=shareId)
								if seller != dummy:
									ss.quantity = ss.quantity - t.quantity
								ss.save()
								seller.money = seller.money + transactionTotal
								buyer.save()
								seller.save()		
							t.save()	
							shareBids[0].delete()
							for shareBid in shareBids:
								shareBid.save()
							i.save()
							if i.quantity == 0:
								i.delete()
				except IndexError:
					break
	else:
			for i in shareBids:
				try:
					if (shareOffers[0].quote < i.quote) or (shareOffers[0].quote == i.quote):
						if shareOffers[0].quantity < i.quantity:
							transactionPrice = shareOffers[0].quote + (i.quote - shareOffers[0].quote)/2
							transactionTotal = transactionPrice*shareOffers[0].quantity
							userId = login.objects.get(pk=i.bidder_id)
							money = userId.money
							if userId != dummy:
								if userId.money < transactionTotal:
									i.delete()
									note = notification(user=userId,notification="Your Bid for "+shareName+" got deleted due to lack of money")
									note.save()
									break
							i.quantity = i.quantity - shareOffers[0].quantity
							i.save()
							try:
								t=transactions(buyer=i.bidder,seller = shareOffers[0].seller , share = shareId , quantity = shareOffers[0].quantity , price = transactionPrice)
								noteBuyer = notification(user=t.buyer,notification=str(t.quantity)+" shares of "+shareId.name+" bought at "+str(t.price))
								noteSeller = notification(user=t.seller,notification=str(t.quantity)+" shares of "+shareId.name+" sold at "+str(t.price))
								noteBuyer.save()
								noteSeller.save()
							except IndexError:
								break
							buyer = t.buyer
							seller = t.seller
							if (buyer!=seller):
								if buyer != dummy:
									buyer.money = buyer.money - transactionTotal
								if (user_share.objects.filter(user=buyer,share=shareId)):
									bs = user_share.objects.get(user=buyer,share=shareId)
									bs.quantity = bs.quantity + t.quantity
								else:
									bs = user_share(user=buyer,share=shareId,quantity=t.quantity)
								bs.save()
								
								ss=user_share.objects.get(user=seller,share=shareId)
								if seller != dummy:
									ss.quantity = ss.quantity - t.quantity
								ss.save()
				
								seller.money = seller.money + transactionTotal
								buyer.save()
								seller.save()		
							
							
							t.save()	
							
							
							
							
							
							temp = shareOffers[0]
							temp.delete()
						else:
							transactionPrice = shareOffers[0].quote + (i.quote - shareOffers[0].quote)/2
							transactionTotal = transactionPrice*i.quantity
							
							userId=login.objects.get(pk=shareBids[0].bidder_id)
							if userId != dummy:
								if userId.money < transactionTotal:
									i.delete()
									note = notification(user=userId,notification="Your Bid for "+shareName+" got deleted due to lack of money")
									note.save()
									break
							
							temp = shareOffers[0]
							temp.quantity = temp.quantity - i.quantity
							temp.save()
							try:
								t=transactions(buyer=i.bidder,seller = shareOffers[0].seller , share = shareId , quantity = i.quantity , price = transactionPrice)
								noteBuyer = notification(user=t.buyer,notification=str(t.quantity)+" shares of "+shareId.name+" bought at "+str(t.price))
								noteSeller = notification(user=t.seller,notification=str(t.quantity)+" shares of "+shareId.name+" sold at "+str(t.price))
								noteBuyer.save()
								noteSeller.save()
							except IndexError:
								break
							buyer = t.buyer
							seller = t.seller
							if (buyer!=seller):
								if buyer != dummy:
									buyer.money = buyer.money - transactionTotal
								
								if (user_share.objects.filter(user=buyer,share=shareId)):
									bs = user_share.objects.get(user=buyer,share=shareId)
									bs.quantity = bs.quantity + t.quantity
								else:
									bs = user_share(user=buyer,share=shareId,quantity=t.quantity)
								bs.save()
								
								ss=user_share.objects.get(user=seller,share=shareId)
								if seller != dummy:
									ss.quantity = ss.quantity - t.quantity
								ss.save()

								seller.money = seller.money + transactionTotal
								buyer.save()
								seller.save()		
							
							t.save()	
							
							i.delete()
							
							if temp.quantity == 0:
								temp.delete()
								break
				except IndexError:
					break		
