import datetime
import io
import json
import os
import tempfile
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

from remita import settings
from .forms import BankDetailsForm
from .permissions import user_is_approver, user_is_support_staff
from .services import *
from .models import ProcessedDeposits, BankDetails, Users, UserLoginHistory, Appym, Aptcr, Apven
import requests
import pandas as pd

transaction_headers=["Content-Type: application/json; charset=utf-8"]

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


def check_and_refresh_token(request):
    """
    Check if token exists and is valid. Refresh if needed.
    Returns token or None if unavailable.
    """
    token = request.session.get('remita_token')
    token_expires = request.session.get('remita_token_expires')

    if not token or not token_expires:
        return None

    # Check if token has expired (with 5 minute buffer)
    current_time = now().timestamp()
    if current_time >= (token_expires - 300):
        # Token expired or about to expire, refresh it
        remita_username = getattr(settings, 'REMITA_API_PUBLIC_KEY', '2LEPNR6RZQAD0J7G')
        remita_password = getattr(settings, 'REMITA_API_SECRET_KEY', 'GZU4BP1PRAKPBE1SD27EW6HH2QMM0US5')

        token_result = get_remita_token(remita_username, remita_password)

        if token_result['success']:
            request.session['remita_token'] = token_result['token']
            request.session['remita_token_expires'] = (
                    now().timestamp() + token_result['expires_in']
            )
            return token_result['token']
        else:
            return None

    return token

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
        # Parse the input date string using the specified format
        date = datetime.datetime.strptime(date_str, "%d-%m-%Y")

        # Set the time portion to "00:00:00"
        formatted_date = date.replace(hour=0, minute=0, second=0)

        # Convert the formatted date to the desired string format
        formatted_date_str = formatted_date.strftime("%Y-%m-%d %H:%M:%S")

        return formatted_date_str
    except ValueError:
        # Handle invalid date strings
        return None


@csrf_exempt
def UserLogin(request):
    """User login with Remita token generation"""
    if request.method == 'POST':
        try:
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)

            if user:
                # Get Remita API credentials from settings
                remita_username = getattr(settings, 'REMITA_API_PUBLIC_KEY', '2LEPNR6RZQAD0J7G')
                remita_password = getattr(settings, 'REMITA_API_SECRET_KEY', 'GZU4BP1PRAKPBE1SD27EW6HH2QMM0US5')

                # Get Remita token
                token_result = get_remita_token(remita_username, remita_password)

                if token_result['success']:
                    # Store token in session
                    request.session['remita_token'] = token_result['token']
                    request.session['remita_token_expires'] = (
                            now().timestamp() + token_result['expires_in']
                    )
                    print(f"Remita token acquired successfully, expires in {token_result['expires_in']} seconds")

                    # Login user
                    login(request, user)

                    if user.role == '001':
                        return redirect('webapp:bank-details')
                    elif user.role == '002':
                        return redirect('webapp:homepage')
                else:
                    print(f"Failed to get Remita token: {token_result.get('error')}")
                    print(f"Response: {token_result.get('response_data')}")
                    messages.warning(
                        request,
                        message="Login successful, but payment service unavailable. Some features may be limited."
                    )
                    login(request, user)
                    if user.role == '001':
                        return redirect('webapp:bank-details')
                    elif user.role == '002':
                        return redirect('webapp:homepage')
            else:
                messages.error(request, message="Username/Password not registered")
                return redirect("webapp:login")

        except Exception as e:
            messages.error(request, message="An error occurred. Please try again.")
            print(f"Login error: {str(e)}")
            return redirect("webapp:login")
    else:
        return render(request, 'index.html')


"""
Functions to Handle Vendor Bank Details Upload and Validation

"""


def zicb_customer_account_number_check(request):
    account_no = request.GET['account_no']
    data = {
        "service": "ZB0627",
        "request": {
            "accountNos": f"{account_no}"
        }
    }
    response = requests.post(url=URL, headers={"Content-Type": "application/json; charset=utf-8", "authkey": API_KEY},
                             json=data, verify=False)
    response = response.json()
    account_list = response['response']['accountList']
    print(account_list)
    if account_list == []:
        return JsonResponse({'response': False}, safe=False)
    else:
        return JsonResponse({'response': account_list}, safe=False)


