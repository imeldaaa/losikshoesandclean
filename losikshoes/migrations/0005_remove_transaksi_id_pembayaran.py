# Generated by Django 4.2.5 on 2023-09-18 05:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('losikshoes', '0004_perawatan_detail_transaksi'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaksi',
            name='id_pembayaran',
        ),
    ]