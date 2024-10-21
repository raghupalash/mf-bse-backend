import os
import sys
import django
import csv
from datetime import datetime
from django.db import transaction


from server.models import MutualFundList


def parse_date(date_string):
    return datetime.strptime(date_string, "%b %d %Y").date()


def parse_time(time_string):
    return datetime.strptime(time_string, "%H:%M:%S").time()


@transaction.atomic
def import_mutual_funds():
    file_path = os.path.join("scheme_master", "SCHMSTRPHY_21082024.txt")

    with open(file_path, "r") as file:
        reader = csv.DictReader(file, delimiter="|")
        for row in reader:
            MutualFundList.objects.create(
                unique_no=int(row["Unique No"]) if row["Unique No"] else None,
                scheme_code=row["Scheme Code"],
                rta_scheme_code=row["RTA Scheme Code"],
                amc_scheme_code=row["AMC Scheme Code"],
                isin=row["ISIN"],
                amc_code=row["AMC Code"],
                scheme_type=row["Scheme Type"],
                scheme_plan=row["Scheme Plan"],
                scheme_name=row["Scheme Name"],
                purchase_allowed=row["Purchase Allowed"],
                purchase_transaction_mode=row["Purchase Transaction mode"],
                minimum_purchase_amount=float(row["Minimum Purchase Amount"]) if row["Minimum Purchase Amount"] else None,
                additional_purchase_amount=float(row["Additional Purchase Amount"]) if row["Additional Purchase Amount"] else None,
                maximum_purchase_amount=float(row["Maximum Purchase Amount"]) if row["Maximum Purchase Amount"] else None,
                purchase_amount_multiplier=float(row["Purchase Amount Multiplier"]) if row["Purchase Amount Multiplier"] else None,
                purchase_cutoff_time=parse_time(row["Purchase Cutoff Time"]),
                redemption_allowed=row["Redemption Allowed"],
                redemption_transaction_mode=row["Redemption Transaction Mode"],
                minimum_redemption_qty=float(row["Minimum Redemption Qty"]) if row["Minimum Redemption Qty"] else None,
                redemption_qty_multiplier=float(row["Redemption Qty Multiplier"]) if row["Redemption Qty Multiplier"] else None,
                maximum_redemption_qty=float(row["Maximum Redemption Qty"]) if row["Maximum Redemption Qty"] else None,
                redemption_amount_minimum=float(row["Redemption Amount - Minimum"]) if row["Redemption Amount - Minimum"] else None,
                redemption_amount_maximum=float(row["Redemption Amount – Maximum"]) if row["Redemption Amount – Maximum"] else None,
                redemption_amount_multiple=float(row["Redemption Amount Multiple"]) if row["Redemption Amount Multiple"] else None,
                redemption_cutoff_time=parse_time(row["Redemption Cut off Time"]),
                rta_agent_code=row["RTA Agent Code"],
                amc_active_flag=int(row["AMC Active Flag"]) if row["AMC Active Flag"] else None,
                dividend_reinvestment_flag=row["Dividend Reinvestment Flag"],
                sip_flag=row["SIP FLAG"],
                stp_flag=row["STP FLAG"],
                swp_flag=row["SWP Flag"],
                switch_flag=row["Switch FLAG"],
                settlement_type=row["SETTLEMENT TYPE"],
                amc_ind=row["AMC_IND"],
                face_value=float(row["Face Value"]) if row["Face Value"] else None,
                start_date=parse_date(row["Start Date"]),
                end_date=parse_date(row["End Date"]),
                exit_load_flag=row["Exit Load Flag"],
                exit_load=int(row["Exit Load"]) if row["Exit Load"] else None,
                lock_in_period_flag=row["Lock-in Period Flag"],
                lock_in_period=int(row["Lock-in Period"]) if row["Lock-in Period"] else None,
                channel_partner_code=row["Channel Partner Code"],
                reopening_date=parse_date(row["ReOpening Date"]) if row["ReOpening Date"] else None,
            )


if __name__ == "__main__":
    try:
        import_mutual_funds()
        print("Data import completed successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("All changes have been rolled back.")
