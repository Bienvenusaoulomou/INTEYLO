"""Catalogue des messages d'erreur français de l'API.

Règle (prompt maître, section 13) : chaque ``ErrorCode`` doit avoir un message ici.
Un test bloquant en CI le vérifie.
"""

from typing import Any

from app.core.errors import ErrorCode

MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.VALIDATION_ERROR: "Certaines informations sont invalides. Vérifiez les champs signalés.",
    ErrorCode.MALFORMED_REQUEST: "La requête est mal formée.",
    ErrorCode.AUTHENTICATION_REQUIRED: "Votre session a expiré ou n'existe pas. Veuillez vous reconnecter.",
    ErrorCode.INVALID_CREDENTIALS: "Adresse e-mail ou mot de passe incorrect.",
    ErrorCode.TOO_MANY_ATTEMPTS: "Trop de tentatives. Veuillez patienter quelques minutes avant de réessayer.",
    ErrorCode.EMAIL_ALREADY_USED: "Un compte existe déjà avec cette adresse e-mail.",
    ErrorCode.CSRF_HEADER_MISSING: "Requête refusée pour des raisons de sécurité.",
    ErrorCode.PERMISSION_DENIED: "Vous n'avez pas l'autorisation d'effectuer cette opération.",
    ErrorCode.ORGANIZATION_NOT_FOUND: "Organisation introuvable.",
    ErrorCode.ORGANIZATION_SUSPENDED: "Cette organisation est suspendue. Contactez le support.",
    ErrorCode.MEMBER_NOT_FOUND: "Membre introuvable.",
    ErrorCode.UNKNOWN_ROLE: "Ce rôle n'existe pas.",
    ErrorCode.ROLE_NOT_ASSIGNABLE: "Vous ne pouvez pas attribuer ce rôle.",
    ErrorCode.MEMBER_NOT_MANAGEABLE: "Vous ne pouvez pas modifier ce membre : son rôle est égal ou supérieur au vôtre.",
    ErrorCode.CANNOT_MODIFY_SELF: "Vous ne pouvez pas modifier vos propres rôles ni désactiver votre propre accès.",
    ErrorCode.LAST_OWNER: "L'organisation doit conserver au moins un propriétaire actif.",
    ErrorCode.ALREADY_MEMBER: "Cette personne est déjà membre de l'organisation.",
    ErrorCode.INVITATION_PENDING: "Une invitation est déjà en attente pour cette adresse e-mail.",
    ErrorCode.INVITATION_INVALID: "Cette invitation n'est plus valide (expirée, révoquée ou déjà utilisée).",
    ErrorCode.INVITATION_NOT_FOUND: "Invitation introuvable.",
    ErrorCode.INVITATION_EMAIL_MISMATCH: "Cette invitation est destinée à une autre adresse e-mail.",
    ErrorCode.INVITATION_LOGIN_REQUIRED: "Un compte existe déjà pour cette adresse. Connectez-vous pour accepter l'invitation.",
    ErrorCode.SESSION_NOT_FOUND: "Session introuvable.",
    ErrorCode.NOT_FOUND: "Ressource introuvable.",
    ErrorCode.METHOD_NOT_ALLOWED: "Méthode non autorisée.",
    ErrorCode.SERVICE_UNAVAILABLE: "Le service est temporairement indisponible.",
    ErrorCode.INTERNAL_ERROR: "Une erreur interne est survenue. Veuillez réessayer plus tard.",
}

# Traduction des erreurs de validation Pydantic (jamais renvoyées brutes).
_VALIDATION_MESSAGES: dict[str, str] = {
    "missing": "Ce champ est obligatoire.",
    "string_too_short": "Ce champ doit contenir au moins {min_length} caractères.",
    "string_too_long": "Ce champ doit contenir au plus {max_length} caractères.",
    "too_short": "Cette liste doit contenir au moins {min_length} élément(s).",
    "too_long": "Cette liste doit contenir au plus {max_length} élément(s).",
    "uuid_parsing": "Identifiant invalide.",
    "uuid_type": "Identifiant invalide.",
    "json_invalid": "Le contenu envoyé n'est pas un JSON valide.",
    "extra_forbidden": "Ce champ n'est pas autorisé.",
    "literal_error": "Valeur non autorisée.",
    "enum": "Valeur non autorisée.",
    "int_parsing": "Un nombre entier est attendu.",
    "less_than_equal": "La valeur doit être inférieure ou égale à {le}.",
    "greater_than_equal": "La valeur doit être supérieure ou égale à {ge}.",
    "string_type": "Une chaîne de caractères est attendue.",
    "list_type": "Une liste est attendue.",
    "bool_parsing": "Une valeur booléenne est attendue.",
    "model_attributes_type": "Un objet est attendu.",
    "dict_type": "Un objet est attendu.",
}

_FIELD_SPECIFIC: dict[str, str] = {
    "email": "Adresse e-mail invalide.",
}

_CUSTOM_VALUE_ERRORS: dict[str, str] = {
    "invalid_timezone": "Fuseau horaire inconnu.",
    "blank": "Ce champ ne peut pas être vide.",
}


def message_for(code: ErrorCode) -> str:
    return MESSAGES[code]


def translate_validation_error(error: dict[str, Any]) -> dict[str, str]:
    loc = [str(part) for part in error.get("loc", ()) if part not in ("body", "query", "path")]
    field = ".".join(loc) or "requête"
    err_type = str(error.get("type", ""))
    ctx = error.get("ctx") or {}

    if err_type == "value_error":
        custom = str(ctx.get("error", ""))
        if custom in _CUSTOM_VALUE_ERRORS:
            return {"field": field, "message": _CUSTOM_VALUE_ERRORS[custom]}
        last = loc[-1] if loc else ""
        if last in _FIELD_SPECIFIC:
            return {"field": field, "message": _FIELD_SPECIFIC[last]}
        return {"field": field, "message": "Valeur invalide."}

    template = _VALIDATION_MESSAGES.get(err_type)
    if template is None:
        if err_type.endswith("_type") or err_type.endswith("_parsing"):
            return {"field": field, "message": "Type de valeur invalide."}
        return {"field": field, "message": "Valeur invalide."}
    try:
        message = template.format(**{k: v for k, v in ctx.items() if isinstance(v, int | str)})
    except (KeyError, IndexError):
        message = "Valeur invalide."
    return {"field": field, "message": message}
