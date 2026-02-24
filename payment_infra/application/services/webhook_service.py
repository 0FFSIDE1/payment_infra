class WebhookService:

    def __init__(self, provider):
        self.provider = provider

    def handle(self, raw_body: bytes, signature: str):

        if not self.provider.verify_signature(raw_body, signature):
            raise ValueError("Invalid signature")

        import json
        payload = json.loads(raw_body)

        event = self.provider.parse_event(payload)

        return event