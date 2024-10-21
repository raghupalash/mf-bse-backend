import csv
import os
from django.core.management.base import BaseCommand
from server.models import KFintechPortfolio

class Command(BaseCommand):
    help = 'Load data from a CSV file into the MutualFundTransaction model'

    def handle(self, *args, **kwargs):
        csv_file_path = "kfin_portfolio/portfolio.csv"

        if not os.path.isfile(csv_file_path):
            self.stdout.write(self.style.ERROR('File does not exist'))
            return

        with transaction.atomic():
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Create a new KFintechPortfolio object
                    transaction = KFintechPortfolio(
                        sno=row.get('SNO'),
                        fmcode=row.get('FMCODE'),
                        td_fund=row.get('TD_FUND'),
                        td_acno=row.get('TD_ACNO'),
                        schpln=row.get('SCHPLN'),
                        divopt=row.get('DIVOPT'),
                        funddesc=row.get('FUNDDESC'),
                        td_purred=row.get('TD_PURRED'),
                        td_trno=row.get('TD_TRNO'),
                        smcode=row.get('SMCODE'),
                        chqno=row.get('CHQNO'),
                        invname=row.get('INVNAME'),
                        jtname1=row.get('JTNAME1'),
                        jtname2=row.get('JTNAME2'),
                        add1=row.get('ADD1'),
                        add2=row.get('ADD2'),
                        add3=row.get('ADD3'),
                        city=row.get('CITY'),
                        pin=row.get('PIN'),
                        state=row.get('STATE'),
                        country=row.get('COUNTRY'),
                        dob=row.get('DOB'),
                        rphone=row.get('RPHONE'),
                        rphone1=row.get('RPHONE1'),
                        rphone2=row.get('RPHONE2'),
                        mobile=row.get('MOBILE'),
                        ophone=row.get('OPHONE'),
                        ophone1=row.get('OPHONE1'),
                        ophone2=row.get('OPHONE2'),
                        fax=row.get('FAX'),
                        faxoff=row.get('FAXOFF'),
                        status=row.get('STATUS'),
                        occpn=row.get('OCCPN'),
                        email=row.get('EMAIL'),
                        bnkacno=row.get('BNKACNO'),
                        bname=row.get('BNAME'),
                        bnkactype=row.get('BNKACTYPE'),
                        branch=row.get('BRANCH'),
                        badd1=row.get('BADD1'),
                        badd2=row.get('BADD2'),
                        badd3=row.get('BADD3'),
                        bcity=row.get('BCITY'),
                        bphone=row.get('BPHONE'),
                        pangno=row.get('PANGNO'),
                        trnmode=row.get('TRNMODE'),
                        trnstat=row.get('TRNSTAT'),
                        td_branch=row.get('TD_BRANCH'),
                        isctrno=row.get('ISCTRNO'),
                        td_trdt=row.get('TD_TRDT'),
                        td_prdt=row.get('TD_PRDT'),
                        td_pop=row.get('TD_POP'),
                        loadper=row.get('LOADPER'),
                        td_units=row.get('TD_UNITS'),
                        td_amt=row.get('TD_AMT'),
                        load1=row.get('LOAD1'),
                        td_agent=row.get('TD_AGENT'),
                        td_broker=row.get('TD_BROKER'),
                        brokper=row.get('BROKPER'),
                        brokcomm=row.get('BROKCOMM'),
                        invid=row.get('INVID'),
                        crdate=row.get('CRDATE'),
                        crtime=row.get('CRTIME'),
                        trnsub=row.get('TRNSUB'),
                        td_appno=row.get('TD_APPNO'),
                        unqno=row.get('UNQNO'),
                        trdesc=row.get('TRDESC'),
                        td_trtype=row.get('TD_TRTYPE'),
                        purdate=row.get('PURDATE'),
                        puramt=row.get('PURAMT'),
                        purunits=row.get('PURUNITS'),
                        trflag=row.get('TRFLAG'),
                        sfunddt=row.get('SFUNDDT'),
                        chqdate=row.get('CHQDATE'),
                        chqbank=row.get('CHQBANK'),
                        nctremarks=row.get('NCTREMARKS'),
                        td_scheme=row.get('TD_SCHEME'),
                        td_plan=row.get('TD_PLAN'),
                        td_nav=row.get('TD_NAV'),
                        annper=row.get('ANNPER'),
                        annamt=row.get('ANNAMT'),
                        td_ptrno=row.get('TD_PTRNO'),
                        td_pbranch=row.get('TD_PBRANCH'),
                        oldacno=row.get('OLDACNO'),
                        ihno=row.get('IHNO'),
                    )
                    transaction.save()

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))