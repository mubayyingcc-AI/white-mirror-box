from execucern import Firewall, Rule


def lookup_order(order_id: str):
    return {"order_id": order_id, "status": "processing"}


firewall = Firewall(
    rules={"lookup_order": Rule(allow=True)},
    approval_secret="replace-me-with-a-secret-manager-value",
)

print(firewall.execute("support-agent", "lookup_order", {"order_id": "o-123"}, lookup_order))
