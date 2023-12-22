import os
os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\lib")
from weasyprint import HTML

from django.db.models import Count, F
from .models import detail_transaksi, perawatan
from django.shortcuts import render, redirect
from django.contrib.auth import login , logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from . import models
from datetime import datetime
import calendar
from .decorators import role_required
from django.forms import inlineformset_factory
from django.forms import DateInput
from django.db import transaction
from django.core.exceptions import ValidationError
import json
from django.template.loader import render_to_string
import tempfile
from django.template import RequestContext
from django.db.models import Sum
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import Sum, F
from django.db.models import F
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from django.db.models import Count
from .models import detail_transaksi, perawatan
# Create your views here.

#  LOGIN
@login_required(login_url="login")
def logoutview(request):
    logout(request)
    messages.info(request,"Berhasil Logout")
    return redirect('login')

def loginview(request):
    if request.user.is_authenticated:
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name

        if group == 'karyawan':
            return redirect('mitra')
        elif group in ['admin', 'owner']:
            return redirect('home')
    else:
        return render(request,"login.html")

def performlogin(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed")
    else:
        username_login = request.POST['username']
        password_login = request.POST['password']
        userobj = authenticate(request, username=username_login,password=password_login)
        if userobj is not None:
            login(request, userobj)
            messages.success(request,"Login success")
            if  userobj.groups.filter(name='owner').exists():
                return redirect("home")
            elif userobj.groups.filter(name='karyawan').exists():
                return redirect("mitra")
            elif userobj.groups.filter(name='admin').exists():
                return redirect("transaksi")

            
        else:
            messages.error(request,"Username atau Password salah !!!")
            return redirect("login")
        
@login_required(login_url="login")
def performlogout(request):
    logout(request)
    return redirect("login")

# dashboard 
@login_required(login_url="login")
@role_required(["owner", 'admin'])
def home(request):
    transaksi_list = models.transaksi.objects.all()

    combined_data = []

    jumlah_transaksi_pelanggan = {}

    # Menghitung jumlah data transaksi
    jumlah_data_transaksi = transaksi_list.count()

    # Mengambil jumlah data pelanggan dari database
    jumlah_data_pelanggan = models.pelanggan.objects.count()

    total_pendapatan = 0  # Inisialisasi total pendapatan
    perawatan_terlaris = models.perawatan.objects.annotate(
        terlaris_count=Count('detail_transaksi')
    ).order_by('-terlaris_count')[:10]

    for transaksi_item in transaksi_list:
        nomor_nota = transaksi_item.nomor_nota
        id_pelanggan = transaksi_item.id_pelanggan_id

        pelanggan_item = models.pelanggan.objects.get(id_pelanggan=id_pelanggan)

        pembayaran_item = models.pembayaran.objects.filter(nomor_nota=nomor_nota).first()

        detail_transaksi_list = models.detail_transaksi.objects.filter(nomor_nota=nomor_nota)

        jenis_perawatan_list = []
        deskripsi_sepatu_list = []

        total_transaction = 0
        for detail_item in detail_transaksi_list:
            total_transaction += detail_item.id_perawatan.harga_perawatan
            jenis_perawatan_list.append(detail_item.id_perawatan.jenis_perawatan)
            deskripsi_sepatu_list.append(detail_item.deskripsi_sepatu)

        total_pendapatan += total_transaction  # Menambahkan total transaksi ke total pendapatan

        if id_pelanggan in jumlah_transaksi_pelanggan:
            jumlah_transaksi_pelanggan[id_pelanggan] += 1
        else:
            jumlah_transaksi_pelanggan[id_pelanggan] = 1

        if jumlah_transaksi_pelanggan[id_pelanggan] % 5 == 0:
            total_transaction *= 0.85

        metode_pembayaran = pembayaran_item.metode_pembayaran if pembayaran_item else "--"
        status = "Lunas" if transaksi_item.status else "Belum Lunas"
        if status == "Belum Lunas":
            metode_pembayaran = "--"
            total_transaction = "--"

        combined_data.append({
            'nomor_nota': nomor_nota,
            'nama_pelanggan': pelanggan_item.nama_pelanggan,
            'status': status,
            'metode_pembayaran': metode_pembayaran,
            'jenis_perawatan': ", ".join(jenis_perawatan_list),
            'deskripsi_sepatu': ", ".join(deskripsi_sepatu_list),
            'tanggal_transaksi': transaksi_item.tanggal_transaksi,
            'total_transaction': total_transaction,
            'jumlah_transaksi_pelanggan': jumlah_transaksi_pelanggan[id_pelanggan],
        })

    return render(request, 'index.html', {
        'combined_data': combined_data,
        'jumlah_data_transaksi': jumlah_data_transaksi,
        'jumlah_data_pelanggan': jumlah_data_pelanggan,
        'total_pendapatan': total_pendapatan,
        'perawatan_terlaris': perawatan_terlaris,  # Menambahkan data perawatan terlaris ke template
    })

# CRUD PELANGGAN 

#Create
@login_required(login_url="login")
@role_required(["owner", 'admin'])
def create_pelanggan(request):
    if request.method == 'GET':
        pelangganobj = models.pelanggan.objects.all()
        return render(request, 'createpelanggan.html', {
            'datapelanggan': pelangganobj
        })
    elif request.method == 'POST':
        nama_pelanggan = request.POST['nama_pelanggan']
        alamat_pelanggan = request.POST['alamat_pelanggan']
        nomor_telepon = request.POST['nomor_telepon']

        newpelanggan = models.pelanggan(
            nama_pelanggan=nama_pelanggan,
            alamat_pelanggan=alamat_pelanggan,
            nomor_telepon=nomor_telepon
        )
        newpelanggan.save()
        customer_name = nama_pelanggan 
        return HttpResponseRedirect(reverse('createtransaksi') + f'?customer_name={customer_name}')
       
#Read
@login_required(login_url="login")
@role_required(["owner", 'admin'])
def pelanggan(request):
    pelangganobj = models.pelanggan.objects.all()
    return render(request, 'pelanggan.html', {
        'pelangganobj' : pelangganobj
    })

#Update
@login_required(login_url="login")
@role_required(["owner", "admin"])
def update_pelanggan(request, id):
    pelangganobj = models.pelanggan.objects.get(id_pelanggan=id)
    
    if request.method == "GET":
        return render(request, "updatepelanggan.html", {"pelangganobj": pelangganobj})
    elif request.method == "POST":
        nama_baru = request.POST.get("nama_pelanggan")
        alamat_baru = request.POST.get("alamat_pelanggan")
        telepon_baru = request.POST.get("nomor_telepon")

        # Check if any of the fields are updated before saving
        if nama_baru:
            pelangganobj.nama_pelanggan = nama_baru
        if alamat_baru:
            pelangganobj.alamat_pelanggan = alamat_baru
        if telepon_baru:
            pelangganobj.nomor_telepon = telepon_baru

        pelangganobj.save()

        return redirect("pelanggan")

#Delete
@login_required(login_url="login")
@role_required(["owner"])
def delete_pelanggan(request, id):
    pelangganobj = models.pelanggan.objects.get(id_pelanggan=id)
    pelangganobj.delete()
    return redirect('pelanggan')


# CRUD PERAWATAN
# create 
@login_required(login_url="login")
@role_required(["owner", 'admin'])

def create_perawatan(request):
    if request.method == 'GET':
        perawatanobj = models.perawatan.objects.all()
        return render(request, 'createperawatan.html', {
            'dataperawatan': perawatanobj
        })
    elif request.method == 'POST':
        jenis_perawatan = request.POST['jenis_perawatan']
        durasi_pengerjaan = request.POST['durasi_pengerjaan']
        harga_perawatan = request.POST['harga_perawatan']

        newperawatan = models.perawatan(
            jenis_perawatan=jenis_perawatan,
            durasi_pengerjaan=durasi_pengerjaan,
            harga_perawatan=harga_perawatan
        )
        newperawatan.save()

        return redirect('perawatan')

#Read
@login_required(login_url="login")
@role_required(["owner", 'admin'])
def getperawatan(request):
    perawatanobj = models.perawatan.objects.all()
    return render(request, 'perawatan.html', {
        'perawatanobj' : perawatanobj
    })
#Update
@login_required(login_url="login")
@role_required(["owner", "admin"])
def update_perawatan(request, id):
    perawatanobj = models.perawatan.objects.get(id_perawatan=id)
    
    if request.method == "GET":
        return render(request, "updateperawatan.html", {
            "perawatanobj": perawatanobj,
            "jenis": perawatanobj.jenis_perawatan,  
            "durasi": perawatanobj.durasi_pengerjaan,  
            "harga": perawatanobj.harga_perawatan,  
        })
    elif request.method == "POST":
        jenis_perawatan_baru = request.POST.get("jenis_perawatan")
        durasi_pengerjaan_baru = request.POST.get("durasi_pengerjaan")
        harga_perawatan_baru = request.POST.get("harga_perawatan")

        if jenis_perawatan_baru:
            perawatanobj.jenis_perawatan = jenis_perawatan_baru
        if durasi_pengerjaan_baru:
            perawatanobj.durasi_pengerjaan = durasi_pengerjaan_baru
        if harga_perawatan_baru:
            perawatanobj.harga_perawatan = harga_perawatan_baru

        perawatanobj.save()

        return redirect("perawatan")

#Delete
@login_required(login_url="login")
@role_required(["owner"])
def delete_perawatan(request, id):
    perawatanobj = models.perawatan.objects.get(id_perawatan=id)
    perawatanobj.delete()
    return redirect('perawatan')
    
# CRUD TRANSAKSI
@login_required(login_url="login")
@role_required(["owner", 'admin'])
def create_transaksi(request):
    customer_name = request.GET.get('customer_name') 

    if request.method == 'GET':
        transaksiobj = models.transaksi.objects.all()
        datapelanggan = models.pelanggan.objects.all()
        return render(request, 'createtransaksi.html', {
            'datatransaksi': transaksiobj,
            'datapelanggan': datapelanggan,
            'customer_name': customer_name,
        })
    elif request.method == 'POST':
        id_pelanggan = request.POST["id_pelanggan"]
        status = request.POST["status"]
        tanggal_transaksi = request.POST["tanggal_transaksi"]

        newtransaksi = models.transaksi.objects.create(
            id_pelanggan_id=id_pelanggan,
            status=status,
            tanggal_transaksi=tanggal_transaksi
        )
        nomor_nota = newtransaksi.nomor_nota

        return HttpResponseRedirect(reverse('createdetailtransaksi') + f'?nomor_nota={nomor_nota}')

#Read
@login_required(login_url="login")
@role_required(["owner", 'admin'])
def gettransaksi(request):
    transaksiobj = models.transaksi.objects.all()
    return render(request, 'transaksi.html', {
        'transaksiobj' : transaksiobj
    })

# Update
@login_required(login_url="login")
@role_required(["owner", "admin"])
def update_transaksi(request, id):
    transaksiobj = models.transaksi.objects.get(nomor_nota=id)
    datapelanggan = models.pelanggan.objects.all()
    status_value = "True" if transaksiobj.status else "False" 

    if request.method == "GET":
        return render(request, 'updatetransaksi.html', {
            'transaksiobj': transaksiobj,
            'datapelanggan': datapelanggan,
            'status_value': status_value,  
        })
    elif request.method == "POST":
        id_pelanggan = request.POST.get("id_pelanggan")
        status = request.POST.get("status")
        tanggal_transaksi_b = request.POST.get("tanggal_transaksi")

        try:
            pelanggan_instance = models.pelanggan.objects.get(id_pelanggan=id_pelanggan)
        except models.pelanggan.DoesNotExist:
            pass

        if pelanggan_instance:
            transaksiobj.id_pelanggan = pelanggan_instance
        if status:
            transaksiobj.status = status
        if tanggal_transaksi_b:
            transaksiobj.tanggal_transaksi = tanggal_transaksi_b

        transaksiobj.save()

        return redirect("transaksi")


#Delete
@login_required(login_url="login")
@role_required(["owner"])
def delete_transaksi(request, id):
    transaksiobj = models.transaksi.objects.get(nomor_nota=id)
    transaksiobj.delete()
    return redirect('transaksi')
    
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from .models import transaksi, perawatan, detail_transaksi
from .forms import DetailTransaksiForm
from django.shortcuts import redirect

DetailTransaksiFormSet = inlineformset_factory(
    transaksi,
    detail_transaksi,
    fields=['id_perawatan', 'deskripsi_sepatu'],
    extra=5,
)
@login_required(login_url="login")
@role_required(["owner", 'admin'])
def create_detail_transaksi(request):
    nomor_nota = request.GET.get('nomor_nota')
    if request.method == 'POST':
        nomor_nota = request.POST.get("nomor_nota")
        formset = DetailTransaksiFormSet(request.POST)
        if formset.is_valid():
            if nomor_nota:
                transaksi_instance = get_object_or_404(models.transaksi, nomor_nota=nomor_nota)
                for form in formset:
                    if form.cleaned_data.get('id_perawatan'):
                        newdetailtransaksi = form.save(commit=False)
                        newdetailtransaksi.nomor_nota = transaksi_instance
                        newdetailtransaksi.save()

                if transaksi_instance.status:  
                    return HttpResponseRedirect(reverse('createpembayaran') + f'?nomor_nota={nomor_nota}')
                else:
                    return redirect('alltransaksi')
        else:
            pass
    else:
        formset = DetailTransaksiFormSet(queryset=models.detail_transaksi.objects.none())

    datatransaksi = models.transaksi.objects.all()
    dataperawatan = models.perawatan.objects.all()
    return render(request, 'createdetailtransaksi.html', {
        'formset': formset,
        'datatransaksi': datatransaksi,
        'dataperawatan': dataperawatan,
        'nomor_nota': nomor_nota,
    })



#Read
@login_required(login_url="login")
@role_required(["owner", 'admin'])

def detail_transaksi(request):
    detailtransaksiobj = models.detail_transaksi.objects.all().order_by('nomor_nota')
    return render(request, 'detailtransaksi.html', {
        'detailtransaksiobj' : detailtransaksiobj
    })

#Update
@login_required(login_url="login")
@role_required(["owner", "admin"])
def update_detail_transaksi(request, id):
    detailtransaksiobj = models.detail_transaksi.objects.get(id_detail_transaksi=id)
    datatransaksi = models.transaksi.objects.all()
    dataperawatan = models.perawatan.objects.all()
    if request.method == "GET":
        return render(request, 'updatedetailtransaksi.html', {
            'detailtransaksiobj': detailtransaksiobj,
            'datatransaksi': datatransaksi,
            'dataperawatan': dataperawatan,
        })
    elif request.method == "POST":
        nomor_nota = request.POST.get("nomor_nota")
        id_perawatan = request.POST.get("id_perawatan")
        deskripsi_sepatu_b = request.POST.get("deskripsi_sepatu")

        try:
            transaksi_instance = get_object_or_404(models.transaksi, nomor_nota=nomor_nota)
            perawatan_instance = get_object_or_404(models.perawatan, id_perawatan=id_perawatan)
        except models.transaksi.DoesNotExist:
            pass

        if transaksi_instance:
            detailtransaksiobj.nomor_nota = transaksi_instance
        if perawatan_instance:
            detailtransaksiobj.id_perawatan = perawatan_instance
        if deskripsi_sepatu_b:
            detailtransaksiobj.deskripsi_sepatu = deskripsi_sepatu_b

        detailtransaksiobj.save()

        return redirect("detailtransaksi")

#Delete
@login_required(login_url="login")
@role_required(["owner"])
def delete_detail_transaksi(request, id):
    detailtransaksiobj = models.detail_transaksi.objects.get(id_detail_transaksi=id)
    detailtransaksiobj.delete()
    return redirect('detailtransaksi')

# CRUD PEMBAYARAN
# KODE DISINI
# CREATE

# CREATE
@login_required(login_url="login")
@role_required(["owner", "admin"])

def create_pembayaran(request):
    nomor_nota = request.GET.get('nomor_nota', None)
    if request.method == 'GET':
        pembayaranobj = models.pembayaran.objects.all()
        datatransaksi = models.transaksi.objects.all()
        return render(request, 'createpembayaran.html', {
            'datapembayaran': pembayaranobj,
            'datatransaksi': datatransaksi,
            'nomor_nota': nomor_nota,
        })
    elif request.method == 'POST':
        nomor_nota = request.POST['nomor_nota']
        tanggal_pembayaran = request.POST['tanggal_pembayaran']
        metode_pembayaran = request.POST["metode_pembayaran"]

        transaksi_instance = models.transaksi.objects.get(nomor_nota=nomor_nota)

        newpembayaran = models.pembayaran(
            nomor_nota=transaksi_instance,
            tanggal_pembayaran=tanggal_pembayaran,
            metode_pembayaran=metode_pembayaran
        )
        newpembayaran.save()
        transaksi_instance.status = True  
        transaksi_instance.save()
        return redirect('alltransaksi')

# READ
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from django.db.models import Sum, F, Value, FloatField

@login_required(login_url="login")
@role_required(["owner", 'admin'])

def pembayaran(request):
    pembayaranobj = models.pembayaran.objects.all()
    detailobj = []

    jumlah_transaksi_pelanggan = {}
    for pembayaran_item in pembayaranobj:
        nomor_nota = pembayaran_item.nomor_nota
        total_transaction = models.detail_transaksi.objects.filter(nomor_nota=nomor_nota).aggregate(total=Sum('id_perawatan__harga_perawatan'))['total']

        if total_transaction is not None:  # Periksa apakah total_transaction bukan None
            id_pelanggan = pembayaran_item.nomor_nota.id_pelanggan_id
            if id_pelanggan not in jumlah_transaksi_pelanggan:
                jumlah_transaksi_pelanggan[id_pelanggan] = 1
            else:
                jumlah_transaksi_pelanggan[id_pelanggan] += 1

            if jumlah_transaksi_pelanggan[id_pelanggan] % 5 == 0:
                total_transaction *= 0.85

            detailobj.append({
                'nomor_nota': nomor_nota,
                'total_transaction': total_transaction,
                'pembayaran_item': pembayaran_item,
            })


    return render(request, 'pembayaran.html', {
        'detailobjek': detailobj,
    })




# UPDATE
@login_required(login_url="login")
@role_required(["owner", "admin"])
def update_pembayaran(request, id):
    pembayaranobj = models.pembayaran.objects.get(id_pembayaran=id)
    datatransaksi = models.transaksi.objects.all()
    metode_pembayaran_value = "True" if pembayaranobj.metode_pembayaran else "False"  
    
    if request.method == "GET":
        return render(request, "updatepembayaran.html", {
            'pembayaranobj': pembayaranobj,
            'datatransaksi': datatransaksi,
            'metode_pembayaran_value': metode_pembayaran_value,
        })
    elif request.method == "POST":
        nomor_nota = request.POST.get("nomor_nota")
        tanggal_pembayaran_baru = request.POST.get("tanggal_pembayaran")
        metode_pembayaran = request.POST.get("metode_pembayaran")
        
        try:
            transaksi_instance = models.transaksi.objects.get(nomor_nota=nomor_nota)
        except models.transaksi.DoesNotExist:
            pass
        
        if transaksi_instance:
            pembayaranobj.nomor_nota = transaksi_instance
        if tanggal_pembayaran_baru:
            pembayaranobj.tanggal_pembayaran = tanggal_pembayaran_baru
        if metode_pembayaran:
            pembayaranobj.metode_pembayaran = metode_pembayaran

        pembayaranobj.save()

        return redirect("pembayaran")

    
# DELETE
@login_required(login_url="login")
@role_required(["owner"])
def delete_pembayaran(request, id):
    pembayaranobj = models.pembayaran.objects.get(id_pembayaran=id)
    pembayaranobj.delete()
    return redirect('pembayaran')


# LAPORAN
@login_required(login_url="login")
@role_required(["owner"])

def laporanpendapatanbulanan(request):
    if request.method == "GET":
        return render(request, 'laporanpendapatan.html')
    elif request.method == "POST":
        detailobj = []

        mulai = request.POST['mulai']
        akhir = request.POST['akhir']

        mulai_date = datetime.strptime(mulai, "%Y-%m-%d")
        akhir_date = datetime.strptime(akhir, "%Y-%m-%d")

        getlaporanpendapatanbulanan = models.transaksi.objects.filter(
            tanggal_transaksi__range=(mulai_date, akhir_date),
            status=True
        ).select_related('id_pelanggan')

        for item in getlaporanpendapatanbulanan:
            datadetailobj = []
            datadetailobj.append(item.nomor_nota)  
            datadetailobj.append(item.id_pelanggan.nama_pelanggan)  
            datadetailobj.append("Lunas" if item.status else "Belum Lunas")  

            getdetailobject = models.detail_transaksi.objects.filter(nomor_nota=item).select_related('id_perawatan')

            listperawatan = []
            listdeskripsi_sepatu = []
            total_transaction = 0

            for detail in getdetailobject:
                perawatan_instance = detail.id_perawatan
                listperawatan.append(perawatan_instance.jenis_perawatan)  
                listdeskripsi_sepatu.append(detail.deskripsi_sepatu) 
                total_transaction += perawatan_instance.harga_perawatan

            datadetailobj.append(", ".join(listperawatan))  
            datadetailobj.append(", ".join(listdeskripsi_sepatu))  
            datadetailobj.append(item.tanggal_transaksi)  
            datadetailobj.append(total_transaction)  
            
            pembayaran = models.pembayaran.objects.filter(nomor_nota=item).first()

            if pembayaran:
                datadetailobj.append(pembayaran.metode_pembayaran)  
                datadetailobj.append(pembayaran.tanggal_pembayaran)  
            else:
                datadetailobj.append("") 

            detailobj.append(datadetailobj)


        totalkeseluruhan = sum(detail[6] if len(detail) > 6 else 0 for detail in detailobj)

        return render(request, 'laporanpendapatanbulanan.html', {
            'detailobjek': detailobj,
            'tanggalmulai': mulai_date,
            'tanggalakhir': akhir_date,
            'pemasukan': totalkeseluruhan
        })

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from datetime import datetime
from django.shortcuts import render
from . import models
@login_required(login_url="login")
@role_required(["owner"])
def laporanpendapatanbulananpdf(request, mulai, akhir):
    mulai = datetime.strptime(mulai, "%Y-%m-%d")
    akhir = datetime.strptime(akhir, "%Y-%m-%d")
    detailobj = []

    getlaporanpendapatanbulanan = models.transaksi.objects.filter(
        tanggal_transaksi__range=(mulai, akhir),
        status=True
    ).select_related('id_pelanggan')

    for item in getlaporanpendapatanbulanan:
        datadetailobj = []
        datadetailobj.append(item.nomor_nota)
        datadetailobj.append(item.id_pelanggan.nama_pelanggan)
        datadetailobj.append("Lunas" if item.status else "Belum Lunas")

        getdetailobject = models.detail_transaksi.objects.filter(nomor_nota=item).select_related('id_perawatan')

        listperawatan = []
        listdeskripsi_sepatu = []
        total_transaction = 0

        for detail in getdetailobject:
            perawatan_instance = detail.id_perawatan
            listperawatan.append(perawatan_instance.jenis_perawatan)
            listdeskripsi_sepatu.append(detail.deskripsi_sepatu)
            total_transaction += perawatan_instance.harga_perawatan

        datadetailobj.append(", ".join(listperawatan))
        datadetailobj.append(", ".join(listdeskripsi_sepatu))
        datadetailobj.append(item.tanggal_transaksi)
        datadetailobj.append(total_transaction)

        pembayaran = models.pembayaran.objects.filter(nomor_nota=item).first()

        if pembayaran:
            datadetailobj.append(pembayaran.metode_pembayaran)
            datadetailobj.append(pembayaran.tanggal_pembayaran)
        else:
            datadetailobj.append("")

        detailobj.append(datadetailobj)

    totalkeseluruhan = sum(detail[6] if len(detail) > 6 else 0 for detail in detailobj)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=laporan_pendapatan_bulanan.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    html_string = render_to_string(
        'laporanpendapatanpdf.html', {
            'detailobjek': detailobj,
            'tanggalmulai': mulai,
            'tanggalakhir': akhir,
            'pemasukan': totalkeseluruhan
        })
    html = HTML(string=html_string)
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output.seek(0)
        response.write(output.read())

    return response

@login_required(login_url="login")
@role_required(["owner", "admin"])


def alltransaksi(request):
    transaksi_list = models.transaksi.objects.all()

    combined_data = []

    jumlah_transaksi_pelanggan = {}

    for transaksi_item in transaksi_list:
        nomor_nota = transaksi_item.nomor_nota
        id_pelanggan = transaksi_item.id_pelanggan_id

        pelanggan_item = models.pelanggan.objects.get(id_pelanggan=id_pelanggan)

        pembayaran_item = models.pembayaran.objects.filter(nomor_nota=nomor_nota).first()

        detail_transaksi_list = models.detail_transaksi.objects.filter(nomor_nota=nomor_nota)

        jenis_perawatan_list = []
        deskripsi_sepatu_list = []

        total_transaction = 0
        for detail_item in detail_transaksi_list:
            total_transaction += detail_item.id_perawatan.harga_perawatan
            jenis_perawatan_list.append(detail_item.id_perawatan.jenis_perawatan)
            deskripsi_sepatu_list.append(detail_item.deskripsi_sepatu)

        if id_pelanggan in jumlah_transaksi_pelanggan:
            jumlah_transaksi_pelanggan[id_pelanggan] += 1
        else:
            jumlah_transaksi_pelanggan[id_pelanggan] = 1

        if jumlah_transaksi_pelanggan[id_pelanggan] % 5 == 0:
            total_transaction *= 0.85 

        metode_pembayaran = pembayaran_item.metode_pembayaran if pembayaran_item else "--"
        status = "Lunas" if transaksi_item.status else "Belum Lunas"
        if status == "Belum Lunas":
            metode_pembayaran = "--"
            total_transaction = "--"

        combined_data.append({
            'nomor_nota': nomor_nota,
            'nama_pelanggan': pelanggan_item.nama_pelanggan,
            'status': status,
            'metode_pembayaran': metode_pembayaran,
            'jenis_perawatan': ", ".join(jenis_perawatan_list),
            'deskripsi_sepatu': ", ".join(deskripsi_sepatu_list),
            'tanggal_transaksi': transaksi_item.tanggal_transaksi,
            'total_transaction': total_transaction,
        })

    return render(request, 'alltransaksi.html', {'combined_data': combined_data})


def cetak_notatransaksi_pdf(request, nomor_nota):
    transaksi_obj = get_object_or_404(models.transaksi, nomor_nota=nomor_nota)
    getpelanggan = models.transaksi.objects.filter(id_pelanggan = transaksi_obj.id_pelanggan.id_pelanggan) #diubah
    
    detail_transaksi_list = models.detail_transaksi.objects.filter(nomor_nota=transaksi_obj)
    print(detail_transaksi_list)
    jenis_perawatan_dict = {}
    total_transaction = 0

    for detail_item in detail_transaksi_list:
        jenis_perawatan = detail_item.id_perawatan.jenis_perawatan
        deskripsi_sepatu = detail_item.deskripsi_sepatu
        harga_perawatan = detail_item.id_perawatan.harga_perawatan

        if jenis_perawatan in jenis_perawatan_dict:
            jenis_perawatan_dict[jenis_perawatan].append(deskripsi_sepatu)
        else:
            jenis_perawatan_dict[jenis_perawatan] = [deskripsi_sepatu]
        total_transaction += harga_perawatan

    rows = []

    if transaksi_obj.status:
        pembayaran_obj = models.pembayaran.objects.filter(nomor_nota=transaksi_obj).first()
        if pembayaran_obj:
            if pembayaran_obj.metode_pembayaran:
                metode_pembayaran = "Tunai"
            else:
                metode_pembayaran = "Non Tunai"
        else:
            metode_pembayaran = "--"
    else:
        metode_pembayaran = "--"
   
    if not transaksi_obj.status:
        total_transaction = "--"

    jumlah_transaksi_pelanggan = {}
    id_pelanggan = transaksi_obj.id_pelanggan_id

    if id_pelanggan in jumlah_transaksi_pelanggan:
        jumlah_transaksi_pelanggan[id_pelanggan] += 1
    else:
        jumlah_transaksi_pelanggan[id_pelanggan] = 1

    if getpelanggan.count() % 5 == 0: #diubah
        total_transaction = 0.85 * total_transaction #diubah

    for jenis_perawatan, deskripsi_sepatu_list in jenis_perawatan_dict.items():
        for deskripsi_sepatu in deskripsi_sepatu_list:
            row = {
                'nomor_nota': transaksi_obj.nomor_nota,
                'nama_pelanggan': transaksi_obj.id_pelanggan.nama_pelanggan,
                'status': 'Lunas' if transaksi_obj.status else 'Belum Lunas',
                'jenis_perawatan': jenis_perawatan,
                'deskripsi_sepatu': deskripsi_sepatu,
                'harga_perawatan' : harga_perawatan,
                'tanggal_transaksi': transaksi_obj.tanggal_transaksi,
                'metode_pembayaran': metode_pembayaran,
                'total_transaction': 'Rp {}'.format(total_transaction),

            }
            rows.append(row)
    html_string = render_to_string('nota_transaksi_pdf.html', {'rows': rows, 'total_transaction':total_transaction})
    html = HTML(string=html_string)

    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="nota_transaksi.pdf"'

    return response

# def jenis_perawatan_terlaris(request):
#     perawatan_terlaris = perawatan.objects.annotate(terlaris_count=Count('detail_transaksi')).order_by('-terlaris_count')[:10]

#     return render(request, 'grafik.html', {
#         'perawatan_terlaris': perawatan_terlaris
#     })

from django.shortcuts import render
import matplotlib.pyplot as plt

def jenis_perawatan_terlaris(request):
    perawatan_terlaris = models.perawatan.objects.annotate(terlaris_count=Count('detail_transaksi')).order_by('-terlaris_count')[:10]

    # Ambil data untuk grafik
    labels = [perawatan.jenis_perawatan for perawatan in perawatan_terlaris]
    sizes = [perawatan.terlaris_count for perawatan in perawatan_terlaris]

    # Buat grafik proporsi (pie chart)
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Agar grafik menjadi lingkaran

    # Simpan grafik ke gambar atau buatnya di tempat
    # plt.savefig('media/pie_chart.png')  # Jika Anda ingin menyimpannya sebagai gambar

    # Konversi grafik ke base64
    import io
    import base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return render(request, 'grafik.html', {
        'perawatan_terlaris': perawatan_terlaris,
        'pie_chart': graph,  # Kirimkan data grafik sebagai base64 ke template
    })

from django.shortcuts import render, HttpResponse
from django.db.models import Count
from datetime import datetime

def laporan_perawatan_terlaris(request):
    if request.method == "GET":
        perawatan_terlaris = models.perawatan.objects.annotate(terlaris_count=Count('detail_transaksi')).order_by('-terlaris_count')[:10]

        # Ambil data untuk grafik
        labels = [perawatan.jenis_perawatan for perawatan in perawatan_terlaris]
        sizes = [perawatan.terlaris_count for perawatan in perawatan_terlaris]

        # Buat grafik proporsi (pie chart)
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # Agar grafik menjadi lingkaran

        # Simpan grafik ke gambar atau buatnya di tempat
        # plt.savefig('media/pie_chart.png')  # Jika Anda ingin menyimpannya sebagai gambar

        # Konversi grafik ke base64
        import io
        import base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        graph = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        return render(request, 'laporan_perawatan_terlaris.html', {
            'perawatan_terlaris': perawatan_terlaris,
            'pie_chart': graph,  # Kirimkan data grafik sebagai base64 ke template
        })

    elif request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return render(request, 'laporan_perawatan_terlaris.html', {'error_message': 'Format tanggal tidak valid.'})

        # Mengambil data transaksi dalam rentang waktu tertentu yang sudah lunas
        transactions = models.transaksi.objects.filter(
            tanggal_transaksi__range=(start_date, end_date),
            status=True
        )

        # Dictionary untuk menghitung jumlah setiap jenis perawatan
        perawatan_counts = {}

        for transaction in transactions:
            detail_objects = models.detail_transaksi.objects.filter(nomor_nota=transaction)
            for detail in detail_objects:
                perawatan = detail.id_perawatan
                if perawatan.jenis_perawatan in perawatan_counts:
                    perawatan_counts[perawatan.jenis_perawatan] += 1
                else:
                    perawatan_counts[perawatan.jenis_perawatan] = 1

        # Mengurutkan jenis perawatan berdasarkan jumlah pemesanan
        sorted_perawatan = sorted(perawatan_counts.items(), key=lambda x: x[1], reverse=True)

        return render(request, 'laporan_perawatan_terlaristabel.html', {
            'start_date': start_date,
            'end_date': end_date,
            'perawatan_terlaris': sorted_perawatan
        })

    return HttpResponse("Metode HTTP tidak didukung.")
from datetime import datetime
from datetime import datetime
from django.http import HttpResponse
from django.template.loader import get_template

def generate_pdf_laporan_perawatan_terlaris(request, mulai, akhir):
    try:
        # Hapus bagian jam, menit, dan detik
        mulai = datetime.strptime(mulai.split()[0], "%Y-%m-%d")
        akhir = datetime.strptime(akhir.split()[0], "%Y-%m-%d") 
    except ValueError:
        return HttpResponse("Format tanggal tidak valid.")

    # Mengambil data transaksi dalam rentang waktu tertentu yang sudah lunas
    transactions = models.transaksi.objects.filter(
        tanggal_transaksi__range=(mulai, akhir),
        status=True
    )

    # Dictionary untuk menghitung jumlah setiap jenis perawatan
    perawatan_counts = {}

    for transaction in transactions:
        detail_objects = models.detail_transaksi.objects.filter(nomor_nota=transaction)
        for detail in detail_objects:
            perawatan = detail.id_perawatan
            if perawatan.jenis_perawatan in perawatan_counts:
                perawatan_counts[perawatan.jenis_perawatan] += 1
            else:
                perawatan_counts[perawatan.jenis_perawatan] = 1

    # Mengurutkan jenis perawatan berdasarkan jumlah pemesanan
    sorted_perawatan = sorted(perawatan_counts.items(), key=lambda x: x[1], reverse=True)

    if not sorted_perawatan:
        return HttpResponse("Tidak ada data perawatan terlaris yang tersedia untuk rentang tanggal yang diberikan.")

    # Render the HTML template with the data
    template = get_template('perawatanpdf.html')
    context = {
        'tanggalmulai': mulai,
        'tanggalakhir': akhir,
        'perawatan_terlaris': sorted_perawatan
    }
    html = template.render(context)

    # Create the response and return it as a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=laporan_perawatan_terlaris.pdf'

    html = HTML(string=html)
    pdf_file = html.write_pdf()

    response.write(pdf_file)
    return response