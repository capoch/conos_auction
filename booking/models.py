from __future__ import unicode_literals
#Added by Philipp
from django.conf import settings

from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from types import ListType, IntType

import json



# Constants
PERM_ACTION_CREATE = 'perm_action_create'
PERM_ACTION_READ = 'perm_action_read'
PERM_ACTION_UPDATE = 'perm_action_update'
PERM_ACTION_DELETE = 'perm_action_delete'
PERM_ACTIONS = (
    (PERM_ACTION_CREATE, 'Create'),
    (PERM_ACTION_READ, 'Read'),
    (PERM_ACTION_UPDATE, 'Update'),
    (PERM_ACTION_DELETE, 'Delete')
)
PERM_LOCATION_BOOKINGS = 'perm_location_bookings'
PERM_LOCATION_BIDS = 'perm_location_bids'
PERM_LOCATION_TOPUPS = 'perm_location_topups'
PERM_LOCATION_ACCOUNTS = 'perm_location_accounts'
PERM_LOCATIONS = (
    (PERM_LOCATION_BOOKINGS, 'Bookings'),
    (PERM_LOCATION_BIDS, 'Bids'),
    (PERM_LOCATION_TOPUPS, 'Topups'),
    (PERM_LOCATION_ACCOUNTS, 'Account Settings'),
)
PERM_LOCATION_GLOBAL = 'perm_location_global'
TRANS_TYPE_BUY = 'trans_type_buy'
TRANS_TYPE_REDEEM = 'trans_type_redeem'
TRANS_TYPES = (
    (TRANS_TYPE_BUY, 'Buy'),
    (TRANS_TYPE_REDEEM, 'Redeem')
)
TRANS_SOURCE_AGENT = 'trans_source_agent'
TRANS_SOURCE_CONT = 'trans_source_contractor'
TRANS_SOURCE_TYPES = (
    (TRANS_SOURCE_AGENT, 'Agent'),
    (TRANS_SOURCE_CONT, 'Contractor')
)
BOOKING_STATUS_ACTIVE = 'booking_status_active'
BOOKING_STATUS_RESCHEDULED = 'booking_status_rescheduled'
BOOKING_STATUS_CANCELLED = 'booking_status_cancelled'
BOOKING_STATUSES = (
    (BOOKING_STATUS_ACTIVE, 'Active'),
    (BOOKING_STATUS_RESCHEDULED, 'Rescheduled'),
    (BOOKING_STATUS_CANCELLED, 'Cancelled')
)
BID_STATUS_ACTIVE = 'bid_status_active'
BID_STATUS_ACCEPTED = 'bid_status_accepted'
BID_STATUS_EXPIRED = 'bid_status_expired'
BID_STATUS_REVOKED = 'bid_status_revoked'
BID_STATUSES = (
    (BID_STATUS_ACTIVE, 'Active'),
    (BID_STATUS_EXPIRED, 'Expired'),
    (BID_STATUS_REVOKED, 'Revoked')
)
TRANS_STATUS_PENDING = 'trans_status_pending'
TRANS_STATUS_COMMITTED = 'trans_status_committed'
TRANS_STATUS_CANCELLED = 'trans_status_cancelled'
TRANS_STATUSES = (
    (TRANS_STATUS_PENDING, 'Pending'),
    (TRANS_STATUS_COMMITTED, 'Committed'),
    (TRANS_STATUS_CANCELLED, 'Cancelled')
)
ALERT_TARGET_AGENT = 'alert_target_agent'
ALERT_TARGET_CONT = 'alert_target_cont'
ALERT_TARGET_TYPES = (
    (ALERT_TARGET_AGENT, 'Agent'),
    (ALERT_TARGET_CONT, 'Contractor')
)

# Model Definitions


class Permission(models.Model):
    '''Agent access permissions.'''
    action = models.CharField(max_length=30, choices=PERM_ACTIONS)
    location = models.CharField(max_length=30, choices=PERM_LOCATIONS)

    class Meta:
        unique_together = ('action', 'location')

    def __unicode__(self):
        return "%s on %s" % (self.action, self.location)


class AccessLevel(models.Model):
    '''Agent access levels.'''
    name = models.CharField(unique=True, max_length=64)
    default_permissions = models.ManyToManyField(Permission, blank=True)

    def __unicode__(self):
        return self.name


class Agent(models.Model):
    '''Agents. Authenticates via built-in Django user model.'''
    permissions = models.ManyToManyField(Permission, blank=True)
    access_level = models.ForeignKey(AccessLevel, null=True, blank=True)
    user = models.ForeignKey(User, related_name="agent")

    def has_perms(self, action, location):
        '''Checks if this agent has the proper access permissions for a given
           action and location.'''
        for perm_ in self.permissions.all():
            if (perm_.action == action and perm_.location == location):
                return True
        for al_perm_ in self.access_level.default_permissions.all():
            if (al_perm_.action == action and al_perm_.location == location):
                return True
        return False

    def __unicode__(self):
        return "%s (%s)" % (self.user.username, self.access_level)


