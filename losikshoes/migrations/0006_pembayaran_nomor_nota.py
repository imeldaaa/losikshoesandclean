# Generated by Django 4.2.5 on 2023-09-18 05:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('losikshoes', '0005_remove_transaksi_id_pembayaran'),
    ]

    operations = [
        migrations.AddField(
            model_name='pembayaran',
            name='nomor_nota',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='losikshoes.transaksi'),
        ),
    ]
