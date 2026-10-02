class TemporaryError(Exception):
    pass

def call_with_retry(operation):
    return operation()
