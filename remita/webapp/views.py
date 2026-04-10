import datetime
import io
import json
import os
import tempfile
import traceback
import uuid
from itertools import groupby
from operator import attrgetter
from typing import List, Dict, Any, Optional, Tuple

from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from _decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.core import signing
from django.urls import reverse
from django.views.decorators.http import require_GET

from remita import settings
from .forms import BankDetailsForm, RegistrationForm, SourceBankForm
from .permissions import user_is_approver, user_is_support_staff
from .services import *
from .models import *
from .models import Projects

import requests
import pandas as pd



"""
Functions to Handle User Authentication and Authorization

"""


def get_remita_token(username: str, password: str) -> Dict[str, Any]:
    """
    Authenticate with Remita API and get access token.
    Token is valid for 3600 seconds (1 hour).

    Args:
        username: Remita API username
        password: Remita API password

    Returns:
        Dictionary with success status and token/error
    """
    url = getattr(settings, 'REMITA_API_AUTH_URL', "https://demo.remita.net/remita/exapp/api/v1/send/api/uaasvc/uaa/token")

    payload = {
        "username": username,
        "password": password
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Token could be in different fields based on API version
        token = data.get('token') or data.get('accessToken') or data.get('access_token')

        return {
            "success": True,
            "token": token,
            "expires_in": data.get('expiresIn') or data.get('expires_in', 3600),  # 1 hour default
            "response_data": data
        }

    except requests.exceptions.RequestException as e:
        error_detail = None
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
            except:
                error_detail = e.response.text

        return {
            "success": False,
            "error": str(e),
            "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
            "response_data": error_detail
        }


def check_and_refresh_token(request=None):
    """
    Check if token exists and is valid. Refresh if needed.
    Uses database-backed storage instead of sessions.
    Returns token or None if unavailable.
    """


    auth = RemitaAuth.objects.first()

    # If no record exists or no token stored, fetch a new one
    if not auth or not auth.token or not auth.expires_at:
        remita_username = getattr(settings, 'REMITA_API_PUBLIC_KEY', 'C9MEL4NMZM7CNM5M')
        remita_password = getattr(settings, 'REMITA_API_SECRET_KEY', 'N7VSULFSJW25CEMQ740DNM8236JDIA3N')
        token_result = get_remita_token(remita_username, remita_password)
        if token_result['success']:
            expires_at = now() + datetime.timedelta(seconds=token_result['expires_in'])
            if not auth:
                auth = RemitaAuth.objects.create(token=token_result['response_data']['data'][0]['accessToken'], expires_at=expires_at)
            else:
                auth.token = token_result['response_data']['data'][0]['accessToken']
                auth.expires_at = expires_at
                auth.save(update_fields=['token', 'expires_at', 'updated_at'])
            return token_result['response_data']['data'][0]['accessToken']
        return None

    # If token exists, check if it's expiring soon (5-minute buffer)
    buffer = datetime.timedelta(minutes=5)
    if now() >= (auth.expires_at - buffer):
        remita_username = getattr(settings, 'REMITA_API_PUBLIC_KEY', 'C9MEL4NMZM7CNM5M')
        remita_password = getattr(settings, 'REMITA_API_SECRET_KEY', 'N7VSULFSJW25CEMQ740DNM8236JDIA3N')
        token_result = get_remita_token(remita_username, remita_password)
        if token_result['success']:
            auth.token = token_result['response_data']['data'][0]['accessToken']
            auth.expires_at = now() + datetime.timedelta(seconds=token_result['expires_in'])
            auth.save(update_fields=['token', 'expires_at', 'updated_at'])
            return auth.token
        return None

    return auth.token

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'



def checkUserRole(request):
    username = request.GET['username']
    role = Users.objects.filter(username=username).values('role')
    if role:
        return JsonResponse({'role': role[0]})


def UserLogout(request):
    logout(request)
    return redirect('webapp:login')


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        # 👇️ if passed in object is instance of Decimal
        # convert it to a string
        if isinstance(obj, Decimal):
            return str(obj)
        # 👇️ otherwise use the default behavior
        return json.JSONEncoder.default(self, obj)

def format_date(date_str):
    try:
        # Parse input in dd-mm-yyyy format
        date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
        return date
    except ValueError:
        return None

@csrf_exempt
def UserLogin(request):
    """User login with Remita token generation"""

    if request.method != "POST":
        return render(request, "index.html")

    try:
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect("webapp:login")

        user = authenticate(request, username=username, password=password)

        if not user:
            messages.error(request, "Username/Password not registered.")
            return redirect("webapp:login")

        # ----------------------------
        # Get Remita Credentials
        # ----------------------------
        remita_username = getattr(settings, "REMITA_API_PUBLIC_KEY", None)
        remita_password = getattr(settings, "REMITA_API_SECRET_KEY", None)

        remita_ok = False
        access_token = None
        expires_in = 3600  # default fallback

        if remita_username and remita_password:
            token_result = get_remita_token(remita_username, remita_password)
            print("Remita response:", token_result)

            if isinstance(token_result, dict):
                if token_result.get("success"):
                    try:
                        access_token = (
                            token_result.get("response_data", {})
                            .get("data", [{}])[0]
                            .get("accessToken")
                        )
                        expires_in = int(token_result.get("expires_in", 3600))
                        remita_ok = True
                    except Exception as e:
                        print("Token parsing error:", str(e))

        # ----------------------------
        # Save Remita Token If Success
        # ----------------------------
        if remita_ok and access_token:
            expires_at = now() + datetime.timedelta(seconds=expires_in)

            auth = RemitaAuth.objects.first()

            if not auth:
                RemitaAuth.objects.create(
                    token=access_token,
                    expires_at=expires_at,
                )
            else:
                auth.token = access_token
                auth.expires_at = expires_at
                auth.save(update_fields=["token", "expires_at", "updated_at"])

            print(f"Remita token saved. Expires in {expires_in} seconds.")
        else:
            messages.warning(
                request,
                "Login successful, but payment service unavailable."
            )

        # ----------------------------
        # Login User
        # ----------------------------
        login(request, user)

        # ----------------------------
        # Role-based Redirect
        # ----------------------------
        if user.role == "001":
            return redirect("webapp:bank-details")
        elif user.role == "002":
            return redirect("webapp:homepage")
        else:
            return redirect("webapp:homepage")

    except Exception as e:
        print("Login error:", str(e))
        messages.error(request, "An unexpected error occurred.")
        return redirect("webapp:login")
"""
Functions to Handle Vendor Bank Details Upload and Validation

"""




def loadBankList(request):
    """Fetch the list of banks from Remita API (GET request)."""
    transaction_headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "Authorization": f"Bearer {check_and_refresh_token()}",
    }

    try:
        # Make a GET request to the Remita API
        resp = requests.get(
            url=getattr(settings, 'REMITA_API_BANK_LIST_URL',"https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/banks"),
            headers=transaction_headers,
            verify=False
        )

        print("Raw bank list response:", resp.text)

        data = resp.json()

        # ✅ Handle API error properly
        if data.get("status") != "00":
            return JsonResponse(
                {
                    "success": False,
                    "status": data.get("status"),
                    "message": data.get("message", "Failed to fetch bank list"),
                },
                status=400
            )

        # ✅ Extract and return only the bank list
        bank_list = data.get("data", {}).get("banks", [])
        return JsonResponse(bank_list, safe=False)

    except requests.exceptions.RequestException as e:
        print(f"Network error while fetching bank list: {e}")
        return JsonResponse({"error": "Network error while fetching bank list"}, status=500)

    except ValueError:
        return JsonResponse({"error": "Invalid JSON from API"}, status=500)




