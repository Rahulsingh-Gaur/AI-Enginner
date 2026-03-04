"""
Random Email Generator for API Testing
======================================
Generates unique random email addresses for Stage 4 (Email OTP API).
Format: {random_string}_@gmail.com
"""
import random
import string
from datetime import datetime


class EmailGenerator:
    """Generator for unique random email addresses"""
    
    # Track generated emails to ensure uniqueness per session
    generated_emails = set()
    
    @classmethod
    def generate(cls, prefix_length: int = 10, use_timestamp: bool = False) -> str:
        """
        Generate a random email address.
        
        Format: {random_string}_@gmail.com
        
        Args:
            prefix_length: Length of random string (default: 10)
            use_timestamp: If True, prepends timestamp for guaranteed uniqueness
            
        Returns:
            Random email string (e.g., "a7k9m2p4q8_@gmail.com")
        """
        max_attempts = 1000
        
        for _ in range(max_attempts):
            if use_timestamp:
                # Timestamp + random for guaranteed uniqueness
                timestamp = datetime.now().strftime("%H%M%S")
                random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, 
                                                      k=prefix_length - len(timestamp)))
                prefix = f"{timestamp}{random_part}"
            else:
                # Pure random alphanumeric
                prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, 
                                                 k=prefix_length))
            
            email = f"{prefix}_@gmail.com"
            
            if email not in cls.generated_emails:
                cls.generated_emails.add(email)
                return email
        
        raise RuntimeError(f"Could not generate unique email after {max_attempts} attempts")
    
    @classmethod
    def validate(cls, email: str) -> bool:
        """
        Validate email format matches expected pattern.
        
        Args:
            email: Email string to validate
            
        Returns:
            True if valid format, False otherwise
        """
        if not email:
            return False
        
        # Must end with _@gmail.com
        if not email.endswith("_@gmail.com"):
            return False
        
        # Extract prefix
        prefix = email.replace("_@gmail.com", "")
        
        # Prefix must be alphanumeric and at least 5 chars
        if len(prefix) < 5:
            return False
        
        if not prefix.isalnum():
            return False
        
        return True
    
    @classmethod
    def clear_history(cls):
        """Clear generated email history"""
        cls.generated_emails.clear()


# Convenience function for easy import
def generate_random_email(prefix_length: int = 10, use_timestamp: bool = False) -> str:
    """
    Generate a random email address.
    
    Args:
        prefix_length: Length of random string
        use_timestamp: Include timestamp for uniqueness
        
    Returns:
        Random email (e.g., "a7k9m2p4q8_@gmail.com")
    """
    return EmailGenerator.generate(prefix_length, use_timestamp)


# Example usage for testing
if __name__ == "__main__":
    print("🎲 Random Email Generator - Test Samples")
    print("=" * 50)
    
    for i in range(5):
        email = generate_random_email()
        is_valid = EmailGenerator.validate(email)
        print(f"{i+1}. {email} {'✅' if is_valid else '❌'}")
    
    print("\n" + "=" * 50)
    print(f"📊 Total unique emails generated: {len(EmailGenerator.generated_emails)}")
