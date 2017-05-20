# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_auto_20170510_1754'),
    ]

    operations = [
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
            field=models.ForeignKey(related_name='forums_where_its_last', to='forum.ForumMessage', null=True, verbose_name='the last message'),
        ),
        migrations.AddField(
            model_name='forum',
            name='_topic_number',
            field=models.IntegerField(default=0, verbose_name='number of topics'),
        ),
        migrations.AddField(
            model_name='forummessage',
            name='_deleted',
            field=models.BooleanField(default=False, verbose_name='is deleted'),
        ),
        migrations.AddField(
            model_name='forumtopic',
            name='_last_message',
            field=models.ForeignKey(related_name='+', to='forum.ForumMessage', null=True, verbose_name='the last message'),
        ),
        migrations.AddField(
            model_name='forumtopic',
            name='_title',
            field=models.CharField(max_length=64, blank=True, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='forum',
            name='description',
            field=models.CharField(max_length=512, default='', verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='forum',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False, db_index=True),
        ),
    ]