import httpx
import pytest

from sumup.transactions import GetTransactionV21Params


def test_transactions_get_entry_mode_none_is_normalized(sdk_factory):
    captured_request: dict[str, httpx.Request] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_request["request"] = request

        # Minimal-ish payload. If Pydantic complains about missing fields,
        # just add them (see note below).
        payload = {
            "id": "eb5efe2a-4f81-4a74-a14d-2afa3d23c6ef",
            "merchant_code": "merchant-123",
            "amount": 5.0,
            "currency": "EUR",
            "status": "FAILED",
            "simple_status": "FAILED",
            "timestamp": "2025-12-11T20:24:55.471Z",
            "payment_type": "POS",
            "entry_mode": "none",  # <-- the problematic value
            "products": [
                {
                    "name": "Order #2302",
                    "price": 5.0,
                    "quantity": 1,
                    "total_price": 5.0,
                    "total_with_vat": 5.0,
                    "vat_amount": 0.0,
                }
            ],
            "links": [],
            "vat_rates": [],
            "transaction_events": [],
        }
        return httpx.Response(200, json=payload)

    sdk = sdk_factory(handler)

    params = GetTransactionV21Params(
        client_transaction_id="f982b640-1a68-4160-a861-cfc2f6c355f9"
    )
    tx = sdk.transactions.get("merchant-123", params=params)

    # Assert request correctness
    assert "request" in captured_request
    request = captured_request["request"]
    assert request.url.path == "/v2.1/merchants/merchant-123/transactions"
    assert list(request.url.params.multi_items()) == [
        ("client_transaction_id", "f982b640-1a68-4160-a861-cfc2f6c355f9")
    ]

    # Assert parsing result: your fix should convert "none" -> None
    assert tx.entry_mode is None
    assert tx.status == "FAILED"
