# Generated by Django 4.1.6 on 2023-02-16 13:41

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200, unique=True)),
                ('crediteur', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Compte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200, unique=True)),
                ('report', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=8)),
                ('externe', models.BooleanField(default=False)),
                ('actif', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='budget.compte')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exec_date', models.DateField(verbose_name='date')),
                ('montant', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=8)),
                ('note', models.CharField(blank=True, default='', max_length=200)),
                ('regle_budget', models.CharField(blank=True, default='', max_length=500)),
                ('reconcilie', models.BooleanField(default=False, verbose_name='reconciliée')),
                ('dst', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='dest', to='budget.compte')),
                ('src', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='source', to='budget.compte')),
            ],
        ),
        migrations.CreateModel(
            name='Repartition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=8)),
                ('budget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budget.budget')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budget.transaction')),
            ],
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['exec_date'], name='budget_tran_exec_da_37d8cb_idx'),
        ),
    ]
