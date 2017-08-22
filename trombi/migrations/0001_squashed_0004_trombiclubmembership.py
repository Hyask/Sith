# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('trombi', '0001_initial'), ('trombi', '0002_trombi_show_profiles'), ('trombi', '0003_trombicomment_is_moderated'), ('trombi', '0004_trombiclubmembership')]

    dependencies = [
        ('club', '0001_squashed_0007_auto_20170324_0917'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Trombi',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('subscription_deadline', models.DateField(default=datetime.date.today, verbose_name='subscription deadline', help_text='Before this date, users are allowed to subscribe to this Trombi. After this date, users subscribed will be allowed to comment on each other.')),
                ('comments_deadline', models.DateField(default=datetime.date.today, verbose_name='comments deadline', help_text="After this date, users won't be able to make comments anymore.")),
                ('max_chars', models.IntegerField(default=400, verbose_name='maximum characters', help_text='Maximum number of characters allowed in a comment.')),
                ('club', models.OneToOneField(related_name='trombi', to='club.Club')),
            ],
        ),
        migrations.CreateModel(
            name='TrombiComment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('content', models.TextField(default='', verbose_name='content')),
            ],
        ),
        migrations.CreateModel(
            name='TrombiUser',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('profile_pict', models.ImageField(verbose_name='profile pict', blank=True, help_text='The profile picture you want in the trombi (warning: this picture may be published)', upload_to='trombi', null=True)),
                ('scrub_pict', models.ImageField(verbose_name='scrub pict', blank=True, help_text='The scrub picture you want in the trombi (warning: this picture may be published)', upload_to='trombi', null=True)),
                ('trombi', models.ForeignKey(verbose_name='trombi', related_name='users', blank=True, to='trombi.Trombi', null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('user', models.OneToOneField(verbose_name='trombi user', related_name='trombi_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='trombicomment',
            name='author',
            field=models.ForeignKey(verbose_name='author', related_name='given_comments', to='trombi.TrombiUser'),
        ),
        migrations.AddField(
            model_name='trombicomment',
            name='target',
            field=models.ForeignKey(verbose_name='target', related_name='received_comments', to='trombi.TrombiUser'),
        ),
        migrations.AddField(
            model_name='trombi',
            name='show_profiles',
            field=models.BooleanField(default=True, verbose_name='show users profiles to each other'),
        ),
        migrations.AddField(
            model_name='trombicomment',
            name='is_moderated',
            field=models.BooleanField(default=False, verbose_name='is the comment moderated'),
        ),
        migrations.CreateModel(
            name='TrombiClubMembership',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('club', models.CharField(default='', verbose_name='club', max_length=32)),
                ('role', models.CharField(default='', verbose_name='role', max_length=64)),
                ('start', models.CharField(default='', verbose_name='start', max_length=16)),
                ('end', models.CharField(default='', verbose_name='end', max_length=16)),
                ('user', models.ForeignKey(verbose_name='user', related_name='memberships', to='trombi.TrombiUser')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