def checkVendorDetails(request):
    acc = request.GET.get('account_no')
    vendor_id = request.GET.get('vendor_id')
    response = BankDetails.objects.filter(account_no=acc, vendor_id=vendor_id).exists()
    return JsonResponse({'response': response})


def checkVendor(request):
    vendor_id = request.GET.get('vendor_id')
    exists = Apven.objects.using('ABSDAT').filter(vendorid__icontains=vendor_id).exists()
    return JsonResponse({'response': exists})


def delete_vendor(requst, acc_no):
    vendor = BankDetails.objects.filter(account_no=acc_no).all()
    if vendor:
        vendor.delete()
        return redirect('webapp:bank-details')


@login_required(login_url="/")
@user_is_support_staff
def bankUploadViaForm(request):
    """Uploads bank details and auto-fills bank name and details from Remita, with name enquiry validation."""
    form = BankDetailsForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        vendor = form.save(commit=False)
        bank_code = form.cleaned_data.get('bank_code')
        account_no = form.cleaned_data.get('account_no')

        transaction_headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "Authorization": f"Bearer {check_and_refresh_token()}",
        }

        try:
            # Fetch bank list to resolve bank name from bank code
            resp = requests.get(

                url=getattr(settings, 'REMITA_API_BANK_LIST_URL',"https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/banks"),
                headers=transaction_headers,
                verify=False
            )

            data = resp.json()
            bank_list = data.get("data", {}).get("banks", [])

            matched_bank = next((bank for bank in bank_list if bank.get("bankCode") == bank_code), None)

            if matched_bank:
                vendor.bank_name = matched_bank.get("bankName")
            else:
                vendor.bank_name = None

            # Perform name enquiry to validate account and get official account name
            token = check_and_refresh_token()
            enquiry = perform_name_enquiry(token, bank_code, account_no)
            if not enquiry.get('success'):
                # Add a form error and re-render the form without saving
                error_msg = enquiry.get('message') or 'Account not found during name enquiry.'
                form.add_error('account_no', error_msg)
                messages.error(request, error_msg)
                return render(request, 'account-details.html', {'form': form})

            # If successful, override account_name with response to ensure correctness
            vendor.account_name = enquiry.get('account_name') or vendor.account_name

            vendor.save()
            return redirect('webapp:bank-details')

        except Exception as e:
            print(f"Error during bank details processing: {e}")
            return HttpResponse("An error occurred while saving bank details.", status=500)

    return render(request, 'account-details.html', {'form': form})



@login_required(login_url="/")
@user_is_support_staff
def editBankUploadViaForm(request, acc_id):
    """Edit bank details, refetch updated bank info from Remita, and validate via name enquiry."""
    vendor = BankDetails.objects.filter(account_no=acc_id).first()
    if not vendor:
        return HttpResponse("Bank record not found.", status=404)

    form = BankDetailsForm(request.POST or None, instance=vendor)

    if request.method == 'POST' and form.is_valid():
        vendor = form.save(commit=False)
        bank_code = form.cleaned_data.get('bank_code')
        account_no = form.cleaned_data.get('account_no')

        transaction_headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "Authorization": f"Bearer {check_and_refresh_token()}",
        }

        try:
            # Refresh bank name based on bank code
            resp = requests.get(
                url=getattr(settings, 'REMITA_API_BANK_LIST_URL',"https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/banks"),
                headers=transaction_headers,
                verify=False
            )

            data = resp.json()
            bank_list = data.get("data", {}).get("banks", [])

            matched_bank = next((bank for bank in bank_list if bank.get("bankCode") == bank_code), None)

            if matched_bank:
                vendor.bank_name = matched_bank.get("bankName")
            else:
                vendor.bank_name = None

            # Perform name enquiry before saving changes
            token = check_and_refresh_token()
            enquiry = perform_name_enquiry(token, bank_code, account_no)
            if not enquiry.get('success'):
                error_msg = enquiry.get('message') or 'Account not found during name enquiry.'
                form.add_error('account_no', error_msg)
                messages.error(request, error_msg)
                return render(request, 'edit-vendor-bank.html', {'form': form, 'acc_id': vendor.account_no})

            vendor.account_name = enquiry.get('account_name') or vendor.account_name

            vendor.save()
            return redirect('webapp:bank-details')

        except Exception as e:
            print(f"Error during bank details update: {e}")
            return HttpResponse("An error occurred while updating bank details.", status=500)

    return render(request, 'edit-vendor-bank.html', {'form': form, 'acc_id': vendor.account_no})

@login_required(login_url='/')
@user_is_support_staff
def vendorBankDetails(request):
    data = BankDetails.objects.all()
    paginator = Paginator(data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'bank_details': page_obj,
    }
    return render(request, 'vendor-bank-details.html', context)


@login_required(login_url="/")
@user_is_support_staff
def searchvendorBankDetails(request):
    if request.method == 'GET':
        vendor = request.GET['vendor']
        data = BankDetails.objects.filter(account_name__contains=vendor).all()

        paginator = Paginator(data, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'bank_details': page_obj,
        }
        return render(request, 'vendor-bank-details.html', context)


def perform_name_enquiry(token, bank_code, account_number):
    """
    Perform name enquiry to validate account details before transfer

    Args:
        token: Bearer authentication token
        bank_code: Bank code of the destination account
        account_number: Account number to validate

    Returns:
        dict: Response containing account name if successful, error otherwise
    """
    url = getattr(settings, 'REMITA_API_ACCOUNT_LOOKUP_URL',"https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/account/lookup")

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "sourceBankCode": bank_code,
        "sourceAccount": account_number
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response_data = response.json()

        if response.status_code == 200 and response_data.get('status') == '00':
            return {
                'success': True,
                'data': response_data.get('data', {}),
                'account_name': response_data.get('data', {}).get('sourceAccountName', '')
            }
        else:
            return {
                'success': False,
                'message': response_data.get('message', 'Name enquiry failed'),
                'status': response_data.get('status', 'unknown')
            }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': f'Request error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}'
        }


