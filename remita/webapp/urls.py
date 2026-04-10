from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'webapp'

urlpatterns = [
    path('', lambda request: redirect('webapp:login')),  # root redirect
    path('login/', views.UserLogin, name='login'),
    path('register/', views.register, name='register'),
    path('register/approve/<str:token>/', views.approve_registration, name='approve-registration'),
    path('register/reject/<str:token>/', views.reject_registration, name='reject-registration'),
    path('history/', views.transaction_history, name='transaction-history'),
    path('download/', views.transaction_history_xls),
    path('download/json/', views.transaction_history_json, name='transaction-history-json'),
    path('history-export/', views.export_history_filtered, name='history-export'),
    path('account_number/', views.checkAccNumber, name='check-account-number'),

    path('bank_details/upload/verify_account/', views.checkVendorDetails),
    path('bank_details/upload/verify_vendor/', views.checkVendor),
    path('role/', views.checkUserRole),
    path('remove/<str:invoice_id>/<int:project_id>/', views.removetransaction, name='remove-transaction'),
    path('account_details/', views.vendor_account_details),
    path('dashboard/', views.homepage, name='homepage'),
    path('bank_details/edit/<str:acc_id>/', views.editBankUploadViaForm, name='edit-bank-details'),
    path('bank_details/upload/', views.bankUploadViaForm, name='upload-bank-details'),

    path('bank_details/', views.vendorBankDetails, name='bank-details'),
    path('bank_details/search/', views.searchvendorBankDetails, name='search-vendor-bank-details'),
    path('bank_details/live-search/', views.live_search_bank_details, name='live-search-bank-details'),
    path('bank_details/beneficiary/', views.get_beneficiary_details, name='get-beneficiary-details'),
    # Source bank management
    path('source-banks/', views.source_bank_details, name='source-bank-details'),
    path('source-banks/add/', views.add_source_bank, name='add-source-bank'),
    path('source-banks/<int:pk>/edit/', views.edit_source_bank, name='edit-source-bank'),

    path('search/', views.get_search_results, name='search-transactions'),
    path('history-search/', views.get_history_search_results, name='search-transactions-history'),
    path('status/<str:batch_ref>/', views.check_transaction_status, name='check-transaction-status'),
   # path('status/tx/', views.check_single_transaction_status, name='check-single-transaction-status'),
    path('post-transactions/', views.post_transactions, name='post-transactions'),
    path('history-export/json/', views.export_history_filtered_json, name='history-export-json'),
    path('logout', views.UserLogout, name='logout'),
    path('bank_details/upload/loadBanks/', views.loadBankList, name='load-bank-list'),
    path('bank_details/delete/<str:acc_no>/', views.delete_vendor, name='delete'),
    path('transaction_history/delete/<str:invoice_id>/<int:project_id>/', views.delete_pending_transactions, name='delete-pending'),

]
