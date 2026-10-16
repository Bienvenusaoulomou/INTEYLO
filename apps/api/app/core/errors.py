"""Codes d'erreur stables (anglais, lisibles par la machine) et exception applicative.

Le message affiché est toujours français : voir ``messages_fr.py``.
"""

from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    VALIDATION_ERROR = "validation_error"
    MALFORMED_REQUEST = "malformed_request"
    AUTHENTICATION_REQUIRED = "authentication_required"
    INVALID_CREDENTIALS = "invalid_credentials"
    TOO_MANY_ATTEMPTS = "too_many_attempts"
    EMAIL_ALREADY_USED = "email_already_used"
    CSRF_HEADER_MISSING = "csrf_header_missing"
    PERMISSION_DENIED = "permission_denied"
    ORGANIZATION_NOT_FOUND = "organization_not_found"
    ORGANIZATION_SUSPENDED = "organization_suspended"
    MEMBER_NOT_FOUND = "member_not_found"
    UNKNOWN_ROLE = "unknown_role"
    ROLE_NOT_ASSIGNABLE = "role_not_assignable"
    MEMBER_NOT_MANAGEABLE = "member_not_manageable"
    CANNOT_MODIFY_SELF = "cannot_modify_self"
    LAST_OWNER = "last_owner"
    ALREADY_MEMBER = "already_member"
    INVITATION_PENDING = "invitation_pending"
    INVITATION_INVALID = "invitation_invalid"
    INVITATION_NOT_FOUND = "invitation_not_found"
    INVITATION_EMAIL_MISMATCH = "invitation_email_mismatch"
    INVITATION_LOGIN_REQUIRED = "invitation_login_required"
    SESSION_NOT_FOUND = "session_not_found"
    NOT_FOUND = "not_found"
    METHOD_NOT_ALLOWED = "method_not_allowed"
    SERVICE_UNAVAILABLE = "service_unavailable"
    INTERNAL_ERROR = "internal_error"


class ApiError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        status_code: int,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(code.value)
        self.code = code
        self.status_code = status_code
        self.details = details or []
