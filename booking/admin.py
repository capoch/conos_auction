from django.contrib import admin

from booking.models import *


class AccessLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'permissions_parsed')

    def permissions_parsed(self, obj):
        if obj.default_permissions.count() < 1:
            return None
        return ",".join(
            [("%s on %s" %
             (perm.action, perm.location))
             for perm in obj.default_permissions.all()])
    permissions_parsed.short_description = 'Permissions'
    permissions_parsed.empty_value_display = 'No default permissions'


class AgentAdmin(admin.ModelAdmin):
    list_display = ('username', 'access_level', 'permissions_parsed',)
    fields = ('user', 'access_level', 'implicit_permissions', 'permissions',)
    readonly_fields = ('implicit_permissions',)

    def implicit_permissions(self, obj):
        if obj.access_level.default_permissions.count() < 1:
            return None
        return "\n".join(
            [("%s on %s" %
             (perm.action, perm.location)) for
             perm in obj.access_level.default_permissions.all()])
    implicit_permissions.short_name = 'implicit_permissions'
    implicit_permissions.empty_value_display = 'No implicit permissions'

    def username(self, obj):
        return obj.user.username

    def permissions_parsed(self, obj):
        if obj.permissions.count() < 1:
            return None
        return ",".join(
            [("%s on %s" %
             (perm.action, perm.location)) for perm in obj.permissions.all()])
    permissions_parsed.short_description = 'Permissions'
    permissions_parsed.empty_value_display = 'No explicit permissions'


class ContractorAdmin(admin.ModelAdmin):
    list_display = ('active', 'name', 'categories_parsed', 'credits')

    def categories_parsed(self, obj):
        if obj.categories.count() < 1:
            return None
        return ",".join(
            [("%s" % category.name) for category in obj.categories.all()])
    categories_parsed.short_description = 'Categories'
    categories_parsed.empty_value_display = 'No categories set'


class BookingAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'category', 'agent_name', 'consumer_name',
                    'quoted_price', 'base_cost', 'priority_level')

    def consumer_name(self, obj):
        return obj.consumer.name

    def agent_name(self, obj):
        return obj.agent.user.username
# Register your models here.

admin.site.register(Permission)
admin.site.register(AccessLevel, AccessLevelAdmin)
admin.site.register(Agent, AgentAdmin)
# admin.site.register(Contractor, ContractorAdmin)
admin.site.register(Contractor)
admin.site.register(Consumer)
admin.site.register(Category)
admin.site.register(SubType)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Bid)
admin.site.register(Transaction)
admin.site.register(Preferred)
## added by Philipp
admin.site.register(Suburb)