class Consumer(models.Model):
    '''Consumers (end clients).'''
    name = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=32)
    email_address = models.EmailField()

    def __unicode__(self):
        return "%s - (%s)" % (self.name, self.phone_number)

    @property
    def nps(self):
        nps_reqs = NPSRequest.objects.filter(consumer=self, is_received=True)
        return reduce(lambda x, y: x + y.nps, nps_reqs, 0.00)

    #Added by Philipp

    def get_absolute_url(self):
        return reverse('booking:consumer-detail', kwargs = {"id": self.id})


class Category(models.Model):
    '''Categories for booking and contractors.'''
    name = models.CharField(max_length=64, unique=True)

    def __unicode__(self):
        return self.name


class SubType(models.Model):
    '''Booking sub-types.'''
    name = models.CharField(max_length=64, unique=True)

    def __unicode__(self):
        return self.name


class Contractor(models.Model):
    '''Contractors. Authenticates via built-in Django
       user class. Uses a Json-serialized list to store post_ranges.'''
    name = models.CharField(max_length=128, unique=True)
    categories = models.ManyToManyField(Category, blank=True)
    phone_number = models.CharField(max_length=32)
    post_ranges_raw = models.CharField(max_length=128, default="[]")
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, related_name="contractor")

    def __unicode__(self):
        return self.name

    @property
    def credits(self):
        '''Returns contractor's outstanding balance.'''
        def evaluate_transactions(collector, next_transaction):
            if (next_transaction.transaction_type == TRANS_TYPE_BUY):
                return collector + float(next_transaction.amount)
            elif (next_transaction.transaction_type == TRANS_TYPE_REDEEM):
                return collector - float(next_transaction.amount)
        _transactions = self.transactions.filter(
            status__in=[TRANS_STATUS_PENDING, TRANS_STATUS_COMMITTED]
        )

        return reduce(evaluate_transactions, _transactions, 0.00)

    @property
    def post_ranges(self):
        '''Retrieves and de-serializes json from post_ranges_raw.'''
        try:
            return json.loads(self.post_ranges_raw)
        except:
            raise Exception("Unable to load post_ranges_raw. " +
                            "Data may be corrupted.")

    def set_post_ranges(self, post_ranges):
        '''Serializes and sets json to post_ranges_raw.'''

        # Typechecking
        if not isinstance(post_ranges, ListType):
            raise Exception("post_ranges must be ListType.")
        for _pr in post_ranges:
            if len(_pr) < 2:
                raise Exception(
                    "post_ranges must contain lists of 2 Integers.")
            if (not isinstance(_pr[0], IntType) or
                    not isinstance(_pr[1], IntType)):
                raise Exception(
                    "post_ranges must contain lists of 2 Integers.")
        self.post_ranges_raw = json.dumps(post_ranges)
        return self.save()

    def in_post_range(self, post_code):
        '''Returns a Boolean value if post_code is within post_ranges.'''
        post_ranges = self.post_ranges
        for _pr in post_ranges:
            if post_code in range(_pr[0], _pr[1]):
                return True
        return False

    #Added by Philipp
    def get_absolute_url(self):
        return reverse('booking:contractor-detail', kwargs = {"id": self.id})


class Suburb(models.Model):
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name


class Booking(models.Model):
    '''Core booking model. Contains all info about bookings.'''
    consumer = models.ForeignKey(Consumer)
    address_1 = models.CharField(max_length=256)
    address_2 = models.CharField(max_length=256, null=True, blank=True)
    access_instructions = models.TextField(max_length=1024, blank=True, null=True)
    suburb = models.ForeignKey(Suburb)
    phone_number_2 = models.CharField(max_length=32, null=True, blank=True)
    agent = models.ForeignKey(Agent)
    post_code = models.IntegerField()
    preferred_schedule = models.DateTimeField()
    category = models.ForeignKey(Category)
    subtypes = models.ManyToManyField(SubType, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    quoted_price = models.DecimalField(decimal_places=2, max_digits=6)
    cost_adjustment = models.DecimalField(default=0.00, decimal_places=2,
                                          max_digits=6)
    base_cost = models.DecimalField(decimal_places=2, max_digits=6)
    priority_level = models.IntegerField()
    completed = models.BooleanField(default=False)
    status = models.CharField(choices=BOOKING_STATUSES, max_length=30)
    comment_private = models.TextField(max_length=1000, null=True, blank=True)
    comment_public = models.TextField(max_length=1000, null=True, blank=True)
    link = models.ForeignKey('booking', null=True, blank=True)

    def __unicode__(self):
        return "%s: %s (%.2f)" % (self.created_on, self.consumer.name,
                                  self.quoted_price)

    @property
    def total_cost(self):
        return self.base_cost + self.cost_adjustment

    #Added by Philipp
    def get_absolute_url(self):
        return reverse('booking:booking-detail', kwargs = {"id": self.id})



class Bid(models.Model):
    '''Core bid model.'''
    booking = models.ForeignKey(Booking, related_name="bids")
    contractor = models.ForeignKey(Contractor, related_name="bids")
    base_cost = models.DecimalField(decimal_places=2, max_digits=6)
    premium_adjustment = models.DecimalField(default=0.00, decimal_places=2,
                                             max_digits=6)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, default=BID_STATUS_ACTIVE,
                              choices=BID_STATUSES)

    def __unicode__(self):
        return "[%s] %s -- [%s (%.2f)]" % (self.created_on, self.booking,
                                           self.contractor, self.base_cost)

    @property
    def total_cost(self):
        return self.base_cost + self.premium_adjustment


    #Added by Philipp
    def get_absolute_url(self):
        return reverse('booking:bid-detail', kwargs = {"id": self.id})


