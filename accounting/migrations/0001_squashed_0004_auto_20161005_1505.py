# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields
import accounting.models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('accounting', '0001_initial'), ('accounting', '0002_auto_20160824_2152'), ('accounting', '0003_auto_20160824_2203'), ('accounting', '0004_auto_20161005_1505')]

    dependencies = [
        ('club', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountingType',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('code', models.CharField(verbose_name='code', max_length=16, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'An accounting type code contains only numbers')])),
                ('label', models.CharField(verbose_name='label', max_length=128)),
                ('movement_type', models.CharField(verbose_name='movement type', choices=[('CREDIT', 'Credit'), ('DEBIT', 'Debit'), ('NEUTRAL', 'Neutral')], max_length=12)),
            ],
            options={
                'verbose_name': 'accounting type',
                'ordering': ['movement_type', 'code'],
            },
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=30)),
                ('iban', models.CharField(verbose_name='iban', blank=True, max_length=255)),
                ('number', models.CharField(verbose_name='account number', blank=True, max_length=255)),
                ('club', models.ForeignKey(verbose_name='club', to='club.Club', related_name='bank_accounts')),
            ],
            options={
                'verbose_name': 'Bank account',
                'ordering': ['club', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ClubAccount',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=30)),
                ('bank_account', models.ForeignKey(verbose_name='bank account', to='accounting.BankAccount', related_name='club_accounts')),
                ('club', models.ForeignKey(verbose_name='club', to='club.Club', related_name='club_account')),
            ],
            options={
                'verbose_name': 'Club account',
                'ordering': ['bank_account', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=60)),
                ('city', models.CharField(verbose_name='city', blank=True, max_length=60)),
                ('country', models.CharField(verbose_name='country', blank=True, max_length=32)),
                ('email', models.EmailField(verbose_name='email', blank=True, max_length=254)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(verbose_name='phone', blank=True, max_length=128)),
                ('postcode', models.CharField(verbose_name='postcode', blank=True, max_length=10)),
                ('street', models.CharField(verbose_name='street', blank=True, max_length=60)),
                ('website', models.CharField(verbose_name='website', blank=True, max_length=64)),
            ],
            options={
                'verbose_name': 'company',
            },
        ),
        migrations.CreateModel(
            name='GeneralJournal',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('start_date', models.DateField(verbose_name='start date')),
                ('end_date', models.DateField(verbose_name='end date', null=True, blank=True, default=None)),
                ('name', models.CharField(verbose_name='name', max_length=40)),
                ('closed', models.BooleanField(verbose_name='is closed', default=False)),
                ('amount', accounting.models.CurrencyField(verbose_name='amount', max_digits=12, decimal_places=2, default=0)),
                ('effective_amount', accounting.models.CurrencyField(verbose_name='effective_amount', max_digits=12, decimal_places=2, default=0)),
                ('club_account', models.ForeignKey(verbose_name='club account', to='accounting.ClubAccount', related_name='journals')),
            ],
            options={
                'verbose_name': 'General journal',
                'ordering': ['-start_date'],
            },
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('number', models.IntegerField(verbose_name='number')),
                ('amount', accounting.models.CurrencyField(verbose_name='amount', max_digits=12, decimal_places=2)),
                ('date', models.DateField(verbose_name='date')),
                ('remark', models.CharField(verbose_name='comment', max_length=128)),
                ('mode', models.CharField(verbose_name='payment method', choices=[('CHECK', 'Check'), ('CASH', 'Cash'), ('TRANSFERT', 'Transfert'), ('CARD', 'Credit card')], max_length=255)),
                ('cheque_number', models.CharField(verbose_name='cheque number', null=True, blank=True, max_length=32, default='')),
                ('done', models.BooleanField(verbose_name='is done', default=False)),
                ('target_type', models.CharField(verbose_name='target type', choices=[('USER', 'User'), ('CLUB', 'Club'), ('ACCOUNT', 'Account'), ('COMPANY', 'Company'), ('OTHER', 'Other')], max_length=10)),
                ('target_id', models.IntegerField(verbose_name='target id', null=True, blank=True)),
                ('target_label', models.CharField(verbose_name='target label', blank=True, max_length=32, default='')),
                ('accounting_type', models.ForeignKey(verbose_name='accounting type', to='accounting.AccountingType', blank=True, null=True, related_name='operations')),
                ('invoice', models.ForeignKey(verbose_name='invoice', to='core.SithFile', blank=True, null=True, related_name='operations')),
                ('journal', models.ForeignKey(verbose_name='journal', to='accounting.GeneralJournal', related_name='operations')),
                ('linked_operation', models.OneToOneField(verbose_name='linked operation', to='accounting.Operation', blank=True, default=None, null=True, related_name='operation_linked_to')),
            ],
            options={
                'ordering': ['-number'],
            },
        ),
        migrations.CreateModel(
            name='SimplifiedAccountingType',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('label', models.CharField(verbose_name='label', max_length=128)),
                ('accounting_type', models.ForeignKey(verbose_name='simplified accounting types', to='accounting.AccountingType', related_name='simplified_types')),
            ],
            options={
                'verbose_name': 'simplified type',
                'ordering': ['accounting_type__movement_type', 'accounting_type__code'],
            },
        ),
        migrations.AddField(
            model_name='operation',
            name='simpleaccounting_type',
            field=models.ForeignKey(verbose_name='simple type', to='accounting.SimplifiedAccountingType', blank=True, null=True, related_name='operations'),
        ),
        migrations.AlterUniqueTogether(
            name='operation',
            unique_together=set([('number', 'journal')]),
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(verbose_name='label', max_length=64)),
                ('club_account', models.ForeignKey(verbose_name='club account', to='accounting.ClubAccount', related_name='labels')),
            ],
        ),
        migrations.AddField(
            model_name='operation',
            name='label',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='label', to='accounting.Label', blank=True, null=True, related_name='operations'),
        ),
        migrations.AlterUniqueTogether(
            name='label',
            unique_together=set([('name', 'club_account')]),
        ),
    ]
