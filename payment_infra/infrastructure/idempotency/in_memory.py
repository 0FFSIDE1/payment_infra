class InMemoryIdempotencyService:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ttl=None):
        self.store[key] = value
    
    def execute(self, key: str, callback):
        existing = self.get(key)

        if existing:
            if existing['status'] == 'COMPLETED':
                return existing['response_payload']

            if existing['status'] == 'PROCESSING':
                raise RuntimeError("Request already processing.")

        self.set(key, {'status': 'PROCESSING'})

        try:
            result = callback()
            self.set(key, {'status': 'COMPLETED', 'response_payload': result})
            return result
        except Exception:
            self.set(key, {'status': 'FAILED'})
            raise