def other_bank_account_number_check(request):
    account_no = request.GET['account_no']
    serviceID = request.GET['service_id']
    data = {
        "service": "MT002",
        "request": {
            "payload": {
                "serviceID": f"{serviceID}",
                "accountNumber": f"{account_no}",
                "currencyCode": "ZMW",
                "countryCode": "260"
            }
        }
    }
    response = requests.post(url=URL,
                             headers={"Content-Type": "application/json; charset=utf-8", "authkey": API_KEY},
                             json=data, verify=False)
    response = response.json()
    print(response)
    if response["response"]["results"][0]["statusDescription"] == "Account number provided is valid":
        return JsonResponse({'response': response["response"]["results"]}, safe=False)
    else:
        return JsonResponse({'response': False})


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


def loadBankList(request):
    resp = requests.post(url=URL, headers=transaction_headers, json={"service": "BNK9901", "request": {}},
                         verify=False)
    resp = resp.json()
    if resp['operation_status'] == 'SUCCESS':
        resp = resp['response']['bankList']

        return JsonResponse(resp, safe=False)


@login_required(login_url="/")
@user_is_support_staff
def bankUploadViaForm(request):
    try:
        form = BankDetailsForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                if request.htmx:
                    return render(request, 'account-details.html', {'form': form})
                vendor = form.save(commit=False)
                sort_code = form.cleaned_data.get('sort_code')
                resp = requests.post(url=URL, headers=transaction_headers, json={"service": "BNK9901", "request": {}},
                                     verify=False)
                resp = resp.json()
                if resp['operation_status'] == 'SUCCESS':
                    resp = resp['response']['bankList']
                    for resp in resp:
                        if sort_code == resp['sortCode']:
                            bicCode = resp['bicCode']
                            vendor.bicCode = bicCode
                            vendor.save()
                            break
                    else:
                        bicCode = 'ZICB'
                        vendor.bicCode = bicCode
                        vendor.save()
                    return redirect('webapp:bank-details')
                else:
                    return HttpResponse(f'Error saving bank details, Try again later', status=500)

        return render(request, 'account-details.html', {'form': form})
    except Exception as e:
        print(e)


def bankUploadViaFormAddAnother(request):
    try:
        form = BankDetailsForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                if request.htmx:
                    return render(request, 'account-details.html', {'form': form})
                vendor = form.save(commit=False)
                sort_code = form.cleaned_data.get('sort_code')
                resp = requests.post(url=URL, headers=transaction_headers, json={"service": "BNK9901", "request": {}},
                                     verify=False)
                resp = resp.json()
                if resp['operation_status'] == 'SUCCESS':
                    resp = resp['response']['bankList']
                    for resp in resp:
                        if sort_code == resp['sortCode']:
                            bicCode = resp['bicCode']
                            vendor.bicCode = bicCode
                            vendor.save()
                            break
                    else:
                        bicCode = 'ZICB'
                        vendor.bicCode = bicCode
                        vendor.save()
                    return redirect('webapp:account-details')
                else:
                    return HttpResponse(f'Error saving bank details, Try again later', status=500)

        return render(request, 'account-details.html', {'form': form})
    except Exception as e:
        print(e)


