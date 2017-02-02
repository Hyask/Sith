from django.core.exceptions import PermissionDenied
from ajax_select import register, LookupChannel

from core.views.site import search_user
from core.models import User, Group, SithFile
from club.models import Club
from counter.models import Product, Counter
from accounting.models import ClubAccount, Company

def check_token(request):
    return ('counter_token' in request.session.keys() and
        request.session['counter_token'] and
        Counter.objects.filter(token=request.session['counter_token']).exists())

class RightManagedLookupChannel(LookupChannel):
    def check_auth(self, request):
        if not request.user.was_subscribed() and not check_token(request):
            raise PermissionDenied

@register('users')
class UsersLookup(RightManagedLookupChannel):
    model = User

    def get_query(self, q, request):
        return search_user(q)

    def format_match(self, obj):
        return obj.get_mini_item()

    def format_item_display(self, item):
        return item.get_display_name()

@register('groups')
class GroupsLookup(RightManagedLookupChannel):
    model = Group

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q)[:50]

    def format_match(self, obj):
        return obj.name

    def format_item_display(self, item):
        return item.name

@register('clubs')
class ClubLookup(RightManagedLookupChannel):
    model = Club

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q)[:50]

    def format_match(self, obj):
        return obj.name

    def format_item_display(self, item):
        return item.name

@register('counters')
class CountersLookup(RightManagedLookupChannel):
    model = Counter

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q)[:50]

    def format_item_display(self, item):
        return item.name

@register('products')
class ProductsLookup(RightManagedLookupChannel):
    model = Product

    def get_query(self, q, request):
        return (self.model.objects.filter(name__icontains=q) |
                self.model.objects.filter(code__icontains=q)).filter(archived=False)[:50]

    def format_item_display(self, item):
        return "%s (%s)" % (item.name, item.code)

@register('files')
class SithFileLookup(RightManagedLookupChannel):
    model = SithFile

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q)[:50]

@register('club_accounts')
class ClubAccountLookup(RightManagedLookupChannel):
    model = ClubAccount

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q)[:50]

    def format_item_display(self, item):
        return item.name

@register('companies')
class CompaniesLookup(RightManagedLookupChannel):
    model = Company

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q)[:50]

    def format_item_display(self, item):
        return item.name
