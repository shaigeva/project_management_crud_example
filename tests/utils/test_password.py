"""Tests for password utility functions."""

import re

from project_management_crud_example.utils.password import generate_password, hash_password, verify_password


class TestHashPassword:
    """Tests for password hashing."""

    def test_hash_password_creates_valid_bcrypt_hash(self) -> None:
        """Test that password is hashed with bcrypt format."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")  # bcrypt hash prefix
        assert len(hashed) == 60  # Standard bcrypt hash length

    def test_hash_password_different_each_time(self) -> None:
        """Test that same password creates different hashes due to salt."""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        assert hash1.startswith("$2b$")
        assert hash2.startswith("$2b$")


class TestVerifyPassword:
    """Tests for password verification."""

    def test_verify_password_with_correct_password_succeeds(self) -> None:
        """Test that correct password verification succeeds."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_with_wrong_password_fails(self) -> None:
        """Test that wrong password verification fails."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_is_case_sensitive(self) -> None:
        """Test that password verification is case sensitive."""
        password = "TestPassword123"
        hashed = hash_password(password)

        assert verify_password("testpassword123", hashed) is False
        assert verify_password("TESTPASSWORD123", hashed) is False
        assert verify_password(password, hashed) is True


class TestGeneratePassword:
    """Tests for password generation."""

    def test_generate_password_creates_secure_password(self) -> None:
        """Test that generated password meets security requirements."""
        password = generate_password()

        # Check length
        assert len(password) >= 12

        # Check character types
        assert re.search(r"[A-Z]", password) is not None  # Uppercase
        assert re.search(r"[a-z]", password) is not None  # Lowercase
        assert re.search(r"\d", password) is not None  # Digit
        assert re.search(r"[!@#$%^&*()\-_=+\[\]{}|;:,.<>?]", password) is not None  # Special char

    def test_generate_password_creates_different_passwords(self) -> None:
        """Test that each generated password is unique."""
        passwords = [generate_password() for _ in range(10)]

        # All passwords should be different
        assert len(set(passwords)) == 10

    def test_generate_password_always_meets_requirements(self) -> None:
        """Test that all generated passwords meet security requirements."""
        # Generate multiple passwords to test consistency
        for _ in range(20):
            password = generate_password()

            assert len(password) >= 12
            assert re.search(r"[A-Z]", password) is not None
            assert re.search(r"[a-z]", password) is not None
            assert re.search(r"\d", password) is not None
            assert re.search(r"[!@#$%^&*()\-_=+\[\]{}|;:,.<>?]", password) is not None