def editBankUploadViaForm(request, acc_id):
    vendor = BankDetails.objects.filter(account_no=acc_id).first()
    form = BankDetailsForm(request.POST, instance=vendor)
    print(vendor)
    if request.method == 'POST':
        if form.is_valid():
            if request.htmx:
                return render(request, 'account-details.html', {'form': form})
            vendor = form.save(commit=False)
            sort_code = form.cleaned_data.get('sort_code')
            resp = requests.post(url=URL, headers=transaction_headers, json={"service": "BNK9901", "request": {}},
                                 verify=False)
            resp = resp.json()
            if resp['operation_status'] == 'SUCCESS':
                resp = resp['response']['bankList']
                for resp in resp:
                    if sort_code == resp['sortCode']:
                        bicCode = resp['bicCode']
                        vendor.bicCode = bicCode
                        vendor.save()
                        break
                else:
                    bicCode = 'ZICB'
                    vendor.bicCode = bicCode
                    vendor.save()
                return redirect('webapp:bank-details')

        else:
            render(request, 'edit-vendor-bank.html',
                   {'form': BankDetailsForm(instance=vendor), 'acc_id': vendor.account_no})

    return render(request, 'edit-vendor-bank.html', {'form': BankDetailsForm(instance=vendor),
                                                     'acc_id': vendor.account_no})


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
        data = BankDetails.objects.filter(vendor_id=vendor).all()

        paginator = Paginator(data, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'bank_details': page_obj,
        }
        return render(request, 'vendor-bank-details.html', context)


@login_required(login_url="/")
@user_is_support_staff
def bankUploadCSV(request):
    errors = []
    upload_errors = {}
    if request.method == 'POST':
        # try:
        file = request.FILES['csvupload']
        df = pd.read_excel(file, dtype={'account_no': str, 'vendor_id': str, 'account_name': str,
                                        'vendor_mobile_number': str, 'vendor_email': str, 'sort_code': str})
        df.fillna("", inplace=True)
        for row in df.itertuples(index=False):
            account_no = row.account_no
            vendor_id = row.vendor_id
            account_name = row.account_name
            vendor_mobile_number = row.vendor_mobile_number
            vendor_email = row.vendor_email
            bank_name = ''
            branch = ''
            sort_code = row.sort_code
            bicCode = ''
            resp = requests.post(url=URL, headers=transaction_headers, json={"service": "BNK9901", "request": {}},
                                 verify=False)
            resp = resp.json()
            if resp['operation_status'] == 'SUCCESS':
                resp = resp['response']['bankList']
                found = False
                for resp_item in resp:
                    if str(sort_code) == resp_item['sortCode']:
                        bank_name = resp_item['bankName']
                        branch = resp_item['branchDesc']
                        bicCode = resp_item['bicCode']
                        found = True
                        break
                if not found:
                    upload_errors = {
                        'errors': [f'Sort Code associated with {account_name} is invalid']
                    }
                    errors.append(upload_errors)
                else:
                    upload_errors = {
                        'errors': []
                    }
                    errors.append(upload_errors)
            isVend = Apven.objects.using('ABSDAT').filter(vendorid=vendor_id).exists()
            if not isVend:
                print(upload_errors)
                upload_errors['errors'].append(f'Vendor ID {vendor_id} is invalid')

            if not errors[0]['errors']:
                bank = BankDetails(
                    account_no=account_no,
                    vendor_id=vendor_id,
                    account_name=account_name,
                    vendor_mobile_number=vendor_mobile_number,
                    vendor_email=vendor_email,
                    bank_name=bank_name,
                    sort_code=sort_code,
                    branch=branch,
                    bicCode=bicCode
                )
                bank.save()
                return redirect('webapp:bank-details')
            else:
                messages.error(request, ", ".join(errors[0]['errors']))
                return redirect('webapp:upload-bank-details')

        """ except Exception as e:
            print(e)"""


