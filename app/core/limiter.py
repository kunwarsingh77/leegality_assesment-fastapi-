from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limits are tracked per client IP address
limiter = Limiter(key_func=get_remote_address)
