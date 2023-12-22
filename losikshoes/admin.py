from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.pelanggan)
admin.site.register(models.pembayaran)
admin.site.register(models.transaksi)
admin.site.register(models.detail_transaksi)
admin.site.register(models.perawatan)