@login_required(login_url="/")
@user_is_support_staff
def bankUploadCSVTemplate(request):
    try:
        b = io.BytesIO()
        selected_fields = ['account_no', 'vendor_id', 'account_name', 'vendor_mobile_number', 'vendor_email',
                           'sort_code']
        df = pd.DataFrame(columns=selected_fields)
        writer = pd.ExcelWriter(b, engine='openpyxl')
        df.to_excel(writer, sheet_name='vendor bank details', index=False)
        writer.save()

        response = HttpResponse(b.getvalue(),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Report1.xlsx"'
        return response

    except Exception as e:
        return HttpResponse(f'Error exporting data: {str(e)}', status=500)


"""

Functions to Approve and Post Transactions

"""
#@login_required(login_url='/')
#@user_is_approver
def homepage(request):
    # Build transactions grouped by DB alias for accordion display
    vendor_info = BankDetails.objects.all()
    processed_dep = ProcessedDeposits.objects.filter(transaction_date__gte="2025-01-01")
    vendors = [vendor.vendor_id for vendor in vendor_info]
    processed = [processed.invoiceid for processed in processed_dep]

    # Friendly names mapping (fallback to alias if not found)
    friendly_names = {
        'ACCDAT': 'IHVN Accumulated Fund Financial Database',
        'ACTDAT': 'Action Grant Financial Database',
        'ADADAT': 'IHV Adapt Grant Financial Database',
        'ANRDAT': 'Accelerating Nutritional Results In Nigeria (Anrin) Project',
        'APTDAT': 'Africa Postdoctoral Training Initiative (APTI) Fellowship',
        'ASPDAT': 'ASPIRE Project Financial Database',
        'BEADAT': 'Beaming Grant Financial Database',
        'BEGDAT': 'IHVN/BEGET Project Financial Database',
        'BRIDAT': 'HIV Vista Project (BRILLIANT Consortium) Financial Database',
        'BUFDAT': 'Building Fund Financial Database',
        'BUTDAT': 'Building Trust Grant Financial Database',
        'CAMDAT': 'CAMP Study Project Financial Database',
        'CASDAT': 'Case Inspire Grant Financial Database',
        'CIPDAT': 'Cipher Research Grant Financial Database',
        'CLEDAT': 'IHVN/Clear Grant Financial Database',
        'D2EDAT': 'D2EFT Study Grant Financial Database',
        'EFADAT': 'IHVN/Gesundes emergency food aid grants financial Database',
        'ENHDAT': 'ENHANCE Project Financial Database',
        'EQUDAT': 'EQUAL Project Financial Database',
        'EXCDAT': 'EXCEL Rite  Project Financial Database',
        'EXPDAT': 'EXPAND Project Financial Database',
        'FELDAT': 'EDCTP Fellowship Financial Database',
        'GC7DAT': 'Global Fund GC7 Project Financial Database',
        'GDRSDA': 'NIH/IHVN GDRS  Ghana Project Financial Database',
        'GESDAT': 'Gesundes Afrika Project Financial database',
        'GFSDAT': 'IHVN/Gesunde Food Security Financial Database',
        'GFTBSR': 'Global Fund TB Sub-Recipients Financial Database',
        'GFTDAT': 'Global Fund/CCM/TB Grant Financial Database',
        'H3ADAT': 'NIH/H3A/I-HAB Grant Financial Database',
        'HAFDAT': 'Global Fund TB Sub-Recipients Financial Database.',
        'HEPDAT': 'Hepatitis B Project Financial Database',
        'HOMDAT': 'Hominy Project Financial Database',
        'IEVDAT': 'IEV Grant Financial Database',
        'IGHDAT': 'IHVN Guest House',
        'IHVGDA': 'IHVN InterGrant Transactions Database',
        'IHVPAD': 'IHVN Payroll Database',
        'IHVSDA': 'Non UMB Grants Financial Database',
        'IMADAT': 'Impact Malaria Financial Database',
        'IMPDAT': 'IMPACT Project Financial Database',
        'IMUDAT': 'IMPACT UMB Project Financial Database.',
        'INFDAT': 'INFORM Africa Project Financial Database',
        'IRCDAT': 'IHVN International Research Center of Excellence',
        'ISEDAT': 'IRCE Secure Financial Database',
        'ITADAT': 'INSIGHT013 ITAC (The study)',
        'LONDAT': 'USAID/Nigeria Tuberculosis Local Organizations Network',
        'LSTDAT': 'HIV-ST-Evaluation Project (LSTM) Financial Database',
        'MALDAT': 'IHVN/ Ondo State Malaria Impact project Financial Database',
        'NDBSDA': 'Novateur Developement Business Services',
        'NORDAT': 'NORA Project Financial Database',
        'OUTDAT': 'Outcome Study Financial Database',
        'PAVDAT': 'IHVN PAVIA Grant Financial Database',
        'PEDDAT': 'Pediatrics Project Financial Database',
        'PLADAT': 'NIH/UMB/Plasvirec Grant Financial Database',
        'RECDAT': 'IHVN Recoup Database',
        'RSLDAT': 'Resolve To Save Lives Grant Finacial Database',
        'SAFDAT': 'Safe/Thrive Project Financial Database',
        'SCEDAT': 'Scenario Study Financial Database',
        'SGHDAT': 'Strengthng Global Health Security Agenda In Nig(Secure- Nig)',
        'SPEDAT': 'SPEED (Vital Strategies) Project Financial Database',
        'STADAT': 'UNSW/TKI/Start Study Grant Financial Database',
        'SYNDAT': 'Syndemic Project Financial Database',
        'TICDAT': 'TICO Project Financial Database',
        'TIFDAT': 'IHVN TIFA Grant Financial Database',
        'TRIDAT': 'EDCTP - TRiAD Study Financial Database',
        'VERDAT': 'VERDI Mpox Project',
        'WANDAT': 'IHVN Wanetam EDCTP Grant Financial Database.',
        'WONDAT': 'HIV & HCV Clinical Validation Study Financial Database',
    }

    # Determine available SQL Server aliases from settings (exclude default)
    sql_aliases = [k for k in settings.DATABASES.keys() if k != 'default']

    transactions_by_db_list: List[Dict[str, Any]] = []

    for alias in sql_aliases:
        try:
            payments_qs = (
                Appym.objects.using(alias)
                .filter(idvend__in=vendors)
                .filter(datermit__gt=20250101)
                .exclude(idinvc__in=processed)
                .order_by('-cntbtch')
            )
            if not payments_qs.exists():
                continue

            batch_list = list(payments_qs.values_list('cntbtch', flat=True))
            refs = Aptcr.objects.using(alias).filter(cntbtch__in=batch_list).values('cntbtch', 'textrmit')
            ref_map = {r['cntbtch']: (r['textrmit'] or '').strip() for r in refs}

            txns = []
            for payment in payments_qs:
                date = change_date(str(payment.datermit))
                amount = round(payment.amtpaym, 2)
                txns.append({
                    'IDINVC': (payment.idinvc or '').strip(),
                    'DATERMIT': date,
                    'AMTPAYM': amount,
                    'IDVEND': (payment.idvend or '').strip(),
                    'REFERENCE': ref_map.get(payment.cntbtch, ''),
                })
            if txns:
                transactions_by_db_list.append({
                    'alias': alias,
                    'display_name': friendly_names.get(alias, alias),
                    'transactions': txns,
                })
        except Exception as e:
            # Skip problematic aliases but continue others
            print(f"Error fetching from {alias}: {e}")
            continue

    context = {
        'transactions_by_db': transactions_by_db_list,
        'vendor_info': vendor_info,
    }

    return render(request, 'homepage.html', context)

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
    context = {'transaction_info': page_obj,
               'date_list': date_list,
               'count_list': count_list,
               'data_by_month': monthly_data,
               }

    return render(request, "transaction-history.html", context)


def transaction_history_xls(request):
    try:
        if request.method == 'GET':
            start_date_raw = request.GET.get('start_date')
            end_date_raw = request.GET.get('end_date')
            start_date = format_date(start_date_raw)
            end_date = format_date(end_date_raw)
            print(request.GET.get('start_date'), request.GET.get('end_date'))
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
            print(data_rows)
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
    """ Get search results based on query parameters """

    if request.method != 'GET':
        return JsonResponse({'message': 'Only GET requests are allowed'}, status=400)

    try:
        vendor_info = BankDetails.objects.values('vendor_id', 'bank_code',
                                                 'account_no',
                                                 'account_name').all()

        vendors = [vendor['vendor_id'] for vendor in vendor_info]

        field_mapping_vendor = {
            'account_number': 'account_no__icontains',
            'bank_code': 'bank_code__icontains',
            'bank_name': 'bank_name__icontains',

        }

        search_params = request.GET.get('search_params')
        field_option = request.GET.get('filter_options')

        if field_option in ['vendor_id', 'date', 'amount', 'invoice_id']:
            qs = Appym.objects.using('ABSDAT').filter(idvend__in=vendors)
            if field_option == 'vendor_id' and search_params:
                qs = qs.filter(idvend__icontains=search_params)
            elif field_option == 'invoice_id' and search_params:
                qs = qs.filter(idinvc__icontains=search_params)
            elif field_option == 'amount' and search_params:
                try:
                    amt = Decimal(str(search_params))
                    qs = qs.filter(amtpaym=amt)
                except Exception:
                    qs = qs.none()
            elif field_option == 'date' and search_params:
                if str(search_params).isdigit():
                    qs = qs.filter(datermit=int(search_params))
                else:
                    qs = qs.none()

            trans_infor_raw = []
            batch_list = [batch.cntbtch for batch in qs]
            aptcr_qs = Aptcr.objects.using('ABSDAT').filter(cntbtch__in=batch_list)

            for payment, record in zip(qs, aptcr_qs):
                transactions = {
                    'IDINVC': (payment.idinvc).strip(),
                    'DATERMIT': payment.datermit,
                    'AMTPAYM': payment.amtpaym,
                    'IDVEND': (payment.idvend).strip(),
                    'REFERENCE': (record.textrmit).strip()

                }
                trans_infor_raw.append(transactions)
            paginator = Paginator(trans_infor_raw, 20)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'transaction_info': page_obj,
                'vendor_info': vendor_info,
            }

            return render(request, 'homepage.html', context)

        elif field_option in field_mapping_vendor and search_params:
            vendor_info = BankDetails.objects.filter(**{field_mapping_vendor[field_option]: search_params}).values(
                'vendor_id', 'sort_code', 'account_no', 'account_name').all()
            vendor_ids = [vendor['vendor_id'] for vendor in vendor_info]
            trans_infor_raw = []
            transaction_info = Appym.objects.using('ABSDAT').filter(idvend__in=vendor_ids)

            batch_list = [batch.cntbtch for batch in transaction_info]

            aptcr_qs = Aptcr.objects.filter(cntbtch__in=batch_list)

            for payment, record in zip(transaction_info, aptcr_qs):
                transactions = {
                    'IDINVC': (payment.idinvc).strip(),
                    'DATERMIT': payment.datermit,
                    'AMTPAYM': payment.amtpaym,
                    'IDVEND': (payment.idvend).strip(),
                    'REFERENCE': (record.textrmit).strip()

                }
                trans_infor_raw.append(transactions)

            paginator = Paginator(trans_infor_raw, 20)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'transaction_info': page_obj,
                'vendor_info': vendor_info,
                'page_number': page_number
            }

            return render(request, 'homepage.html', context)

    except Exception as e:
        return JsonResponse({'message': f'An error occurred while processing your request {e}'}, status=500)

