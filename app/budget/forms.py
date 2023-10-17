""""
Copyright © 2020-2023 Georges Ménie.
This file is part of mybudget.

mybudget is free software: you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

mybudget is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with mybudget.
If not, see https://www.gnu.org/licenses/
"""

import datetime
from django import forms
from .models import Compte
from decimal import Decimal

class TransactionForm(forms.Form):
    montant = forms.DecimalField(label='Montant', max_digits=8, decimal_places=2, min_value=Decimal('0.0'), required = False)
    date = forms.DateField(label='Date', initial=datetime.date.today, required = False)
    src = forms.ModelChoiceField(label='Source', queryset=Compte.objects.filter(actif=True).order_by('nom'), required = False)
    dst = forms.ModelChoiceField(label='Destination', queryset=Compte.objects.filter(actif=True).order_by('nom'), required = False)
    bis = forms.BooleanField(label='TR', initial=False, required = False)
    montantbis = forms.DecimalField(label='Limite', max_digits=8, decimal_places=2, min_value=Decimal('0.01'), required = False)
    srcbis = forms.ModelChoiceField(label='Compte TR', queryset=Compte.objects.filter(actif=True, externe=False).order_by('nom'), required = False)
    budget = forms.CharField(label='Budget', max_length=499, widget=forms.TextInput(attrs={'size':'31', 'class':'inputText'}), required = False)
    note = forms.CharField(label='Note', max_length=200, widget=forms.TextInput(attrs={'size':'31', 'class':'inputText'}), required = False)

class CompteForm(forms.Form):
    nom = forms.CharField(label='Nom', max_length=200, widget=forms.TextInput(attrs={'size':'31', 'class':'inputText'}))
    report = forms.DecimalField(label='Report', max_digits=8, decimal_places=2, required = False)
    parent = forms.ModelChoiceField(label='Parent', queryset=Compte.objects.filter(actif=True, externe=False).order_by('nom'), required = False)
    actif = forms.BooleanField(label='Actif', required = False)

class BudgetForm(forms.Form):
    nom = forms.CharField(label='Nom', max_length=200, widget=forms.TextInput(attrs={'size':'31', 'class':'inputText'}))
    crediteur = forms.BooleanField(label='Créditeur', initial=False, required = False)
