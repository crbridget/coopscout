from functools import wraps

def retry_on_failure(max_retries=3, delay=2):
    """Retry a function if it fails"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"      ⚠️  Attempt {attempt + 1} failed: {str(e)[:50]}... Retrying...")
                        time.sleep(delay)
                    else:
                        print(f"      ❌ All {max_retries} attempts failed")
                        raise
            return None
        return wrapper
    return decorator