"""

Functions to Approve and Post Transactions

"""
@login_required(login_url='/')
@user_is_approver
def homepage(request):
    # Build transactions grouped by DB alias for accordion display
    vendor_info = BankDetails.objects.all()
    vendors = [vendor.vendor_id for vendor in vendor_info]

    # Build processed invoice IDs per project to avoid cross-project collisions
    processed_map: Dict[int, set] = {}
    for row in ProcessedDeposits.objects.values('project_id', 'invoiceid'):
        pid = row['project_id'] or 1
        inv = (row['invoiceid'] or '').strip()
        processed_map.setdefault(pid, set()).add(inv)
    friendly_names = dict(Projects.objects.values_list('project_code', 'project_name'))
    # Determine available SQL Server aliases from settings (exclude default)
    sql_aliases = [k for k in settings.DATABASES.keys() if k != 'default']

    transactions_by_db_list: List[Dict[str, Any]] = []

    for alias in sql_aliases:
        try:
            # Resolve project id from Projects model using alias as project_code
            try:
                proj_id = Projects.objects.filter(project_code=alias).values_list('id', flat=True).first() or 1
            except Exception:
                proj_id = 1

            processed_for_proj = processed_map.get(proj_id, set())

            payments_qs = (
                Appym.objects.using(alias)
                .filter(datermit__gt=20250501)
                .exclude(idinvc__in=processed_for_proj)
                .order_by('-cntbtch')
            )
            if not payments_qs.exists():
                continue

            batch_list = list(payments_qs.values_list('cntbtch', flat=True))
            refs = Aptcr.objects.using(alias).filter(cntbtch__in=batch_list).values('cntbtch','cntentr', 'textrmit')
            ref_map = {f"{r.get('cntbtch')}-{r.get('cntentr')}": (r.get('textrmit') or '').strip() for r in refs}

            txns = []
            for payment in payments_qs:
                key = f'{payment.cntbtch}-{payment.cntitem}'
                print(key)
                date = change_date(str(payment.datermit))
                amount = round(payment.amtpaym, 2)
                txns.append({
                    'IDINVC': (payment.idinvc or '').strip(),
                    'DATERMIT': date,
                    'AMTPAYM': amount,
                    'IDVEND': (payment.textpayor or '').strip().upper(),
                    'REFERENCE': ref_map.get(key, ''),
                })
            if txns:
                # Individual pagination per accordion group
                try:
                    per_page = int(request.GET.get('per_page', 25))
                except Exception:
                    per_page = 25
                page_key = f"page_{alias}"
                page_num = request.GET.get(page_key, 1)
                paginator = Paginator(txns, per_page)
                page_obj = paginator.get_page(page_num)

                transactions_by_db_list.append({
                    'alias': alias,
                    'display_name': friendly_names.get(alias, alias),
                    'project_id': proj_id,
                    'transactions': list(page_obj.object_list),
                    'total_count': len(txns),
                    'page_obj': page_obj,
                    'page_key': page_key,
                })
        except Exception as e:
            # Skip problematic aliases but continue others
            print(f"Error fetching from {alias}: {e}")
            continue

    context = {
        'transactions_by_db': transactions_by_db_list,
        'vendor_info': vendor_info,
        'source_banks': SourceBankDetails.objects.all(),
    }

    return render(request, 'homepage.html', context)

@login_required(login_url='/')
@user_is_approver
@login_required(login_url='/')
@user_is_approver
def transaction_history(request):
    data = ProcessedDeposits.objects.exclude(status=2).order_by('-timestamp')
    paginator = Paginator(data, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    all_data = data.filter(timestamp__month__in=range(1, 13))
    grouped_data = groupby(all_data, key=attrgetter('timestamp.month'))
    monthly_data = {month: 0 for month in range(1, 13)}
    for month, data in grouped_data:
        monthly_data[month] = len(list(data))
    monthly_data = [{'month': datetime.date(1900, month, 1).strftime('%B'), 'data': count} for month, count in
                    monthly_data.items()]
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)

    date_range = [end_date - datetime.timedelta(days=x) for x in range(7)]
    processed_deposits = ProcessedDeposits.objects.filter(timestamp__date__range=(start_date, end_date))
    processed_deposits = processed_deposits.annotate(trans_date=TruncDate('timestamp')).values('trans_date').annotate(
        count=Count('trans_date'))
    date_dict = {deposit['trans_date'].strftime('%Y-%m-%d'): deposit['count'] for deposit in processed_deposits}
    date_list = [date.strftime('%Y-%m-%d') for date in date_range]
    count_list = [date_dict.get(date.strftime('%Y-%m-%d'), 0) for date in date_range]

    # Build query string excluding page parameter for paginator links
    qs_mut = request.GET.copy()
    qs_mut.pop('page', None)
    query_string = qs_mut.urlencode()

    context = {
        'transaction_info': page_obj,
        'date_list': date_list,
        'count_list': count_list,
        'data_by_month': monthly_data,
        'query_string': query_string,
        'active_filters': {
            'filter_options': '',
            'search_params': ''
        },
        'has_active_filters': False  # Add this line
    }
    return render(request, "transaction-history.html", context)


def transaction_history_xls(request):
    try:
        if request.method == 'GET':
            start_date_raw = request.GET.get('start_date')
            end_date_raw = request.GET.get('end_date')
            start_date = format_date(start_date_raw)
            end_date = format_date(end_date_raw)
            values = ProcessedDeposits.objects.filter(timestamp__range=(start_date, end_date)).exclude(status=2).values(
                'amount', 'invoiceid','timestamp', 'transaction_date', 'transaction_type',
                'vendorid', 'vendorname')

            df = pd.DataFrame.from_records(values)
            if not df.empty:
                df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d')
            # Add the title and column names
            title_row = ['Transaction History']
            column_names = ['Amount', 'Sage Invoice ID', 'Posting Date/Time', 'Transaction Date',
                            'Transaction Type', 'Vendor ID', 'Vendor Name']
            data_rows = [column_names] + df.values.tolist()
            data_rows.insert(0, title_row)

            # Create a temporary file path
            temp_file_path = os.path.join(tempfile.gettempdir(), 'transaction_history.xlsx')

            # Write the DataFrame to the Excel file
            with pd.ExcelWriter(temp_file_path, engine='xlsxwriter', options={'remove_timezone': True}) as writer:
                workbook = writer.book
                worksheet = workbook.add_worksheet('Transaction History')
                for row_num, row_data in enumerate(data_rows):
                    for col_num, cell_data in enumerate(row_data):
                        worksheet.write(row_num, col_num, cell_data)

            # Read the Excel file content
            with open(temp_file_path, 'rb') as file:
                excel_data = file.read()

            # Delete the temporary file
            # os.remove(temp_file_path)

            response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=Transaction_History_{start_date_raw}_{end_date_raw}.xlsx'
            return response
        else:
            return HttpResponse('Get Requests Only')
    except Exception as e:
        print(e)
        return HttpResponse(f'The error {e} occurred while processing your request')

def get_search_results(request):
    """ Get search results for homepage accordion, preserving grouped structure. """
    if request.method != 'GET':
        return JsonResponse({'message': 'Only GET requests are allowed'}, status=400)

    try:
        vendor_info = BankDetails.objects.all()
        allowed_vendor_ids = [v.vendor_id for v in vendor_info]

        search_params = (request.GET.get('search_params') or '').strip()
        field_option = (request.GET.get('filter_options') or '').strip()

        # Determine available SQL Server aliases from settings (exclude default)
        friendly_names = dict(Projects.objects.values_list('project_code', 'project_name'))
        sql_aliases = [k for k in settings.DATABASES.keys() if k != 'default']

        transactions_by_db_list: List[Dict[str, Any]] = []

        for alias in sql_aliases:
            try:
                proj_id = Projects.objects.filter(project_code=alias).values_list('id', flat=True).first() or 1

                payments_qs = (
                    Appym.objects.using(alias)
                    .filter(idvend__in=allowed_vendor_ids)
                    .order_by('-cntbtch')
                )

                # Apply filter
                if field_option and search_params:
                    if field_option == 'vendor_id':
                        payments_qs = payments_qs.filter(idvend__icontains=search_params)
                    elif field_option == 'invoice_id':
                        payments_qs = payments_qs.filter(idinvc__icontains=search_params)
                    elif field_option == 'amount':
                        try:
                            amt = Decimal(str(search_params))
                            payments_qs = payments_qs.filter(amtpaym=amt)
                        except Exception:
                            payments_qs = payments_qs.none()
                    elif field_option == 'date':
                        # datermit is numeric YYYYMMDD
                        if search_params.isdigit():
                            payments_qs = payments_qs.filter(datermit=int(search_params))
                        else:
                            payments_qs = payments_qs.none()

                if not payments_qs.exists():
                    continue

                batch_list = list(payments_qs.values_list('cntbtch', flat=True))
                refs = Aptcr.objects.using(alias).filter(cntbtch__in=batch_list).values('cntbtch','cntentr','textrmit')
                ref_map = {f"{r['cntbtch']}-{r['cntentr']}": (r['textrmit'] or '').strip() for r in refs}

                txns = []
                for payment in payments_qs:
                    key = f"{str(payment.cntbtch)}-{str(payment.cntitem)}"
                    date_fmt = change_date(str(payment.datermit)) if str(payment.datermit).isdigit() else payment.datermit
                    amount = round(payment.amtpaym, 2)
                    txns.append({
                        'IDINVC': (payment.idinvc or '').strip(),
                        'DATERMIT': date_fmt,
                        'AMTPAYM': amount,
                        'IDVEND': (payment.textpayor or '').strip().upper(),
                        'REFERENCE': ref_map.get(key, ''),
                    })

                if txns:
                    try:
                        per_page = int(request.GET.get('per_page', 25))
                    except Exception:
                        per_page = 25
                    page_key = f"page_{alias}"
                    page_num = request.GET.get(page_key, 1)
                    paginator = Paginator(txns, per_page)
                    page_obj = paginator.get_page(page_num)

                    transactions_by_db_list.append({
                        'alias': alias,
                        'display_name': friendly_names.get(alias, alias),
                        'project_id': proj_id,
                        'transactions': list(page_obj.object_list),
                        'total_count': len(txns),
                        'page_obj': page_obj,
                        'page_key': page_key,
                    })
            except Exception as e:
                print(f"Error fetching from {alias} (filtered): {e}")
                continue

        context = {
            'transactions_by_db': transactions_by_db_list,
            'vendor_info': vendor_info,
        }
        return render(request, 'homepage.html', context)

    except Exception as e:
        return JsonResponse({'message': f'An error occurred while processing your request {e}'}, status=500)