def get_history_search_results(request):
    search_params = request.GET.get('search_params')
    field_option = request.GET.get('filter_options')
    field_mapping_vendor = {
        'amount': 'amount__icontains',
        'invoice_id': 'invoice_id__iexact',

    }
    if field_option in field_mapping_vendor and search_params:
        data = BankDetails.objects.filter(**{field_mapping_vendor[field_option]: search_params}).values(
        'vendor_id', 'sort_code', 'account_no', 'account_name')
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
        processed_deposits = processed_deposits.annotate(trans_date=TruncDate('timestamp')).values(
            'trans_date').annotate(
            count=Count('trans_date'))
        date_dict = {deposit['trans_date'].strftime('%Y-%m-%d'): deposit['count'] for deposit in processed_deposits}
        date_list = [date.strftime('%Y-%m-%d') for date in date_range]
        count_list = [date_dict.get(date.strftime('%Y-%m-%d'), 0) for date in date_range]
        context = {
            'transaction_info': page_obj,
            'page_number': page_number,
            'date_list': date_list,
            'count_list': count_list,
            'data_by_month': monthly_data,

        }

        return render(request, 'transaction-history.html', context)

def removetransaction (request,id):
        processed = ProcessedDeposits(amount=0, transaction_date='',
                                          vendorid='',
                                          invoiceid=id,
                                          vendorname='', status=2,
                                          transaction_type="removed transaction",
                                          processed_by=request.user.username)
        processed.save()
        return redirect('webapp:homepage')


