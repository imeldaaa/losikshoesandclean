# Generated by Django 4.2.5 on 2023-09-15 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='pelanggan',
            fields=[
                ('id_pelanggan', models.AutoField(primary_key=True, serialize=False)),
                ('nama_pelanggan', models.CharField(max_length=30)),
                ('alamat_pelanggan', models.TextField(blank=True, null=True)),
                ('nomor_telepon', models.PositiveIntegerField()),
            ],
        ),
    ]
