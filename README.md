## BSE XSIP Order Entry

### Function
`soap_bse_xsip_order_entry`

### Arguments
- `client_code` (str)
- `scheme_code` (str)
- `mandate_id` (str)
- `amount` (str)
- `start_date` (str)
- `end_date` (str, optional) Default: ""
- `first_order_today` (str, optional) Default: "Y"
- `transaction_type` (str, optional) Default: "NEW"
- `unique_ref_no` (str, optional) Default: ""
- `xsip_regn_id` (str, optional) Default: ""
- `frequency_type` (str, optional) Default: "MONTHLY"
- `no_of_installments` (str, optional) Default: "" # Mandatory for DAILY XSIP

### Response

#### Success
```
NEW|3010284860|59729|8428|5972901|119494864|X-SIP HAS BEEN REGISTERED, REG NO IS : 119494864|0|1531828799

# First order today = N
NEW|1714005434|59729|8428|5972901|119494770|X-SIP HAS BEEN REGISTERED, REG NO IS : 119494770|0|0
```

#### Failure
```
NEW|2998860996|59729|8428|5972901|0|FAILED: INSTALLMENT AMT IS LESS THAN MINIMUM INSTALLMENT AMT|1|0

NEW|4386573726|59729|8428|5972901|0|FAILED: NO OF INSTALLMENT NOT ALLOWED IN DAILY XSIP\\ ISIP|1|0
```

---

## Cancel XSIP

### Function
`rest_starmf_cancel_xsip`

### Arguments
- `client_code`
- `xsip_regn_id`
- `internal_ref_no`

### Response

#### Success
```json
{
  "XSIPRegId": "119236449",
  "BSERemarks": "X-SIP OR I-SIP WITH REGN NO 119236449 IS CANCELLED SUCCESSFULLY",
  "SuccessFlag": "0",
  "IntRefNo": ""
}
```

#### Failure
**Reason**: Wrong SIP registration ID or wrong client code.
```json
{
  "XSIPRegId": "119236443",
  "BSERemarks": "XSIP REGISTRATION NO. IS NOT EXISTS",
  "SuccessFlag": "1",
  "IntRefNo": ""
}
```

---