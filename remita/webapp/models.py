
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Permission,Group
from django.db import models

from .managers import MyAbstractUserManager



ROLE = (
    ('001', "001"),  # Adds Bank Details
    ('002', "002"),  # Posts Transactions
)


class ApiCallErrors(models.Model):
    service = models.CharField(max_length=255)
    error_list = models.TextField()
    transaction_type = models.CharField(max_length=255)

class Users(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, choices=ROLE)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)
    objects = MyAbstractUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

class UserLoginHistory(models.Model):
    username = models.CharField(max_length=255)
    ipaddress = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now=True)


class Projects(models.Model):
    project_name = models.CharField(max_length=255,help_text='Database friendly name', unique=True)
    project_code = models.CharField(max_length=255, help_text='Database alias',unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_name

class SourceBankDetails(models.Model):
    bank_name = models.CharField(max_length=255, verbose_name='Bank Name')
    bank_code = models.CharField(max_length=255, verbose_name='Bank Code')
    bank_account_number = models.CharField(max_length=255, verbose_name='Bank Account Number')
    bank_account_name = models.CharField(max_length=255, verbose_name='Bank Account Name')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='source_bank_details',default=1)
    def __str__(self):
        return  self.bank_account_number


class BankDetails(models.Model):
    account_no = models.CharField(max_length=20, verbose_name='Account Number')
    account_name = models.CharField(max_length=255, verbose_name='Account Name')
    vendor_id = models.CharField(max_length=255, verbose_name='Vendor ID')
    vendor_mobile_number = models.CharField(max_length=20, verbose_name='Vendor Mobile Number', blank=True)
    vendor_email = models.EmailField(max_length=255, verbose_name='Vendor Email', blank=True)
    bank_name = models.CharField(max_length=255, verbose_name='Bank Name')
    bank_code = models.CharField(max_length=255, verbose_name='Bank Code')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='bank_details',default=1)


class ProcessedDeposits(models.Model):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='processed_deposits', default=1)
    batch_identifier = models.CharField(max_length=255, blank=False, default='5674883')
    invoiceid = models.CharField(max_length=255, blank=False)
    transaction_ref = models.CharField(max_length=255, null=True, blank=True, help_text='Provider transactionRef for this item')
    vendorid = models.CharField(max_length=255, blank=False,)
    vendorname = models.CharField(max_length=255, blank=False)
    transaction_date = models.CharField(max_length=255, blank=False, unique=False)
    amount = models.CharField(max_length=255, blank=False)
    status = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)
    processed_by = models.CharField(max_length=255)

    class Meta:
        unique_together = (('project', 'invoiceid'),)


class RemitaAuth(models.Model):
    """Stores the latest Remita access token and its expiry time.
    Using a single-row table; use id=1 for the singleton record.
    """
    token = models.TextField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"RemitaAuth(exp={self.expires_at})"


