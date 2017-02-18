from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone
import datetime

from .forms import (BidForm, BookingForm, ConsumerForm, ContractorForm,
TransactionForm)
from .managers import BookingManager
from .models import Agent, Bid, Booking, Category, Consumer, Contractor, Suburb, Transaction

# Create your views here.
def create_bid(request):
    if not request.user.is_authenticated:
        raise Http404
    form = BidForm(request.POST or None)
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
    booking = BookingManager()
    form = BookingForm(request.POST or None, initial={"agent":request.user,"preferred_schedule":timezone.now()})
    if form.is_valid():
        kwargs = form.cleaned_data
        instance = booking.create_booking(agent=agent, **kwargs)
        messages.success(request,"Successfully created")
        return HttpResponseRedirect(instance.get_absolute_url())
    elif form.errors:
        messages.error(request,"There was a problem, please try again")
    context = {
        "form": form,
        }
    return render(request,'booking_form.html', context)


def booking_detail(request, pk, *args, **kwargs):
    booking = Booking.objects.get(pk=pk)
    context = {
        "booking": booking,
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
    context = {
        "consumer": consumer,
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
    if not request.user.is_staff or not request.user==contractor.user:
        raise Http404
    credits = contractor.credits
    context = {
        "contractor": contractor,
        "credits": credits,
    }
    return render(request,'contractor_detail.html', context)

def contractor_list(request):
    contractors = Contractor.objects.all()
    context = {
        "contractors": contractors,
    }
    return render(request,'contractor_list.html', context)




def create_transaction(request, *args, **kwargs):
    if not request.user.is_authenticated:
        raise Http404
    form = TransactionForm(request.POST or None)
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