def get_history_search_results(request):
    """Filter transaction history by provided criteria and render the history page.
    Supported fields: invoice_id, vendor_id, vendor_name, amount, status, batch, processed_by, project, date.
    Query params:
      - filter_options: one of [invoice_id, vendor_id, vendor_name, amount, status, batch, processed_by, project, date]
      - search_params: value to search for (not used when filter_options=date)
      - start_date, end_date: optional when filter_options=date (accepts YYYY-MM-DD or dd-mm-YYYY)
    """
    search_params = (request.GET.get('search_params') or '').strip()
    field_option = (request.GET.get('filter_options') or '').strip()
    start_date_raw = (request.GET.get('start_date') or '').strip()
    end_date_raw = (request.GET.get('end_date') or '').strip()

    qs = ProcessedDeposits.objects.exclude(status=2)

    # Date range filter (when explicitly selected or when both dates are provided)
    def _parse_date(s: str):
        if not s:
            return None
        # Try ISO (YYYY-MM-DD)
        try:
            return datetime.date.fromisoformat(s)
        except Exception:
            pass
        # Try legacy dd-mm-YYYY via helper
        try:
            return format_date(s)
        except Exception:
            return None

    if field_option == 'date' or (start_date_raw and end_date_raw):
        start_date = _parse_date(start_date_raw)
        end_date = _parse_date(end_date_raw)
        if start_date and end_date:
            # Ensure start <= end
            if start_date > end_date:
                start_date, end_date = end_date, start_date
            qs = qs.filter(timestamp__date__range=(start_date, end_date))
        # When date filter is chosen, ignore generic search_params to avoid conflicts
        if field_option == 'date':
            search_params = ''

    # Field-based filters
    if field_option and search_params:
        if field_option == 'invoice_id':
            qs = qs.filter(invoiceid__icontains=search_params)
        elif field_option == 'vendor_id':
            qs = qs.filter(vendorid__icontains=search_params)
        elif field_option == 'vendor_name':
            qs = qs.filter(vendorname__icontains=search_params)
        elif field_option == 'amount':
            qs = qs.filter(amount__icontains=search_params)
        elif field_option == 'status':
            status_map = {
                'pending': 0, '0': 0,
                'success': 1, '1': 1,
                'failed': 2, '2': 2,
            }
            code = status_map.get(search_params.lower())
            if code is not None:
                qs = qs.filter(status=code)
            else:
                qs = qs.none()
        elif field_option == 'batch':
            qs = qs.filter(batch_identifier__icontains=search_params)
        elif field_option == 'processed_by':
            qs = qs.filter(processed_by__icontains=search_params)
        elif field_option == 'project':
            # allow by name or id
            if search_params.isdigit():
                qs = qs.filter(project_id=int(search_params))
            else:
                qs = qs.filter(project__project_name__icontains=search_params)

    qs = qs.order_by('-timestamp')

    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Graphs (use the current filtered queryset within last 7 days for counts)
    end_date_graph = datetime.date.today()
    start_date_graph = end_date_graph - datetime.timedelta(days=7)
    date_range = [end_date_graph - datetime.timedelta(days=x) for x in range(7)]

    processed_deposits = ProcessedDeposits.objects.filter(timestamp__date__range=(start_date_graph, end_date_graph))
    processed_deposits = processed_deposits.annotate(trans_date=TruncDate('timestamp')).values('trans_date').annotate(count=Count('trans_date'))
    date_dict = {deposit['trans_date'].strftime('%Y-%m-%d'): deposit['count'] for deposit in processed_deposits}
    date_list = [date.strftime('%Y-%m-%d') for date in date_range]
    count_list = [date_dict.get(date.strftime('%Y-%m-%d'), 0) for date in date_range]

    # Build query string excluding only page for paginator; retain date params for export
    qs_mut = request.GET.copy()
    qs_mut.pop('page', None)
    query_string = qs_mut.urlencode()

    context = {
        'transaction_info': page_obj,
        'page_number': page_number,
        'date_list': date_list,
        'count_list': count_list,
        'data_by_month': [
            {'month': datetime.date(1900, m, 1).strftime('%B'), 'data': ProcessedDeposits.objects.filter(timestamp__month=m).exclude(status=2).count()}
            for m in range(1, 13)
        ],
        'active_filters': {
            'filter_options': field_option,
            'search_params': search_params,
            'start_date': start_date_raw,
            'end_date': end_date_raw,
        },
        'query_string': query_string,
        'has_active_filters': bool(search_params or (start_date_raw and end_date_raw)),
    }

    return render(request, 'transaction-history.html', context)

def removetransaction(request, invoice_id, project_id):
        try:
            project = Projects.objects.get(id=project_id)
        except Projects.DoesNotExist:
            # Fallback to default project id=1 if not found
            project = Projects.objects.filter(id=1).first()
        processed = ProcessedDeposits(
            project=project,
            amount=0,
            transaction_date='',
            vendorid='',
            invoiceid=invoice_id,
            vendorname='',
            status=2,  # mark as removed/failed so it won’t be processed
            processed_by=request.user.username
        )
        processed.save()
        return redirect('webapp:homepage')



def vendor_account_details(request):
    account_name = request.GET['account_name']
    data = BankDetails.objects.filter(account_name__icontains=account_name).values('account_no', 'bank_code',
                                                                                   'bank_name')
    return JsonResponse({'account_details': list(data)}, status=200)


def change_date(date_str):
    date_obj = datetime.datetime.strptime(date_str, "%Y%m%d")
    formatted_date = date_obj.strftime("%d-%m-%Y")
    return formatted_date



def checkAccNumber(request):
    acc = request.GET.get('acc_name')
    print(acc)
    """account_number = BankDetails.objects.filter(account_name__icontains=acc).values('account_no')
    acc_no = [acc_no for acc_no in account_number]
    print(acc_no)"""
    data = {
        "service": "ZB0627",
        "request": {
            "accountNos": f"{acc}"
        }
    }
    response = requests.post(headers={"Content-Type": "application/json; charset=utf-8"},
                             json=data, verify=False)
    response = response.json()
    print(response)
    account_list = response['response']['accountList']
    return JsonResponse({'resp': list(account_list)})


