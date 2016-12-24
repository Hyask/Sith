from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, RedirectView
from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy as _
from django.forms.models import modelform_factory
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, ImproperlyConfigured
from django.forms import CheckboxSelectMultiple
from django.utils import timezone
from django.conf import settings
from django import forms

from core.views import CanViewMixin, CanEditMixin, CanEditPropMixin, CanCreateMixin
from django.db.models.query import QuerySet
from django.views.generic.edit import FormMixin
from core.views.forms import SelectDateTime
from election.models import Election, Role, Candidature, ElectionList, Vote

from ajax_select.fields import AutoCompleteSelectField


# Custom form field

class LimitedCheckboxField(forms.ModelMultipleChoiceField):
    """
        Used to replace ModelMultipleChoiceField but with
        automatic backend verification
    """
    def __init__(self, queryset, max_choice, required=True, widget=None, label=None,
                 initial=None, help_text='', *args, **kwargs):
        self.max_choice = max_choice
        widget = forms.CheckboxSelectMultiple()
        super(LimitedCheckboxField, self).__init__(queryset, None, required, widget, label,
                                           initial, help_text, *args, **kwargs)

    def clean(self, value):
        qs = super(LimitedCheckboxField, self).clean(value)
        self.validate(qs)
        return qs

    def validate(self, qs):
        if qs.count() > self.max_choice:
            raise forms.ValidationError(_("You have selected too much candidates."), code='invalid')


# Forms


class CandidateForm(forms.ModelForm):
    """ Form to candidate """
    class Meta:
        model = Candidature
        fields = ['user', 'role', 'program', 'election_list']
        widgets = {
            'program': forms.Textarea
        }

    user = AutoCompleteSelectField('users', label=_('User to candidate'), help_text=None, required=True)

    def __init__(self, *args, **kwargs):
        election_id = kwargs.pop('election_id', None)
        can_edit = kwargs.pop('can_edit', False)
        super(CandidateForm, self).__init__(*args, **kwargs)
        if election_id:
            self.fields['role'].queryset = Role.objects.filter(election__id=election_id).all()
            self.fields['election_list'].queryset = ElectionList.objects.filter(election__id=election_id).all()
        if not can_edit:
            self.fields['user'].widget = forms.HiddenInput()


class VoteForm(forms.Form):
    def __init__(self, election, user, *args, **kwargs):
        super(VoteForm, self).__init__(*args, **kwargs)
        if not election.has_voted(user):
            for role in election.roles.all():
                cand = role.candidatures
                if role.max_choice > 1:
                    self.fields[role.title] = LimitedCheckboxField(cand, role.max_choice, required=False)
                else:
                    self.fields[role.title] = forms.ModelChoiceField(cand, required=False,
                                                                     widget=forms.RadioSelect(), empty_label=_("Blank vote"))


class RoleForm(forms.ModelForm):
    """ Form for creating a role """
    class Meta:
        model = Role
        fields = ['title', 'election', 'description', 'max_choice']

    def clean(self):
        cleaned_data = super(RoleForm, self).clean()
        title = cleaned_data.get('title')
        election = cleaned_data.get('election')
        if Role.objects.filter(title=title, election=election).exists():
            raise forms.ValidationError(_("This role already exists for this election"), code='invalid')


# Display elections


class ElectionsListView(CanViewMixin, ListView):
    """
    A list with all responsabilities and their candidates
    """
    model = Election
    template_name = 'election/election_list.jinja'

    def get_queryset(self):
        qs = super(ElectionsListView, self).get_queryset()
        today = timezone.now()
        qs = qs.filter(end_date__gte=today, start_date__lte=today)
        return qs


class ElectionDetailView(CanViewMixin, DetailView):
    """
    Details an election responsability by responsability
    """
    model = Election
    template_name = 'election/election_detail.jinja'
    pk_url_kwarg = "election_id"

    def get_context_data(self, **kwargs):
        """ Add additionnal data to the template """
        kwargs = super(ElectionDetailView, self).get_context_data(**kwargs)
        kwargs['election_form'] = VoteForm(self.object, self.request.user)
        kwargs['election_results'] = self.object.results
        return kwargs


# Form view

