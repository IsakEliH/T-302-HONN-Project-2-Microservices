import json
import os


class PaymentRepository:
    DB_FILE: str = "data/paymentData.json"
    INDENT: int = 4

    def save_payment(self, orderId, status):
        format_message: dict = {
            "orderId": orderId,
            "status": status
        }

        self.data_list.append(format_message)
        with open(self.DB_FILE, "w", encoding="utf-8") as file:
            json.dump(self.data_list, file, indent=self.INDENT)





    def get_payment(self, orderId) -> dict:

        if os.path.exists(self.DB_FILE) and os.path.getsize(self.DB_FILE) > 0:
            with open(self.DB_FILE, "r", encoding="utf-8") as file:
                data_list: dict = json.load(file)
                for entry_dict in data_list:
                    if entry_dict.get("orderId") == orderId:
                        return entry_dict
        return {}