def generate_unique_reference():
    """Generate a unique reference for bulk transactions"""
    unique_id = str(uuid.uuid4().int)[:5]
    return f"{unique_id}"




def initiate_bulk_payment(token, source_account_details, transactions, batch_ref=None):
    """
    Initiate bulk payment request

    Args:
        token: Bearer authentication token
        source_account_details: Dict containing source account info
            - sourceBankCode: Source bank code
            - sourceAccount: Source account number
            - sourceAccountName: Source account name
            - originalBankCode: Original bank code (if different from source)
            - originalAccountNumber: Original account number
        transactions: List of transaction dicts, each containing:
            - amount: Transaction amount
            - invoice_id: Invoice/transaction reference
            - account_no: Destination account number
            - bank_code: Destination bank code
            - account_name: Destination account name
            - remarks: Transaction narration/remarks

    Returns:
        dict: Response containing batch reference and status
    """
    url =  getattr(settings, 'REMITA_API_BULK_PAYMENT_URL',"https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/bulk/payment")

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Use provided batch reference if available, otherwise generate
    batch_ref = batch_ref

    # Calculate total amount
    total_amount = sum(float(t['amount']) for t in transactions)

    # Build transaction array
    transaction_items = []
    for idx, trans in enumerate(transactions, 1):
        # Prefer client-provided transaction reference; otherwise generate a unique one
        trans_ref = trans.get('transaction_ref')
        # Build destination narration and include invoice id
        base_narr = trans.get('remarks', 'Bulk Transfer')
        inv_id = trans.get('invoice_id')
        if inv_id:
            dest_narr = f"{base_narr} | TransactionId: {inv_id}"
        else:
            dest_narr = base_narr

        transaction_items.append({
            "amount": float(trans['amount']),
            "transactionRef": trans_ref,
            "destinationBankCode": trans['bank_code'],
            "destinationAccount": trans['account_no'],
            "destinationAccountName": trans['account_name'],
            "destinationNarration": dest_narr
        })

    # Build request payload
    payload = {
        "batchRef": batch_ref,
        "customReference": batch_ref,
        "currency": "NGN",
        "totalAmount": total_amount,
        "sourceBankCode": source_account_details['sourceBankCode'],
        "sourceAccount": source_account_details['sourceAccount'],
        "sourceAccountName": source_account_details['sourceAccountName'],
        "originalBankCode": source_account_details.get('originalBankCode', source_account_details['sourceBankCode']),
        "originalAccountNumber": source_account_details.get('originalAccountNumber',
                                                            source_account_details['sourceAccount']),
        "sourceNarration": source_account_details.get('sourceNarration', 'Bulk Payment Transaction'),
        "transactions": transaction_items
    }
    print(payload)
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response_data = response.json()

        return {
            'success': response.status_code == 200 and response_data.get('status') == '00',
            'batch_ref': batch_ref,
            'response': response_data,
            'status_code': response.status_code,
            'message': response_data.get('message', 'Unknown response')
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'batch_ref': batch_ref,
            'message': f'Request error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'batch_ref': batch_ref,
            'message': f'Error: {str(e)}'
        }


