#import requests

from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail

from booking.exceptions import AgentNotAuthorized, ContractorNotEligible
from booking.models import *


class BookingManager(object):
    '''Manages CRUD operations for Bookings, performed by Agents.
       Performs auth checking for every operation.'''
    @classmethod
    def create_booking(cls, agent=None, *args, **kwargs):
        '''Creates a booking with an agent, checking necessary perms.
           Returns the created booking.'''
        if not agent:
            raise Exception('First parameter agent is required.')
        if not agent.has_perms(PERM_ACTION_CREATE, PERM_LOCATION_BOOKINGS):
            raise AgentNotAuthorized('CREATE', 'BOOKINGS')
        _subtypes = []
        if 'subtypes' in kwargs:
            _subtypes = kwargs.get('subtypes', [])
            del kwargs['subtypes']
        _booking = Booking(agent=agent, *args, **kwargs)
        _booking.save()
        if len(_subtypes) > 0:
            for _subtype in _subtypes:
                _booking.subtypes.add(_subtype)
        _booking.save()
        return _booking

    @classmethod
    def update_booking(cls, agent=None, booking=None, *args, **kwargs):
        '''Updates a booking's details. Returns the result of
           QuerySet.update().'''
        if not agent:
            raise Exception('First parameter agent is required.')
        if not booking:
            raise Exception('Second parameter booking is required.')
        if not agent.has_perms(PERM_ACTION_UPDATE, PERM_LOCATION_BOOKINGS):
            raise AgentNotAuthorized('UPDATE', 'BOOKINGS')
        _subtypes = []
        if 'subtypes' in kwargs:
            _subtypes = kwargs.get('subtypes', [])
            del kwargs['subtypes']
        if len(_subtypes) > 0:
            _booking = Booking.objects.get(pk=booking.pk)
            for _subtype in _booking.subtypes.all():
                if _subtype not in _subtypes:
                    _booking.subtypes.remove(_subtype)
                else:
                    _subtypes.remove(_subtype)
            for _subtype in _subtypes:
                _booking.subtypes.add(_subtype)
            _booking.save()
        return Booking.objects.filter(pk=booking.pk).update(*args, **kwargs)

class BidSummary(object):
    bid = None
    total_cost = 0
    preferred = False
    created_on = datetime.now()

    def __init__(self, booking=None, bid=None):
        if not booking:
            raise Exception('First parameter booking is required.')
        if not bid:
            raise Exception('Second parameter bid is required.')

        self.bid = bid
        self.total_cost = bid.total_cost
        self.created_on = bid.created_on

        pref = None
        try:
            pref = Preferred.objects.get(contractor=bid.contractor,
                        category=booking.category)
        except Preferred.DoesNotExist:
            self.preferred = False
        except Preferred.MultipleObjectsReturned:
            self.preferred = False

        if pref:
            if pref.in_post_range(booking.post_code):
                self.preferred = True

    def __unicode__(self):
        return "%s / %d / %s" % (self.bid.contractor.name,
                self.total_cost, self.preferred)


