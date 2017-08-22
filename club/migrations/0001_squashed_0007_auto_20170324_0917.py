# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import django.core.validators
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [('club', '0001_initial'), ('club', '0002_auto_20160824_2152'), ('club', '0003_auto_20160902_2042'), ('club', '0004_auto_20160915_1057'), ('club', '0005_auto_20161120_1149'), ('club', '0006_auto_20161229_0040'), ('club', '0007_auto_20170324_0917')]

    dependencies = [
        ('core', '0001_squashed_0019_preferences_receive_weekmail'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=64)),
                ('unix_name', models.CharField(validators=[django.core.validators.RegexValidator('^[a-z0-9][a-z0-9._-]*[a-z0-9]$', 'Enter a valid unix name. This value may contain only letters, numbers ./-/_ characters.')], unique=True, error_messages={'unique': 'A club with that unix name already exists.'}, max_length=30, verbose_name='unix name')),
                ('address', models.CharField(verbose_name='address', max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('start_date', models.DateField(verbose_name='start date', default=django.utils.timezone.now)),
                ('end_date', models.DateField(verbose_name='end date', null=True, blank=True)),
                ('role', models.IntegerField(verbose_name='role', choices=[(0, 'Curious'), (1, 'Active member'), (2, 'Board member'), (3, 'IT supervisor'), (4, 'Secretary'), (5, 'Communication supervisor'), (7, 'Treasurer'), (9, 'Vice-President'), (10, 'President')], default=0)),
                ('description', models.CharField(verbose_name='description', max_length=128, blank=True)),
                ('club', models.ForeignKey(verbose_name='club', to='club.Club', related_name='members')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, related_name='memberships')),
            ],
        ),
        migrations.AddField(
            model_name='club',
            name='edit_groups',
            field=models.ManyToManyField(related_name='editable_club', to='core.Group', blank=True),
        ),
        migrations.AddField(
            model_name='club',
            name='home',
            field=models.OneToOneField(verbose_name='home', related_name='home_of_club', on_delete=django.db.models.deletion.SET_NULL, to='core.SithFile', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='club',
            name='owner_group',
            field=models.ForeignKey(default=1, to='core.Group', related_name='owned_club'),
        ),
        migrations.AddField(
            model_name='club',
            name='parent',
            field=models.ForeignKey(related_name='children', to='club.Club', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='club',
            name='view_groups',
            field=models.ManyToManyField(related_name='viewable_club', to='core.Group', blank=True),
        ),
        migrations.AlterModelOptions(
            name='club',
            options={'ordering': ['name', 'unix_name']},
        ),
    ]
