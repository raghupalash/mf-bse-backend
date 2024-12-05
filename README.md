## BSE XSIP Order Entry

### Function
`soap_bse_xsip_order_entry`

### Arguments
- `client_code` (str): The client's unique code.
- `scheme_code` (str): The code of the scheme for the XSIP order.
- `mandate_id` (str): The mandate ID associated with the order.
- `amount` (str): The amount for the XSIP order.
- `start_date` (str): The start date for the XSIP order.
- `end_date` (str, optional): The end date for the XSIP order. Defaults to an empty string.
- `first_order_today` (str, optional): Indicates if the first order should be placed today. Defaults to "Y".
- `transaction_type` (str, optional): The type of transaction. Defaults to "NEW".
- `unique_ref_no` (str, optional): A unique reference number for the order. Defaults to an empty string.
- `xsip_regn_id` (str, optional): The XSIP registration ID. Defaults to an empty string.
- `frequency_type` (str, optional): The frequency type for the XSIP order. Defaults to "MONTHLY".

### Description
This function is used to place an XSIP order entry with the BSE. It requires the client code, scheme code, mandate ID, amount, and start date as mandatory parameters. Optional parameters include end date, first order placement, transaction type, unique reference number, XSIP registration ID, and frequency type.
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