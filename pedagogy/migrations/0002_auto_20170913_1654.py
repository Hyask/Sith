# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedagogy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='category',
            field=models.CharField(verbose_name='Category', choices=[('CS', 'Science Knowledge'), ('QC', 'Ask and Create'), ('EC', 'Expression and Communication'), ('OM', 'Organize and Manage'), ('TM', 'Tech and Method')], max_length=255),
        ),
        migrations.AlterField(
            model_name='course',
            name='formation',
            field=models.CharField(verbose_name='Formation type', choices=[('GMC', 'Mechanical and Conception'), ('IMSI', 'POUSSE CARTON'), ('TC', 'Common Core'), ('INFO', 'Computer Science'), ('EDIM', 'Mechanical and Conception'), ('EE', 'Powering')], max_length=255),
        ),
        migrations.AlterField(
            model_name='course',
            name='semester',
            field=models.CharField(verbose_name='Semester', choices=[('A', 'Autumn'), ('S', 'Spring')], max_length=60),
        ),
    ]
