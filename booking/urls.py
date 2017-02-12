from django.conf.urls import url
from django.contrib import admin

from .views import (booking, create_consumer, consumer_list, consumer_detail,
create_contractor, contractor_list, contractor_detail, create_transaction,
transaction_list, transaction_detail, create_booking, booking_list,
booking_detail, create_bid, bid_list, bid_detail)

urlpatterns = [
    url(r'^consumer/create', create_consumer, name="create-consumer"),
    url(r'^consumer/$', consumer_list, name="consumer-list"),
    url(r'^consumer/(?P<id>[\w+])', consumer_detail, name="consumer-detail"),
    url(r'^contractor/create', create_contractor, name="create-contractor"),
    url(r'^contractor/$', contractor_list, name="contractor-list"),
    url(r'^contractor/(?P<id>[\w+])', contractor_detail, name="contractor-detail"),
    url(r'^transaction/create', create_transaction, name="create-transaction"),
    url(r'^transaction/$', transaction_list, name="transaction-list"),
    url(r'^transaction/(?P<id>[\w+])', transaction_detail, name="transaction-detail"),
    url(r'^booking/create', create_booking, name="create-booking"),
    url(r'^booking/$', booking_list, name="booking-list"),
    url(r'^booking/(?P<id>[\w+])', booking_detail, name="booking-detail"),
    url(r'^bid/create', create_bid, name="create-bid"),
    url(r'^bid/$', bid_list, name="bid-list"),
    url(r'^bid/(?P<id>[\w+])', bid_detail, name="bid-detail"),
    url(r'^test', booking, name="test"),
]
