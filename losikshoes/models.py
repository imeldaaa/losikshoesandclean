from django.db import models

# Create your models here.
class pelanggan(models.Model):
    id_pelanggan = models.AutoField(primary_key=True)
    nama_pelanggan = models.CharField(max_length=30)
    alamat_pelanggan = models.TextField(blank=True, null=True)
    nomor_telepon = models.PositiveIntegerField()

    def __str__(self):
        return str(self.nama_pelanggan)


class transaksi(models.Model):
    nomor_nota = models.AutoField(primary_key=True)
    id_pelanggan = models.ForeignKey(pelanggan, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    tanggal_transaksi = models.DateField()
    
    def __str__(self):
        return str(self.nomor_nota)


class perawatan(models.Model):
    id_perawatan = models.AutoField(primary_key=True)
    jenis_perawatan= models.CharField(max_length=30)
    durasi_pengerjaan= models.PositiveIntegerField()
    harga_perawatan= models.PositiveBigIntegerField() 

    def __str__(self):
        return str (self.jenis_perawatan)

class pembayaran(models.Model):
    id_pembayaran = models.AutoField(primary_key=True)
    nomor_nota = models.ForeignKey(transaksi, on_delete=models.CASCADE)
    tanggal_pembayaran = models.DateField()
    metode_pembayaran = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id_pembayaran)

class detail_transaksi (models.Model) :
    id_detail_transaksi = models.AutoField(primary_key=True)
    nomor_nota = models.ForeignKey(transaksi, on_delete=models.CASCADE)
    id_perawatan = models.ForeignKey(perawatan, on_delete=models.CASCADE, null=True)
    deskripsi_sepatu = models.CharField(max_length=100)

    def __str__(self):
        return str (self.nomor_nota)
