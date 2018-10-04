from django.db import models
from ordered_model.models import OrderedModel
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from core.models import User, Group


class Election(models.Model):
    """
    This class allows to create a new election
    """

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), null=True, blank=True)
    start_candidature = models.DateTimeField(_("start candidature"), blank=False)
    end_candidature = models.DateTimeField(_("end candidature"), blank=False)
    start_date = models.DateTimeField(_("start date"), blank=False)
    end_date = models.DateTimeField(_("end date"), blank=False)

    edit_groups = models.ManyToManyField(
        Group,
        related_name="editable_elections",
        verbose_name=_("edit groups"),
        blank=True,
    )

    view_groups = models.ManyToManyField(
        Group,
        related_name="viewable_elections",
        verbose_name=_("view groups"),
        blank=True,
    )

    vote_groups = models.ManyToManyField(
        Group,
        related_name="votable_elections",
        verbose_name=_("vote groups"),
        blank=True,
    )

    candidature_groups = models.ManyToManyField(
        Group,
        related_name="candidate_elections",
        verbose_name=_("candidature groups"),
        blank=True,
    )

    voters = models.ManyToManyField(
        User, verbose_name=("voters"), related_name="voted_elections"
    )
    archived = models.BooleanField(_("archived"), default=False)

    def __str__(self):
        return self.title

    @property
    def is_vote_active(self):
        now = timezone.now()
        return bool(now <= self.end_date and now >= self.start_date)

    @property
    def is_vote_finished(self):
        return bool(timezone.now() > self.end_date)

    @property
    def is_candidature_active(self):
        now = timezone.now()
        return bool(now <= self.end_candidature and now >= self.start_candidature)

    @property
    def is_vote_editable(self):
        return bool(timezone.now() <= self.end_candidature)

    def can_candidate(self, user):
        for group in self.candidature_groups.all():
            if user.is_in_group(group):
                return True
        return False

    def can_vote(self, user):
        if not self.is_vote_active or self.has_voted(user):
            return False
        for group in self.vote_groups.all():
            if user.is_in_group(group):
                return True
        return False

    def has_voted(self, user):
        return self.voters.filter(id=user.id).exists()

    @property
    def results(self):
        results = {}
        total_vote = self.voters.count()
        for role in self.roles.all():
            results[role.title] = role.results(total_vote)
        return results

    def delete(self):
        for election_list in self.election_lists.all():
            election_list.delete()
        super(Election, self).delete()

    # Permissions


class Role(OrderedModel):
    """
    This class allows to create a new role avaliable for a candidature
    """

    election = models.ForeignKey(
        Election, related_name="roles", verbose_name=_("election")
    )
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), null=True, blank=True)
    max_choice = models.IntegerField(_("max choice"), default=1)

    def results(self, total_vote):
        results = {}
        total_vote *= self.max_choice
        non_blank = 0
        for candidature in self.candidatures.all():
            cand_results = {}
            cand_results["vote"] = self.votes.filter(candidature=candidature).count()
            if total_vote == 0:
                cand_results["percent"] = 0
            else:
                cand_results["percent"] = cand_results["vote"] * 100 / total_vote
            non_blank += cand_results["vote"]
            results[candidature.user.username] = cand_results
        results["total vote"] = total_vote
        if total_vote == 0:
            results["blank vote"] = {"vote": 0, "percent": 0}
        else:
            results["blank vote"] = {
                "vote": total_vote - non_blank,
                "percent": (total_vote - non_blank) * 100 / total_vote,
            }
        return results

    @property
    def edit_groups(self):
        return self.election.edit_groups

    def __str__(self):
        return ("%s : %s") % (self.election.title, self.title)


class ElectionList(models.Model):
    """
    To allow per list vote
    """

    title = models.CharField(_("title"), max_length=255)
    election = models.ForeignKey(
        Election, related_name="election_lists", verbose_name=_("election")
    )

    def can_be_edited_by(self, user):
        return user.can_edit(self.election)

    def delete(self):
        for candidature in self.candidatures.all():
            candidature.delete()
        super(ElectionList, self).delete()

    def __str__(self):
        return self.title


class Candidature(models.Model):
    """
    This class is a component of responsability
    """

    role = models.ForeignKey(Role, related_name="candidatures", verbose_name=_("role"))
    user = models.ForeignKey(
        User, verbose_name=_("user"), related_name="candidates", blank=True
    )
    program = models.TextField(_("description"), null=True, blank=True)
    election_list = models.ForeignKey(
        ElectionList, related_name="candidatures", verbose_name=_("election list")
    )

    def delete(self):
        for vote in self.votes.all():
            vote.delete()
        super(Candidature, self).delete()

    def can_be_edited_by(self, user):
        return (user == self.user) or user.can_edit(self.role.election)

    def __str__(self):
        return "%s : %s" % (self.role.title, self.user.username)


class Vote(models.Model):
    """
    This class allows to vote for candidates
    """

    role = models.ForeignKey(Role, related_name="votes", verbose_name=_("role"))
    candidature = models.ManyToManyField(
        Candidature, related_name="votes", verbose_name=_("candidature")
    )

    def __str__(self):
        return "Vote"