def check_bulk_payment_status_summary(token, batch_ref):
    """
    Check overall status of bulk payment batch

    Args:
        token: Bearer authentication token
        batch_ref: Batch reference from initiate_bulk_payment

    Returns:
        dict: Summary of batch status including success/failed counts
    """
    url =getattr(settings, 'REMITA_API_BULK_PAYMENT_STATUS_URL',f"https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/bulk/payment/status/{batch_ref}")

    headers = {
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response_data = response.json()

        if response.status_code == 200 and response_data.get('status') == '00':
            data = response_data.get('data', {})
            return {
                'success': True,
                'batch_ref': data.get('batchPaymentIdentifier'),
                'status': data.get('status'),
                'total_debit_amount': data.get('totalDebitAmount'),
                'total_credited_amount': data.get('totalCreditedAmount'),
                'transaction_count': data.get('transactionCount'),
                'successful_transactions': data.get('successfulTransactions'),
                'failed_transactions': data.get('failedTransactions'),
                'raw_response': response_data
            }
        else:
            return {
                'success': False,
                'message': response_data.get('message', 'Status check failed'),
                'status': response_data.get('status')
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error checking status: {str(e)}'
        }


def check_bulk_payment_details(token, batch_ref):
    """
    Get detailed status of each transaction in bulk payment batch

    Args:
        token: Bearer authentication token
        batch_ref: Batch reference from initiate_bulk_payment

    Returns:
        dict: Detailed status of each transaction in the batch
    """
    url = getattr(settings, 'REMITA_API_BULK_PAYMENT_DETAILS_URL', f"https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/bulk/payment/details/{batch_ref}")

    headers = {
        'Authorization': f'Bearer {token}'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response_data = response.json()

        if response.status_code == 200 and response_data.get('status') == '00':
            return {
                'success': True,
                'data': response_data.get('data', {}),
                'transactions': response_data.get('data', {}).get('transactions', []),
                'raw_response': response_data
            }
        else:
            return {
                'success': False,
                'message': response_data.get('message', 'Details check failed'),
                'status': response_data.get('status')
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error checking details: {str(e)}'
        }

def create_entry(project_id, batch_ref, transaction, processed_by, status):
    project = Projects.objects.get(id=project_id)

    deposit = ProcessedDeposits.objects.create(
        project=project,
        batch_identifier=batch_ref,
        invoiceid=transaction.get('invoice_id', ''),
        transaction_ref=transaction.get('transaction_ref'),
        vendorid=transaction.get('vendor_id', ''),
        vendorname=transaction.get('account_name', ''),
        transaction_date=transaction.get('date', ''),
        amount=str(transaction.get('amount', 0)),
        status=status,
        processed_by=processed_by
    )

    return deposit
def log_processed_deposit(project_id, batch_ref, transaction, status_code, processed_by,
                          transaction_type='BULK_TRANSFER'):
    """
    Log a processed transaction to the database

    Args:
        project_id: Project ID
        batch_ref: Batch reference from bulk payment
        transaction: Transaction dict with details
        status_code: Status code from API (00=success, others=pending/failed)
        processed_by: Username of person who initiated the transaction
        transaction_type: Type of transaction (default: BULK_TRANSFER)

    Returns:
        ProcessedDeposits object or None if error
    """

    try:
        # Determine status based on status code
        # Status: 0=Pending, 1=Success, 2=Failed
        if status_code == '00':
            status = 1  # Success
            create_entry(project_id, batch_ref, transaction, processed_by, status)
        elif status_code in ['01', '02', '04', '13', '16', '17', '18', '22', '24',
                             '26', '27', '28', '29', '30', '31', '33', '34', '36',
                             '37', '38', '42', '43', '44', '46', '50', '51', '54',
                             '55', '58', '59', '60', '65', '68', '71', '72', '74',
                             '75', '76', '77', '78', '79', '91', '94', '96']:
            status = 2  # Failed
            # Don't create entry for failed transactions
            return None
        else:
            status = 0  # Pending (all other codes including 001, 61, 07, 09, etc.)
            create_entry(project_id, batch_ref, transaction, processed_by, status)

    except Exception as e:
        print(f"Error logging deposit: {str(e)}")
        traceback.print_exc()
        return None

def delete_pending_transactions(request, invoice_id, project_id):
    try:
        pending = ProcessedDeposits.objects.get(status=0, invoiceid=invoice_id, project_id=project_id)
        pending.delete()
        messages.success(request, f'Pending transaction {invoice_id} has been deleted successfully.')
        return redirect('webapp:transaction-history')
    except ProcessedDeposits.DoesNotExist:
        messages.error(request, f'No pending transaction found with invoice ID {invoice_id} for this project.')
        return redirect('webapp:transaction-history')
    except Exception as e:
        messages.error(request, f'Error deleting transaction: {str(e)}')
        return redirect('webapp:transaction-history')

def update_transaction_status(invoice_id, status_code, response_message=''):
    """
    Update the status of existing transaction(s) matching the invoice ID.
    Note: Invoice IDs can collide across projects, so we do not assume global uniqueness.

    Args:
        invoice_id: Invoice ID to update
        status_code: New status code from API
        response_message: Optional message from API response

    Returns:
        bool: True if any record updated successfully, False otherwise
    """

    try:
        # Determine status based on status code
        if status_code == '00':
            status = 1  # Success
        elif status_code in ['01', '02', '04', '13', '16', '17', '18', '22', '24',
                             '26', '27', '28', '29', '30', '31', '33', '34', '36',
                             '37', '38', '42', '43', '44', '46', '50', '51', '54',
                             '55', '58', '59', '60', '65', '68', '71', '72', '74',
                             '75', '76', '77', '78', '79', '91', '94', '96']:
            status = 2  # Failed
        else:
            status = 0  # Pending

        updated = ProcessedDeposits.objects.filter(invoiceid=invoice_id).update(status=status)
        if updated:
            print(f"Updated {updated} transaction(s) with invoice {invoice_id} to status {status}")
            return True
        else:
            print(f"Transaction {invoice_id} not found")
            return False
    except Exception as e:
        print(f"Error updating transaction status: {str(e)}")
        return False

def post_transactions(request):
    """
    Django view to handle bulk payment posting
    Integrates with existing transaction data structure and logs all transactions
    """
    if request.method == 'POST':
        try:
            # Check and get valid token
            secret_key = check_and_refresh_token(request)
            if not secret_key:
                return JsonResponse({
                    'success': False,
                    'message': 'Payment service unavailable. Please logout and login again.',
                    'error': 'No valid authentication token'
                }, status=401)

            # Parse incoming transactions
            transacs = json.loads(request.POST.get('transactions'))
            project_id = request.POST.get('project_id', 1)
            processed_by = request.user.username if hasattr(request, 'user') else 'system'

            # Optional mapping of invoice_id -> client-generated transaction_ref
            tx_refs_raw = request.POST.get('transaction_refs')
            tx_refs = {}
            try:
                if tx_refs_raw:
                    tx_refs = json.loads(tx_refs_raw)
            except Exception:
                tx_refs = {}

            print("Raw transactions:", transacs)

            transactions = []
            for entry in transacs:
                values = entry['values']
                entry_project_id = entry.get('project_id') or project_id or 1
                inv_id = values[2]
                transaction_element = {
                    'date': values[0],
                    'amount': values[1],
                    'invoice_id': inv_id,
                    'remarks': values[3],
                    'vendor_id': values[4],
                    'account_name': values[5],
                    'account_no': values[7],
                    'bank_code': values[8],
                    'bank_name': values[9],
                    'email': values[10] if len(values) > 10 else '',
                    'project_id': int(entry_project_id),
                }
                # Attach client transaction_ref if provided
                if inv_id in tx_refs:
                    transaction_element['transaction_ref'] = tx_refs.get(inv_id)
                transactions.append(transaction_element)


            # Get source account details from selected SourceBankDetails model (fallback to settings if not provided)
            source_bank_id = request.POST.get('source_bank_id')
            source_account_details = None
            if source_bank_id:
                try:
                    sb = SourceBankDetails.objects.get(pk=int(source_bank_id))
                    source_account_details = {
                        'sourceBankCode': sb.bank_code,
                        'sourceAccount': sb.bank_account_number,
                        'sourceAccountName': sb.bank_account_name,
                        'originalBankCode': sb.bank_code,
                        'originalAccountNumber': sb.bank_account_number,
                        'sourceNarration': request.POST.get('narration', 'Bulk Payment Transaction')
                    }
                except Exception as _e:
                    # Fallback to settings if invalid id
                    pass
            if not source_account_details:
                source_account_details = {
                    'sourceBankCode': getattr(settings, 'REMITA_SOURCE_BANK_CODE', '058'),
                    'sourceAccount': getattr(settings, 'REMITA_SOURCE_ACCOUNT_NO', '0581426964'),
                    'sourceAccountName': getattr(settings, 'REMITA_SOURCE_ACCOUNT_NAME', 'ABC'),
                    'originalBankCode': getattr(settings, 'REMITA_SOURCE_BANK_CODE', '058'),
                    'originalAccountNumber': getattr(settings, 'REMITA_SOURCE_ACCOUNT_NO', '0581426964'),
                    'sourceNarration': request.POST.get('narration', 'Bulk Payment Transaction')
                }

            # Optional: Check balance before initiating

            # Initiate bulk payment (use client-provided batch_ref if available)
            client_batch_ref = request.POST.get('batch_ref')
            result = initiate_bulk_payment(secret_key, source_account_details, transactions, batch_ref=client_batch_ref)
            batch_ref = result['batch_ref']
            # Log all transactions to database regardless of success/failure
            logged_count = 0
            for transaction in transactions:
                # Get status code from response
                status_code = result.get('response', {}).get('status', '81')  # Default to pending

                log_processed_deposit(
                    project_id=transaction.get('project_id', project_id),
                    batch_ref=batch_ref,
                    transaction=transaction,
                    status_code=status_code,
                    processed_by=request.user,
                    transaction_type='BULK_TRANSFER'
                )



            if result['success']:
                return JsonResponse({
                    'success': True,
                    'message': 'Bulk payment initiated successfully',
                    'batch_ref': batch_ref,
                    'logged_transactions': logged_count,
                    'total_transactions': len(transactions),
                    'data': result['response']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': result['message'],
                    'batch_ref': batch_ref,
                    'logged_transactions': logged_count,
                    'total_transactions': len(transactions),
                    'data': result.get('response')
                }, status=400)

        except Exception as e:
            print(f"Error processing transactions: {str(e)}")

            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': 'Error processing transactions',
                'error': str(e)
            }, status=500)

    return JsonResponse({'message': 'GET Request Not Allowed'}, status=400)


