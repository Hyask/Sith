#!/usr/bin/env python3
# -*- coding:utf-8 -*
#
# Skia < skia AT libskia DOT so >
#
# Beerware licensed software - 2016
#

import os
import sys
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sith.settings")
import django
django.setup()

from counter.models import Selling, Product

with open("data.dat", 'w') as f:
    for date in Selling.objects.filter(date__gte=datetime(year=2016, month=12, day=9)).datetimes("date", "minute"):
        print(date)
        prods = [s.product.id for s in Selling.objects.filter(date__gte=date, date__lt=date+timedelta(minutes=1)).all() if s.product]
        f.write(" ".join([str(p) for p in prods]))
        # f.write(" ".join([str(p.id)+"="+("1" if p in [s.product for s in Selling.objects.filter(date__gte=date,
        #     date__lt=date+timedelta(minutes=1)).all()] else "0") for p in Product.objects.filter(archived=False)]))
        f.write("\n")




