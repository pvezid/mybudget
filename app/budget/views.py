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

from decimal import Decimal
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.urls import reverse
from django.db import models
from django.db.models import Case, When, Value, F, Q, Sum
from django.db.models.functions import TruncMonth, TruncYear
from django.conf import settings
from .models import Compte, Transaction, Repartition, Budget
from .forms import TransactionForm, CompteForm, BudgetForm
from collections import defaultdict
import re
import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import logging

logger = logging.getLogger('django')

#class HttpResponseSeeOther(HttpResponseRedirect):
#    status_code = 303

# utiliser avec:
#    return HttpResponseSeeOther(request.META['HTTP_REFERER'])

def index(request):
    return HttpResponseRedirect(reverse('budget:lister_comptes'))

def lister_comptes(request):
    comptes = get_list_or_404(Compte.objects.order_by('-actif', 'externe', 'parent', 'nom'))
    return render(request, 'budget/comptes.html', {'comptes': comptes, 'form': CompteForm()})

# XHR
def ajouter_compte(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        if 'cancel' not in request.POST:
            # create a form instance and populate it with data from the request:
            form = CompteForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                nom = form.cleaned_data['nom']
                report = form.cleaned_data['report']
                parent = form.cleaned_data['parent']
                actif = form.cleaned_data['actif']
                cpt = Compte(nom=nom, report=report, parent=parent, actif=actif)
                cpt.save()
            else:
                logger.warn(form.errors)
                return HttpResponseBadRequest()
    return HttpResponse('')

# XHR
def editer_compte(request, compte_id):
    compte = get_object_or_404(Compte, pk=compte_id)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        if 'cancel' not in request.POST:
            # create a form instance and populate it with data from the request:
            form = CompteForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                compte.nom = form.cleaned_data['nom']
                compte.report = form.cleaned_data['report']
                compte.parent = form.cleaned_data['parent']
                compte.actif = form.cleaned_data['actif']
                compte.save()
            else:
                logger.warn(form.errors)
                return HttpResponseBadRequest()
    return HttpResponse('')

# XHR
def supprimer_cpt(request, compte_id):
    compte = get_object_or_404(Compte, pk=compte_id)
    tr_list = Transaction.objects.filter(Q(src=compte)|Q(dst=compte))[:1]
    if tr_list.count() == 0:
        compte.delete()
        return HttpResponse('')
    return HttpResponseBadRequest()

def lister_op(request, compte_id, period=1):
    compte = get_object_or_404(Compte, pk=compte_id)
    budgets = list(Budget.objects.order_by('nom'))
    if period != 0:
        today = datetime.date.today()
        begOfThisMonth = today.replace(day=1)
        monthsAgo = begOfThisMonth + relativedelta(months=-period)
        tr_list = list(Transaction.objects.filter(Q(src=compte)|Q(dst=compte), exec_date__gte=monthsAgo).order_by('-exec_date'))
    else:
        tr_list = list(Transaction.objects.filter(Q(src=compte)|Q(dst=compte)).order_by('-exec_date'))
    trp_list = []
    for tr in tr_list:
        trp_list.append
        trp_list.append({"tr": tr, "part": None})
    return render(request, 'budget/lister_op.html', {'compte_ctx': compte, 'transactions': trp_list, 'balances': compte.balances(), 'budgets': budgets, 'form': TransactionForm(), 'periode': period, 'trset': settings.TR })

def lister_op_budget(request, budget_id, period=6):
    budget = get_object_or_404(Budget, pk=budget_id)
    budgets = list(Budget.objects.order_by('nom'))
    if period != 0:
        today = datetime.date.today()
        begOfThisMonth = today.replace(day=1)
        monthsAgo = begOfThisMonth + relativedelta(months=-period)
        rep_list = list(Repartition.objects.filter(budget=budget, transaction__exec_date__gte=monthsAgo).order_by('-transaction__exec_date'))
    else:
        rep_list = list(Repartition.objects.filter(budget=budget).order_by('-transaction__exec_date'))
    trp_list = []
    total_ctx = { "debit": Decimal('0.00'), "credit": Decimal('0.00') }
    for rep in rep_list:
        #logger.info(rep)
        part = Decimal(0.0)
        if (rep.transaction.src is None or rep.transaction.src.externe) and not (rep.transaction.dst is None or rep.transaction.dst.externe):
            total_ctx['credit'] += Decimal(rep.montant)
            part += Decimal(rep.montant)
        if (not (rep.transaction.src is None or rep.transaction.src.externe)) and (rep.transaction.dst is None or rep.transaction.dst.externe):
            total_ctx['debit'] += Decimal(rep.montant)
            part -= Decimal(rep.montant)
        trp_list.append({"tr": rep.transaction, "part": part})
    return render(request, 'budget/lister_op.html', {'budget_ctx': budget, 'transactions': trp_list, 'budgets': budgets, 'total_ctx': total_ctx,'form': TransactionForm(), 'periode': period })

def mensuel_op(request, compte_id):
    compte = get_object_or_404(Compte, pk=compte_id)
    today = datetime.date.today()
    begOfThisMonth = today.replace(day=1)
    begOfPreviousMonth = begOfThisMonth + relativedelta(months=-2)
    trLastMonth = Transaction.objects.filter(Q(src=compte)|Q(dst=compte)).filter(note__icontains='mensuel').filter(exec_date__gte=begOfPreviousMonth).exclude(exec_date__gte=begOfThisMonth).order_by('-exec_date')
    for tr in trLastMonth:
        trThisMonth = Transaction.objects.filter(Q(src=compte)|Q(dst=compte)).filter(note__iexact=tr.note).filter(exec_date__gte=begOfThisMonth)
        if trThisMonth.count() == 0:
            newtr = Transaction(src=tr.src, dst=tr.dst, exec_date=today, montant=tr.montant, note=tr.note, regle_budget=tr.regle_budget)
            _save_and_finalize_tr(newtr)
    return HttpResponseRedirect(reverse('budget:lister_op', args=(compte_id,)))

def transfert_op(request, compte_id):
    compte = get_object_or_404(Compte, pk=compte_id)
    if compte.parent != compte:
        tr_list = Transaction.objects.filter(Q(src=compte)|Q(dst=compte), reconcilie=True)
        for tr in tr_list:
            #logger.info('transfert: {}'.format(tr))
            if tr.src == compte:
                tr.src = compte.parent
            if tr.dst == compte:
                tr.dst = compte.parent
            tr.save()
    return HttpResponseRedirect(reverse('budget:lister_op', args=(compte.parent.id,)))

#
# Répartition sur budgets multiples
# liste de budgets séparés par un ;
# exemple pour un total de 300:
# Alimentation*2;Voiture:100;Divers;Gateaux:17
#
# l'ordre des budgets n'est pas important
# on prend en premier les budgets pour lesquels une somme est donnée (avec : suivi du nombre à budgeter)
# 100 pour Voiture et 17 pour Gateaux
# ce qui reste est réparti en fonction du poids de chacun:
# Alimentation pour 2 parts
# Divers pour une part
# le nombre de parts au total est donc 3
# Alimentation reçoit 2/3 de la somme restante (300-117 = 183) soit 122 €
# Divers reçoit 1/3 soit 61 €
#
# bug: on ignore les virgules après *p
# Maison*2,2;Transports:33;Maison;Transports
# = Maison*2;Transports:33;Maison;Transports
#
def _calculate_repartition(rbudget, total):
    blist = [ x for x in map(str.strip, rbudget.split(';')) if x != '' ]
    reste = total
    budget = defaultdict(Decimal)
    blist2 = []
    for b in blist:
        m = re.match(r'^([^:*]+):([0-9,]+)$', b)
        if m:
            bdg = Budget.objects.get(pk=m.group(1).strip())
            part = min(Decimal(m.group(2).replace(',','.')), reste)
            if part > 0:
                reste -= part
                budget[bdg.id] += part
        else:
            blist2.append(b)
    #logger.info('blist2: {}'.format(blist2))
    parts = 0
    for b in blist2:
        m = re.match(r'^([^:*]+)\*([0-9]+)', b)
        parts += int(m.group(2)) if m else 1
    #logger.info('parts: {}'.format(parts))
    for b in blist2:
        m = re.match(r'^([^:*]+)\*([0-9]+)', b)
        if m:
            bdg = Budget.objects.get(pk=m.group(1).strip())
            repar = (reste * int(m.group(2))) / parts
        else:
            bdg = Budget.objects.get(pk=b)
            repar = reste / parts
        if repar > 0:
            budget[bdg.id] += repar
    return budget

def _save_and_finalize_tr(tr):
    # sauvegarde de la transaction
    tr.save()
    # suppression des répartitions précédentes éventuelles
    Repartition.objects.filter(transaction=tr).delete()
    # recalcul des budgets
    budget = _calculate_repartition(tr.regle_budget, tr.montant)
    #logger.info('Budget: {}'.format(str(budget)))
    # création des nouvelles répartitions
    for key in budget.keys():
        bdg = Budget.objects.get(pk=key)
        rep_obj = Repartition(budget=bdg, montant=budget[key], transaction=tr)
        rep_obj.save()

# XHR
def nouvelle_op(request, compte_id):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        if 'cancel' not in request.POST:
            # create a form instance and populate it with data from the request:
            form = TransactionForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                src = form.cleaned_data['src']
                srcbis = form.cleaned_data['srcbis']
                bis = form.cleaned_data['bis']
                dst = form.cleaned_data['dst']
                date = form.cleaned_data['date']
                montant = Decimal(form.cleaned_data['montant'])
                montantbis = Decimal(form.cleaned_data['montantbis'])
                note = form.cleaned_data['note']
                rbudget = Repartition.rule_with_name_to_id(form.cleaned_data['budget'])
                if bis and montantbis > Decimal('0.01') and srcbis is not None:
                    m = min(montant,montantbis)
                    note_extra = ' [TR {0:.2f}]'.format(montant).replace('.', ',') # TODO utlisier les fonctions de locale
                    tr1 = Transaction(src=srcbis, dst=dst, exec_date=date, montant=m, note=note+note_extra, regle_budget=rbudget)
                    _save_and_finalize_tr(tr1)
                    if (montant-m) > 0:
                        m = montant-montantbis
                        tr2 = Transaction(src=src, dst=dst, exec_date=date, montant=m, note=note+note_extra, regle_budget=rbudget)
                        _save_and_finalize_tr(tr2)
                else:
                    tr = Transaction(src=src, dst=dst, exec_date=date, montant=montant, note=note, regle_budget=rbudget)
                    _save_and_finalize_tr(tr)
            else:
                logger.warn(form.errors)
                return HttpResponseBadRequest()
    return HttpResponse('')

# XHR
def editer_tr(request, transaction_id):
    tr = get_object_or_404(Transaction, pk=transaction_id)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        if 'cancel' not in request.POST:
            # create a form instance and populate it with data from the request:
            form = TransactionForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                if not tr.reconcilie:
                    tr.src = form.cleaned_data['src']
                    tr.dst = form.cleaned_data['dst']
                    tr.exec_date = form.cleaned_data['date']
                    tr.montant = Decimal(form.cleaned_data['montant'])
                tr.note = form.cleaned_data['note']
                tr.regle_budget = Repartition.rule_with_name_to_id(form.cleaned_data['budget'])
                _save_and_finalize_tr(tr)
            else:
                logger.warn(form.errors)
                return HttpResponseBadRequest()
    return HttpResponse('')

def reconcilier_tr(request, transaction_id):
    tr = Transaction.objects.get(pk=transaction_id)
    tr.reconcilie = True
    tr.save()
    return HttpResponse('')

def dereconcilier_tr(request, transaction_id):
    tr = Transaction.objects.get(pk=transaction_id)
    tr.reconcilie = False
    tr.save()
    return HttpResponse('')

def supprimer_tr(request, transaction_id):
    tr = Transaction.objects.get(pk=transaction_id)
    tr.delete()
    return HttpResponse('')

def lister_budgets(request):
    budgets = get_list_or_404(Budget.objects.order_by('nom'))
    return render(request, 'budget/budgets.html', {'budgets': budgets, 'form': BudgetForm()})

# XHR
def ajouter_budget(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        if 'cancel' not in request.POST:
            # create a form instance and populate it with data from the request:
            form = BudgetForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                nom = form.cleaned_data['nom']
                crediteur = form.cleaned_data['crediteur']
                bdg = Budget(nom=nom, crediteur=crediteur)
                bdg.save()
            else:
                logger.warn(form.errors)
                return HttpResponseBadRequest()
    return HttpResponse('')

# XHR
def editer_budget(request, budget_id):
    budget = get_object_or_404(Budget, pk=budget_id)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        if 'cancel' not in request.POST:
            # create a form instance and populate it with data from the request:
            form = BudgetForm(request.POST)
            # check whether it's valid:
            if form.is_valid():
                nvnom = form.cleaned_data['nom']
                if budget.nom != nvnom:
                    bcount = Budget.objects.filter(nom__exact=nvnom).count()
                    if bcount == 0:
                        budget.nom = nvnom
                        budget.crediteur = form.cleaned_data['crediteur']
                        budget.save()
                    else:
                        # if faut joindre le budget édité au budget avec le nouveau nom:
                        #   lister toutes les transactions qui citent l'ancien budget
                        #   recalculer les répartitions en changeant l'ancien budget par le nouveau
                        # puis supprimer l'ancien budget si il est vide
                        newBudget = Budget.objects.get(nom=nvnom)
                        for tr in Transaction.objects.all():
                            blist = [ x for x in map(str.strip, tr.regle_budget.split(';')) if x != '' ]
                            rbudget = []
                            remap = False
                            for b in blist:
                                m = re.match(r'^([^:*]+)(.*)$', b)
                                if m and m.group(1).strip() == str(budget_id):
                                    rbudget.append(str(newBudget.id)+str(m.group(2)))
                                    remap = True
                                else:
                                    rbudget.append(b)
                            rbudget.append('')
                            result = ';'.join(rbudget)
                            if remap:
                                #logger.info('Transaction before remap: {} with {}'.format(tr,result))
                                tr.regle_budget = result
                                #logger.info('Transaction after remap: {}'.format(tr))
                                _save_and_finalize_tr(tr)
                        if budget.is_empty:
                            budget.delete()

            else:
                logger.warn(form.errors)
                return HttpResponseBadRequest()
    return HttpResponse('')

# XHR
def supprimer_bdg(request, budget_id):
    budget = get_object_or_404(Budget, pk=budget_id)
    rep_list = Repartition.objects.filter(budget=budget)[:1]
    if rep_list.count() == 0:
        budget.delete()
        return HttpResponse('')
    return HttpResponseBadRequest()

def graph_budget(request, compte_id, period=1):
    compte = get_object_or_404(Compte, pk=compte_id)
    if period != 0:
        today = datetime.date.today()
        begOfThisMonth = today.replace(day=1)
        monthsAgo = begOfThisMonth + relativedelta(months=-period)
        tr_list = Transaction.objects.filter(Q(src=compte)|Q(dst=compte), exec_date__gte=monthsAgo)
    else:
        tr_list = Transaction.objects.filter(Q(src=compte)|Q(dst=compte))
    budgets = {}
    for tr in tr_list:
        m = 0
        if tr.src == compte:
            m = 1
        if tr.dst == compte:
            m = -1
        for r in Repartition.objects.filter(transaction=tr):
            b = r.budget.nom
            if b in budgets.keys():
                budgets[b] += r.montant * m
            else:
                budgets[b] = r.montant * m
    budgets_list = []
    for b in budgets.keys():
        item = {}
        item['budget'] = b
        item['montant'] = str(budgets[b]).replace(',','.')
        budgets_list.append(item)
    budgets_list = sorted(budgets_list, key=lambda x: float(x['montant']), reverse=True)
    budgets_list = budgets_list[:16]
    return render(request, 'budget/graph_budget.html', {'compte': compte, 'budgets': budgets_list, 'periode': period})

def graphes(request):
    today = datetime.date.today()
    begOfThisMonth = today.replace(day=1)
    monthsAgo = begOfThisMonth + relativedelta(months=-24)
    budgets_par_mois = \
        Repartition.objects.values('budget__nom','budget__crediteur') \
            .filter(((Q(transaction__src__isnull=True)|Q(transaction__src__externe=True))&Q(transaction__dst__externe=False))|(Q(transaction__src__externe=False)&(Q(transaction__dst__isnull=True)|Q(transaction__dst__externe=True))), transaction__exec_date__gte=monthsAgo) \
            .annotate(mois=TruncMonth('transaction__exec_date')) \
            .annotate(montant_mois=Sum(Case(When(Q(transaction__src__isnull=True)|Q(transaction__src__externe=True), then=F('montant')), default=-1*F('montant'), output_field=models.DecimalField()))) \
            .order_by('mois')
    return render(request, 'budget/graphes.html', { 'budgets_par_mois': budgets_par_mois })
