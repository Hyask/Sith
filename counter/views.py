from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, RedirectView, TemplateView
from django.views.generic.edit import UpdateView, CreateView, DeleteView, ProcessFormView, FormMixin
from django.forms.models import modelform_factory
from django.forms import CheckboxSelectMultiple
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db import DataError, transaction, models

import re
import pytz
from datetime import date, timedelta, datetime
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
from ajax_select import make_ajax_form, make_ajax_field

import os
from sys import exit, exc_info
from itertools import combinations
from collections import defaultdict

from core.views import CanViewMixin, CanEditMixin, CanEditPropMixin, CanCreateMixin, TabedViewMixin
from core.views.forms import SelectUser, LoginForm, SelectDate, SelectDateTime
from core.models import User
from subscription.models import Subscription
from counter.models import Counter, Customer, Product, Selling, Refilling, ProductType, \
        CashRegisterSummary, CashRegisterSummaryItem, Eticket, Permanency
from accounting.models import CurrencyField

class GetUserForm(forms.Form):
    """
    The Form class aims at providing a valid user_id field in its cleaned data, in order to pass it to some view,
    reverse function, or any other use.

    The Form implements a nice JS widget allowing the user to type a customer account id, or search the database with
    some nickname, first name, or last name (TODO)
    """
    code = forms.CharField(label="Code", max_length=10, required=False)
    id = AutoCompleteSelectField('users', required=False, label=_("Select user"), help_text=None)

    def as_p(self):
        self.fields['code'].widget.attrs['autofocus'] = True
        return super(GetUserForm, self).as_p()

    def clean(self):
        cleaned_data = super(GetUserForm, self).clean()
        cus = None
        if cleaned_data['code'] != "":
            cus = Customer.objects.filter(account_id__iexact=cleaned_data['code']).first()
        elif cleaned_data['id'] is not None:
            cus = Customer.objects.filter(user=cleaned_data['id']).first()
        sub = cus.user if cus is not None else None
        if (cus is None or sub is None or not sub.subscriptions.last() or
            (date.today() - sub.subscriptions.last().subscription_end) > timedelta(days=90)):
            raise forms.ValidationError(_("User not found"))
        cleaned_data['user_id'] = cus.user.id
        cleaned_data['user'] = cus.user
        return cleaned_data

class RefillForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    class Meta:
        model = Refilling
        fields = ['amount', 'payment_method', 'bank']
        widgets = {
            'amount': forms.NumberInput(attrs={'class':'focus'},)
        }

class CounterTabsMixin(TabedViewMixin):
    def get_tabs_title(self):
        return self.object
    def get_list_of_tabs(self):
        tab_list = []
        tab_list.append({
            'url': reverse_lazy('counter:details', kwargs={'counter_id': self.object.id}),
            'slug': 'counter',
            'name': _("Counter"),
            })
        if self.object.type == "BAR":
            tab_list.append({
                'url': reverse_lazy('counter:cash_summary', kwargs={'counter_id': self.object.id}),
                'slug': 'cash_summary',
                'name': _("Cash summary"),
                })
            tab_list.append({
                'url': reverse_lazy('counter:last_ops', kwargs={'counter_id': self.object.id}),
                'slug': 'last_ops',
                'name': _("Last operations"),
                })
        return tab_list