class VoteFormView(CanCreateMixin, FormView):
    """
    Alows users to vote
    """
    form_class = VoteForm
    template_name = 'election/election_detail.jinja'

    def dispatch(self, request, *arg, **kwargs):
        self.election = get_object_or_404(Election, pk=kwargs['election_id'])
        return super(VoteFormView, self).dispatch(request, *arg, **kwargs)

    def vote(self, election_data):
        for role_title in election_data.keys():
            # If we have a multiple choice field
            if isinstance(election_data[role_title], QuerySet):
                if election_data[role_title].count() > 0:
                    vote = Vote(role=election_data[role_title].first().role)
                    vote.save()
                for el in election_data[role_title]:
                    vote.candidature.add(el)
            # If we have a single choice
            elif election_data[role_title] is not None:
                vote = Vote(role=election_data[role_title].role)
                vote.save()
                vote.candidature.add(election_data[role_title])
        self.election.voters.add(self.request.user)

    def get_form_kwargs(self):
        kwargs = super(VoteFormView, self).get_form_kwargs()
        kwargs['election'] = self.election
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
            Verify that the user is part in a vote group
        """
        data = form.clean()
        res = super(FormView, self).form_valid(form)
        for grp in self.election.vote_groups.all():
            if self.request.user.is_in_group(grp):
                self.vote(data)
                return res
        return res

    def get_success_url(self, **kwargs):
        return reverse_lazy('election:detail', kwargs={'election_id': self.election.id})

    def get_context_data(self, **kwargs):
        """ Add additionnal data to the template """
        kwargs = super(VoteFormView, self).get_context_data(**kwargs)
        kwargs['object'] = self.election
        kwargs['election'] = self.election
        kwargs['election_form'] = self.get_form()
        return kwargs


# Create views

class CandidatureCreateView(CanCreateMixin, CreateView):
    """
    View dedicated to a cundidature creation
    """
    form_class = CandidateForm
    model = Candidature
    template_name = 'election/candidate_form.jinja'

    def dispatch(self, request, *arg, **kwargs):
        self.election = get_object_or_404(Election, pk=kwargs['election_id'])
        return super(CandidatureCreateView, self).dispatch(request, *arg, **kwargs)

    def get_initial(self):
        init = {}
        self.can_edit = self.request.user.can_edit(self.election)
        init['user'] = self.request.user.id
        return init

    def get_form_kwargs(self):
        kwargs = super(CandidatureCreateView, self).get_form_kwargs()
        kwargs['election_id'] = self.election.id
        kwargs['can_edit'] = self.can_edit
        return kwargs

    def form_valid(self, form):
        """
            Verify that the selected user is in candidate group
        """
        obj = form.instance
        obj.election = Election.objects.get(id=self.election.id)
        if(obj.election.can_candidate(obj.user)) and (obj.user == self.request.user or self.can_edit):
            return super(CreateView, self).form_valid(form)
        raise PermissionDenied

    def get_context_data(self, **kwargs):
        kwargs = super(CandidatureCreateView, self).get_context_data(**kwargs)
        kwargs['election'] = self.election
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse_lazy('election:detail', kwargs={'election_id': self.election.id})


class ElectionCreateView(CanCreateMixin, CreateView):
    model = Election
    form_class = modelform_factory(Election,
        fields=['title', 'description', 'start_candidature', 'end_candidature', 'start_date', 'end_date',
                'edit_groups', 'view_groups', 'vote_groups', 'candidature_groups'],
        widgets={
            'edit_groups': CheckboxSelectMultiple,
            'view_groups': CheckboxSelectMultiple,
            'edit_groups': CheckboxSelectMultiple,
            'vote_groups': CheckboxSelectMultiple,
            'candidature_groups': CheckboxSelectMultiple,
            'start_date': SelectDateTime,
            'end_date': SelectDateTime,
            'start_candidature': SelectDateTime,
            'end_candidature': SelectDateTime,
        })
    template_name = 'core/page_prop.jinja'

    def form_valid(self, form):
        """
            Verify that the user is suscribed
        """
        res = super(CreateView, self).form_valid(form)
        if self.request.user.is_subscribed():
            return res

    def get_success_url(self, **kwargs):
        return reverse_lazy('election:detail', kwargs={'election_id': self.object.id})


class RoleCreateView(CanCreateMixin, CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'core/page_prop.jinja'

    def form_valid(self, form):
        """
            Verify that the user can edit proprely
        """
        obj = form.instance
        if obj.election:
            for grp in obj.election.edit_groups.all():
                if self.request.user.is_in_group(grp):
                    return super(CreateView, self).form_valid(form)
        raise PermissionDenied

    def get_success_url(self, **kwargs):
        return reverse_lazy('election:detail', kwargs={'election_id': self.object.election.id})


class ElectionListCreateView(CanCreateMixin, CreateView):
    model = ElectionList
    form_class = modelform_factory(ElectionList,
        fields=['title', 'election'])
    template_name = 'core/page_prop.jinja'

    def form_valid(self, form):
        """
            Verify that the user can vote on this election
        """
        obj = form.instance
        if obj.election:
            for grp in obj.election.candidature_groups.all():
                if self.request.user.is_in_group(grp):
                    return super(CreateView, self).form_valid(form)
            for grp in obj.election.edit_groups.all():
                if self.request.user.is_in_group(grp):
                    return super(CreateView, self).form_valid(form)
        raise PermissionDenied

    def get_success_url(self, **kwargs):
        return reverse_lazy('election:detail', kwargs={'election_id': self.object.election.id})