def check_transaction_status(request, batch_ref):
    """
    Check status for a previous bulk payment batch and return ONLY the minimal schema:
    {
        "status": "00" | <code>,
        "message": <string>,
        "meta": null,
        "links": null,
        "code": null,
        "data": {
            "transactions": [{"paymentIdentifier": str, "status": str}, ...],
            "pagination": { ... } | null
        }
    }
    """
    if request.method != 'GET':
        return JsonResponse({'message': 'Only GET requests allowed'}, status=400)

    try:
        # Acquire/refresh token
        secret_key = check_and_refresh_token(request)
        if not secret_key:
            # Follow the minimal schema even for auth errors
            return JsonResponse({
                'status': '401',
                'message': 'Authentication required',
                'meta': None,
                'links': None,
                'code': None,
                'data': {
                    'transactions': [],
                    'pagination': None
                }
            }, status=401)

        # Fetch detailed status from provider
        details = check_bulk_payment_details(secret_key, batch_ref)

        # Extract transactions (only the required fields)
        transactions = []
        try:
            for t in details.get('transactions') or ((details.get('data') or {}).get('transactions') or []):
                transactions.append({
                    'paymentIdentifier': t.get('paymentIdentifier'),
                    'status': t.get('status')
                })
        except Exception:
            transactions = []

        # Extract pagination if present
        pagination = None
        try:
            pagination = (details.get('data') or {}).get('pagination')
        except Exception:
            pagination = None

        # Determine top-level status/message
        raw = details.get('raw_response') or {}
        top_status = None
        top_message = None
        if isinstance(raw, dict):
            top_status = raw.get('status')
            top_message = raw.get('message')
        if not top_status:
            top_status = details.get('status') or ('00' if details.get('success') else '99')
        if not top_message:
            top_message = details.get('message') or ('Approved or completed successfully' if details.get('success') else 'Details check failed')

        # Return exactly the requested schema
        return JsonResponse({
            'status': top_status,
            'message': top_message,
            'meta': None,
            'links': None,
            'code': None,
            'data': {
                'transactions': transactions,
                'pagination': pagination
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': '99',
            'message': str(e),
            'meta': None,
            'links': None,
            'code': None,
            'data': {
                'transactions': [],
                'pagination': None
            }
        }, status=500)


def get_beneficiary_details(request):
    """Get beneficiary bank details by vendor ID.
    
    Query params:
      - vendor_id: vendor ID (required)
    Returns JSON {account_name, account_no, bank_name, bank_code, vendor_id} or {error: message}
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET requests allowed'}, status=400)

    vendor_id = (request.GET.get('vendor_id') or '').strip()
    
    if not vendor_id:
        return JsonResponse({'error': 'Vendor ID is required'}, status=400)

    try:
        beneficiary = BankDetails.objects.filter(vendor_id=vendor_id).first()
        if beneficiary:
            return JsonResponse({
                'account_name': beneficiary.account_name,
                'account_no': beneficiary.account_no,
                'bank_name': beneficiary.bank_name,
                'bank_code': beneficiary.bank_code,
                'vendor_id': beneficiary.vendor_id
            })
        else:
            return JsonResponse({'error': f'No bank details found for vendor {vendor_id}'}, status=404)
            
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)


def live_search_bank_details(request):
    """Live search endpoint for bank details by account name.

    Query params:
      - q: search term (required)
      - vendor_id: optional vendor filter to limit results to the row's vendor
      - limit: optional max results (default 20)
    Returns JSON {results: [{account_name, account_no, bank_name, bank_code, vendor_id}]}
    """
    if request.method != 'GET':
        return JsonResponse({'message': 'Only GET requests allowed'}, status=400)

    q = (request.GET.get('q') or '').strip()
    vendor_id = (request.GET.get('vendor_id') or '').strip()
    try:
        limit = int(request.GET.get('limit') or 20)
    except Exception:
        limit = 20

    if not q or len(q) < 2:
        return JsonResponse({'results': []})

    try:
        qs = BankDetails.objects.all()
        # Search by account_name icontains
        qs = qs.filter(account_name__icontains=q)

        qs = qs.values('account_name', 'account_no', 'bank_name', 'bank_code', 'vendor_id')[:limit]
        print('results' , qs)
        return JsonResponse({'results': list(qs)})
    except Exception as e:
        return JsonResponse({'message': f'Error: {e}'}, status=500)




REGISTRATION_SALT = 'user-registration-approval'


def _superuser_recipients():
    # superusers with valid email
    emails = list(Users.objects.filter(is_superuser=True).exclude(email__isnull=True).exclude(email='').values_list('email', flat=True))
    # optional fallback via settings.APPROVER_EMAILS if defined
    fallback = getattr(settings, 'APPROVER_EMAILS', [])
    for e in fallback:
        if e not in emails:
            emails.append(e)
    return emails


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # email superusers for approval
            token = signing.dumps({'uid': user.id}, salt=REGISTRATION_SALT)
            approve_url = request.build_absolute_uri(reverse('webapp:approve-registration', args=[token]))
            reject_url = request.build_absolute_uri(reverse('webapp:reject-registration', args=[token]))
            subject = 'New user registration pending approval'
            body = (
                f'A new user has registered and is pending approval.\n\n'
                f'Username: {user.username}\n'
                f'Role: {user.role}\n'
                f'Email: {user.email or "(not provided)"}\n\n'
                f'Approve: {approve_url}\n'
                f'Reject: {reject_url}\n\n'
                f'This link will expire in 7 days.'
            )
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')
            recipients = _superuser_recipients()
            if recipients:
                try:
                    send_mail(subject, body, from_email, recipients, fail_silently=True)
                except Exception:
                    pass
            messages.success(request, 'Registration submitted. You will receive an email once an administrator approves or rejects your request.')
            return redirect('webapp:login')
    else:
        form = RegistrationForm()
    return render(request, 'registration.html', {'form': form})


def approve_registration(request, token: str):
    try:
        data = signing.loads(token, max_age=7*24*3600, salt=REGISTRATION_SALT)
        uid = data.get('uid')
        user = Users.objects.get(id=uid)
    except Exception:
        return render(request, 'registration_result.html', {'title': 'Invalid or expired link', 'message': 'The approval link is invalid or has expired.'})

    if not user.is_active:
        user.is_active = True
        user.save(update_fields=['is_active'])
        # notify user
        if user.email:
            try:
                send_mail(
                    'Your account has been approved',
                    'Your registration has been approved. You can now sign in.',
                    getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
                    [user.email],
                    fail_silently=True
                )
            except Exception:
                pass
    return render(request, 'registration_result.html', {'title': 'User approved', 'message': f'User {user.username} has been approved.'})


def reject_registration(request, token: str):
    try:
        data = signing.loads(token, max_age=7*24*3600, salt=REGISTRATION_SALT)
        uid = data.get('uid')
        user = Users.objects.get(id=uid)
    except Exception:
        return render(request, 'registration_result.html', {'title': 'Invalid or expired link', 'message': 'The rejection link is invalid or has expired.'})

    username = user.username
    user_email = user.email
    # delete the pending user account
    user.delete()
    if user_email:
        try:
            send_mail(
                'Your account registration was rejected',
                'We are sorry, your payment portal registration has been rejected.',
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
                [user_email],
                fail_silently=True
            )
        except Exception:
            pass
    return render(request, 'registration_result.html', {'title': 'User rejected', 'message': f'User {username} has been rejected and removed.'})



@require_GET
def transaction_history_json(request):
    """Return transaction history as JSON within a date range for client-side PDF export."""
    start_date_raw = request.GET.get('start_date')
    end_date_raw = request.GET.get('end_date')
    if not start_date_raw or not end_date_raw:
        return JsonResponse({'success': False, 'message': 'start_date and end_date are required'}, status=400)

    try:
        start_date = format_date(start_date_raw)
        end_date = format_date(end_date_raw)

        # Filter only by date (ignoring time)
        qs = ProcessedDeposits.objects.filter(
            timestamp__date__range=(start_date, end_date)
        ).exclude(status=2)

        values = qs.values(
            'amount', 'invoiceid', 'timestamp', 'transaction_date', 'transaction_ref',
            'vendorid', 'vendorname', 'batch_identifier', 'status', 'processed_by', 'project__project_name'
        )

        rows = list(values)

        # Format timestamp to a simple date (if you only want the date in the JSON too)
        for r in rows:
            ts = r.get('timestamp')
            try:
                r['timestamp'] = ts.strftime('%Y-%m-%d') if ts else ''
            except Exception:
                r['timestamp'] = str(ts) if ts else ''

        return JsonResponse({'success': True, 'results': rows})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {e}'}, status=500)


def export_history_filtered(request):
    """Export filtered transaction history as an Excel file (XLSX).
    Reuses the same filter semantics as get_history_search_results.
    Accepts query params:
      - filter_options
      - search_params
      - start_date, end_date (dd-mm-YYYY)
    """
    try:
        if request.method != 'GET':
            return HttpResponse('Only GET requests are allowed', status=405)

        search_params = (request.GET.get('search_params') or '').strip()
        field_option = (request.GET.get('filter_options') or '').strip()
        start_date_raw = request.GET.get('start_date')
        end_date_raw = request.GET.get('end_date')

        qs = ProcessedDeposits.objects.exclude(status=2)

        # Date range filter
        try:
            if start_date_raw and end_date_raw:
                start_date = format_date(start_date_raw)
                end_date = format_date(end_date_raw)
                qs = qs.filter(timestamp__range=(start_date, end_date))
        except Exception:
            pass

        # Field-based filters
        if field_option and search_params:
            if field_option == 'invoice_id':
                qs = qs.filter(invoiceid__icontains=search_params)
            elif field_option == 'vendor_id':
                qs = qs.filter(vendorid__icontains=search_params)
            elif field_option == 'vendor_name':
                qs = qs.filter(vendorname__icontains=search_params)
            elif field_option == 'amount':
                qs = qs.filter(amount__icontains=search_params)
            elif field_option == 'status':
                status_map = {
                    'pending': 0, '0': 0,
                    'success': 1, '1': 1,
                    'failed': 2, '2': 2,
                }
                code = status_map.get(search_params.lower()) if isinstance(search_params, str) else None
                if code is not None:
                    qs = qs.filter(status=code)
                else:
                    qs = qs.none()
            elif field_option == 'batch':
                qs = qs.filter(batch_identifier__icontains=search_params)
            elif field_option == 'processed_by':
                qs = qs.filter(processed_by__icontains=search_params)
            elif field_option == 'project':
                if str(search_params).isdigit():
                    qs = qs.filter(project_id=int(search_params))
                else:
                    qs = qs.filter(project__project_name__icontains=search_params)

        qs = qs.order_by('-timestamp')

        values = qs.values(
            'amount',
            'invoiceid',
            'timestamp',
            'transaction_date',
            'vendorid',
            'vendorname',
            'project__project_name',
            'batch_identifier',
            'status',
            'processed_by',
        )

        df = pd.DataFrame.from_records(values)
        # Normalize/format columns
        if not df.empty:
            # Timestamp to string
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
            # Status to labels
            status_labels = {0: 'Pending', 1: 'Success', 2: 'Failed'}
            try:
                df['status'] = df['status'].map(status_labels).fillna('Unknown')
            except Exception:
                pass

        # Reorder and rename columns for readability
        desired_cols = [
            'amount', 'invoiceid', 'timestamp', 'transaction_date', 'vendorid', 'vendorname',
            'project__project_name', 'batch_identifier', 'status', 'processed_by'
        ]
        for col in desired_cols:
            if col not in df.columns:
                df[col] = ''
        df = df[desired_cols]
        df.columns = [
            'Amount', 'Payment Number', 'Posting Date/Time', 'Transaction Date', 'Beneficiary ID', 'Beneficiary Name',
            'Project', 'Batch', 'Status', 'Processed By'
        ]

        # Write to in-memory buffer
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter', options={'remove_timezone': True}) as writer:
            sheet_name = 'Filtered History'
            df.to_excel(writer, index=False, sheet_name=sheet_name)

        # Build filename
        if start_date_raw and end_date_raw:
            fname = f"Filtered_Transaction_History_{start_date_raw}_{end_date_raw}.xlsx"
        else:
            fname = "Filtered_Transaction_History.xlsx"

        resp = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        resp['Content-Disposition'] = f'attachment; filename="{fname}"'
        return resp
    except Exception as e:
        return HttpResponse(f'Error exporting filtered history: {e}', status=500)



def export_history_filtered_json(request):
    """Return filtered transaction history as JSON rows, reusing the same
    semantics as export_history_filtered. This enables client-side PDF export.
    Query params: filter_options, search_params, start_date, end_date (dd-mm-YYYY)
    """
    try:
        if request.method != 'GET':
            return JsonResponse({'success': False, 'message': 'Only GET allowed'}, status=405)

        search_params = (request.GET.get('search_params') or '').strip()
        field_option = (request.GET.get('filter_options') or '').strip()
        start_date_raw = request.GET.get('start_date')
        end_date_raw = request.GET.get('end_date')

        qs = ProcessedDeposits.objects.exclude(status=2)

        # Date range
        try:
            if start_date_raw and end_date_raw:
                start_date = format_date(start_date_raw)
                end_date = format_date(end_date_raw)
                qs = qs.filter(timestamp__range=(start_date, end_date))
        except Exception:
            pass

        # Field filters
        if field_option and search_params:
            if field_option == 'invoice_id':
                qs = qs.filter(invoiceid__icontains=search_params)
            elif field_option == 'vendor_id':
                qs = qs.filter(vendorid__icontains=search_params)
            elif field_option == 'vendor_name':
                qs = qs.filter(vendorname__icontains=search_params)
            elif field_option == 'amount':
                qs = qs.filter(amount__icontains=search_params)
            elif field_option == 'status':
                status_map = {
                    'pending': 0, '0': 0,
                    'success': 1, '1': 1,
                    'failed': 2, '2': 2,
                }
                code = status_map.get(search_params.lower()) if isinstance(search_params, str) else None
                if code is not None:
                    qs = qs.filter(status=code)
                else:
                    qs = qs.none()
            elif field_option == 'batch':
                qs = qs.filter(batch_identifier__icontains=search_params)
            elif field_option == 'processed_by':
                qs = qs.filter(processed_by__icontains=search_params)
            elif field_option == 'project':
                if str(search_params).isdigit():
                    qs = qs.filter(project_id=int(search_params))
                else:
                    qs = qs.filter(project__project_name__icontains=search_params)

        qs = qs.order_by('-timestamp')

        values = qs.values(
            'amount',
            'invoiceid',
            'timestamp',
            'transaction_date',
            'transaction_ref',
            'vendorid',
            'vendorname',
            'batch_identifier',
            'status',
            'processed_by',
            'project__project_name',
        )
        rows = list(values)
        for r in rows:
            ts = r.get('timestamp')
            try:
                r['timestamp'] = ts.strftime('%Y-%m-%d %H:%M:%S') if ts else ''
            except Exception:
                r['timestamp'] = str(ts) if ts else ''
        return JsonResponse({'success': True, 'results': rows})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error exporting filtered JSON: {e}'}, status=500)


@login_required(login_url='/')
def source_bank_details(request):
    banks = SourceBankDetails.objects.select_related('project').all().order_by('bank_name')
    context = {
        'source_banks': banks,
    }
    return render(request, 'source-bank-details.html', context)


@login_required(login_url='/')
def add_source_bank(request):
    if request.method == 'POST':
        form = SourceBankForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Source bank account added successfully.')
            return redirect('webapp:source-bank-details')
    else:
        form = SourceBankForm()
    return render(request, 'edit-source-bank.html', {'form': form, 'is_edit': False})


@login_required(login_url='/')
def edit_source_bank(request, pk: int):
    try:
        bank = SourceBankDetails.objects.get(pk=pk)
    except SourceBankDetails.DoesNotExist:
        messages.error(request, 'Source bank record not found.')
        return redirect('webapp:source-bank-details')

    if request.method == 'POST':
        form = SourceBankForm(request.POST, instance=bank)
        if form.is_valid():
            form.save()
            messages.success(request, 'Source bank account updated successfully.')
            return redirect('webapp:source-bank-details')
    else:
        form = SourceBankForm(instance=bank)

    return render(request, 'edit-source-bank.html', {'form': form, 'is_edit': True})
