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

from django.urls import path

from . import views

app_name = 'budget'
urlpatterns = [
    path('', views.index, name='index'),
    path('comptes', views.lister_comptes, name='lister_comptes'),
    path('comptes/ajouter', views.ajouter_compte, name='ajouter_compte'),
    path('compte/<int:compte_id>', views.lister_op, name='lister_op'),
    path('compte/<int:compte_id>/<int:period>', views.lister_op, name='lister_op'),
    path('compte/<int:compte_id>/editer_compte', views.editer_compte, name='editer_compte'),
    path('compte/<int:compte_id>/nouvelle_op', views.nouvelle_op, name='nouvelle_op'),
    path('compte/<int:compte_id>/mensuel_op', views.mensuel_op, name='mensuel_op'),
    path('compte/<int:compte_id>/transfert_op', views.transfert_op, name='transfert_op'),
    path('compte/<int:compte_id>/supprimer_cpt', views.supprimer_cpt, name='supprimer_cpt'),
    path('transaction/<int:transaction_id>/reconcilier_tr', views.reconcilier_tr, name='reconcilier_tr'),
    path('transaction/<int:transaction_id>/dereconcilier_tr', views.dereconcilier_tr, name='dereconcilier_tr'),
    path('transaction/<int:transaction_id>/supprimer_tr', views.supprimer_tr, name='supprimer_tr'),
    path('transaction/<int:transaction_id>/editer_tr', views.editer_tr, name='editer_tr'),
    path('budgets', views.lister_budgets, name='lister_budgets'),
    path('budgets/ajouter', views.ajouter_budget, name='ajouter_budget'),
    path('budget/<int:budget_id>', views.lister_op_budget, name='lister_op_budget'),
    path('budget/<int:budget_id>/<int:period>', views.lister_op_budget, name='lister_op_budget'),
    path('budget/<int:budget_id>/editer_budget', views.editer_budget, name='editer_budget'),
    path('budget/<int:budget_id>/supprimer_bdg', views.supprimer_bdg, name='supprimer_bdg'),
    path('graphes', views.graphes, name='graphes'),
]