def forgotPassword(request):
    return render(request, 'forgot-password.html')


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
    response = requests.post(url=URL, headers={"Content-Type": "application/json; charset=utf-8", "authkey": API_KEY},
                             json=data, verify=False)
    response = response.json()
    print(response)
    account_list = response['response']['accountList']
    return JsonResponse({'resp': list(account_list)})


def generate_unique_reference():
    """Generate a unique reference for bulk transactions"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4().int)[:6]
    return f"{timestamp}{unique_id}"


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
    url = "https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/account/lookup"

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


def check_account_balance(token, account_number, bank_code):
    """
    Check account balance before initiating transfer

    Args:
        token: Bearer authentication token
        account_number: Source account number
        bank_code: Source bank code

    Returns:
        dict: Response containing balance information
    """
    url = "https://demo.remita.net/remita/exapp/api/v1/send/api/rpgsvc/v3/rpg/account/balance"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "sourceAccount": account_number,
        "sourceBankCode": bank_code,
        "transRef": generate_unique_reference()
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response_data = response.json()

        if response.status_code == 200 and response_data.get('status') == '00':
            return {
                'success': True,
                'data': response_data.get('data', {}),
                'available_balance': float(response_data.get('data', {}).get('availableBalance', 0))
            }
        else:
            return {
                'success': False,
                'message': response_data.get('message', 'Balance check failed')
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error checking balance: {str(e)}'
        }


def initiate_bulk_payment(token, source_account_details, transactions):
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
    url = "https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/bulk/payment"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Generate unique batch reference
    batch_ref = generate_unique_reference()

    # Calculate total amount
    total_amount = sum(float(t['amount']) for t in transactions)

    # Build transaction array
    transaction_items = []
    for idx, trans in enumerate(transactions, 1):
        # Generate unique transaction reference if not provided
        trans_ref = trans.get('invoice_id') or f"{batch_ref}{idx:04d}"

        transaction_items.append({
            "amount": float(trans['amount']),
            "transactionRef": trans_ref,
            "destinationBankCode": trans['bank_code'],
            "destinationAccount": trans['account_no'],
            "destinationAccountName": trans['account_name'],
            "destinationNarration": trans.get('remarks', 'Bulk Transfer')
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
    url = f"https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/bulk/payment/status/{batch_ref}"

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
    url = f"https://api-demo.systemspecsng.com/services/connect-gateway/api/v1/integration/bulk/payment/details/{batch_ref}"

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
    from .models import ProcessedDeposits, Projects

    try:
        # Determine status based on status code
        # Status: 0=Pending, 1=Success, 2=Failed
        if status_code == '00':
            status = 1  # Success
        elif status_code in ['01', '02', '04', '13', '16', '17', '18', '22', '24',
                             '26', '27', '28', '29', '30', '31', '33', '34', '36',
                             '37', '38', '42', '43', '44', '46', '50', '51', '54',
                             '55', '58', '59', '60', '65', '68', '71', '72', '74',
                             '75', '76', '77', '78', '79', '91', '94', '96']:
            status = 2  # Failed
        else:
            status = 0  # Pending (all other codes including 001, 61, 07, 09, etc.)

        project = Projects.objects.get(id=project_id)

        deposit = ProcessedDeposits.objects.create(
            project=project,
            batch_identifier=batch_ref,
            invoiceid=transaction.get('invoice_id', ''),
            vendorid=transaction.get('vendor_id', ''),
            vendorname=transaction.get('account_name', ''),
            transaction_date=transaction.get('date', ''),
            amount=str(transaction.get('amount', 0)),
            status=status,
            transaction_type=transaction_type,
            processed_by=processed_by
        )

        return deposit

    except Exception as e:
        print(f"Error logging deposit: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def update_transaction_status(invoice_id, status_code, response_message=''):
    """
    Update the status of an existing transaction

    Args:
        invoice_id: Invoice ID to update
        status_code: New status code from API
        response_message: Optional message from API response

    Returns:
        bool: True if updated successfully, False otherwise
    """
    from .models import ProcessedDeposits

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

        deposit = ProcessedDeposits.objects.get(invoiceid=invoice_id)
        deposit.status = status
        deposit.save()

        print(f"Updated transaction {invoice_id} to status {status}")
        return True

    except ProcessedDeposits.DoesNotExist:
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

            print("Raw transactions:", transacs)

            transactions = []
            for entry in transacs:
                values = entry['values']
                transaction_element = {
                    'date': values[0],
                    'amount': values[1],
                    'invoice_id': values[2],
                    'remarks': values[3],
                    'vendor_id': values[4],
                    'account_name': values[5],
                    'account_no': values[7],
                    'bank_code': values[8],
                    'bank_name': values[9],
                    'email': values[10] if len(values) > 10 else ''
                }
                transactions.append(transaction_element)

            print("Parsed transactions:", transactions)

            # Get source account details from request or settings
            source_account_details = {
                'sourceBankCode': getattr(settings.REMITA_SOURCE_BANK_CODE, '925'),
                'sourceAccount':getattr(settings.REMITA_SOURCE_ACCOUNT_NO, '9256258124'),
                'sourceAccountName': getattr(settings.REMITA_SOURCE_ACCOUNT_NAME, '9256258124'),
                'originalBankCode': getattr(settings.REMITA_SOURCE_BANK_CODE, '925'),
                'originalAccountNumber': getattr(settings.REMITA_SOURCE_ACCOUNT_NO, '9256258124'),
                'sourceNarration': request.POST.get('narration', 'Bulk Payment Transaction')
            }

            # Optional: Check balance before initiating
            balance_check = check_account_balance(
                secret_key,
                source_account_details['sourceAccount'],
                source_account_details['sourceBankCode']
            )

            if balance_check['success']:
                total_amount = sum(float(t['amount']) for t in transactions)
                if balance_check['available_balance'] < total_amount:
                    return JsonResponse({
                        'success': False,
                        'message': 'Insufficient balance',
                        'available_balance': balance_check['available_balance'],
                        'required_amount': total_amount
                    }, status=400)

            # Initiate bulk payment
            result = initiate_bulk_payment(secret_key, source_account_details, transactions)
            batch_ref = result['batch_ref']

            # Log all transactions to database regardless of success/failure
            logged_count = 0
            for transaction in transactions:
                # Get status code from response
                status_code = result.get('response', {}).get('status', '81')  # Default to pending

                deposit = log_processed_deposit(
                    project_id=project_id,
                    batch_ref=batch_ref,
                    transaction=transaction,
                    status_code=status_code,
                    processed_by=processed_by,
                    transaction_type='BULK_TRANSFER'
                )

                if deposit:
                    logged_count += 1
                    print(f"Logged transaction: {transaction['invoice_id']}")

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
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': 'Error processing transactions',
                'error': str(e)
            }, status=500)

    return JsonResponse({'message': 'GET Request Not Allowed'}, status=400)


def check_transaction_status(request, batch_ref):
    """
    Django view to check status of bulk payment
    """
    if request.method == 'GET':
        try:
            # Get valid token
            secret_key = check_and_refresh_token(request)

            if not secret_key:
                return JsonResponse({
                    'success': False,
                    'message': 'Authentication required'
                }, status=401)

            # Get summary status
            summary = check_bulk_payment_status_summary(secret_key, batch_ref)

            # Get detailed status
            details = check_bulk_payment_details(secret_key, batch_ref)

            return JsonResponse({
                'success': True,
                'summary': summary,
                'details': details
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)

    return JsonResponse({'message': 'Only GET requests allowed'}, status=400)