import pytest
from app.core.security import SecretRedactor, sanitize_and_validate_log_input


def test_secret_redactor_redacts_credentials():
    dirty_log = """
    2026-10-10 12:00:00 ERROR DB Connection failed
    URI: postgresql://admin:SuperSecret123@db.prod.internal:5432/core
    AWS Key: AKIAIOSFODNN7EXAMPLE
    GitHub Token: ghp_1234567890abcdefghijklmnopqrstuvwxyz
    Authorization: Bearer mySecretToken1234567890abcdef
    Config: password="MyDbPassword456!"
    """

    cleaned, count = SecretRedactor.redact(dirty_log)

    assert count >= 4
    assert "SuperSecret123" not in cleaned
    assert "[REDACTED_PASSWORD]" in cleaned
    assert "AKIAIOSFODNN7EXAMPLE" not in cleaned
    assert "[REDACTED_AWS_ACCESS_KEY]" in cleaned
    assert "ghp_1234567890abcdefghijklmnopqrstuvwxyz" not in cleaned
    assert "[REDACTED_GITHUB_TOKEN]" in cleaned
    assert "mySecretToken1234567890abcdef" not in cleaned
    assert "[REDACTED_BEARER_TOKEN]" in cleaned


def test_sanitize_and_validate_log_input():
    # Empty string should raise ValueError
    with pytest.raises(ValueError, match="cannot be empty"):
        sanitize_and_validate_log_input("   ")

    # Log exceeding character limit should raise ValueError
    large_log = "x" * 200
    with pytest.raises(ValueError, match="exceeds the maximum allowed size"):
        sanitize_and_validate_log_input(large_log, max_chars=100)

    # Valid string should be stripped and normalized
    valid = "  sample error log line\r\nnext line  "
    result = sanitize_and_validate_log_input(valid, max_chars=100)
    assert result == "sample error log line\nnext line"
