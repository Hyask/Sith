# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [('subscription', '0001_initial'), ('subscription', '0002_auto_20160830_1719'), ('subscription', '0003_auto_20160902_1914'), ('subscription', '0004_auto_20170821_1849'), ('subscription', '0005_auto_20170821_2054')]

    dependencies = [
        ('core', '0001_squashed_0019_preferences_receive_weekmail'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_type', models.CharField(max_length=255, choices=[('amicale/doceo', 'Amicale/DOCEO member'), ('assidu', 'Assidu member'), ('crous', 'CROUS member'), ('cursus-alternant', 'Alternating cursus'), ('cursus-branche', 'Branch cursus'), ('cursus-tronc-commun', 'Common core cursus'), ('deux-semestres', 'Two semesters'), ('membre-honoraire', 'Honorary member'), ('reseau-ut', 'UT network member'), ('sbarro/esta', 'Sbarro/ESTA member'), ('un-semestre', 'One semester'), ('un-semestre-welcome', 'One semester Welcome Week')], verbose_name='subscription type')),
                ('subscription_start', models.DateField(verbose_name='subscription start')),
                ('subscription_end', models.DateField(verbose_name='subscription end')),
                ('payment_method', models.CharField(max_length=255, choices=[('CHECK', 'Check'), ('CARD', 'Credit card'), ('CASH', 'Cash'), ('EBOUTIC', 'Eboutic'), ('OTHER', 'Other')], verbose_name='payment method')),
                ('location', models.CharField(max_length=20, choices=[('BELFORT', 'Belfort'), ('SEVENANS', 'Sevenans'), ('MONTBELIARD', 'Montbéliard'), ('EBOUTIC', 'Eboutic')], verbose_name='location')),
                ('member', models.ForeignKey(related_name='subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['subscription_start'],
            },
        ),
    ]