class Appym(models.Model):
    idbank = models.CharField(db_column='IDBANK', primary_key=True,max_length=8, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idvend = models.CharField(db_column='IDVEND', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idrmit = models.CharField(db_column='IDRMIT', max_length=18, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    longserial = models.BigIntegerField(db_column='LONGSERIAL')  # Field name made lowercase.
    datermit = models.DecimalField(db_column='DATERMIT', max_digits=9, decimal_places=0)  # Field name made lowercase.
    audtdate = models.DecimalField(db_column='AUDTDATE', max_digits=9, decimal_places=0)  # Field name made lowercase.
    audttime = models.DecimalField(db_column='AUDTTIME', max_digits=9, decimal_places=0)  # Field name made lowercase.
    audtuser = models.CharField(db_column='AUDTUSER', max_length=8, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    audtorg = models.CharField(db_column='AUDTORG', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    datebatch = models.DecimalField(db_column='DATEBATCH', max_digits=9, decimal_places=0)  # Field name made lowercase.
    amtrmittc = models.DecimalField(db_column='AMTRMITTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtpaym = models.DecimalField(db_column='AMTPAYM', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtdisc = models.DecimalField(db_column='AMTDISC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    paymcode = models.CharField(db_column='PAYMCODE', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codecurn = models.CharField(db_column='CODECURN', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idratetype = models.CharField(db_column='IDRATETYPE', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    rateexchhc = models.DecimalField(db_column='RATEEXCHHC', max_digits=15, decimal_places=7)  # Field name made lowercase.
    swovrdrate = models.SmallIntegerField(db_column='SWOVRDRATE')  # Field name made lowercase.
    textretrn = models.CharField(db_column='TEXTRETRN', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    amtrounder = models.DecimalField(db_column='AMTROUNDER', max_digits=19, decimal_places=3)  # Field name made lowercase.
    daterate = models.DecimalField(db_column='DATERATE', max_digits=9, decimal_places=0)  # Field name made lowercase.
    cntfiscyr = models.CharField(db_column='CNTFISCYR', max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    cntfiscper = models.CharField(db_column='CNTFISCPER', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    textpayor = models.CharField(db_column='TEXTPAYOR', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    cntbtch = models.DecimalField(db_column='CNTBTCH', max_digits=9, decimal_places=0)  # Field name made lowercase.
    cntitem = models.DecimalField(db_column='CNTITEM', max_digits=7, decimal_places=0)  # Field name made lowercase.
    swchkclrd = models.SmallIntegerField(db_column='SWCHKCLRD')  # Field name made lowercase.
    amtrmithc = models.DecimalField(db_column='AMTRMITHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtadj = models.DecimalField(db_column='AMTADJ', max_digits=19, decimal_places=3)  # Field name made lowercase.
    dateclrd = models.DecimalField(db_column='DATECLRD', max_digits=9, decimal_places=0)  # Field name made lowercase.
    datervrsd = models.DecimalField(db_column='DATERVRSD', max_digits=9, decimal_places=0)  # Field name made lowercase.
    trxtypetxt = models.SmallIntegerField(db_column='TRXTYPETXT')  # Field name made lowercase.
    idinvc = models.CharField(db_column='IDINVC', max_length=22, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    rateop = models.SmallIntegerField(db_column='RATEOP')  # Field name made lowercase.
    paymtype = models.SmallIntegerField(db_column='PAYMTYPE')  # Field name made lowercase.
    cuid = models.IntegerField(db_column='CUID')  # Field name made lowercase.
    drillapp = models.CharField(db_column='DRILLAPP', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    drilltype = models.SmallIntegerField(db_column='DRILLTYPE')  # Field name made lowercase.
    drilldwnlk = models.DecimalField(db_column='DRILLDWNLK', max_digits=19, decimal_places=0)  # Field name made lowercase.
    idacct = models.CharField(db_column='IDACCT', max_length=45, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    swnonrcvbl = models.SmallIntegerField(db_column='SWNONRCVBL')  # Field name made lowercase.
    swjob = models.SmallIntegerField(db_column='SWJOB')  # Field name made lowercase.
    idinvcmtch = models.CharField(db_column='IDINVCMTCH', max_length=22, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    swtxamtctl = models.SmallIntegerField(db_column='SWTXAMTCTL')  # Field name made lowercase.
    swtxbsectl = models.SmallIntegerField(db_column='SWTXBSECTL')  # Field name made lowercase.
    codetaxgrp = models.CharField(db_column='CODETAXGRP', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codetax1 = models.CharField(db_column='CODETAX1', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codetax2 = models.CharField(db_column='CODETAX2', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codetax3 = models.CharField(db_column='CODETAX3', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codetax4 = models.CharField(db_column='CODETAX4', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codetax5 = models.CharField(db_column='CODETAX5', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    taxclass1 = models.SmallIntegerField(db_column='TAXCLASS1')  # Field name made lowercase.
    taxclass2 = models.SmallIntegerField(db_column='TAXCLASS2')  # Field name made lowercase.
    taxclass3 = models.SmallIntegerField(db_column='TAXCLASS3')  # Field name made lowercase.
    taxclass4 = models.SmallIntegerField(db_column='TAXCLASS4')  # Field name made lowercase.
    taxclass5 = models.SmallIntegerField(db_column='TAXCLASS5')  # Field name made lowercase.
    txbse1tc = models.DecimalField(db_column='TXBSE1TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse2tc = models.DecimalField(db_column='TXBSE2TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse3tc = models.DecimalField(db_column='TXBSE3TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse4tc = models.DecimalField(db_column='TXBSE4TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse5tc = models.DecimalField(db_column='TXBSE5TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt1tc = models.DecimalField(db_column='TXAMT1TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt2tc = models.DecimalField(db_column='TXAMT2TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt3tc = models.DecimalField(db_column='TXAMT3TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt4tc = models.DecimalField(db_column='TXAMT4TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt5tc = models.DecimalField(db_column='TXAMT5TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txtottc = models.DecimalField(db_column='TXTOTTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtnettc = models.DecimalField(db_column='AMTNETTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txalltc = models.DecimalField(db_column='TXALLTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txexptc = models.DecimalField(db_column='TXEXPTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txrectc = models.DecimalField(db_column='TXRECTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    codecurnrc = models.CharField(db_column='CODECURNRC', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    swtxctlrc = models.SmallIntegerField(db_column='SWTXCTLRC')  # Field name made lowercase.
    raterc = models.DecimalField(db_column='RATERC', max_digits=15, decimal_places=7)  # Field name made lowercase.
    ratetyperc = models.CharField(db_column='RATETYPERC', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    ratedaterc = models.DecimalField(db_column='RATEDATERC', max_digits=9, decimal_places=0)  # Field name made lowercase.
    rateoprc = models.SmallIntegerField(db_column='RATEOPRC')  # Field name made lowercase.
    txamt1rc = models.DecimalField(db_column='TXAMT1RC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt2rc = models.DecimalField(db_column='TXAMT2RC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt3rc = models.DecimalField(db_column='TXAMT3RC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt4rc = models.DecimalField(db_column='TXAMT4RC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt5rc = models.DecimalField(db_column='TXAMT5RC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txtotrc = models.DecimalField(db_column='TXTOTRC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txallrc = models.DecimalField(db_column='TXALLRC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txexprc = models.DecimalField(db_column='TXEXPRC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txrecrc = models.DecimalField(db_column='TXRECRC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse1hc = models.DecimalField(db_column='TXBSE1HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse2hc = models.DecimalField(db_column='TXBSE2HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse3hc = models.DecimalField(db_column='TXBSE3HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse4hc = models.DecimalField(db_column='TXBSE4HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse5hc = models.DecimalField(db_column='TXBSE5HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt1hc = models.DecimalField(db_column='TXAMT1HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt2hc = models.DecimalField(db_column='TXAMT2HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt3hc = models.DecimalField(db_column='TXAMT3HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt4hc = models.DecimalField(db_column='TXAMT4HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt5hc = models.DecimalField(db_column='TXAMT5HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txtothc = models.DecimalField(db_column='TXTOTHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtnethc = models.DecimalField(db_column='AMTNETHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txallhc = models.DecimalField(db_column='TXALLHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txexphc = models.DecimalField(db_column='TXEXPHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txrechc = models.DecimalField(db_column='TXRECHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    cntacc = models.IntegerField(db_column='CNTACC')  # Field name made lowercase.
    amtacctc = models.DecimalField(db_column='AMTACCTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtacchc = models.DecimalField(db_column='AMTACCHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    datebus = models.DecimalField(db_column='DATEBUS', max_digits=9, decimal_places=0)  # Field name made lowercase.
    amtwht1tc = models.DecimalField(db_column='AMTWHT1TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtwht2tc = models.DecimalField(db_column='AMTWHT2TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtwht3tc = models.DecimalField(db_column='AMTWHT3TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtwht4tc = models.DecimalField(db_column='AMTWHT4TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtwht5tc = models.DecimalField(db_column='AMTWHT5TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxbs1tc = models.DecimalField(db_column='AMTCXBS1TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxbs2tc = models.DecimalField(db_column='AMTCXBS2TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxbs3tc = models.DecimalField(db_column='AMTCXBS3TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxbs4tc = models.DecimalField(db_column='AMTCXBS4TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxbs5tc = models.DecimalField(db_column='AMTCXBS5TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxtx1tc = models.DecimalField(db_column='AMTCXTX1TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxtx2tc = models.DecimalField(db_column='AMTCXTX2TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxtx3tc = models.DecimalField(db_column='AMTCXTX3TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxtx4tc = models.DecimalField(db_column='AMTCXTX4TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxtx5tc = models.DecimalField(db_column='AMTCXTX5TC', max_digits=19, decimal_places=3)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'APPYM'
        unique_together = (('idbank', 'idvend', 'idrmit', 'longserial', 'datermit'),)


class Apven(models.Model):
    vendorid = models.CharField(db_column='VENDORID', primary_key=True, max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    audtdate = models.DecimalField(db_column='AUDTDATE', max_digits=9, decimal_places=0)  # Field name made lowercase.
    audttime = models.DecimalField(db_column='AUDTTIME', max_digits=9, decimal_places=0)  # Field name made lowercase.
    audtuser = models.CharField(db_column='AUDTUSER', max_length=8, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    audtorg = models.CharField(db_column='AUDTORG', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    shortname = models.CharField(db_column='SHORTNAME', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idgrp = models.CharField(db_column='IDGRP', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    swactv = models.SmallIntegerField(db_column='SWACTV')  # Field name made lowercase.
    dateinac = models.DecimalField(db_column='DATEINAC', max_digits=9, decimal_places=0)  # Field name made lowercase.
    datelastmn = models.DecimalField(db_column='DATELASTMN', max_digits=9, decimal_places=0)  # Field name made lowercase.
    swhold = models.SmallIntegerField(db_column='SWHOLD')  # Field name made lowercase.
    datestart = models.DecimalField(db_column='DATESTART', max_digits=9, decimal_places=0)  # Field name made lowercase.
    idppnt = models.CharField(db_column='IDPPNT', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    vendname = models.CharField(db_column='VENDNAME', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    textstre1 = models.CharField(db_column='TEXTSTRE1', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    textstre2 = models.CharField(db_column='TEXTSTRE2', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    textstre3 = models.CharField(db_column='TEXTSTRE3', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    textstre4 = models.CharField(db_column='TEXTSTRE4', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    namecity = models.CharField(db_column='NAMECITY', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codestte = models.CharField(db_column='CODESTTE', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codepstl = models.CharField(db_column='CODEPSTL', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codectry = models.CharField(db_column='CODECTRY', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    namectac = models.CharField(db_column='NAMECTAC', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    textphon1 = models.CharField(db_column='TEXTPHON1', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    textphon2 = models.CharField(db_column='TEXTPHON2', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    primrmit = models.CharField(db_column='PRIMRMIT', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idacctset = models.CharField(db_column='IDACCTSET', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    curncode = models.CharField(db_column='CURNCODE', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    ratetype = models.CharField(db_column='RATETYPE', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    bankid = models.CharField(db_column='BANKID', max_length=8, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    prtsepchks = models.SmallIntegerField(db_column='PRTSEPCHKS')  # Field name made lowercase.
    distsetid = models.CharField(db_column='DISTSETID', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    distcode = models.CharField(db_column='DISTCODE', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    glaccnt = models.CharField(db_column='GLACCNT', max_length=45, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    termscode = models.CharField(db_column='TERMSCODE', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    dupinvccd = models.SmallIntegerField(db_column='DUPINVCCD')  # Field name made lowercase.
    dupamtcode = models.SmallIntegerField(db_column='DUPAMTCODE')  # Field name made lowercase.
    dupdatecd = models.SmallIntegerField(db_column='DUPDATECD')  # Field name made lowercase.
    codetaxgrp = models.CharField(db_column='CODETAXGRP', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    taxclass1 = models.SmallIntegerField(db_column='TAXCLASS1')  # Field name made lowercase.
    taxclass2 = models.SmallIntegerField(db_column='TAXCLASS2')  # Field name made lowercase.
    taxclass3 = models.SmallIntegerField(db_column='TAXCLASS3')  # Field name made lowercase.
    taxclass4 = models.SmallIntegerField(db_column='TAXCLASS4')  # Field name made lowercase.
    taxclass5 = models.SmallIntegerField(db_column='TAXCLASS5')  # Field name made lowercase.
    taxrptsw = models.SmallIntegerField(db_column='TAXRPTSW')  # Field name made lowercase.
    subjtowthh = models.SmallIntegerField(db_column='SUBJTOWTHH')  # Field name made lowercase.
    taxnbr = models.CharField(db_column='TAXNBR', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    taxidtype = models.SmallIntegerField(db_column='TAXIDTYPE')  # Field name made lowercase.
    taxnote2sw = models.SmallIntegerField(db_column='TAXNOTE2SW')  # Field name made lowercase.
    clasid = models.CharField(db_column='CLASID', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    amtcrlimt = models.DecimalField(db_column='AMTCRLIMT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtbalduet = models.DecimalField(db_column='AMTBALDUET', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtbaldueh = models.DecimalField(db_column='AMTBALDUEH', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtppdinvt = models.DecimalField(db_column='AMTPPDINVT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtppdinvh = models.DecimalField(db_column='AMTPPDINVH', max_digits=19, decimal_places=3)  # Field name made lowercase.
    dtlastrval = models.DecimalField(db_column='DTLASTRVAL', max_digits=9, decimal_places=0)  # Field name made lowercase.
    amtballarv = models.DecimalField(db_column='AMTBALLARV', max_digits=19, decimal_places=3)  # Field name made lowercase.
    cntopeninv = models.DecimalField(db_column='CNTOPENINV', max_digits=7, decimal_places=0)  # Field name made lowercase.
    cntppdinvc = models.DecimalField(db_column='CNTPPDINVC', max_digits=7, decimal_places=0)  # Field name made lowercase.
    cntinvpaid = models.DecimalField(db_column='CNTINVPAID', max_digits=7, decimal_places=0)  # Field name made lowercase.
    daystopay = models.DecimalField(db_column='DAYSTOPAY', max_digits=7, decimal_places=0)  # Field name made lowercase.
    dateinvchi = models.DecimalField(db_column='DATEINVCHI', max_digits=9, decimal_places=0)  # Field name made lowercase.
    datebalhi = models.DecimalField(db_column='DATEBALHI', max_digits=9, decimal_places=0)  # Field name made lowercase.
    dateinvhil = models.DecimalField(db_column='DATEINVHIL', max_digits=9, decimal_places=0)  # Field name made lowercase.
    datebalhil = models.DecimalField(db_column='DATEBALHIL', max_digits=9, decimal_places=0)  # Field name made lowercase.
    datelastac = models.DecimalField(db_column='DATELASTAC', max_digits=9, decimal_places=0)  # Field name made lowercase.
    datelastiv = models.DecimalField(db_column='DATELASTIV', max_digits=9, decimal_places=0)  # Field name made lowercase.
    datelastcr = models.DecimalField(db_column='DATELASTCR', max_digits=9, decimal_places=0)  # Field name made lowercase.
    datelastdr = models.DecimalField(db_column='DATELASTDR', max_digits=9, decimal_places=0)  # Field name made lowercase.
    datelastpa = models.DecimalField(db_column='DATELASTPA', max_digits=9, decimal_places=0)  # Field name made lowercase.
    datelastdi = models.DecimalField(db_column='DATELASTDI', max_digits=9, decimal_places=0)  # Field name made lowercase.
    datelstadj = models.DecimalField(db_column='DATELSTADJ', max_digits=9, decimal_places=0)  # Field name made lowercase.
    idinvchi = models.CharField(db_column='IDINVCHI', max_length=22, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idinvchily = models.CharField(db_column='IDINVCHILY', max_length=22, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    amtinvhit = models.DecimalField(db_column='AMTINVHIT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtbalhit = models.DecimalField(db_column='AMTBALHIT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtwthtcur = models.DecimalField(db_column='AMTWTHTCUR', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtinvhilt = models.DecimalField(db_column='AMTINVHILT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtbalhilt = models.DecimalField(db_column='AMTBALHILT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtwthlytc = models.DecimalField(db_column='AMTWTHLYTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtlastivt = models.DecimalField(db_column='AMTLASTIVT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtlastcrt = models.DecimalField(db_column='AMTLASTCRT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtlastdrt = models.DecimalField(db_column='AMTLASTDRT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtlastpyt = models.DecimalField(db_column='AMTLASTPYT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtlastdit = models.DecimalField(db_column='AMTLASTDIT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtlastadt = models.DecimalField(db_column='AMTLASTADT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtinvhih = models.DecimalField(db_column='AMTINVHIH', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtbalhih = models.DecimalField(db_column='AMTBALHIH', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtwthhcur = models.DecimalField(db_column='AMTWTHHCUR', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtinvhilh = models.DecimalField(db_column='AMTINVHILH', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtbalhilh = models.DecimalField(db_column='AMTBALHILH', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtwthlyhc = models.DecimalField(db_column='AMTWTHLYHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtlastivh = models.DecimalField(db_column='AMTLASTIVH', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtlastcrh = models.DecimalField(db_column='AMTLASTCRH', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtlastdrh = models.DecimalField(db_column='AMTLASTDRH', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtlastpyh = models.DecimalField(db_column='AMTLASTPYH', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtlastdih = models.DecimalField(db_column='AMTLASTDIH', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtlastadh = models.DecimalField(db_column='AMTLASTADH', max_digits=19, decimal_places=3)  # Field name made lowercase.
    paymcode = models.CharField(db_column='PAYMCODE', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idtaxregi1 = models.CharField(db_column='IDTAXREGI1', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idtaxregi2 = models.CharField(db_column='IDTAXREGI2', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idtaxregi3 = models.CharField(db_column='IDTAXREGI3', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idtaxregi4 = models.CharField(db_column='IDTAXREGI4', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idtaxregi5 = models.CharField(db_column='IDTAXREGI5', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    swdistby = models.SmallIntegerField(db_column='SWDISTBY')  # Field name made lowercase.
    codecheck = models.CharField(db_column='CODECHECK', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    avgdayspay = models.DecimalField(db_column='AVGDAYSPAY', max_digits=9, decimal_places=1)  # Field name made lowercase.
    avgpayment = models.DecimalField(db_column='AVGPAYMENT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtinvpdhc = models.DecimalField(db_column='AMTINVPDHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtinvpdtc = models.DecimalField(db_column='AMTINVPDTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    cntnbrchks = models.DecimalField(db_column='CNTNBRCHKS', max_digits=7, decimal_places=0)  # Field name made lowercase.
    swtxinc1 = models.SmallIntegerField(db_column='SWTXINC1')  # Field name made lowercase.
    swtxinc2 = models.SmallIntegerField(db_column='SWTXINC2')  # Field name made lowercase.
    swtxinc3 = models.SmallIntegerField(db_column='SWTXINC3')  # Field name made lowercase.
    swtxinc4 = models.SmallIntegerField(db_column='SWTXINC4')  # Field name made lowercase.
    swtxinc5 = models.SmallIntegerField(db_column='SWTXINC5')  # Field name made lowercase.
    email1 = models.CharField(db_column='EMAIL1', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    email2 = models.CharField(db_column='EMAIL2', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    website = models.CharField(db_column='WEBSITE', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    ctacphone = models.CharField(db_column='CTACPHONE', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    ctacfax = models.CharField(db_column='CTACFAX', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    delmethod = models.SmallIntegerField(db_column='DELMETHOD')  # Field name made lowercase.
    rtgpercent = models.DecimalField(db_column='RTGPERCENT', max_digits=9, decimal_places=5)  # Field name made lowercase.
    rtgdays = models.SmallIntegerField(db_column='RTGDAYS')  # Field name made lowercase.
    rtgterms = models.CharField(db_column='RTGTERMS', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    rtgamttc = models.DecimalField(db_column='RTGAMTTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    rtgamthc = models.DecimalField(db_column='RTGAMTHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    values = models.IntegerField(db_column='VALUES')  # Field name made lowercase.
    nextcuid = models.IntegerField(db_column='NEXTCUID')  # Field name made lowercase.
    legalname = models.CharField(db_column='LEGALNAME', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    chk1099amt = models.SmallIntegerField(db_column='CHK1099AMT')  # Field name made lowercase.
    idcust = models.CharField(db_column='IDCUST', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    brn = models.CharField(db_column='BRN', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    firstname = models.CharField(db_column='FIRSTNAME', max_length=15, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    lastname = models.CharField(db_column='LASTNAME', max_length=25, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    fatca = models.SmallIntegerField(db_column='FATCA')  # Field name made lowercase.
    secondtin = models.SmallIntegerField(db_column='SECONDTIN')  # Field name made lowercase.
    taxwhstte = models.CharField(db_column='TAXWHSTTE', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'APVEN'


class Aptcr(models.Model):
    btchtype = models.CharField(db_column='BTCHTYPE', primary_key=True, max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    cntbtch = models.DecimalField(db_column='CNTBTCH', max_digits=9, decimal_places=0)  # Field name made lowercase.
    cntentr = models.DecimalField(db_column='CNTENTR', max_digits=7, decimal_places=0)  # Field name made lowercase.
    audtdate = models.DecimalField(db_column='AUDTDATE', max_digits=9, decimal_places=0)  # Field name made lowercase.
    audttime = models.DecimalField(db_column='AUDTTIME', max_digits=9, decimal_places=0)  # Field name made lowercase.
    audtuser = models.CharField(db_column='AUDTUSER', max_length=8, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    audtorg = models.CharField(db_column='AUDTORG', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idrmit = models.CharField(db_column='IDRMIT', max_length=18, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idvend = models.CharField(db_column='IDVEND', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    datermit = models.DecimalField(db_column='DATERMIT', max_digits=9, decimal_places=0)  # Field name made lowercase.
    textrmit = models.CharField(db_column='TEXTRMIT', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    namermit = models.CharField(db_column='NAMERMIT', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    amtrmit = models.DecimalField(db_column='AMTRMIT', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtrmittc = models.DecimalField(db_column='AMTRMITTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    rateexchtc = models.DecimalField(db_column='RATEEXCHTC', max_digits=15, decimal_places=7)  # Field name made lowercase.
    swratetc = models.SmallIntegerField(db_column='SWRATETC')  # Field name made lowercase.
    cntpayment = models.DecimalField(db_column='CNTPAYMENT', max_digits=5, decimal_places=0)  # Field name made lowercase.
    amtppaytc = models.DecimalField(db_column='AMTPPAYTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtdisctc = models.DecimalField(db_column='AMTDISCTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    paymcode = models.CharField(db_column='PAYMCODE', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codecurn = models.CharField(db_column='CODECURN', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    ratetypehc = models.CharField(db_column='RATETYPEHC', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    rateexchhc = models.DecimalField(db_column='RATEEXCHHC', max_digits=15, decimal_places=7)  # Field name made lowercase.
    swratehc = models.SmallIntegerField(db_column='SWRATEHC')  # Field name made lowercase.
    rmittype = models.SmallIntegerField(db_column='RMITTYPE')  # Field name made lowercase.
    doctype = models.SmallIntegerField(db_column='DOCTYPE')  # Field name made lowercase.
    cntlstline = models.DecimalField(db_column='CNTLSTLINE', max_digits=5, decimal_places=0)  # Field name made lowercase.
    fiscyr = models.CharField(db_column='FISCYR', max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    fiscper = models.CharField(db_column='FISCPER', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    dateratetc = models.DecimalField(db_column='DATERATETC', max_digits=9, decimal_places=0)  # Field name made lowercase.
    ratetypetc = models.CharField(db_column='RATETYPETC', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    amtadjtcur = models.DecimalField(db_column='AMTADJTCUR', max_digits=19, decimal_places=3)  # Field name made lowercase.
    dateratehc = models.DecimalField(db_column='DATERATEHC', max_digits=9, decimal_places=0)  # Field name made lowercase.
    remreapltc = models.DecimalField(db_column='REMREAPLTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    adjtotdbhc = models.DecimalField(db_column='ADJTOTDBHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtrmithc = models.DecimalField(db_column='AMTRMITHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    docnbr = models.CharField(db_column='DOCNBR', max_length=22, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    paymstts = models.SmallIntegerField(db_column='PAYMSTTS')  # Field name made lowercase.
    swprntrmit = models.SmallIntegerField(db_column='SWPRNTRMIT')  # Field name made lowercase.
    idrmitto = models.CharField(db_column='IDRMITTO', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    txtrmitref = models.CharField(db_column='TXTRMITREF', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    adjtotcrhc = models.DecimalField(db_column='ADJTOTCRHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtadjhcur = models.DecimalField(db_column='AMTADJHCUR', max_digits=19, decimal_places=3)  # Field name made lowercase.
    cntdepsseq = models.BigIntegerField(db_column='CNTDEPSSEQ')  # Field name made lowercase.
    swprinted = models.SmallIntegerField(db_column='SWPRINTED')  # Field name made lowercase.
    textstre1 = models.CharField(db_column='TEXTSTRE1', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    textstre2 = models.CharField(db_column='TEXTSTRE2', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    textstre3 = models.CharField(db_column='TEXTSTRE3', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    textstre4 = models.CharField(db_column='TEXTSTRE4', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    namecity = models.CharField(db_column='NAMECITY', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codestte = models.CharField(db_column='CODESTTE', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codepstl = models.CharField(db_column='CODEPSTL', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codectry = models.CharField(db_column='CODECTRY', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    checklang = models.CharField(db_column='CHECKLANG', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    operbank = models.SmallIntegerField(db_column='OPERBANK')  # Field name made lowercase.
    opervend = models.SmallIntegerField(db_column='OPERVEND')  # Field name made lowercase.
    adjtotdbtc = models.DecimalField(db_column='ADJTOTDBTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    adjtotcrtc = models.DecimalField(db_column='ADJTOTCRTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    dateactvpp = models.DecimalField(db_column='DATEACTVPP', max_digits=9, decimal_places=0)  # Field name made lowercase.
    swjob = models.SmallIntegerField(db_column='SWJOB')  # Field name made lowercase.
    applymeth = models.SmallIntegerField(db_column='APPLYMETH')  # Field name made lowercase.
    errbatch = models.IntegerField(db_column='ERRBATCH')  # Field name made lowercase.
    errentry = models.IntegerField(db_column='ERRENTRY')  # Field name made lowercase.
    idinvcmtch = models.CharField(db_column='IDINVCMTCH', max_length=22, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    values = models.IntegerField(db_column='VALUES')  # Field name made lowercase.
    srceappl = models.CharField(db_column='SRCEAPPL', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    idbank = models.CharField(db_column='IDBANK', max_length=8, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codecurnbc = models.CharField(db_column='CODECURNBC', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    paymtype = models.SmallIntegerField(db_column='PAYMTYPE')  # Field name made lowercase.
    cashacct = models.CharField(db_column='CASHACCT', max_length=45, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    drillapp = models.CharField(db_column='DRILLAPP', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    drilltype = models.SmallIntegerField(db_column='DRILLTYPE')  # Field name made lowercase.
    drilldwnlk = models.DecimalField(db_column='DRILLDWNLK', max_digits=19, decimal_places=0)  # Field name made lowercase.
    code1099 = models.CharField(db_column='CODE1099', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    amt1099 = models.DecimalField(db_column='AMT1099', max_digits=19, decimal_places=3)  # Field name made lowercase.
    swtxamtctl = models.SmallIntegerField(db_column='SWTXAMTCTL')  # Field name made lowercase.
    swtxbsectl = models.SmallIntegerField(db_column='SWTXBSECTL')  # Field name made lowercase.
    codetaxgrp = models.CharField(db_column='CODETAXGRP', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    taxversion = models.IntegerField(db_column='TAXVERSION')  # Field name made lowercase.
    codetax1 = models.CharField(db_column='CODETAX1', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codetax2 = models.CharField(db_column='CODETAX2', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codetax3 = models.CharField(db_column='CODETAX3', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codetax4 = models.CharField(db_column='CODETAX4', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    codetax5 = models.CharField(db_column='CODETAX5', max_length=12, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    taxclass1 = models.SmallIntegerField(db_column='TAXCLASS1')  # Field name made lowercase.
    taxclass2 = models.SmallIntegerField(db_column='TAXCLASS2')  # Field name made lowercase.
    taxclass3 = models.SmallIntegerField(db_column='TAXCLASS3')  # Field name made lowercase.
    taxclass4 = models.SmallIntegerField(db_column='TAXCLASS4')  # Field name made lowercase.
    taxclass5 = models.SmallIntegerField(db_column='TAXCLASS5')  # Field name made lowercase.
    swtaxincl1 = models.SmallIntegerField(db_column='SWTAXINCL1')  # Field name made lowercase.
    swtaxincl2 = models.SmallIntegerField(db_column='SWTAXINCL2')  # Field name made lowercase.
    swtaxincl3 = models.SmallIntegerField(db_column='SWTAXINCL3')  # Field name made lowercase.
    swtaxincl4 = models.SmallIntegerField(db_column='SWTAXINCL4')  # Field name made lowercase.
    swtaxincl5 = models.SmallIntegerField(db_column='SWTAXINCL5')  # Field name made lowercase.
    txbse1tc = models.DecimalField(db_column='TXBSE1TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse2tc = models.DecimalField(db_column='TXBSE2TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse3tc = models.DecimalField(db_column='TXBSE3TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse4tc = models.DecimalField(db_column='TXBSE4TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse5tc = models.DecimalField(db_column='TXBSE5TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt1tc = models.DecimalField(db_column='TXAMT1TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt2tc = models.DecimalField(db_column='TXAMT2TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt3tc = models.DecimalField(db_column='TXAMT3TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt4tc = models.DecimalField(db_column='TXAMT4TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt5tc = models.DecimalField(db_column='TXAMT5TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txtottc = models.DecimalField(db_column='TXTOTTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtnettc = models.DecimalField(db_column='AMTNETTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txalltc = models.DecimalField(db_column='TXALLTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txexptc = models.DecimalField(db_column='TXEXPTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txrectc = models.DecimalField(db_column='TXRECTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    codecurnrc = models.CharField(db_column='CODECURNRC', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    swtxctlrc = models.SmallIntegerField(db_column='SWTXCTLRC')  # Field name made lowercase.
    raterc = models.DecimalField(db_column='RATERC', max_digits=15, decimal_places=7)  # Field name made lowercase.
    ratetyperc = models.CharField(db_column='RATETYPERC', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    ratedaterc = models.DecimalField(db_column='RATEDATERC', max_digits=9, decimal_places=0)  # Field name made lowercase.
    rateoprc = models.SmallIntegerField(db_column='RATEOPRC')  # Field name made lowercase.
    swraterc = models.SmallIntegerField(db_column='SWRATERC')  # Field name made lowercase.
    txamt1rc = models.DecimalField(db_column='TXAMT1RC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt2rc = models.DecimalField(db_column='TXAMT2RC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt3rc = models.DecimalField(db_column='TXAMT3RC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt4rc = models.DecimalField(db_column='TXAMT4RC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt5rc = models.DecimalField(db_column='TXAMT5RC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txtotrc = models.DecimalField(db_column='TXTOTRC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txallrc = models.DecimalField(db_column='TXALLRC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txexprc = models.DecimalField(db_column='TXEXPRC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txrecrc = models.DecimalField(db_column='TXRECRC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtppayhc = models.DecimalField(db_column='AMTPPAYHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtdischc = models.DecimalField(db_column='AMTDISCHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    remreaplhc = models.DecimalField(db_column='REMREAPLHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse1hc = models.DecimalField(db_column='TXBSE1HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse2hc = models.DecimalField(db_column='TXBSE2HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse3hc = models.DecimalField(db_column='TXBSE3HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse4hc = models.DecimalField(db_column='TXBSE4HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txbse5hc = models.DecimalField(db_column='TXBSE5HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt1hc = models.DecimalField(db_column='TXAMT1HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt2hc = models.DecimalField(db_column='TXAMT2HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt3hc = models.DecimalField(db_column='TXAMT3HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt4hc = models.DecimalField(db_column='TXAMT4HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txamt5hc = models.DecimalField(db_column='TXAMT5HC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txtothc = models.DecimalField(db_column='TXTOTHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtnethc = models.DecimalField(db_column='AMTNETHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txallhc = models.DecimalField(db_column='TXALLHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txexphc = models.DecimalField(db_column='TXEXPHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    txrechc = models.DecimalField(db_column='TXRECHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    apversion = models.CharField(db_column='APVERSION', max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    cntacc = models.IntegerField(db_column='CNTACC')  # Field name made lowercase.
    amtacctc = models.DecimalField(db_column='AMTACCTC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtacchc = models.DecimalField(db_column='AMTACCHC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    enteredby = models.CharField(db_column='ENTEREDBY', max_length=8, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    datebus = models.DecimalField(db_column='DATEBUS', max_digits=9, decimal_places=0)  # Field name made lowercase.
    idacctset = models.CharField(db_column='IDACCTSET', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    amtwht1tc = models.DecimalField(db_column='AMTWHT1TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtwht2tc = models.DecimalField(db_column='AMTWHT2TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtwht3tc = models.DecimalField(db_column='AMTWHT3TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtwht4tc = models.DecimalField(db_column='AMTWHT4TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtwht5tc = models.DecimalField(db_column='AMTWHT5TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxbs1tc = models.DecimalField(db_column='AMTCXBS1TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxbs2tc = models.DecimalField(db_column='AMTCXBS2TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxbs3tc = models.DecimalField(db_column='AMTCXBS3TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxbs4tc = models.DecimalField(db_column='AMTCXBS4TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxbs5tc = models.DecimalField(db_column='AMTCXBS5TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxtx1tc = models.DecimalField(db_column='AMTCXTX1TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxtx2tc = models.DecimalField(db_column='AMTCXTX2TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxtx3tc = models.DecimalField(db_column='AMTCXTX3TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxtx4tc = models.DecimalField(db_column='AMTCXTX4TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtcxtx5tc = models.DecimalField(db_column='AMTCXTX5TC', max_digits=19, decimal_places=3)  # Field name made lowercase.
    amtgrosdst = models.DecimalField(db_column='AMTGROSDST', max_digits=19, decimal_places=3)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'APTCR'
        unique_together = (('btchtype', 'cntbtch', 'cntentr'),)

