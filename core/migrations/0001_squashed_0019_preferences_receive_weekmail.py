# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import phonenumber_field.modelfields
import django.core.validators
import core.models
import django.db.models.deletion
from django.conf import settings
import django.contrib.auth.models


class Migration(migrations.Migration):

    replaces = [('core', '0001_initial'), ('core', '0002_auto_20160831_0144'), ('core', '0003_auto_20160902_1914'), ('core', '0004_user_godfathers'), ('core', '0005_auto_20161105_1035'), ('core', '0006_auto_20161108_1703'), ('core', '0008_sithfile_asked_for_removal'), ('core', '0009_auto_20161120_1155'), ('core', '0010_sithfile_is_in_sas'), ('core', '0011_auto_20161124_0848'), ('core', '0012_notification'), ('core', '0013_auto_20161209_2338'), ('core', '0014_auto_20161210_0009'), ('core', '0015_sithfile_moderator'), ('core', '0016_auto_20161212_1922'), ('core', '0017_auto_20161220_1626'), ('core', '0018_auto_20161224_0211'), ('core', '0019_preferences_receive_weekmail')]

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('username', models.CharField(validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.')], unique=True, verbose_name='username', help_text='Required. 254 characters or fewer. Letters, digits and @/./+/-/_ only.', error_messages={'unique': 'A user with that username already exists.'}, max_length=254)),
                ('first_name', models.CharField(max_length=64, verbose_name='first name')),
                ('last_name', models.CharField(max_length=64, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('date_of_birth', models.DateField(null=True, verbose_name='date of birth', blank=True)),
                ('nick_name', models.CharField(null=True, max_length=64, verbose_name='nick name', blank=True)),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status', help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(default=True, verbose_name='active', help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateField(auto_now_add=True, verbose_name='date joined')),
                ('last_update', models.DateField(auto_now=True, verbose_name='last update')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser', help_text='Designates whether this user is a superuser. ')),
                ('sex', models.CharField(choices=[('MAN', 'Man'), ('WOMAN', 'Woman')], max_length=10, verbose_name='sex', default='MAN')),
                ('tshirt_size', models.CharField(choices=[('-', '-'), ('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')], max_length=5, verbose_name='tshirt size', default='-')),
                ('role', models.CharField(choices=[('STUDENT', 'Student'), ('ADMINISTRATIVE', 'Administrative agent'), ('TEACHER', 'Teacher'), ('AGENT', 'Agent'), ('DOCTOR', 'Doctor'), ('FORMER STUDENT', 'Former student'), ('SERVICE', 'Service')], max_length=15, verbose_name='role', blank=True, default='')),
                ('department', models.CharField(choices=[('TC', 'TC'), ('IMSI', 'IMSI'), ('IMAP', 'IMAP'), ('INFO', 'INFO'), ('GI', 'GI'), ('E', 'E'), ('EE', 'EE'), ('GESC', 'GESC'), ('GMC', 'GMC'), ('MC', 'MC'), ('EDIM', 'EDIM'), ('HUMA', 'Humanities'), ('NA', 'N/A')], max_length=15, verbose_name='department', blank=True, default='NA')),
                ('dpt_option', models.CharField(max_length=32, verbose_name='dpt option', blank=True, default='')),
                ('semester', models.CharField(max_length=5, verbose_name='semester', blank=True, default='')),
                ('quote', models.CharField(max_length=256, verbose_name='quote', blank=True, default='')),
                ('school', models.CharField(max_length=80, verbose_name='school', blank=True, default='')),
                ('promo', models.IntegerField(null=True, validators=[core.models.validate_promo], verbose_name='promo', blank=True)),
                ('forum_signature', models.TextField(max_length=256, verbose_name='forum signature', blank=True, default='')),
                ('second_email', models.EmailField(null=True, max_length=254, verbose_name='second email address', blank=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(null=True, max_length=128, verbose_name='phone', blank=True)),
                ('parent_phone', phonenumber_field.modelfields.PhoneNumberField(null=True, max_length=128, verbose_name='parent phone', blank=True)),
                ('address', models.CharField(max_length=128, verbose_name='address', blank=True, default='')),
                ('parent_address', models.CharField(max_length=128, verbose_name='parent address', blank=True, default='')),
                ('is_subscriber_viewable', models.BooleanField(verbose_name='is subscriber viewable', default=True)),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('group_ptr', models.OneToOneField(primary_key=True, parent_link=True, to='auth.Group', serialize=False, auto_created=True)),
                ('is_meta', models.BooleanField(default=False, verbose_name='meta group status', help_text='Whether a group is a meta group or not')),
                ('description', models.CharField(max_length=60, verbose_name='description')),
            ],
            bases=('auth.group',),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=30, verbose_name='page name')),
                ('_full_name', models.CharField(max_length=255, verbose_name='page name', blank=True)),
                ('edit_groups', models.ManyToManyField(to='core.Group', related_name='editable_page', verbose_name='edit group', blank=True)),
                ('owner_group', models.ForeignKey(verbose_name='owner group', default=1, to='core.Group', related_name='owned_page')),
                ('parent', models.ForeignKey(null=True, blank=True, verbose_name='parent', to='core.Page', related_name='children', on_delete=django.db.models.deletion.SET_NULL)),
                ('view_groups', models.ManyToManyField(to='core.Group', related_name='viewable_page', verbose_name='view group', blank=True)),
            ],
            options={
                'permissions': (('change_prop_page', "Can change the page's properties (groups, ...)"), ('view_page', 'Can view the page')),
            },
        ),
        migrations.CreateModel(
            name='PageRev',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('revision', models.IntegerField(verbose_name='revision')),
                ('title', models.CharField(max_length=255, verbose_name='page title', blank=True)),
                ('content', models.TextField(verbose_name='page content', blank=True)),
                ('date', models.DateTimeField(auto_now=True, verbose_name='date')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='page_rev')),
                ('page', models.ForeignKey(to='core.Page', related_name='revisions')),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Preferences',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('show_my_stats', models.BooleanField(default=False, verbose_name='define if we show a users stats', help_text='Show your account statistics to others')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='preferences')),
                ('receive_weekmail', models.BooleanField(verbose_name='do you want to receive the weekmail', default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SithFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=256, verbose_name='file name')),
                ('file', models.FileField(null=True, max_length=256, verbose_name='file', blank=True, upload_to=core.models.get_directory)),
                ('is_folder', models.BooleanField(verbose_name='is folder', default=True)),
                ('mime_type', models.CharField(max_length=30, verbose_name='mime type')),
                ('size', models.IntegerField(verbose_name='size', default=0)),
                ('date', models.DateTimeField(verbose_name='date', default=django.utils.timezone.now)),
                ('edit_groups', models.ManyToManyField(to='core.Group', related_name='editable_files', verbose_name='edit group', blank=True)),
                ('owner', models.ForeignKey(verbose_name='owner', to=settings.AUTH_USER_MODEL, related_name='owned_files')),
                ('parent', models.ForeignKey(null=True, blank=True, verbose_name='parent', to='core.SithFile', related_name='children')),
                ('view_groups', models.ManyToManyField(to='core.Group', related_name='viewable_files', verbose_name='view group', blank=True)),
                ('is_moderated', models.BooleanField(verbose_name='is moderated', default=False)),
                ('asked_for_removal', models.BooleanField(verbose_name='asked for removal', default=False)),
                ('compressed', models.FileField(null=True, max_length=256, verbose_name='compressed file', blank=True, upload_to=core.models.get_compressed_directory)),
                ('thumbnail', models.FileField(null=True, max_length=256, verbose_name='thumbnail', blank=True, upload_to=core.models.get_thumbnail_directory)),
                ('is_in_sas', models.BooleanField(verbose_name='is in the SAS', default=False)),
            ],
            options={
                'verbose_name': 'file',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='avatar_pict',
            field=models.OneToOneField(null=True, blank=True, verbose_name='avatar', to='core.SithFile', related_name='avatar_of', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='user',
            name='home',
            field=models.OneToOneField(null=True, blank=True, verbose_name='home', to='core.SithFile', related_name='home_of', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_pict',
            field=models.OneToOneField(null=True, blank=True, verbose_name='profile', to='core.SithFile', related_name='profile_of', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='user',
            name='scrub_pict',
            field=models.OneToOneField(null=True, blank=True, verbose_name='scrub', to='core.SithFile', related_name='scrub_of', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.CreateModel(
            name='MetaGroup',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.group',),
            managers=[
                ('objects', core.models.MetaGroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='RealGroup',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('core.group',),
            managers=[
                ('objects', core.models.RealGroupManager()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('name', 'parent')]),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(to='core.RealGroup', related_name='users', blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(validators=[django.core.validators.RegexValidator('^[\\w.+-]+$', 'Enter a valid username. This value may contain only letters, numbers and ./+/-/_ characters.')], unique=True, verbose_name='username', help_text='Required. 254 characters or fewer. Letters, digits and ./+/-/_ only.', error_messages={'unique': 'A user with that username already exists.'}, max_length=254),
        ),
        migrations.AddField(
            model_name='user',
            name='godfathers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='godchildren', blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='lock_timeout',
            field=models.DateTimeField(null=True, verbose_name='lock_timeout', blank=True, default=None),
        ),
        migrations.AddField(
            model_name='page',
            name='lock_user',
            field=models.ForeignKey(null=True, blank=True, verbose_name='lock user', default=None, to=settings.AUTH_USER_MODEL, related_name='locked_pages'),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('url', models.CharField(max_length=255, verbose_name='url')),
                ('type', models.CharField(choices=[('NEWS_MODERATION', 'A fresh new to be moderated'), ('FILE_MODERATION', 'New files to be moderated'), ('SAS_MODERATION', 'New pictures/album to be moderated in the SAS'), ('NEW_PICTURES', "You've been identified on some pictures"), ('REFILLING', 'You just refilled of %s €'), ('SELLING', 'You just bought %s'), ('GENERIC', 'You have a notification')], max_length=32, verbose_name='type', default='GENERIC')),
                ('date', models.DateTimeField(verbose_name='date', default=django.utils.timezone.now)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='notifications')),
                ('param', models.CharField(max_length=128, verbose_name='param', default='')),
                ('viewed', models.BooleanField(verbose_name='viewed', default=False)),
            ],
        ),
        migrations.AddField(
            model_name='sithfile',
            name='moderator',
            field=models.ForeignKey(null=True, blank=True, verbose_name='owner', to=settings.AUTH_USER_MODEL, related_name='moderated_files'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='last update'),
        ),
    ]
