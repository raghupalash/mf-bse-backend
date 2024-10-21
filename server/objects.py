# trans_no, trans_code, order_type, client_code, scheme_code, order_value, order_id=None


class OrderEntryParam:
    def __init__(self, data):
        self.trans_code = data.get("trans_code")
        self.order_type = data.get("order_type")
        self.client_code = data.get("client_code")
        self.scheme_code = data.get("scheme_code")
        self.order_value = data.get("order_value")
        self.order_id = data.get("order_id")
