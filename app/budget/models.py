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

from django.db import models
from django.db.models import Q
from decimal import Decimal
import re
import logging

logger = logging.getLogger('django')

class Budget(models.Model):
    nom = models.CharField(max_length=200, unique=True)
    crediteur = models.BooleanField(default=False)

    def __str__(self):
        return self.nom

    @property
    def is_empty(self):
        tr_list = Repartition.objects.filter(budget=self)[:1]
        return (tr_list.count() == 0)

class Compte(models.Model):
    nom = models.CharField(max_length=200, unique=True)
    report = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    externe = models.BooleanField(default=False)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

    @property
    def has_parent(self):
        return self.parent is not None

    @property
    def is_empty(self):
        tr_list = Transaction.objects.filter(Q(src=self)|Q(dst=self))[:1]
        return (tr_list.count() == 0)

    def balances(self):
        balances = {}
        balances['solde'] = Decimal(self.report)
        balances['reconciliation'] = Decimal('0.00')
        balances['banque'] = Decimal(self.report)
        balances['futur'] = Decimal(self.report)
        for tr in Transaction.objects.filter(src=self):
            if tr.reconcilie:
                balances['reconciliation'] -= Decimal(tr.montant)
                balances['banque'] -= Decimal(tr.montant)
            balances['futur'] -= Decimal(tr.montant)
        for tr in Transaction.objects.filter(dst=self):
            if tr.reconcilie:
                balances['reconciliation'] += Decimal(tr.montant)
                balances['banque'] += Decimal(tr.montant)
            balances['futur'] += Decimal(tr.montant)
        return balances

class Transaction(models.Model):
    src = models.ForeignKey(Compte, on_delete=models.RESTRICT, related_name='source', null=True, blank=True)
    dst = models.ForeignKey(Compte, on_delete=models.RESTRICT, related_name='dest', null=True, blank=True)
    exec_date = models.DateField('date')
    montant = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    note = models.CharField(max_length=200, blank=True, default='')
    regle_budget = models.CharField(max_length=500, blank=True, default='')
    reconcilie = models.BooleanField('reconciliée', default=False)

    class Meta:
        indexes = [
            models.Index(fields=['exec_date']),
        ]

    def __str__(self):
        return '{}:{:.2f}:{}:{}'.format(self.exec_date, self.montant, self.note, self.regle_budget)

class Repartition(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))

    @staticmethod
    def rule_with_name_to_id(regle):
        #logger.info('Repartition.rule_with_name_to_id: enter: {}'.format(regle))
        blist = [ x for x in map(str.strip, regle.split(';')) if x != '' ]
        rbudget = []
        for b in blist:
            m = re.match(r'^([^:*]+)(.*)$', b)
            if m:
                bdg, _ = Budget.objects.get_or_create(nom=m.group(1).strip())
                rbudget.append(str(bdg.id)+str(m.group(2)))
        if len(rbudget) > 0:
            rbudget.append('')
            result = ';'.join(rbudget)
            #logger.info('Repartition.rule_with_name_to_id: result: {}'.format(result))
            return result
        #logger.info('Repartition.rule_with_name_to_id: result: {}'.format(regle))
        return regle

    @staticmethod
    def rule_with_id_to_name(regle):
        #logger.info('Repartition.rule_with_id_to_name: enter: {}'.format(regle))
        blist = [ x for x in map(str.strip, regle.split(';')) if x != '' ]
        rbudget = []
        for b in blist:
            m = re.match(r'^([^:*]+)(.*)$', b)
            if m:
                bdg = Budget.objects.get(pk=m.group(1).strip())
                rbudget.append(str(bdg.nom)+str(m.group(2)))
        if len(rbudget) > 0:
            rbudget.append('')
            result = ';'.join(rbudget)
            #logger.info('Repartition.rule_with_id_to_name: result: {}'.format(result))
            return result
        #logger.info('Repartition.rule_with_id_to_name: result: {}'.format(regle))
        return regle

    def __str__(self):
        return '{}:{}:{}'.format(self.transaction, self.budget.nom, self.montant)
