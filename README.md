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