class BiddingManager(object):
    '''Manages CRUD operations for biddings, done by contractors.
       Checks for available balance and so on.'''

    @classmethod
    def place_bid(cls, contractor=None, *args, **kwargs):
        '''Places a bid with a contractor, checking credits and account
           permissions. Returns a tuple (Bid, Transaction).'''
        if not contractor:
            raise Exception('First parameter contractor is required.')

        if not contractor.active:
            raise ContractorNotEligible()

        try:
            booking = kwargs['booking']
            if booking.total_cost > contractor.credits:
                raise ContractorNotEligible('Insufficient credits.')
            if booking.category not in contractor.categories.all():
                raise ContractorNotEligible('Category mismatched.')
        except KeyError:
                raise Exception('Required parameter booking not found.')

        _bid = Bid(contractor=contractor, *args, **kwargs)
        _bid.save()

        _transaction = Transaction(
            transaction_type=TRANS_TYPE_REDEEM,
            amount=booking.total_cost,
            contractor=contractor,
            source_type=TRANS_SOURCE_CONT,
            target_bid=_bid
        )
        _transaction.save()
        return (_bid, _transaction)

    @classmethod
    def close_bid(cls, bid=None, status=BID_STATUS_EXPIRED):
        '''Closes a bid with the given status. Returns a tuple
           (Bid, Transaction).'''
        if not bid:
            raise Exception('First parameter bid is required.')
        if status not in [BID_STATUS_ACCEPTED,
                          BID_STATUS_EXPIRED, BID_STATUS_REVOKED]:
            raise ValueError('Invalid status.')
        bid.status = status
        bid.save()

        _transaction = Transaction.objects.get(target_bid=bid)
        if status in [BID_STATUS_EXPIRED, BID_STATUS_REVOKED]:
            _transaction = Transaction.objects.get(
                target_bid=bid)
            _transaction.status = TRANS_STATUS_CANCELLED
            _transaction.comment = 'Bid closed/expired and lost.'
        elif status == BID_STATUS_ACCEPTED:
            _transaction.status = TRANS_STATUS_COMMITTED
        _transaction.save()

        return (bid, _transaction)

    @classmethod
    def get_winning_bid(cls, bid_list=None):
        '''Gets the winning bid from a list of bids in a booking. Returns
           the winning bid.'''
        if not bid_list:
            raise Exception('First parameter bid_list is required.')

        def eval_bid_from_group(group):
            # Get earliest bid in the set of highest bids
            _hb = group[max(group.keys())]  # Highest bids
            _hbd = map(                     # Dates of highest bids
                lambda b: b.created_on, _hb)
            return _hb[_hbd.index(min(_hbd))]

        _p = {}         # Preferred bids
        _np = {}        # Non-preferred bids
        _sg = None      # Selected group
        for bid in bid_list:
            _total_cost = bid.total_cost
            _sg = _p if bid.preferred else _np
            if _total_cost not in _sg:
                _sg[_total_cost] = [bid]
            else:
                _sg[_total_cost].append(bid)

        return eval_bid_from_group(_p)\
            if len(_p) > 0 else eval_bid_from_group(_np)

    @classmethod
    def exec_auction(cls, booking=None):
        '''Performs a Vickrey auction on the given booking.
           Returns a 3-ple, winning_bid, second_bid, losing_bids.'''

        if not booking:
            raise Exception('First parameter booking is required.')

        _bids = [BidSummary(booking, _bid) for _bid in booking.bids.all()]
        _winning_bid = cls.get_winning_bid(_bids)
        _bids.remove(_winning_bid)
        _second_bid = cls.get_winning_bid(_bids)
        _bids.remove(_second_bid)
        print "Winner: %s" % (_winning_bid.__unicode__())
        print "2nd: %s" % (_second_bid.__unicode__())
        print "Lost: %s" % (", ".join([_b.__unicode__() for _b in _bids]))
        return (_winning_bid, _second_bid, _bids)


class AlertsManager(object):
    '''Manages creation and sending of alerts.'''

    @classmethod
    def send_alert(cls, target=None, body=None, _send_email=False):
        Alert.create(target=target, body=body)
        if _send_email:
            send_mail('Notifcation from Conos',
                      body, settings.DEFAULT_FROM_EMAIL, [target.user.email])

    @classmethod
    def send_asknicely(cls, consumer=None):
        if not consumer:
            raise Exception("First parameter consumer required.")
        if not isinstance(consumer, Consumer):
            raise Exception("Invalid consumer type.")

        r = requests.post("https://conos.asknice.ly/api/v1/person/trigger",
                data={
                    "email": consumer.email_address,
                    "name": consumer.name,
                    "addperson": False,
                    "delayminutes": 0
                }, headers={
                    "X-apikey":
                    "sqDNYMtYQwu6JeDHQnNl4FXvq6k2hP3auB0QNRAWoxC"
                });

        res = r.json()
        if not res["success"]:
            raise Exception("Failed: %s" % (res["msg"]))