class CounterMain(CounterTabsMixin, DetailView, ProcessFormView, FormMixin):
    """
    The public (barman) view
    """
    model = Counter
    template_name = 'counter/counter_main.jinja'
    pk_url_kwarg = "counter_id"
    form_class = GetUserForm # Form to enter a client code and get the corresponding user id
    current_tab = "counter"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.type == "BAR" and not ('counter_token' in self.request.session.keys() and
                self.request.session['counter_token'] == self.object.token): # Check the token to avoid the bar to be stolen
            return HttpResponseRedirect(reverse_lazy('counter:details', args=self.args,
                kwargs={'counter_id': self.object.id})+'?bad_location')
        return super(CounterMain, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        We handle here the login form for the barman
        """
        if self.request.method == 'POST':
            self.object = self.get_object()
        self.object.update_activity()
        kwargs = super(CounterMain, self).get_context_data(**kwargs)
        kwargs['login_form'] = LoginForm()
        kwargs['login_form'].fields['username'].widget.attrs['autofocus'] = True
        kwargs['login_form'].cleaned_data = {} # add_error fails if there are no cleaned_data
        if "credentials" in self.request.GET:
            kwargs['login_form'].add_error(None, _("Bad credentials"))
        if "sellers" in self.request.GET:
            kwargs['login_form'].add_error(None, _("User is not barman"))
        kwargs['form'] = self.get_form()
        kwargs['form'].cleaned_data = {} # same as above
        if "bad_location" in self.request.GET:
            kwargs['form'].add_error(None, _("Bad location, someone is already logged in somewhere else"))
        if self.object.type == 'BAR':
            kwargs['barmen'] = self.object.get_barmen_list()
        elif self.request.user.is_authenticated():
            kwargs['barmen'] = [self.request.user]
        if 'last_basket' in self.request.session.keys():
            kwargs['last_basket'] = self.request.session.pop('last_basket')
            kwargs['last_customer'] = self.request.session.pop('last_customer')
            kwargs['last_total'] = self.request.session.pop('last_total')
            kwargs['new_customer_amount'] = self.request.session.pop('new_customer_amount')
        return kwargs

    def form_valid(self, form):
        """
        We handle here the redirection, passing the user id of the asked customer
        """
        self.kwargs['user_id'] = form.cleaned_data['user_id']
        return super(CounterMain, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('counter:click', args=self.args, kwargs=self.kwargs)

class CounterClick(CounterTabsMixin, DetailView):
    """
    The click view
    This is a detail view not to have to worry about loading the counter
    Everything is made by hand in the post method
    """
    model = Counter
    template_name = 'counter/counter_click.jinja'
    pk_url_kwarg = "counter_id"
    current_tab = "counter"

    def get(self, request, *args, **kwargs):
        """Simple get view"""
        self.customer = Customer.objects.filter(user__id=self.kwargs['user_id']).first()
        if 'basket' not in request.session.keys(): # Init the basket session entry
            request.session['basket'] = {}
            request.session['basket_total'] = 0
        request.session['not_enough'] = False # Reset every variable
        request.session['too_young'] = False
        request.session['not_allowed'] = False
        request.session['no_age'] = False
        self.refill_form = None
        ret = super(CounterClick, self).get(request, *args, **kwargs)
        if ((self.object.type != "BAR" and not request.user.is_authenticated()) or
                (self.object.type == "BAR" and
                len(self.object.get_barmen_list()) < 1)): # Check that at least one barman is logged in
            ret = self.cancel(request) # Otherwise, go to main view
        return ret

    def post(self, request, *args, **kwargs):
        """ Handle the many possibilities of the post request """
        self.object = self.get_object()
        self.customer = Customer.objects.filter(user__id=self.kwargs['user_id']).first()
        self.refill_form = None
        if ((self.object.type != "BAR" and not request.user.is_authenticated()) or
                (self.object.type == "BAR" and
                len(self.object.get_barmen_list()) < 1)): # Check that at least one barman is logged in
            return self.cancel(request)
        if self.object.type == "BAR" and not ('counter_token' in self.request.session.keys() and
                self.request.session['counter_token'] == self.object.token): # Also check the token to avoid the bar to be stolen
            return HttpResponseRedirect(reverse_lazy('counter:details', args=self.args,
                kwargs={'counter_id': self.object.id})+'?bad_location')
        if 'basket' not in request.session.keys():
            request.session['basket'] = {}
            request.session['basket_total'] = 0
        request.session['not_enough'] = False # Reset every variable
        request.session['too_young'] = False
        request.session['not_allowed'] = False
        request.session['no_age'] = False
        if self.object.type != "BAR":
            self.operator = request.user
        elif self.is_barman_price():
            self.operator = self.customer.user
        else:
            self.operator = self.object.get_random_barman()

        if 'add_product' in request.POST['action']:
            self.add_product(request)
        elif 'del_product' in request.POST['action']:
            self.del_product(request)
        elif 'refill' in request.POST['action']:
            self.refill(request)
        elif 'code' in request.POST['action']:
            return self.parse_code(request)
        elif 'cancel' in request.POST['action']:
            return self.cancel(request)
        elif 'finish' in request.POST['action']:
            return self.finish(request)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def is_barman_price(self):
        if self.object.type == "BAR" and self.customer.user.id in [s.id for s in self.object.get_barmen_list()]:
            return True
        else:
            return False

    def get_product(self, pid):
        return Product.objects.filter(pk=int(pid)).first()

    def get_price(self, pid):
        p = self.get_product(pid)
        if self.is_barman_price():
            price = p.special_selling_price
        else:
            price = p.selling_price
        return price

    def sum_basket(self, request):
        total = 0
        for pid,infos in request.session['basket'].items():
            total += infos['price'] * infos['qty']
        return total / 100

    def get_total_quantity_for_pid(self, request, pid):
        pid = str(pid)
        try:
            return request.session['basket'][pid]['qty'] + request.session['basket'][pid]['bonus_qty']
        except:
            return 0

    def add_product(self, request, q = 1, p=None):
        """
        Add a product to the basket
        q is the quantity passed as integer
        p is the product id, passed as an integer
        """
        pid = p or request.POST['product_id']
        pid = str(pid)
        price = self.get_price(pid)
        total = self.sum_basket(request)
        product = self.get_product(pid)
        can_buy = False
        if not product.buying_groups.exists():
            can_buy = True
        else:
            for g in product.buying_groups.all():
                if self.customer.user.is_in_group(g.name):
                    can_buy = True
        if not can_buy:
            request.session['not_allowed'] = True
            return False
        bq = 0 # Bonus quantity, for trays
        if product.tray: # Handle the tray to adjust the quantity q to add and the bonus quantity bq
            total_qty_mod_6 = self.get_total_quantity_for_pid(request, pid) % 6
            bq = int((total_qty_mod_6 + q) / 6) # Integer division
            q -= bq
        if self.customer.amount < (total + q*float(price)): # Check for enough money
            request.session['not_enough'] = True
            return False
        if product.limit_age >= 18 and not self.customer.user.date_of_birth:
            request.session['no_age'] = True
            return False
        if product.limit_age >= 18 and self.customer.user.is_banned_alcohol:
            request.session['not_allowed'] = True
            return False
        if self.customer.user.is_banned_counter:
            request.session['not_allowed'] = True
            return False
        if self.customer.user.date_of_birth and self.customer.user.get_age() < product.limit_age: # Check if affordable
            request.session['too_young'] = True
            return False
        if pid in request.session['basket']: # Add if already in basket
            request.session['basket'][pid]['qty'] += q
            request.session['basket'][pid]['bonus_qty'] += bq
        else: # or create if not
            request.session['basket'][pid] = {'qty': q, 'price': int(price*100), 'bonus_qty': bq}
        request.session.modified = True
        return True

    def del_product(self, request):
        """ Delete a product from the basket """
        pid = str(request.POST['product_id'])
        product = self.get_product(pid)
        if pid in request.session['basket']:
            if product.tray and (self.get_total_quantity_for_pid(request, pid) % 6 == 0) and request.session['basket'][pid]['bonus_qty']:
                request.session['basket'][pid]['bonus_qty'] -= 1
            else:
                request.session['basket'][pid]['qty'] -= 1
            if request.session['basket'][pid]['qty'] <= 0:
                del request.session['basket'][pid]
        else:
            request.session['basket'][pid] = None
        request.session.modified = True

    def parse_code(self, request):
        """Parse the string entered by the barman"""
        string = str(request.POST['code']).upper()
        if string == _("END"):
            return self.finish(request)
        elif string == _("CAN"):
            return self.cancel(request)
        regex = re.compile(r"^((?P<nb>[0-9]+)X)?(?P<code>[A-Z0-9]+)$")
        m = regex.match(string)
        if m is not None:
            nb = m.group('nb')
            code = m.group('code')
            if nb is None:
                nb = 1
            else:
                nb = int(nb)
            p = self.object.products.filter(code=code).first()
            if p is not None:
                while nb > 0 and not self.add_product(request, nb, p.id):
                    nb -= 1
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def finish(self, request):
        """ Finish the click session, and validate the basket """
        with transaction.atomic():
            request.session['last_basket'] = []
            for pid,infos in request.session['basket'].items():
                # This duplicates code for DB optimization (prevent to load many times the same object)
                p = Product.objects.filter(pk=pid).first()
                if self.is_barman_price():
                    uprice = p.special_selling_price
                else:
                    uprice = p.selling_price
                if uprice * infos['qty'] > self.customer.amount:
                    raise DataError(_("You have not enough money to buy all the basket"))
                request.session['last_basket'].append("%d x %s" % (infos['qty']+infos['bonus_qty'], p.name))
                s = Selling(label=p.name, product=p, club=p.club, counter=self.object, unit_price=uprice,
                       quantity=infos['qty'], seller=self.operator, customer=self.customer)
                s.save()
                if infos['bonus_qty']:
                    s = Selling(label=p.name + " (Plateau)", product=p, club=p.club, counter=self.object, unit_price=0,
                           quantity=infos['bonus_qty'], seller=self.operator, customer=self.customer)
                    s.save()
            request.session['last_customer'] = self.customer.user.get_display_name()
            request.session['last_total'] = "%0.2f" % self.sum_basket(request)
            request.session['new_customer_amount'] = str(self.customer.amount)
            del request.session['basket']
            request.session.modified = True
            kwargs = {
                    'counter_id': self.object.id,
                    }
            return HttpResponseRedirect(reverse_lazy('counter:details', args=self.args, kwargs=kwargs))

    def cancel(self, request):
        """ Cancel the click session """
        kwargs = {'counter_id': self.object.id}
        request.session.pop('basket', None)
        return HttpResponseRedirect(reverse_lazy('counter:details', args=self.args, kwargs=kwargs))

    def refill(self, request):
        """Refill the customer's account"""
        form = RefillForm(request.POST)
        if form.is_valid():
            form.instance.counter = self.object
            form.instance.operator = self.operator
            form.instance.customer = self.customer
            form.instance.save()
        else:
            self.refill_form = form

    def get_context_data(self, **kwargs):
        """ Add customer to the context """
        kwargs = super(CounterClick, self).get_context_data(**kwargs)
        kwargs['customer'] = self.customer
        kwargs['basket_total'] = self.sum_basket(self.request)
        kwargs['refill_form'] = self.refill_form or RefillForm()
        kwargs['categories'] = ProductType.objects.all()

        kwargs['rules']= APriori_algorithm.calculate_rules_main(os.path.join(settings.BASE_DIR)+'/counter/stats_data/data_test.dat')
        return kwargs

class CounterLogin(RedirectView):
    """
    Handle the login of a barman

    Logged barmen are stored in the Permanency model
    """
    permanent = False
    def post(self, request, *args, **kwargs):
        """
        Register the logged user as barman for this counter
        """
        self.counter_id = kwargs['counter_id']
        self.counter = Counter.objects.filter(id=kwargs['counter_id']).first()
        form = LoginForm(request, data=request.POST)
        self.errors = []
        if form.is_valid():
            user = User.objects.filter(username=form.cleaned_data['username']).first()
            if user in self.counter.sellers.all() and not user in self.counter.get_barmen_list():
                if len(self.counter.get_barmen_list()) <= 0:
                    self.counter.gen_token()
                    request.session['counter_token'] = self.counter.token
                self.counter.add_barman(user)
            else:
                self.errors += ["sellers"]
        else:
            self.errors += ["credentials"]
        return super(CounterLogin, self).post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('counter:details', args=args, kwargs=kwargs)+"?"+'&'.join(self.errors)

class CounterLogout(RedirectView):
    permanent = False
    def post(self, request, *args, **kwargs):
        """
        Unregister the user from the barman
        """
        self.counter = Counter.objects.filter(id=kwargs['counter_id']).first()
        user = User.objects.filter(id=request.POST['user_id']).first()
        self.counter.del_barman(user)
        return super(CounterLogout, self).post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('counter:details', args=args, kwargs=kwargs)

## Counter admin views

class CounterAdminTabsMixin(TabedViewMixin):
    tabs_title = _("Counter administration")
    list_of_tabs = [
            {
                'url': reverse_lazy('counter:admin_list'),
                'slug': 'counters',
                'name': _("Counters"),
                },
            {
                'url': reverse_lazy('counter:product_list'),
                'slug': 'products',
                'name': _("Products"),
                },
            {
                'url': reverse_lazy('counter:product_list_archived'),
                'slug': 'archive',
                'name': _("Archived products"),
                },
            {
                'url': reverse_lazy('counter:producttype_list'),
                'slug': 'product_types',
                'name': _("Product types"),
                },
            {
                'url': reverse_lazy('counter:cash_summary_list'),
                'slug': 'cash_summary',
                'name': _("Cash register summaries"),
                },
            {
                'url': reverse_lazy('counter:invoices_call'),
                'slug': 'invoices_call',
                'name': _("Invoices call"),
                },
            {
                'url': reverse_lazy('counter:eticket_list'),
                'slug': 'etickets',
                'name': _("Etickets"),
                },
            ]

class CounterListView(CounterAdminTabsMixin, CanViewMixin, ListView):
    """
    A list view for the admins
    """
    model = Counter
    template_name = 'counter/counter_list.jinja'
    current_tab = "counters"

class CounterEditForm(forms.ModelForm):
    class Meta:
        model = Counter
        fields = ['sellers', 'products']
    sellers = make_ajax_field(Counter, 'sellers', 'users', help_text="")
    products = make_ajax_field(Counter, 'products', 'products', help_text="")

class CounterEditView(CounterAdminTabsMixin, CanEditMixin, UpdateView):
    """
    Edit a counter's main informations (for the counter's manager)
    """
    model = Counter
    form_class = CounterEditForm
    pk_url_kwarg = "counter_id"
    template_name = 'core/edit.jinja'
    current_tab = "counters"

    def get_success_url(self):
        return reverse_lazy('counter:admin', kwargs={'counter_id': self.object.id})

class CounterEditPropView(CounterAdminTabsMixin, CanEditPropMixin, UpdateView):
    """
    Edit a counter's main informations (for the counter's admin)
    """
    model = Counter
    form_class = modelform_factory(Counter, fields=['name', 'club', 'type'])
    pk_url_kwarg = "counter_id"
    template_name = 'core/edit.jinja'
    current_tab = "counters"

class CounterCreateView(CounterAdminTabsMixin, CanEditMixin, CreateView):
    """
    Create a counter (for the admins)
    """
    model = Counter
    form_class = modelform_factory(Counter, fields=['name', 'club', 'type', 'products'],
            widgets={'products':CheckboxSelectMultiple})
    template_name = 'core/create.jinja'
    current_tab = "counters"

class CounterDeleteView(CounterAdminTabsMixin, CanEditMixin, DeleteView):
    """
    Delete a counter (for the admins)
    """
    model = Counter
    pk_url_kwarg = "counter_id"
    template_name = 'core/delete_confirm.jinja'
    success_url = reverse_lazy('counter:admin_list')
    current_tab = "counters"

# Product management

class ProductTypeListView(CounterAdminTabsMixin, CanEditPropMixin, ListView):
    """
    A list view for the admins
    """
    model = ProductType
    template_name = 'counter/producttype_list.jinja'
    current_tab = "product_types"

class ProductTypeCreateView(CounterAdminTabsMixin, CanCreateMixin, CreateView):
    """
    A create view for the admins
    """
    model = ProductType
    fields = ['name', 'description', 'icon']
    template_name = 'core/create.jinja'
    current_tab = "products"

class ProductTypeEditView(CounterAdminTabsMixin, CanEditPropMixin, UpdateView):
    """
    An edit view for the admins
    """
    model = ProductType
    template_name = 'core/edit.jinja'
    fields = ['name', 'description', 'icon']
    pk_url_kwarg = "type_id"
    current_tab = "products"

class ProductArchivedListView(CounterAdminTabsMixin, CanEditPropMixin, ListView):
    """
    A list view for the admins
    """
    model = Product
    template_name = 'counter/product_list.jinja'
    queryset = Product.objects.filter(archived=True)
    ordering = ['name']
    current_tab = "archive"

class ProductListView(CounterAdminTabsMixin, CanEditPropMixin, ListView):
    """
    A list view for the admins
    """
    model = Product
    template_name = 'counter/product_list.jinja'
    queryset = Product.objects.filter(archived=False)
    ordering = ['name']
    current_tab = "products"

class ProductEditForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'product_type', 'code', 'parent_product', 'buying_groups', 'purchase_price',
                'selling_price', 'special_selling_price', 'icon', 'club', 'limit_age', 'tray', 'archived']
    parent_product = AutoCompleteSelectField('products', show_help_text=False, label=_("Parent product"), required=False)
    buying_groups = AutoCompleteSelectMultipleField('groups', show_help_text=False, help_text="", label=_("Buying groups"), required=False)
    club = AutoCompleteSelectField('clubs', show_help_text=False)
    counters = AutoCompleteSelectMultipleField('counters', show_help_text=False, help_text="", label=_("Counters"), required=False)

    def __init__(self, *args, **kwargs):
        super(ProductEditForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['counters'].initial = [str(c.id) for c in self.instance.counters.all()]

    def save(self, *args, **kwargs):
        ret = super(ProductEditForm, self).save(*args, **kwargs)
        if self.fields['counters'].initial:
            for cid in self.fields['counters'].initial:
                c = Counter.objects.filter(id=int(cid)).first()
                c.products.remove(self.instance)
                c.save()
        for cid in self.cleaned_data['counters']:
            c = Counter.objects.filter(id=int(cid)).first()
            c.products.add(self.instance)
            c.save()
        return ret

class ProductCreateView(CounterAdminTabsMixin, CanCreateMixin, CreateView):
    """
    A create view for the admins
    """
    model = Product
    form_class = ProductEditForm
    template_name = 'core/create.jinja'
    current_tab = "products"

class ProductEditView(CounterAdminTabsMixin, CanEditPropMixin, UpdateView):
    """
    An edit view for the admins
    """
    model = Product
    form_class = ProductEditForm
    pk_url_kwarg = "product_id"
    template_name = 'core/edit.jinja'
    current_tab = "products"

class RefillingDeleteView(DeleteView):
    """
    Delete a refilling (for the admins)
    """
    model = Refilling
    pk_url_kwarg = "refilling_id"
    template_name = 'core/delete_confirm.jinja'

    def dispatch(self, request, *args, **kwargs):
        """
        We have here a very particular right handling, we can't inherit from CanEditPropMixin
        """
        self.object = self.get_object()
        if (timezone.now() - self.object.date <= timedelta(minutes=settings.SITH_LAST_OPERATIONS_LIMIT) and
                'counter_token' in request.session.keys() and
                request.session['counter_token'] and # check if not null for counters that have no token set
                Counter.objects.filter(token=request.session['counter_token']).exists()):
            self.success_url = reverse('counter:details', kwargs={'counter_id': self.object.counter.id})
            return super(RefillingDeleteView, self).dispatch(request, *args, **kwargs)
        elif self.object.is_owned_by(request.user):
            self.success_url = reverse('core:user_account', kwargs={'user_id': self.object.customer.user.id})
            return super(RefillingDeleteView, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

class SellingDeleteView(DeleteView):
    """
    Delete a selling (for the admins)
    """
    model = Selling
    pk_url_kwarg = "selling_id"
    template_name = 'core/delete_confirm.jinja'

    def dispatch(self, request, *args, **kwargs):
        """
        We have here a very particular right handling, we can't inherit from CanEditPropMixin
        """
        self.object = self.get_object()
        if (timezone.now() - self.object.date <= timedelta(minutes=settings.SITH_LAST_OPERATIONS_LIMIT) and
                'counter_token' in request.session.keys() and
                request.session['counter_token'] and # check if not null for counters that have no token set
                Counter.objects.filter(token=request.session['counter_token']).exists()):
            self.success_url = reverse('counter:details', kwargs={'counter_id': self.object.counter.id})
            return super(SellingDeleteView, self).dispatch(request, *args, **kwargs)
        elif self.object.is_owned_by(request.user):
            self.success_url = reverse('core:user_account', kwargs={'user_id': self.object.customer.user.id})
            return super(SellingDeleteView, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

# Cash register summaries

class CashRegisterSummaryForm(forms.Form):
    """
    Provide the cash summary form
    """
    ten_cents = forms.IntegerField(label=_("10 cents"), required=False)
    twenty_cents = forms.IntegerField(label=_("20 cents"), required=False)
    fifty_cents = forms.IntegerField(label=_("50 cents"), required=False)
    one_euro = forms.IntegerField(label=_("1 euro"), required=False)
    two_euros = forms.IntegerField(label=_("2 euros"), required=False)
    five_euros = forms.IntegerField(label=_("5 euros"), required=False)
    ten_euros = forms.IntegerField(label=_("10 euros"), required=False)
    twenty_euros = forms.IntegerField(label=_("20 euros"), required=False)
    fifty_euros = forms.IntegerField(label=_("50 euros"), required=False)
    hundred_euros = forms.IntegerField(label=_("100 euros"), required=False)
    check_1_value = forms.DecimalField(label=_("Check amount"), required=False)
    check_1_quantity = forms.IntegerField(label=_("Check quantity"), required=False)
    check_2_value = forms.DecimalField(label=_("Check amount"), required=False)
    check_2_quantity = forms.IntegerField(label=_("Check quantity"), required=False)
    check_3_value = forms.DecimalField(label=_("Check amount"), required=False)
    check_3_quantity = forms.IntegerField(label=_("Check quantity"), required=False)
    check_4_value = forms.DecimalField(label=_("Check amount"), required=False)
    check_4_quantity = forms.IntegerField(label=_("Check quantity"), required=False)
    check_5_value = forms.DecimalField(label=_("Check amount"), required=False)
    check_5_quantity = forms.IntegerField(label=_("Check quantity"), required=False)
    comment = forms.CharField(label=_("Comment"), required=False)
    emptied = forms.BooleanField(label=_("Emptied"), required=False)

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        super(CashRegisterSummaryForm, self).__init__(*args, **kwargs)
        if instance:
            self.fields['ten_cents'].initial = instance.ten_cents.quantity if instance.ten_cents else 0
            self.fields['twenty_cents'].initial = instance.twenty_cents.quantity if instance.twenty_cents else 0
            self.fields['fifty_cents'].initial = instance.fifty_cents.quantity if instance.fifty_cents else 0
            self.fields['one_euro'].initial = instance.one_euro.quantity if instance.one_euro else 0
            self.fields['two_euros'].initial = instance.two_euros.quantity if instance.two_euros else 0
            self.fields['five_euros'].initial = instance.five_euros.quantity if instance.five_euros else 0
            self.fields['ten_euros'].initial = instance.ten_euros.quantity if instance.ten_euros else 0
            self.fields['twenty_euros'].initial = instance.twenty_euros.quantity if instance.twenty_euros else 0
            self.fields['fifty_euros'].initial = instance.fifty_euros.quantity if instance.fifty_euros else 0
            self.fields['hundred_euros'].initial = instance.hundred_euros.quantity if instance.hundred_euros else 0
            self.fields['check_1_quantity'].initial = instance.check_1.quantity if instance.check_1 else 0
            self.fields['check_2_quantity'].initial = instance.check_2.quantity if instance.check_2 else 0
            self.fields['check_3_quantity'].initial = instance.check_3.quantity if instance.check_3 else 0
            self.fields['check_4_quantity'].initial = instance.check_4.quantity if instance.check_4 else 0
            self.fields['check_5_quantity'].initial = instance.check_5.quantity if instance.check_5 else 0
            self.fields['check_1_value'].initial = instance.check_1.value if instance.check_1 else 0
            self.fields['check_2_value'].initial = instance.check_2.value if instance.check_2 else 0
            self.fields['check_3_value'].initial = instance.check_3.value if instance.check_3 else 0
            self.fields['check_4_value'].initial = instance.check_4.value if instance.check_4 else 0
            self.fields['check_5_value'].initial = instance.check_5.value if instance.check_5 else 0
            self.fields['comment'].initial = instance.comment
            self.fields['emptied'].initial = instance.emptied
            self.instance = instance
        else:
            self.instance = None

    def save(self, counter=None):
        cd = self.cleaned_data
        summary = self.instance or CashRegisterSummary(
                counter=counter,
                user=counter.get_random_barman(),
                )
        summary.comment = cd['comment']
        summary.emptied = cd['emptied']
        summary.save()
        summary.items.all().delete()
        # Cash
        if cd['ten_cents']: CashRegisterSummaryItem(cash_summary=summary, value=0.1, quantity=cd['ten_cents']).save()
        if cd['twenty_cents']: CashRegisterSummaryItem(cash_summary=summary, value=0.2, quantity=cd['twenty_cents']).save()
        if cd['fifty_cents']: CashRegisterSummaryItem(cash_summary=summary, value=0.5, quantity=cd['fifty_cents']).save()
        if cd['one_euro']: CashRegisterSummaryItem(cash_summary=summary, value=1, quantity=cd['one_euro']).save()
        if cd['two_euros']: CashRegisterSummaryItem(cash_summary=summary, value=2, quantity=cd['two_euros']).save()
        if cd['five_euros']: CashRegisterSummaryItem(cash_summary=summary, value=5, quantity=cd['five_euros']).save()
        if cd['ten_euros']: CashRegisterSummaryItem(cash_summary=summary, value=10, quantity=cd['ten_euros']).save()
        if cd['twenty_euros']: CashRegisterSummaryItem(cash_summary=summary, value=20, quantity=cd['twenty_euros']).save()
        if cd['fifty_euros']: CashRegisterSummaryItem(cash_summary=summary, value=50, quantity=cd['fifty_euros']).save()
        if cd['hundred_euros']: CashRegisterSummaryItem(cash_summary=summary, value=100, quantity=cd['hundred_euros']).save()
        # Checks
        if cd['check_1_quantity']: CashRegisterSummaryItem(cash_summary=summary, value=cd['check_1_value'],
                quantity=cd['check_1_quantity'], check=True).save()
        if cd['check_2_quantity']: CashRegisterSummaryItem(cash_summary=summary, value=cd['check_2_value'],
                quantity=cd['check_2_quantity'], check=True).save()
        if cd['check_3_quantity']: CashRegisterSummaryItem(cash_summary=summary, value=cd['check_3_value'],
                quantity=cd['check_3_quantity'], check=True).save()
        if cd['check_4_quantity']: CashRegisterSummaryItem(cash_summary=summary, value=cd['check_4_value'],
                quantity=cd['check_4_quantity'], check=True).save()
        if cd['check_5_quantity']: CashRegisterSummaryItem(cash_summary=summary, value=cd['check_5_value'],
                quantity=cd['check_5_quantity'], check=True).save()
        if summary.items.count() < 1:
            summary.delete()

class CounterLastOperationsView(CounterTabsMixin, CanViewMixin, DetailView):
    """
    Provide the last operations to allow barmen to delete them
    """
    model = Counter
    pk_url_kwarg = "counter_id"
    template_name = 'counter/last_ops.jinja'
    current_tab = "last_ops"

    def dispatch(self, request, *args, **kwargs):
        """
        We have here again a very particular right handling
        """
        self.object = self.get_object()
        if (self.object.get_barmen_list() and 'counter_token' in request.session.keys() and
            request.session['counter_token'] and # check if not null for counters that have no token set
            Counter.objects.filter(token=request.session['counter_token']).exists()):
            return super(CounterLastOperationsView, self).dispatch(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('counter:details', kwargs={'counter_id': self.object.id})+'?bad_location')

    def get_context_data(self, **kwargs):
        """Add form to the context """
        kwargs = super(CounterLastOperationsView, self).get_context_data(**kwargs)
        threshold = timezone.now() - timedelta(minutes=settings.SITH_LAST_OPERATIONS_LIMIT)
        kwargs['last_refillings'] = self.object.refillings.filter(date__gte=threshold).all()
        kwargs['last_sellings'] = self.object.sellings.filter(date__gte=threshold).all()
        return kwargs

class CounterCashSummaryView(CounterTabsMixin, CanViewMixin, DetailView):
    """
    Provide the cash summary form
    """
    model = Counter
    pk_url_kwarg = "counter_id"
    template_name = 'counter/cash_register_summary.jinja'
    current_tab = "cash_summary"

    def dispatch(self, request, *args, **kwargs):
        """
        We have here again a very particular right handling
        """
        self.object = self.get_object()
        if (self.object.get_barmen_list() and 'counter_token' in request.session.keys() and
            request.session['counter_token'] and # check if not null for counters that have no token set
            Counter.objects.filter(token=request.session['counter_token']).exists()):
            return super(CounterCashSummaryView, self).dispatch(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('counter:details', kwargs={'counter_id': self.object.id})+'?bad_location')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.form = CashRegisterSummaryForm()
        return super(CounterCashSummaryView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.form = CashRegisterSummaryForm(request.POST)
        if self.form.is_valid():
            self.form.save(self.object)
            return HttpResponseRedirect(self.get_success_url())
        return super(CounterCashSummaryView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('counter:details', kwargs={'counter_id': self.object.id})

    def get_context_data(self, **kwargs):
        """ Add form to the context """
        kwargs = super(CounterCashSummaryView, self).get_context_data(**kwargs)
        kwargs['form'] = self.form
        return kwargs

class CounterActivityView(DetailView):
    """
    Show the bar activity
    """
    model = Counter
    pk_url_kwarg = "counter_id"
    template_name = 'counter/activity.jinja'

class CounterStatView(DetailView, CanEditMixin):
    """
    Show the bar stats
    """
    model = Counter
    pk_url_kwarg = "counter_id"
    template_name = 'counter/stats.jinja'

    def get_context_data(self, **kwargs):
        """ Add stats to the context """
        from django.db.models import Sum, Case, When, F, DecimalField
        kwargs = super(CounterStatView, self).get_context_data(**kwargs)
        kwargs['Customer'] = Customer
        kwargs['User'] = User
        semester_start = Subscription.compute_start(d=date.today(), duration=3)
        kwargs['total_sellings_semester'] = Selling.objects.filter(date__gte=semester_start,
                counter=self.object).aggregate(total_sellings_semester=Sum(F('quantity')*F('unit_price'),
                    output_field=CurrencyField()))['total_sellings_semester']
        kwargs['total_sellings'] = Selling.objects.filter(counter=self.object).aggregate(
                    total_sellings=Sum(F('quantity')*F('unit_price'),
                    output_field=CurrencyField()))['total_sellings']
        kwargs['top_semester'] = Selling.objects.values('customer__user').annotate(
                selling_sum=Sum(
                    Case(When(counter=self.object,
                            date__gte=semester_start,
                            unit_price__gt=0,
                        then=F('unit_price')*F('quantity')),
                        output_field=CurrencyField()
                        )
                    )
                ).exclude(selling_sum=None).order_by('-selling_sum').all()[:100]
        kwargs['top'] = Selling.objects.values('customer__user').annotate(
                selling_sum=Sum(
                    Case(When(counter=self.object,
                            unit_price__gt=0,
                        then=F('unit_price')*F('quantity')),
                        output_field=CurrencyField()
                        )
                    )
                ).exclude(selling_sum=None).order_by('-selling_sum').all()[:100]
        kwargs['top_barman'] = Permanency.objects.values('user').annotate(
                perm_sum=Sum(
                    Case(When(counter=self.object,
                            end__gt=datetime(year=1999, month=1, day=1),
                        then=F('end')-F('start')),
                        output_field=models.DateTimeField(auto_now=True)
                        )
                    )
                ).exclude(perm_sum=None).order_by('-perm_sum').all()[:100]
        kwargs['top_barman_semester'] = Permanency.objects.values('user').annotate(
                perm_sum=Sum(
                    Case(When(counter=self.object,
                            start__gt=semester_start,
                            end__gt=datetime(year=1999, month=1, day=1),
                        then=F('end')-F('start')),
                        output_field=models.DateTimeField(auto_now=True)
                        )
                    )
                ).exclude(perm_sum=None).order_by('-perm_sum').all()[:100]

        kwargs['sith_date']=settings.SITH_START_DATE[0]
        kwargs['semester_start']=semester_start

        return kwargs

    def dispatch(self, request, *args, **kwargs):
        try:
            return super(CounterStatView, self).dispatch(request, *args, **kwargs)
        except:
            if (request.user.is_root
                or request.user.is_board_member
                or self.object.is_owned_by(request.user)):
                return super(CanEditMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

class CashSummaryEditView(CanEditPropMixin, CounterAdminTabsMixin, UpdateView):
    """Edit cash summaries"""
    model = CashRegisterSummary
    template_name = 'counter/cash_register_summary.jinja'
    context_object_name = "cashsummary"
    pk_url_kwarg = "cashsummary_id"
    form_class = CashRegisterSummaryForm
    current_tab = "cash_summary"

    def get_success_url(self):
        return reverse('counter:cash_summary_list')

class CashSummaryFormBase(forms.Form):
    begin_date = forms.DateTimeField(['%Y-%m-%d %H:%M:%S'], label=_("Begin date"), required=False, widget=SelectDateTime)
    end_date = forms.DateTimeField(['%Y-%m-%d %H:%M:%S'], label=_("End date"), required=False, widget=SelectDateTime)

class CashSummaryListView(CanEditPropMixin, CounterAdminTabsMixin, ListView):
    """Display a list of cash summaries"""
    model = CashRegisterSummary
    template_name = 'counter/cash_summary_list.jinja'
    context_object_name = "cashsummary_list"
    current_tab = "cash_summary"

    def get_context_data(self, **kwargs):
        """ Add sums to the context """
        kwargs = super(CashSummaryListView, self).get_context_data(**kwargs)
        form = CashSummaryFormBase(self.request.GET)
        kwargs['form'] = form
        kwargs['summaries_sums'] = {}
        kwargs['refilling_sums'] = {}
        for c in Counter.objects.filter(type="BAR").all():
            refillings = Refilling.objects.filter(counter=c)
            cashredistersummaries = CashRegisterSummary.objects.filter(counter=c)
            if form.is_valid() and form.cleaned_data['begin_date']:
                refillings = refillings.filter(date__gte=form.cleaned_data['begin_date'])
                cashredistersummaries = cashredistersummaries.filter(date__gte=form.cleaned_data['begin_date'])
            else:
                last_summary = CashRegisterSummary.objects.filter(counter=c, emptied=True).order_by('-date').first()
                if last_summary:
                    refillings = refillings.filter(date__gt=last_summary.date)
                    cashredistersummaries = cashredistersummaries.filter(date__gt=last_summary.date)
                else:
                    refillings = refillings.filter(date__gte=datetime(year=1994, month=5, day=17, tzinfo=pytz.UTC)) # My birth date should be old enough
                    cashredistersummaries = cashredistersummaries.filter(date__gte=datetime(year=1994, month=5, day=17, tzinfo=pytz.UTC))
            if form.is_valid() and form.cleaned_data['end_date']:
                refillings = refillings.filter(date__lte=form.cleaned_data['end_date'])
                cashredistersummaries = cashredistersummaries.filter(date__lte=form.cleaned_data['end_date'])
            kwargs['summaries_sums'][c.name] = sum([s.get_total() for s in cashredistersummaries.all()])
            kwargs['refilling_sums'][c.name] = sum([s.amount for s in refillings.all()])
        return kwargs

class InvoiceCallView(CounterAdminTabsMixin, TemplateView):
    template_name = 'counter/invoices_call.jinja'
    current_tab = 'invoices_call'

    def get_context_data(self, **kwargs):
        """ Add sums to the context """
        kwargs = super(InvoiceCallView, self).get_context_data(**kwargs)
        kwargs['months'] = Selling.objects.datetimes('date', 'month', order='DESC')
        start_date = None
        end_date = None
        try:
            start_date = datetime.strptime(self.request.GET['month'], '%Y-%m')
        except:
            start_date = datetime(year=timezone.now().year, month=(timezone.now().month+10)%12+1, day=1)
        start_date = start_date.replace(tzinfo=pytz.UTC)
        end_date = (start_date + timedelta(days=32)).replace(day=1, hour=0, minute=0, microsecond=0)
        from django.db.models import Sum, Case, When, F, DecimalField
        kwargs['start_date'] = start_date
        kwargs['sums'] = Selling.objects.values('club__name').annotate(selling_sum=Sum(
            Case(When(date__gte=start_date,
                date__lt=end_date,
                then=F('unit_price')*F('quantity')),
                output_field=CurrencyField()
                )
            )).exclude(selling_sum=None).order_by('-selling_sum')
        return kwargs

class EticketListView(CounterAdminTabsMixin, CanEditPropMixin, ListView):
    """
    A list view for the admins
    """
    model = Eticket
    template_name = 'counter/eticket_list.jinja'
    ordering = ['id']
    current_tab = "etickets"

class EticketForm(forms.ModelForm):
    class Meta:
        model = Eticket
        fields = ['product', 'banner', 'event_title', 'event_date']
        widgets = {
                'event_date': SelectDate,
                }
    product = AutoCompleteSelectField('products', show_help_text=False, label=_("Product"), required=True)

class EticketCreateView(CounterAdminTabsMixin, CanEditPropMixin, CreateView):
    """
    Create an eticket
    """
    model = Eticket
    template_name = 'core/create.jinja'
    form_class = EticketForm
    current_tab = "etickets"

class EticketEditView(CounterAdminTabsMixin, CanEditPropMixin, UpdateView):
    """
    Edit an eticket
    """
    model = Eticket
    template_name = 'core/edit.jinja'
    form_class = EticketForm
    pk_url_kwarg = "eticket_id"
    current_tab = "etickets"

class EticketPDFView(CanViewMixin, DetailView):
    """
    Display the PDF of an eticket
    """
    model = Selling
    pk_url_kwarg = "selling_id"

    def get(self, request, *args, **kwargs):
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        from reportlab.lib.units import cm
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.barcode.qr import QrCodeWidget
        from reportlab.graphics import renderPDF
        self.object = self.get_object()
        eticket = self.object.product.eticket
        user = self.object.customer.user
        code = "%s %s %s %s" % (self.object.customer.user.id, self.object.product.id, self.object.id, self.object.quantity)
        code += " " + eticket.get_hash(code)[:8].upper()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="eticket.pdf"'
        p = canvas.Canvas(response)
        p.setTitle("Eticket")
        im = ImageReader("core/static/core/img/eticket.jpg")
        width, height = im.getSize()
        size = max(width, height)
        width = 8 * cm * width / size
        height = 8 * cm * height / size
        p.drawImage(im, 10 * cm, 25 * cm, width, height)
        if eticket.banner:
            im = ImageReader(eticket.banner)
            width, height = im.getSize()
            size = max(width, height)
            width = 6 * cm * width / size
            height = 6 * cm * height / size
            p.drawImage(im, 1 * cm, 25 * cm, width, height)
        if user.profile_pict:
            im = ImageReader(user.profile_pict.file)
            width, height = im.getSize()
            size = max(width, height)
            width = 150 * width / size
            height = 150 * height / size
            p.drawImage(im, 10.5 * cm - width / 2, 16 * cm, width, height)
        if eticket.event_title:
            p.setFont("Helvetica-Bold", 20)
            p.drawCentredString(10.5 * cm, 23.6 * cm, eticket.event_title)
        if eticket.event_date:
            p.setFont("Helvetica-Bold", 16)
            p.drawCentredString(10.5 * cm, 22.6 * cm, eticket.event_date.strftime("%d %b %Y")) # FIXME with a locale
        p.setFont("Helvetica-Bold", 14)
        p.drawCentredString(10.5 * cm, 15 * cm, "%s : %d %s" % (user.get_display_name(), self.object.quantity, str(_("people(s)"))))
        p.setFont("Courier-Bold", 14)
        qrcode = QrCodeWidget(code)
        bounds = qrcode.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        d = Drawing(260, 260, transform=[260./width, 0, 0, 260./height, 0, 0])
        d.add(qrcode)
        renderPDF.draw(d, p, 10.5 * cm - 130, 6.1 * cm)
        p.drawCentredString(10.5 * cm, 6 * cm, code)

        p.showPage()
        p.save()
        return response


class APriori_algorithm():
    """
    class implementation of the APriori_algorithm
    """

    def get_transactions_from_file(file_name):
        '''returns the transactions from a given file, where the items must be
        separated by spaces.

        :returns transactions: a list of transactions, where each transaction is a
            frozenset containing items
        '''
        try:
            with open(file_name) as f:
                content = f.readlines()
                f.close()
        except IOError as e:
            print('I/O error({0}): {1}'.format(e.errno, e.strerror))
            exit()
        except:
            print('Unexpected error: ', exc_info()[0])
            exit()
        transactions = []
        for line in content:
            transactions.append(frozenset(line.strip().split()))
        return transactions


    def get_formated_results(itemsets_list, rules, transactions):
        '''prints the results of the algorithm according to the standard specified
        in the documentation of the task. The confidence values are first rounded
        and then truncated
        '''
        for idx, itemsets in enumerate(itemsets_list):
            if len(itemsets) == 0:
                continue
            print('Itemsets of size', idx + 1)
            formatted_itemsets = []
            for itemset, freq in itemsets.items():
                support = float(freq) / len(transactions)
                formatted_itemsets.append((','.join(sorted(map(str, itemset))), round(support, 3)))
            sorted_itemsets = sorted(formatted_itemsets, key=lambda tup: (-tup[1], tup[0]))
            for itemset, support in sorted_itemsets:
                print(itemset, '{0:.3f}'.format(support))

            print()

        print('RULES')
        formatted_rules = [(','.join(sorted(map(str, rule[0]))) + ' -> ' + 
            ','.join(sorted(map(str, rule[1]))), round(acc, 3)) for rule, acc in rules]
        sorted_rules = sorted(formatted_rules, key=lambda tup: (-tup[1], tup[0]))
        
        return sorted_rules
        #for rule, acc in sorted_rules:
        #    print(rule, '{0:.3f}'.format(acc))


    def remove_itemsets_without_min_support(itemsets, min_sup, transactions, min_atm):
        '''remove the itemsets that don't have the minimum support and, if given,
        the minimum value for atm
        '''
        to_del=[]
        for itemset, freq in itemsets.items():
            if float(freq) / len(transactions) < min_sup:
                if min_atm is not None and len(itemset) >= 2:
                    mul = 1.0
                    for item in itemset:
                        mul *= itemsets_list[0][frozenset([item])]
                    atm = pow(freq, len(itemset)) / mul
                    if atm < min_atm:
                        to_del.append(itemset)
                if min_atm is None:
                    to_del.append(itemset)
                    
        for i in to_del:
            del itemsets[i]


    def generate_itemsets(itemsets_list, min_sup, transactions, min_atm):
        '''given the trivial itemsets of length 1, this function generates the
        following itemsets using self joins, and then eliminating the itemsets
        without the minimum support

        :param itemsets_list: a list containing only one element which, at this
            stage, is the dictionary of itemsets of length 1
        '''
        try:
            next_candidate_item_sets = APriori_algorithm.self_join(itemsets_list[0])
        except IndexError:
            return
        while(len(next_candidate_item_sets) != 0):
            itemsets_list.append(defaultdict(int))
            for idx, item_set in enumerate(next_candidate_item_sets):
                for transaction in transactions:
                    if item_set.issubset(transaction):
                        itemsets_list[-1][item_set] += 1

            APriori_algorithm.remove_itemsets_without_min_support(itemsets_list[-1], min_sup, transactions, min_atm)
            try:
                next_candidate_item_sets = APriori_algorithm.self_join(itemsets_list[-1])
            except IndexError:
                break


    def build_k_minus_one_members_and_their_occurrences(itemsets, k):
        '''in order to self join the itemsets, they must be sorted in lexical
        order. Then, all the unique sets of k-1 members must be idenfified and
        and the itemsets of length k in which they appear, associated

        :param itemsets: list of itemsets
        :param k: length of the itemsets
        :returns k_minus_one_members_and_occurrences: dictionary where keys are
            k-1 members, and values are itemsets of length k, where the members in
            its key appear
        '''
        k_minus_one_members_and_occurrences = defaultdict(list)
        for itemset in itemsets:
            # small cheat to make a list a hashable type
            k_minus_one_members = ''.join(sorted(itemset)[:k - 1])
            k_minus_one_members_and_occurrences[k_minus_one_members].\
                append(itemset)
        return k_minus_one_members_and_occurrences


    def generate_itemsets_from_kmomo(kmomo):
        '''here we identify pairs with the same first k-1 members and produce a new
        itemset of length k+1. Given the kmomo dictionary, this task is easy as we
        simply generate the combinations of size 2 of the associated itemsets where
        they appear

        :param kmomo: dictionary where keys are k-1 members, and values are
            itemsets of length k, where the members in its key appear
        :returns new_itemsets: list of itemsets containing k+1 members
        '''
        new_itemsets = []
        to_del = []
        for k_minus_one_members, occurrences in kmomo.items():
            if len(occurrences) < 2:
                # delete those k_minus_one_members that have only one occurrence
                to_del.append(k_minus_one_members)
            else:  # generate the new itemsets
                for combination in combinations(occurrences, 2):
                    union = combination[0].union(combination[1])
                    new_itemsets.append(union)

        for k in to_del:
            del kmomo[k]

        return new_itemsets


    def self_join(itemsets):
        '''generates itemsets efficiently by selfjoining the itemsets

        :param itemsets: list of itemsets
        :returns new_itemsets: list of itemsets containing l+1 members
        '''
        itemsets = list(itemsets.keys())  # we are only interested on the itemsets
                                    # themselves, not the frequencies
        k = len(itemsets[0])  # length of the itemsets
        # making sure all the itemsets have the same length
        assert(all(len(itemset) == k for itemset in itemsets))
        kmomo = APriori_algorithm.build_k_minus_one_members_and_their_occurrences(itemsets, k)
        return APriori_algorithm.generate_itemsets_from_kmomo(kmomo)


    def build_one_consequent_rules(itemset, freq, itemsets_list, min_conf):
        '''builds one-consequent rules based on an itemset and its frequency, but
        most importantly, it also generates the accurate consequents that will be
        used to generate the two-consequent rules. In other words "if one or other
        of the single-consequent rules does not hold, there is no point in
        considering the double-consequent one" [Witten et. al., Data mining :
        practical machine learning tools and techniques]

        :param itemset: an itemset
        :param freq: frequency of the above mentioned itemset
        :param itemsets_list: dictionaries of itemsets of all lengths
        '''
        accurate_consequents = []
        rules = []
        for combination in combinations(itemset, 1):
            consequent = frozenset(combination)
            antecedent = itemset - consequent
            ant_len_itemsets = itemsets_list[len(antecedent) - 1]
            conf = float(freq) / ant_len_itemsets[antecedent]
            if conf >= min_conf:
                accurate_consequents.append(consequent)
                rules.append(((antecedent, consequent), conf))
        return accurate_consequents, rules


    def build_n_plus_one_consequent_rules(itemset, freq, accurate_consequents, itemsets_list, min_conf):
        '''similarly to the build_one_consequent_rules method, this one generates
        the n plus one consequent rules, the same way the former method does

        :param itemset: an itemset
        :param freq: frequency of the above mentioned itemset
        :param accurate_consequents: the accurate consequents generated in the
            former method
        :param itemsets_list: dictionaries of itemsets of all lengths
        '''
        rules = []
        consequent_length = 2
        while(len(accurate_consequents) != 0 and
              consequent_length < len(itemset)):
            new_accurate_consequents = []
            for combination in combinations(accurate_consequents, 2):
                consequent = frozenset.union(*combination)
                if len(consequent) != consequent_length:
                    # combined itemsets must share n-1 common items
                    continue
                antecedent = itemset - consequent
                ant_len_itemsets = itemsets_list[len(antecedent) - 1]
                conf = float(freq) / ant_len_itemsets[antecedent]
                if conf >= min_conf:
                    new_accurate_consequents.append(consequent)
                    rules.append(((antecedent, consequent), conf))
            accurate_consequents = new_accurate_consequents
            consequent_length += 1
        return rules


    def generate_rules(itemsets, min_conf, itemsets_list):
        '''
        :param itemsets: itemsets of same lenght to be used for generating subsets
        :param min_conf: minimum confidence
        :param itemsets_list: dictionaries of itemsets of all lengths
        :returns rules: list of rules in the form of
            [((antecedent, consequent), confidence), ...]
        '''
        rules = []
        for itemset, freq in itemsets.items():
            accurate_consequents, new_rules = \
                APriori_algorithm.build_one_consequent_rules(itemset, freq, itemsets_list, min_conf)
            rules += new_rules
            # 2-item-itemsets only produce 1-consequent rules,
            # no need to go further with those
            if len(itemset) <= 2:
                continue

            rules += APriori_algorithm.build_n_plus_one_consequent_rules(itemset, freq, accurate_consequents, itemsets_list, min_conf)
        return list(set(rules))

    def calculate_rules_main(file_name):

        print(file_name)

        if hasattr(settings, 'SITH_MINIMUM_ATM_METRIC'):
            min_atm = settings.SITH_MINIMUM_ATM_METRIC
        else:
            min_atm = None            

        transactions = APriori_algorithm.get_transactions_from_file(file_name)
        itemsets_list = [defaultdict(int)]

        # generate itemsets of length 1
        for transaction in transactions:
            for item in transaction:
                itemsets_list[0][frozenset([item])] += 1
        APriori_algorithm.remove_itemsets_without_min_support(itemsets_list[0], settings.SITH_MINIMUM_SUPPORT, transactions, min_atm)

        # generate itemsets of length > 1
        APriori_algorithm.generate_itemsets(itemsets_list, settings.SITH_MINIMUM_SUPPORT, transactions, min_atm)

        # generating rules
        rules = []
        for itemsets in list(reversed(itemsets_list))[:-1]:
            rules += APriori_algorithm.generate_rules(itemsets, settings.SITH_MINIMUM_CONFIANCE, itemsets_list)

        return APriori_algorithm.get_formated_results(itemsets_list, rules, transactions)
        #return (itemsets_list, rules, transactions)
                

