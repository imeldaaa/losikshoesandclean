from django.urls import path
from . import views
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [

    # HOME
    path('home',views.home, name="home"),
    path('logout/', LogoutView.as_view(), name='logout'),

    # LOGIN
    path('',views.loginview, name='login'),
    path('performlogin',views.performlogin,name="performlogin"),
    path('performlogout',views.performlogout,name="performlogout"),

    #PELANGGAN
    path('pelanggan', views.pelanggan, name='pelanggan'),
    path('createpelanggan', views.create_pelanggan, name='createpelanggan'),
    path('updatepelanggan/<str:id>', views.update_pelanggan, name='updatepelanggan'),
    path('deletepelanggan/<str:id>', views.delete_pelanggan, name='deletepelanggan'),

    #TRANSAKSI
    path('transaksi', views.gettransaksi, name='transaksi'),
    path('createtransaksi', views.create_transaksi, name='createtransaksi'),
    path('updatetransaksi/<str:id>', views.update_transaksi, name='updatetransaksi'),
    path('deletetransaksi/<str:id>', views.delete_transaksi, name='deletetransaksi'),

    #PERAWATAN
    path('perawatan', views.getperawatan, name='perawatan'), 
    path('createperawatan', views.create_perawatan, name='createperawatan'),
    path('updateperawatan/<str:id>', views.update_perawatan, name='updateperawatan'),
    path('deleteperawatan/<str:id>', views.delete_perawatan, name='deleteperawatan'),
    
    #PEMBAYARAN
    path('pembayaran', views.pembayaran, name='pembayaran'),
    path('createpembayaran', views.create_pembayaran, name='createpembayaran'),
    path('updatepembayaran/<str:id>', views.update_pembayaran, name='updatepembayaran'),
    path('deletepembayaran/<str:id>', views.delete_pembayaran, name='deletepembayaran'),

    #DETAIL TRANSAKSI
    path('detailtransaksi', views.detail_transaksi, name='detailtransaksi'),
    path('createdetailtransaksi', views.create_detail_transaksi, name='createdetailtransaksi'),
    path('updatedetailtransaksi/<str:id>', views.update_detail_transaksi, name='updatedetailtransaksi'),
    path('deletedetailtransaksi/<str:id>', views.delete_detail_transaksi, name='deletedetailtransaksi'),

    # LAPORAN
    path('laporanpendapatan', views.laporanpendapatanbulanan, name='laporanpendapatanbulanan'),
    path('laporanpendapatanpdf/<str:mulai>/<str:akhir>/', views.laporanpendapatanbulananpdf, name='laporanpendapatanbulananpdf'),

    # ALL TRANSAKSI 
    path('getalltransaksi', views.alltransaksi, name='alltransaksi'),
    path('cetak-nota/<str:nomor_nota>/', views.cetak_notatransaksi_pdf, name='cetak_notatransaksi_pdf'),

    path('produk_terlaris', views.jenis_perawatan_terlaris, name='produk_terlaris'),

    path('laporan_perawatan_terlaris', views.laporan_perawatan_terlaris, name='laporan_perawatan_terlaris'),
    path('laporan_perawatan_terlaris/tabel/', views.laporan_perawatan_terlaris, name='laporan_perawatan_terlaristabel'),
    path('generate_laporan_perawatan_terlaris_pdf/<str:mulai>/<str:akhir>/', views.generate_pdf_laporan_perawatan_terlaris, name='generate_pdf_laporan_perawatan_terlaris'),


]