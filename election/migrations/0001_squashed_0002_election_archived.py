# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [('election', '0001_initial'), ('election', '0002_election_archived')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_squashed_0019_preferences_receive_weekmail'),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidature',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('program', models.TextField(null=True, blank=True, verbose_name='description')),
            ],
        ),
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('description', models.TextField(null=True, blank=True, verbose_name='description')),
                ('start_candidature', models.DateTimeField(verbose_name='start candidature')),
                ('end_candidature', models.DateTimeField(verbose_name='end candidature')),
                ('start_date', models.DateTimeField(verbose_name='start date')),
                ('end_date', models.DateTimeField(verbose_name='end date')),
                ('candidature_groups', models.ManyToManyField(to='core.Group', blank=True, verbose_name='candidature groups', related_name='candidate_elections')),
                ('edit_groups', models.ManyToManyField(to='core.Group', blank=True, verbose_name='edit groups', related_name='editable_elections')),
                ('view_groups', models.ManyToManyField(to='core.Group', blank=True, verbose_name='view groups', related_name='viewable_elections')),
                ('vote_groups', models.ManyToManyField(to='core.Group', blank=True, verbose_name='vote groups', related_name='votable_elections')),
                ('voters', models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='voted_elections', verbose_name='voters')),
            ],
        ),
        migrations.CreateModel(
            name='ElectionList',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('election', models.ForeignKey(to='election.Election', related_name='election_lists', verbose_name='election')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('description', models.TextField(null=True, blank=True, verbose_name='description')),
                ('max_choice', models.IntegerField(verbose_name='max choice', default=1)),
                ('election', models.ForeignKey(to='election.Election', related_name='roles', verbose_name='election')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('candidature', models.ManyToManyField(to='election.Candidature', related_name='votes', verbose_name='candidature')),
                ('role', models.ForeignKey(to='election.Role', related_name='votes', verbose_name='role')),
            ],
        ),
        migrations.AddField(
            model_name='candidature',
            name='election_list',
            field=models.ForeignKey(to='election.ElectionList', related_name='candidatures', verbose_name='election list'),
        ),
        migrations.AddField(
            model_name='candidature',
            name='role',
            field=models.ForeignKey(to='election.Role', related_name='candidatures', verbose_name='role'),
        ),
        migrations.AddField(
            model_name='candidature',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, verbose_name='user', related_name='candidates'),
        ),
        migrations.AddField(
            model_name='election',
            name='archived',
            field=models.BooleanField(verbose_name='archived', default=False),
        ),
    ]
