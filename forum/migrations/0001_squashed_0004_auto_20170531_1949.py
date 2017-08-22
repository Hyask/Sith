# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import django.utils.timezone
from django.utils.timezone import utc
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [('forum', '0001_initial'), ('forum', '0002_auto_20170312_1753'), ('forum', '0003_auto_20170510_1754'), ('forum', '0004_auto_20170531_1949')]

    dependencies = [
        ('club', '0001_squashed_0007_auto_20170324_0917'),
        ('core', '0001_squashed_0019_preferences_receive_weekmail'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(verbose_name='name', max_length=64)),
                ('description', models.CharField(verbose_name='description', max_length=256, default='')),
                ('is_category', models.BooleanField(verbose_name='is a category', default=False)),
                ('edit_groups', models.ManyToManyField(related_name='editable_forums', blank=True, to='core.Group', default=[4])),
                ('owner_club', models.ForeignKey(related_name='owned_forums', verbose_name='owner club', to='club.Club', default=1)),
                ('parent', models.ForeignKey(related_name='children', null=True, blank=True, to='forum.Forum')),
                ('view_groups', models.ManyToManyField(related_name='viewable_forums', blank=True, to='core.Group', default=[2])),
            ],
        ),
        migrations.CreateModel(
            name='ForumMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('title', models.CharField(verbose_name='title', blank=True, max_length=64, default='')),
                ('message', models.TextField(verbose_name='message', default='')),
                ('date', models.DateTimeField(verbose_name='date', default=django.utils.timezone.now)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='forum_messages')),
                ('readers', models.ManyToManyField(related_name='read_messages', verbose_name='readers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ForumMessageMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('date', models.DateTimeField(verbose_name='date', default=django.utils.timezone.now)),
                ('action', models.CharField(verbose_name='action', choices=[('EDIT', 'Message edited by'), ('DELETE', 'Message deleted by'), ('UNDELETE', 'Message undeleted by')], max_length=16)),
                ('message', models.ForeignKey(to='forum.ForumMessage', related_name='metas')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='forum_message_metas')),
            ],
        ),
        migrations.CreateModel(
            name='ForumTopic',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('description', models.CharField(verbose_name='description', max_length=256, default='')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='forum_topics')),
                ('forum', models.ForeignKey(to='forum.Forum', related_name='topics')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ForumUserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('last_read_date', models.DateTimeField(verbose_name='last read date', default=datetime.datetime(1999, 1, 1, 0, 0, tzinfo=utc))),
                ('user', models.OneToOneField(related_name='_forum_infos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='forummessage',
            name='topic',
            field=models.ForeignKey(to='forum.ForumTopic', related_name='messages'),
        ),
        migrations.AlterModelOptions(
            name='forum',
            options={'ordering': ['number']},
        ),
        migrations.AddField(
            model_name='forum',
            name='number',
            field=models.IntegerField(verbose_name='number to choose a specific forum ordering', default=1),
        ),
        migrations.AlterField(
            model_name='forum',
            name='edit_groups',
            field=models.ManyToManyField(related_name='editable_forums', blank=True, to='core.Group', default=[331]),
        ),
        migrations.AlterField(
            model_name='forum',
            name='edit_groups',
            field=models.ManyToManyField(related_name='editable_forums', blank=True, to='core.Group', default=[4]),
        ),
        migrations.AlterModelOptions(
            name='forummessage',
            options={'ordering': ['-date']},
        ),
        migrations.AlterModelOptions(
            name='forumtopic',
            options={'ordering': ['-_last_message__date']},
        ),
        migrations.AddField(
            model_name='forum',
            name='_last_message',
            field=models.ForeignKey(related_name='forums_where_its_last', verbose_name='the last message', null=True, to='forum.ForumMessage', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='forum',
            name='_topic_number',
            field=models.IntegerField(verbose_name='number of topics', default=0),
        ),
        migrations.AddField(
            model_name='forummessage',
            name='_deleted',
            field=models.BooleanField(verbose_name='is deleted', default=False),
        ),
        migrations.AddField(
            model_name='forumtopic',
            name='_last_message',
            field=models.ForeignKey(related_name='+', verbose_name='the last message', null=True, to='forum.ForumMessage', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='forumtopic',
            name='_message_number',
            field=models.IntegerField(verbose_name='number of messages', default=0),
        ),
        migrations.AddField(
            model_name='forumtopic',
            name='_title',
            field=models.CharField(verbose_name='title', blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='forum',
            name='description',
            field=models.CharField(verbose_name='description', max_length=512, default=''),
        ),
        migrations.AlterField(
            model_name='forum',
            name='id',
            field=models.AutoField(db_index=True, primary_key=True, serialize=False),
        ),
    ]
