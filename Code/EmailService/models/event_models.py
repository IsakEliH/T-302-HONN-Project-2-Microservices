from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrderCreatedEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    order_id: int = Field(default=0, alias="orderId")
    product_id: int = Field(default=0, alias="productId")
    merchant_id: int = Field(default=0, alias="merchantId")
    buyer_id: int = Field(default=0, alias="buyerId")
    product_name: str = Field(default="", alias="productName")
    buyer_email: str = Field(default="", alias="buyerEmail")
    merchant_email: str = Field(default="", alias="merchantEmail")
    total_price: float = Field(default=0.0, alias="totalPrice")
    discount: float = Field(default=0.0)

    @model_validator(mode="before")
    def normalize_data(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        flattened = dict(data)

        # Handle nested 'order' dictionary if present (e.g. from OrderService event publisher)
        if "order" in flattened and isinstance(flattened["order"], dict):
            order_data = flattened.pop("order")
            for key, val in order_data.items():
                if key not in flattened or flattened[key] is None or flattened[key] == "":
                    flattened[key] = val

        # Handle field alias alternatives and typos
        if "orderId" in flattened and "order_id" not in flattened:
            flattened["order_id"] = flattened["orderId"]
        elif "order_id" in flattened and "orderId" not in flattened:
            flattened["orderId"] = flattened["order_id"]

        if "productId" in flattened and "product_id" not in flattened:
            flattened["product_id"] = flattened["productId"]
        if "merchantId" in flattened and "merchant_id" not in flattened:
            flattened["merchant_id"] = flattened["merchantId"]
        if "buyerId" in flattened and "buyer_id" not in flattened:
            flattened["buyer_id"] = flattened["buyerId"]

        if "productName" in flattened and "product_name" not in flattened:
            flattened["product_name"] = flattened["productName"]
        if "buyerEmail" in flattened and "buyer_email" not in flattened:
            flattened["buyer_email"] = flattened["buyerEmail"]
        if "merchantEmail" in flattened and "merchant_email" not in flattened:
            flattened["merchant_email"] = flattened["merchantEmail"]
        if "totalPrice" in flattened and "total_price" not in flattened:
            flattened["total_price"] = flattened["totalPrice"]
        return flattened


class PaymentEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    order_id: int = Field(default=0, alias="orderId")
    status: Optional[str] = None
    payment_result: Optional[str] = Field(default=None, alias="paymentResult")
    buyer_email: Optional[str] = Field(default=None, alias="buyerEmail")
    merchant_email: Optional[str] = Field(default=None, alias="merchantEmail")

    @property
    def is_success(self) -> bool:
        val = (self.status or self.payment_result or "").strip().lower()
        return val in ("success", "successful", "ok", "paid")

    @model_validator(mode="before")
    def normalize_payment(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        flattened = dict(data)
        if "orderId" in flattened and "order_id" not in flattened:
            flattened["order_id"] = flattened["orderId"]
        elif "order_id" in flattened and "orderId" not in flattened:
            flattened["orderId"] = flattened["order_id"]

        if "paymentResult" in flattened and "payment_result" not in flattened:
            flattened["payment_result"] = flattened["paymentResult"]
        elif "payment_result" in flattened and "paymentResult" not in flattened:
            flattened["paymentResult"] = flattened["payment_result"]

        if "buyerEmail" in flattened and "buyer_email" not in flattened:
            flattened["buyer_email"] = flattened["buyerEmail"]
        elif "buyer_email" in flattened and "buyerEmail" not in flattened:
            flattened["buyerEmail"] = flattened["buyer_email"]

        if "merchantEmail" in flattened and "merchant_email" not in flattened:
            flattened["merchant_email"] = flattened["merchantEmail"]
        elif "merchant_email" in flattened and "merchantEmail" not in flattened:
            flattened["merchantEmail"] = flattened["merchant_email"]

        event_type = (flattened.get("eventType") or flattened.get("event_type") or flattened.get("type") or "").lower()
        if not flattened.get("status") and not flattened.get("paymentResult") and not flattened.get("payment_result"):
            if "success" in event_type:
                flattened["status"] = "success"
            elif "fail" in event_type:
                flattened["status"] = "failed"
        elif not flattened.get("status") and (flattened.get("paymentResult") or flattened.get("payment_result")):
            flattened["status"] = flattened.get("paymentResult") or flattened.get("payment_result")
        return flattened
