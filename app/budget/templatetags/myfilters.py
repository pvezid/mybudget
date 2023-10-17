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

from django import template
from ..models import Repartition

register = template.Library()

@register.filter
def to_budget_name(value):
    return Repartition.rule_with_id_to_name(value)

@register.filter
def comma_to_dot(value):
    return value.replace(",",".")