class Transaction(models.Model):
    '''Transactions. Serves as the contractor's ledger. Outstanding balance
       is derived from here.'''
    transaction_type = models.CharField(choices=TRANS_TYPES, max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=6)
    source_agent = models.ForeignKey(Agent, null=True, blank=True)
    contractor = models.ForeignKey(Contractor, related_name='transactions',
                                   null=True, blank=True)
    source_type = models.CharField(choices=TRANS_SOURCE_TYPES, max_length=30)
    target_bid = models.ForeignKey(Bid, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, default=TRANS_STATUS_PENDING,
                              choices=TRANS_STATUSES)
    comment = models.TextField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return "%s %s (%.2f)" % (self.timestamp, self.transaction_type,
                                 self.amount)

    #Added by Philipp
    def get_absolute_url(self):
        return reverse('booking:transaction-detail', kwargs = {"id": self.id})


class Preferred(models.Model):
    '''Preferred contractors per category per postcode range.'''
    contractor = models.ForeignKey(Contractor)
    category = models.ForeignKey(Category)
    post_ranges_raw = models.CharField(max_length=128, default="[]")

    @property
    def post_ranges(self):
        '''Retrieves and de-serializes json from post_ranges_raw.'''
        try:
            return json.loads(self.post_ranges_raw)
        except:
            raise Exception("Unable to load post_ranges_raw. " +
                            "Data may be corrupted.")

    def set_post_ranges(self, post_ranges):
        '''Serializes and sets json to post_ranges_raw.'''

        # Typechecking
        if not isinstance(post_ranges, ListType):
            raise Exception("post_ranges must be ListType.")
        for _pr in post_ranges:
            if len(_pr) < 2:
                raise Exception(
                    "post_ranges must contain lists of 2 Integers.")
            if (not isinstance(_pr[0], IntType) or
                    not isinstance(_pr[1], IntType)):
                raise Exception(
                    "post_ranges must contain lists of 2 Integers.")
        self.post_ranges_raw = json.dumps(post_ranges)
        return self.save()

    def in_post_range(self, post_code):
        '''Returns a Boolean value if post_code is within post_ranges.'''
        post_ranges = self.post_ranges
        for _pr in post_ranges:
            if post_code in range(_pr[0], _pr[1]):
                return True
        return False


class Alert(models.Model):
    '''Alerts for contractors and/or agents.'''
    target = models.IntegerField()              # pk of the target
    target_type = models.CharField(max_length=32, choices=ALERT_TARGET_TYPES,
                                   default=ALERT_TARGET_CONT)
    body = models.TextField(max_length=5000)
    is_read = models.BooleanField(default=False)

    @classmethod
    def create(cls, target=None, body=None):
        if not target:
            raise Exception("Missing target.")
        if (not isinstance(target, Agent)
                and not isinstance(target, Contractor)):
            raise Exception("Invalid target type.")
        if not body:
            raise Exception("Missing body.")

        _ttype = ALERT_TARGET_AGENT if isinstance(target, Agent) else\
                 ALERT_TARGET_CONT

        _alert = cls(target=target.pk, target_type=_ttype, body=body)
        _alert.save()
        return _alert

    @classmethod
    def get_alerts(cls, target=None):
        if not target:
            raise Exception("Missing target.")
        if (not isinstance(target, Agent)
                and not isinstance(target, Contractor)):
            raise Exception("Invalid target type.")

        _ttype = ALERT_TARGET_AGENT if isinstance(target, Agent) else\
                 ALERT_TARGET_CONT

        return cls.objects.filter(target=target.pk, target_type=_ttype)


class NPSRequest(models.Model):
    consumer = models.ForeignKey(Consumer)
    nps_id = models.IntegerField()
    is_received = models.BooleanField(default=False)
    nps = models.DecimalField(default=0.00, max_digits=5,
                              decimal_places=2)
