from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages


from Vendas.models import Venda

from datetime import date, datetime
import re
import logging


class IndexView(TemplateView):
    template_name = 'index.html'

