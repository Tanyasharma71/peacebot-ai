"""
Input Validation and Sanitization for Peacebot
Provides comprehensive validation and sanitization for user inputs.
"""

import re
import html
from typing import Optional, Dict, Any, List
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.logger_config import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.field = field
        self.details = details or {}
        super().__init__(self.message)


class InputValidator:
    """
    Comprehensive input validation and sanitization.
    """
    
    # Validation rules
    MAX_MESSAGE_LENGTH = 5000
    MIN_MESSAGE_LENGTH = 1
    MAX_MOOD_NOTE_LENGTH = 1000
    
    # Dangerous patterns
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers
        r'<iframe[^>]*>',  # Iframes
        r'<object[^>]*>',  # Objects
        r'<embed[^>]*>',  # Embeds
    ]
    
    # SQL injection patterns
    SQL_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bSELECT\b.*\bFROM\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bDROP\b.*\bTABLE\b)",
    ]
    
    # Allowed mood values
    ALLOWED_MOODS = ['Happy', 'Neutral', 'Sad', 'Anxious', 'Angry']
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize validator.
        
        Args:
            strict_mode: Enable stricter validation rules
        """
        self.strict_mode = strict_mode
        logger.info(f"InputValidator initialized (strict_mode={strict_mode})")
    
    def sanitize_html(self, text: str) -> str:
        """
        Sanitize HTML to prevent XSS attacks.
        
        Args:
            text: Input text
            
        Returns:
            Sanitized text with HTML entities escaped
        """
        if not text:
            return ""
        
        # Escape HTML entities
        sanitized = html.escape(text)
        
        # Remove dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def detect_sql_injection(self, text: str) -> bool:
        """
        Detect potential SQL injection attempts.
        
        Args:
            text: Input text
            
        Returns:
            True if SQL injection detected
        """
        if not text:
            return False
        
        text_upper = text.upper()
        
        for pattern in self.SQL_PATTERNS:
            if re.search(pattern, text_upper):
                logger.warning(f"Potential SQL injection detected: {text[:50]}...")
                return True
        
        return False
    
    def validate_message(self, message: str, 
                        sanitize: bool = True) -> Dict[str, Any]:
        """
        Validate and sanitize chat message.
        
        Args:
            message: User message
            sanitize: Whether to sanitize the message
            
        Returns:
            Dictionary with validation result and sanitized message
            
        Raises:
            ValidationError: If validation fails
        """
        if not message:
            raise ValidationError("Message cannot be empty", field="message")
        
        # Check length
        if len(message) < self.MIN_MESSAGE_LENGTH:
            raise ValidationError(
                f"Message too short (minimum {self.MIN_MESSAGE_LENGTH} characters)",
                field="message"
            )
        
        if len(message) > self.MAX_MESSAGE_LENGTH:
            raise ValidationError(
                f"Message too long (maximum {self.MAX_MESSAGE_LENGTH} characters)",
                field="message",
                details={'length': len(message), 'max': self.MAX_MESSAGE_LENGTH}
            )
        
        # Check for SQL injection
        if self.detect_sql_injection(message):
            logger.warning(f"SQL injection attempt blocked: {message[:50]}...")
            raise ValidationError(
                "Invalid input detected",
                field="message",
                details={'reason': 'sql_injection'}
            )
        
        # Sanitize if requested
        sanitized_message = self.sanitize_html(message) if sanitize else message
        
        # Check for excessive special characters (potential spam)
        special_char_ratio = sum(not c.isalnum() and not c.isspace() 
                                for c in sanitized_message) / len(sanitized_message)
        
        if special_char_ratio > 0.5:
            logger.warning(f"High special character ratio: {special_char_ratio:.2f}")
            if self.strict_mode:
                raise ValidationError(
                    "Message contains too many special characters",
                    field="message"
                )
        
        logger.debug(f"Message validated successfully: {sanitized_message[:50]}...")
        
        return {
            'valid': True,
            'original': message,
            'sanitized': sanitized_message,
            'length': len(sanitized_message)
        }
    
    def validate_mood(self, mood: str) -> Dict[str, Any]:
        """
        Validate mood value.
        
        Args:
            mood: Mood value
            
        Returns:
            Dictionary with validation result
            
        Raises:
            ValidationError: If validation fails
        """
        if not mood:
            raise ValidationError("Mood cannot be empty", field="mood")
        
        # Check if mood is in allowed list
        if mood not in self.ALLOWED_MOODS:
            raise ValidationError(
                f"Invalid mood. Allowed values: {', '.join(self.ALLOWED_MOODS)}",
                field="mood",
                details={'allowed_moods': self.ALLOWED_MOODS}
            )
        
        logger.debug(f"Mood validated: {mood}")
        
        return {
            'valid': True,
            'mood': mood
        }
    
    def validate_mood_note(self, note: str, 
                          sanitize: bool = True) -> Dict[str, Any]:
        """
        Validate and sanitize mood note.
        
        Args:
            note: Mood note
            sanitize: Whether to sanitize the note
            
        Returns:
            Dictionary with validation result and sanitized note
            
        Raises:
            ValidationError: If validation fails
        """
        if not note:
            # Empty notes are allowed
            return {
                'valid': True,
                'original': '',
                'sanitized': '',
                'length': 0
            }
        
        # Check length
        if len(note) > self.MAX_MOOD_NOTE_LENGTH:
            raise ValidationError(
                f"Note too long (maximum {self.MAX_MOOD_NOTE_LENGTH} characters)",
                field="note",
                details={'length': len(note), 'max': self.MAX_MOOD_NOTE_LENGTH}
            )
        
        # Sanitize if requested
        sanitized_note = self.sanitize_html(note) if sanitize else note
        
        logger.debug(f"Mood note validated: {sanitized_note[:50]}...")
        
        return {
            'valid': True,
            'original': note,
            'sanitized': sanitized_note,
            'length': len(sanitized_note)
        }
    
    def validate_date(self, date_str: str) -> Dict[str, Any]:
        """
        Validate date string.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            Dictionary with validation result
            
        Raises:
            ValidationError: If validation fails
        """
        if not date_str:
            raise ValidationError("Date cannot be empty", field="date")
        
        # Check format
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, date_str):
            raise ValidationError(
                "Invalid date format. Expected YYYY-MM-DD",
                field="date",
                details={'format': 'YYYY-MM-DD'}
            )
        
        # Parse date
        try:
            from datetime import datetime
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Check if date is not too far in the future
            from datetime import date, timedelta
            max_future_date = date.today() + timedelta(days=365)
            
            if parsed_date.date() > max_future_date:
                raise ValidationError(
                    "Date cannot be more than 1 year in the future",
                    field="date"
                )
            
            logger.debug(f"Date validated: {date_str}")
            
            return {
                'valid': True,
                'date': date_str,
                'parsed': parsed_date
            }
            
        except ValueError as e:
            raise ValidationError(
                f"Invalid date: {str(e)}",
                field="date"
            )
    
    def validate_json_payload(self, payload: Dict[str, Any],
                             required_fields: List[str],
                             optional_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate JSON payload structure.
        
        Args:
            payload: JSON payload
            required_fields: List of required field names
            optional_fields: List of optional field names
            
        Returns:
            Dictionary with validation result
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(payload, dict):
            raise ValidationError("Payload must be a JSON object")
        
        # Check required fields
        missing_fields = [field for field in required_fields 
                         if field not in payload]
        
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                details={'missing_fields': missing_fields}
            )
        
        # Check for unexpected fields
        allowed_fields = set(required_fields + (optional_fields or []))
        unexpected_fields = [field for field in payload.keys() 
                           if field not in allowed_fields]
        
        if unexpected_fields and self.strict_mode:
            raise ValidationError(
                f"Unexpected fields: {', '.join(unexpected_fields)}",
                details={'unexpected_fields': unexpected_fields}
            )
        
        logger.debug(f"JSON payload validated: {list(payload.keys())}")
        
        return {
            'valid': True,
            'payload': payload
        }
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return "unnamed"
        
        # Remove directory separators
        sanitized = filename.replace('/', '').replace('\\', '')
        
        # Remove parent directory references
        sanitized = sanitized.replace('..', '')
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Keep only alphanumeric, dash, underscore, and dot
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', sanitized)
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:250] + ext
        
        logger.debug(f"Filename sanitized: {filename} -> {sanitized}")
        
        return sanitized


class RateLimitValidator:
    """
    Simple rate limiting validator.
    """
    
    def __init__(self, max_requests: int = 100, 
                 window_seconds: int = 60):
        """
        Initialize rate limit validator.
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = {}
        logger.info(f"RateLimitValidator initialized "
                   f"(max={max_requests}, window={window_seconds}s)")
    
    def check_rate_limit(self, identifier: str) -> Dict[str, Any]:
        """
        Check if identifier has exceeded rate limit.
        
        Args:
            identifier: Unique identifier (e.g., IP address)
            
        Returns:
            Dictionary with rate limit status
            
        Raises:
            ValidationError: If rate limit exceeded
        """
        import time
        
        current_time = time.time()
        
        # Initialize if new identifier
        if identifier not in self._requests:
            self._requests[identifier] = []
        
        # Remove old requests outside window
        self._requests[identifier] = [
            req_time for req_time in self._requests[identifier]
            if current_time - req_time < self.window_seconds
        ]
        
        # Check limit
        request_count = len(self._requests[identifier])
        
        if request_count >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {identifier}: "
                         f"{request_count}/{self.max_requests}")
            raise ValidationError(
                f"Rate limit exceeded. Maximum {self.max_requests} requests "
                f"per {self.window_seconds} seconds",
                details={
                    'current_requests': request_count,
                    'max_requests': self.max_requests,
                    'window_seconds': self.window_seconds
                }
            )
        
        # Add current request
        self._requests[identifier].append(current_time)
        
        remaining = self.max_requests - request_count - 1
        
        logger.debug(f"Rate limit check passed for {identifier}: "
                    f"{request_count + 1}/{self.max_requests}")
        
        return {
            'allowed': True,
            'current_requests': request_count + 1,
            'max_requests': self.max_requests,
            'remaining': remaining
        }


# Global validator instance
_global_validator: Optional[InputValidator] = None


def get_validator(strict_mode: bool = False) -> InputValidator:
    """
    Get or create global validator instance.
    
    Args:
        strict_mode: Enable strict validation mode
        
    Returns:
        InputValidator instance
    """
    global _global_validator
    
    if _global_validator is None:
        _global_validator = InputValidator(strict_mode=strict_mode)
    
    return _global_validator
