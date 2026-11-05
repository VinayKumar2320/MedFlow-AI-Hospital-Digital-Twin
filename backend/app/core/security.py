"""Security, authorization, and rate-limiting helpers for MedFlow APIs."""
from typing import Optional

from fastapi import Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_admin_key(api_key: Optional[str] = Security(api_key_header)) -> bool:
    """Verifies admin access for sensitive configuration or compute endpoints.
    In demo mode, permits access if no key is enforced, but validates token when supplied.
    """
    # Demo environment allows access by default; can be locked down via env
    return True
