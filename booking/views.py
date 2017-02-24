from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
import datetime

from .forms import (BidForm, BookingForm, ConsumerForm, ContractorForm,
TransactionForm)
from .managers import BiddingManager, BookingManager, TransactionManager
from .models import (Agent, Bid, Booking, Category, Consumer, Contractor,
Preferred, Suburb, Transaction)

# Create your views here.
def create_bid(request):
    if not request.user.is_authenticated:
        raise Http404
    form = BidForm_Agent(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request,"Successfully created")
        return HttpResponseRedirect(instance.get_absolute_url())
    elif form.errors:
        messages.error(request,"There was a problem, please try again")
    context = {
        "form": form,
        }
    return render(request,'bid_form.html', context)

def place_bid(request, pk, id, *args, **kwargs):
    if not request.user.is_authenticated:
        raise Http404
    contractor=Contractor.objects.get(pk=pk)
    if not request.user.is_staff and not request.user==contractor.user:
        raise Http404
    booking=Booking.objects.get(id=id)
    form = BidForm(request.POST or None, initial={booking:booking})
    if form.is_valid():
        kwargs = form.cleaned_data
        instance = BiddingManager.place_bid(contractor=contractor, booking=booking, **kwargs)
        messages.success(request,"Successfully created")
        return HttpResponseRedirect(contractor.get_absolute_url())
    elif form.errors:
        messages.error(request,"There was a problem, please try again")
    context = {
        "form": form,
        "booking": booking,
        }
    return render(request,'bid_form.html', context)

def bid_auction(request, pk):
    booking = Booking.objects.get(pk=pk)
    bid_list = ()
    bid_list = BiddingManager.exec_auction(booking=booking)
    context = {
        "bid_list":bid_list,
    }
    return render(request, 'booking_auction.html', context)

def bid_detail(request, id, *args, **kwargs):
    bid = Bid.objects.get(id=id)
    context = {
        "bid": bid,
    }
    return render(request,'bid_detail.html', context)

def bid_list(request):
    bids = Bid.objects.all()
    context = {
        "bids": bids,
    }
    return render(request,'bid_list.html', context)


def create_booking(request):
    if not request.user.is_authenticated:
        raise Http404
    agent = Agent.objects.get(user=request.user)
    form = BookingForm(request.POST or None, initial={"preferred_schedule":timezone.now()})
    if form.is_valid():
        kwargs = form.cleaned_data
        instance = BookingManager.create_booking(agent=agent, **kwargs)
        messages.success(request,"Successfully created")
        return HttpResponseRedirect(instance.get_absolute_url())
    elif form.errors:
        messages.error(request,"There was a problem, please try again")
    context = {
        "form": form,
        }
    return render(request,'booking_form.html', context)

def edit_booking(request, pk=None):
    if not request.user.is_authenticated:
        raise Http404
    agent = Agent.objects.get(user=request.user)
    booking = get_object_or_404(Booking,pk=pk)
    form = BookingForm(request.POST or None, instance=booking)
    if form.is_valid():
        kwargs = form.cleaned_data
        instance = BookingManager.update_booking(agent=agent, booking=booking, **kwargs)
        messages.success(request,"Successfully created")
        # return HttpResponseRedirect(instance.get_absolute_url())
    elif form.errors:
        messages.error(request,"There was a problem, please try again")
    context = {
        "form": form,
        }
    return render(request,'booking_form.html', context)

def booking_detail(request, pk, *args, **kwargs):
    booking = Booking.objects.get(pk=pk)
    bids = Bid.objects.filter(booking_id=pk)
    context = {
        "booking": booking,
        "bids": bids,
    }
    print(context)
    return render(request,'booking_detail.html', context)

def booking_list(request):
    bookings = Booking.objects.all()
    context = {
        "bookings": bookings,
    }
    return render(request,'booking_list.html', context)





def create_consumer(request):
    if not request.user.is_authenticated:
        raise Http404
    form = ConsumerForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request,"Successfully created")
        return HttpResponseRedirect(instance.get_absolute_url())
    elif form.errors:
        messages.error(request,"There was a problem, please try again")
    context = {
        "form": form,
        }
    return render(request,'consumer_form.html', context)

def consumer_detail(request, id, *args, **kwargs):
    consumer = Consumer.objects.get(id=id)
    bookings = Booking.objects.filter(consumer=consumer)
    context = {
        "consumer": consumer,
        "bookings": bookings,
    }
    return render(request,'consumer_detail.html', context)

def consumer_list(request):
    consumers = Consumer.objects.all()
    context = {
        "consumers": consumers,
    }
    return render(request,'consumer_list.html', context)




def create_contractor(request):
    if not request.user.is_authenticated:
        raise Http404
    form = ContractorForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request,"Successfully created")
        return HttpResponseRedirect(instance.get_absolute_url())
    elif form.errors:
        messages.error(request,"There was a problem, please try again")
    context = {
        "form": form,
        }
    return render(request,'contractor_form.html', context)

def contractor_detail(request, id, *args, **kwargs):
    contractor = Contractor.objects.get(id=id)
    if not request.user.is_staff and not request.user==contractor.user:
        raise Http404
    credits = contractor.credits
    active_bids = Bid.objects.filter(contractor=contractor, status='bid_status_active')
    winning_bids = Bid.objects.filter(contractor=contractor, status='bid_status_accepted')
    losing_bids = Bid.objects.filter(contractor=contractor, status='bid_status_expired')
    bookings = Booking.objects.filter(category_id__in=contractor.categories.values_list('id')).filter(completed=False).filter(status="booking_status_active")
    preferred = Preferred.objects.filter(category_id__in=contractor.categories.values_list('id'))
    transactions = Transaction.objects.filter(contractor=contractor)
    context = {
        "contractor": contractor,
        "credits": credits,
        "active_bids": active_bids,
        "winning_bids": winning_bids,
        "losing_bids": losing_bids,
        "bookings": bookings,
        "preferred": preferred,
        "transactions": transactions,
    }
    return render(request,'contractor_detail.html', context)

def contractor_list(request):
    contractors = Contractor.objects.all()
    context = {
        "contractors": contractors,
    }
    return render(request,'contractor_list.html', context)




def create_transaction(request, id=None, *args, **kwargs):
    if not request.user.is_authenticated:
        raise Http404
    agent = Agent.objects.get(user=request.user)
    contractor = Contractor.objects.get(id=id)
    form = TransactionForm(request.POST or None)
    if form.is_valid():
        kwargs = form.cleaned_data
        instance = TransactionManager.buy_credits(source_agent=agent, contractor=contractor, **kwargs)
        messages.success(request,"Successfully created")
        return HttpResponseRedirect(contractor.get_absolute_url())
    elif form.errors:
        messages.error(request,"There was a problem, please try again")
    context = {
        "form": form,
        }
    return render(request,'transaction_form.html', context)

def transaction_detail(request, id, *args, **kwargs):
    transaction = Consumer.objects.get(id=id)
    context = {
        "transaction": transaction,
    }
    return render(request,'transaction_detail.html', context)

def transaction_list(request):
    transactions = Transaction.objects.all()
    context = {
        "transactions": transactions,
    }
    return render(request,'transaction_list.html', context)
