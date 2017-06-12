# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('code', models.CharField(max_length=10)),
                ('formation', models.CharField(max_length=255, choices=[('IMSI', 'POUSSE CARTON'), ('EE', 'Powering'), ('GMC', 'Mechanical and Conception'), ('EDIM', 'Mechanical and Conception'), ('TC', 'Common Core'), ('INFO', 'Computer Science')], verbose_name='Formation type')),
                ('category', models.CharField(max_length=255, choices=[('EC', 'Expression and Communication'), ('OM', 'Organize and Manage'), ('TM', 'Tech and Method'), ('CS', 'Science Knowledge'), ('QC', 'Ask and Create')], verbose_name='Category')),
                ('semester', models.CharField(max_length=60, choices=[('S', 'Spring'), ('A', 'Autumn')], verbose_name='Semester')),
            ],
        ),
        migrations.CreateModel(
            name='PedaComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(default='', verbose_name='content')),
                ('is_moderated', models.BooleanField(default=False, verbose_name='is the comment moderated')),
                ('comment_date', models.DateField(default=datetime.date.today, verbose_name='comment date')),
                ('interest', models.IntegerField(default=5, verbose_name='Interest')),
                ('utility', models.IntegerField(default=5, verbose_name='Utility')),
                ('work', models.IntegerField(default=5, verbose_name='Work')),
                ('teaching', models.IntegerField(default=5, verbose_name='Teaching')),
                ('global_mark', models.IntegerField(default=5, verbose_name='Global mark')),
                ('author', models.ForeignKey(related_name='given_comments', to=settings.AUTH_USER_MODEL)),
                ('uv', models.ForeignKey(related_name='received_comments', to='pedagogy.Course', verbose_name='subject')),
            ],
            options={
                'ordering': ('interest', 'utility', 'work', 'teaching'),
            },
        ),
    ]
