# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import accounting.models


class Migration(migrations.Migration):

    replaces = [('counter', '0001_initial'), ('counter', '0002_auto_20160826_1342'), ('counter', '0003_permanency_activity'), ('counter', '0004_auto_20160826_1907'), ('counter', '0005_auto_20160826_2330'), ('counter', '0006_auto_20160831_1304'), ('counter', '0007_product_archived'), ('counter', '0008_counter_token'), ('counter', '0009_eticket'), ('counter', '0010_auto_20161003_1900'), ('counter', '0011_auto_20161004_2039'), ('counter', '0012_auto_20170515_2202')]

    dependencies = [
        ('club', '0001_squashed_0007_auto_20170324_0917'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscription', '0001_squashed_0005_auto_20170821_2054'),
        ('core', '0001_squashed_0019_preferences_receive_weekmail'),
    ]

    operations = [
        migrations.CreateModel(
            name='Counter',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(verbose_name='name', max_length=30)),
                ('type', models.CharField(verbose_name='counter type', choices=[('BAR', 'Bar'), ('OFFICE', 'Office'), ('EBOUTIC', 'Eboutic')], max_length=255)),
                ('club', models.ForeignKey(to='club.Club', related_name='counters')),
                ('edit_groups', models.ManyToManyField(to='core.Group', related_name='editable_counters', blank=True)),
            ],
            options={
                'verbose_name': 'counter',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, primary_key=True, serialize=False)),
                ('account_id', models.CharField(verbose_name='account id', unique=True, max_length=10)),
                ('amount', accounting.models.CurrencyField(decimal_places=2, verbose_name='amount', max_digits=12)),
            ],
            options={
                'verbose_name_plural': 'customers',
                'verbose_name': 'customer',
                'ordering': ['account_id'],
            },
        ),
        migrations.CreateModel(
            name='Permanency',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('start', models.DateTimeField(verbose_name='start date')),
                ('end', models.DateTimeField(db_index=True, null=True, verbose_name='end date')),
                ('counter', models.ForeignKey(verbose_name='counter', related_name='permanencies', to='counter.Counter')),
                ('user', models.ForeignKey(verbose_name='user', related_name='permanencies', to=settings.AUTH_USER_MODEL)),
                ('activity', models.DateTimeField(auto_now=True, verbose_name='last activity date')),
            ],
            options={
                'verbose_name': 'permanency',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(verbose_name='name', max_length=64)),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('code', models.CharField(verbose_name='code', max_length=16, blank=True)),
                ('purchase_price', accounting.models.CurrencyField(decimal_places=2, verbose_name='purchase price', max_digits=12)),
                ('selling_price', accounting.models.CurrencyField(decimal_places=2, verbose_name='selling price', max_digits=12)),
                ('special_selling_price', accounting.models.CurrencyField(decimal_places=2, verbose_name='special selling price', max_digits=12)),
                ('icon', models.ImageField(null=True, verbose_name='icon', upload_to='products', blank=True)),
                ('limit_age', models.IntegerField(verbose_name='limit age', default=0)),
                ('tray', models.BooleanField(verbose_name='tray price', default=False)),
                ('buying_groups', models.ManyToManyField(verbose_name='buying groups', to='core.Group', related_name='products')),
                ('club', models.ForeignKey(verbose_name='club', related_name='products', to='club.Club')),
                ('parent_product', models.ForeignKey(verbose_name='parent product', related_name='children_products', blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='counter.Product')),
            ],
            options={
                'verbose_name': 'product',
            },
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(verbose_name='name', max_length=30)),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('icon', models.ImageField(null=True, upload_to='products', blank=True)),
            ],
            options={
                'verbose_name': 'product type',
            },
        ),
        migrations.CreateModel(
            name='Refilling',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('amount', accounting.models.CurrencyField(decimal_places=2, verbose_name='amount', max_digits=12)),
                ('date', models.DateTimeField(verbose_name='date')),
                ('payment_method', models.CharField(verbose_name='payment method', default='CASH', choices=[('CHECK', 'Check'), ('CASH', 'Cash'), ('CARD', 'Credit card')], max_length=255)),
                ('bank', models.CharField(verbose_name='bank', default='OTHER', choices=[('OTHER', 'Autre'), ('SOCIETE-GENERALE', 'Société générale'), ('BANQUE-POPULAIRE', 'Banque populaire'), ('BNP', 'BNP'), ('CAISSE-EPARGNE', "Caisse d'épargne"), ('CIC', 'CIC'), ('CREDIT-AGRICOLE', 'Crédit Agricole'), ('CREDIT-MUTUEL', 'Credit Mutuel'), ('CREDIT-LYONNAIS', 'Credit Lyonnais'), ('LA-POSTE', 'La Poste')], max_length=255)),
                ('is_validated', models.BooleanField(verbose_name='is validated', default=False)),
                ('counter', models.ForeignKey(to='counter.Counter', related_name='refillings')),
                ('customer', models.ForeignKey(to='counter.Customer', related_name='refillings')),
                ('operator', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='refillings_as_operator')),
            ],
            options={
                'verbose_name': 'refilling',
            },
        ),
        migrations.CreateModel(
            name='Selling',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('label', models.CharField(verbose_name='label', max_length=64)),
                ('unit_price', accounting.models.CurrencyField(decimal_places=2, verbose_name='unit price', max_digits=12)),
                ('quantity', models.IntegerField(verbose_name='quantity')),
                ('date', models.DateTimeField(verbose_name='date')),
                ('payment_method', models.CharField(verbose_name='payment method', default='SITH_ACCOUNT', choices=[('SITH_ACCOUNT', 'Sith account'), ('CARD', 'Credit card')], max_length=255)),
                ('is_validated', models.BooleanField(verbose_name='is validated', default=False)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='sellings', null=True, to='club.Club')),
                ('counter', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='sellings', null=True, to='counter.Counter')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='buyings', null=True, to='counter.Customer')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='sellings', blank=True, null=True, to='counter.Product')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='sellings_as_operator', null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'selling',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.ForeignKey(verbose_name='product type', related_name='products', blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='counter.ProductType'),
        ),
        migrations.AddField(
            model_name='counter',
            name='products',
            field=models.ManyToManyField(to='counter.Product', related_name='counters', blank=True),
        ),
        migrations.AddField(
            model_name='counter',
            name='sellers',
            field=models.ManyToManyField(verbose_name='sellers', to=settings.AUTH_USER_MODEL, related_name='counters', blank=True),
        ),
        migrations.AddField(
            model_name='counter',
            name='view_groups',
            field=models.ManyToManyField(to='core.Group', related_name='viewable_counters', blank=True),
        ),
        migrations.CreateModel(
            name='CashRegisterSummary',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('date', models.DateTimeField(verbose_name='date')),
                ('comment', models.TextField(null=True, verbose_name='comment', blank=True)),
                ('emptied', models.BooleanField(verbose_name='emptied', default=False)),
                ('counter', models.ForeignKey(verbose_name='counter', related_name='cash_summaries', to='counter.Counter')),
                ('user', models.ForeignKey(verbose_name='user', related_name='cash_summaries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'cash register summary',
            },
        ),
        migrations.CreateModel(
            name='CashRegisterSummaryItem',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('value', accounting.models.CurrencyField(decimal_places=2, verbose_name='value', max_digits=12)),
                ('quantity', models.IntegerField(verbose_name='quantity', default=0)),
                ('check', models.BooleanField(verbose_name='check', default=False)),
                ('cash_summary', models.ForeignKey(verbose_name='cash summary', related_name='items', to='counter.CashRegisterSummary')),
            ],
            options={
                'verbose_name': 'cash register summary item',
            },
        ),
        migrations.AlterField(
            model_name='counter',
            name='club',
            field=models.ForeignKey(verbose_name='club', related_name='counters', to='club.Club'),
        ),
        migrations.AlterField(
            model_name='counter',
            name='products',
            field=models.ManyToManyField(verbose_name='products', to='counter.Product', related_name='counters', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='buying_groups',
            field=models.ManyToManyField(verbose_name='buying groups', to='core.Group', related_name='products', blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='archived',
            field=models.BooleanField(verbose_name='archived', default=False),
        ),
        migrations.AddField(
            model_name='counter',
            name='token',
            field=models.CharField(null=True, verbose_name='token', max_length=30, blank=True),
        ),
        migrations.CreateModel(
            name='Eticket',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('banner', models.ImageField(null=True, verbose_name='banner', upload_to='etickets', blank=True)),
                ('secret', models.CharField(verbose_name='secret', unique=True, max_length=64)),
                ('product', models.OneToOneField(verbose_name='product', related_name='eticket', to='counter.Product')),
                ('event_date', models.DateField(null=True, verbose_name='event date', blank=True)),
                ('event_title', models.CharField(null=True, verbose_name='event title', max_length=64, blank=True)),
            ],
        ),
    ]
