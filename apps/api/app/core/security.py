import re
from typing import Tuple

# Compiled patterns for secret detection
REDACTION_PATTERNS = [
    # AWS Access Key ID
    (re.compile(r"\b(AKIA[0-9A-Z]{16})\b"), "[REDACTED_AWS_ACCESS_KEY]"),
    # GitHub Personal Access Tokens
    (re.compile(r"\b(ghp_[a-zA-Z0-9]{36})\b"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"\b(github_pat_[a-zA-Z0-9_]{22,82})\b"), "[REDACTED_GITHUB_TOKEN]"),
    # OpenAI API Keys
    (re.compile(r"\b(sk-[a-zA-Z0-9\-_]{20,})\b"), "[REDACTED_OPENAI_KEY]"),
    # Google API Keys
    (re.compile(r"\b(AIza[0-9A-Za-z\-_]{35})\b"), "[REDACTED_GOOGLE_API_KEY]"),
    # Bearer Tokens
    (re.compile(r"(?i)\bBearer\s+([a-zA-Z0-9\-\._~\+\/]+=*)"), "Bearer [REDACTED_BEARER_TOKEN]"),
    # JSON Web Tokens (JWT)
    (
        re.compile(r"\b(eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})\b"),
        "[REDACTED_JWT_TOKEN]",
    ),
    # Database URIs with passwords (e.g., postgresql://user:password@host:port/db)
    (
        re.compile(r"([a-zA-Z0-9+]+://[^:\s]+:)([^@\s]+)(@[^\s]+)"),
        r"\1[REDACTED_PASSWORD]\3",
    ),
    # Key-Value secrets (password=secret, secret_key: "abc")
    (
        re.compile(
            r"""(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token|client[_-]?secret)\s*[:=]\s*(['"][^'"]{4,}['"]|[^\s,;]{4,})"""
        ),
        r"\1: [REDACTED_SECRET]",
    ),
    # RSA / OpenSSH Private Keys
    (
        re.compile(
            r"-----BEGIN\s+(?:[A-Z\s]+)?PRIVATE\s+KEY-----[\s\S]+?-----END\s+(?:[A-Z\s]+)?PRIVATE\s+KEY-----"
        ),
        "[REDACTED_PRIVATE_KEY]",
    ),
]


class SecretRedactor:
    """
    Scans raw log text and replaces detected secrets, tokens, and credentials
    with safe placeholder tags before sending content to AI models.
    """

    @classmethod
    def redact(cls, text: str) -> Tuple[str, int]:
        redacted_text = text
        total_redactions = 0

        for pattern, replacement in REDACTION_PATTERNS:
            matches = list(pattern.finditer(redacted_text))
            if matches:
                total_redactions += len(matches)
                redacted_text = pattern.sub(replacement, redacted_text)

        return redacted_text, total_redactions


def sanitize_and_validate_log_input(raw_logs: str, max_chars: int = 65536) -> str:
    """
    Normalizes log strings and checks maximum payload limits.
    Prevents empty or oversized log payloads from exhausting memory.
    """
    if not raw_logs or not raw_logs.strip():
        raise ValueError("Log input cannot be empty or solely whitespace.")

    # Normalize line endings
    cleaned = raw_logs.replace("\r\n", "\n").replace("\r", "\n")

    if len(cleaned) > max_chars:
        raise ValueError(
            f"Log payload exceeds the maximum allowed size of {max_chars} characters (received {len(cleaned)} chars)."
        )

    return cleaned.strip()
