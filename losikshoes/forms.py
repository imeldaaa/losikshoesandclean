from django import forms
from .models import detail_transaksi

class DetailTransaksiForm(forms.ModelForm):
    class Meta:
        model = detail_transaksi
        fields = ['id_perawatan', 'deskripsi_sepatu']

    def __init__(self, *args, **kwargs):
        super(DetailTransaksiForm, self).__init__(*args, **kwargs)
        self.fields['id_perawatan'].required = False
        self.fields['deskripsi_sepatu'].required = False
