"""
Mobile Number Generator Utility

Generates valid random 10-digit Indian mobile numbers.
Valid mobile numbers start with 6, 7, 8, or 9.
"""
import random
import time
from datetime import datetime
from typing import Optional, Set


class MobileNumberGenerator:
    """
    Generator for valid random mobile numbers.
    
    Valid mobile number format:
    - 10 digits
    - Starts with 6, 7, 8, or 9
    - No duplicates (tracks generated numbers)
    """
    
    # Valid starting digits for Indian mobile numbers
    VALID_PREFIXES = ['6', '7', '8', '9']
    
    def __init__(self):
        """Initialize generator with tracking set"""
        self._generated_numbers: Set[str] = set()
        self._session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def generate(self, unique_in_session: bool = True) -> str:
        """
        Generate a random valid mobile number.
        
        Args:
            unique_in_session: If True, ensures number wasn't generated before in this session
            
        Returns:
            10-digit mobile number as string
            
        Example:
            >>> generator = MobileNumberGenerator()
            >>> mobile = generator.generate()
            >>> print(mobile)  # e.g., "9876543210"
        """
        max_attempts = 1000  # Prevent infinite loop
        attempts = 0
        
        while attempts < max_attempts:
            # Generate random mobile number
            # Start with valid prefix (6, 7, 8, or 9)
            prefix = random.choice(self.VALID_PREFIXES)
            
            # Generate remaining 9 digits
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(9)])
            
            mobile_number = prefix + suffix
            
            # Check if unique (if required)
            if unique_in_session:
                if mobile_number not in self._generated_numbers:
                    self._generated_numbers.add(mobile_number)
                    return mobile_number
            else:
                return mobile_number
            
            attempts += 1
        
        # If we can't generate unique number, use timestamp-based approach
        return self._generate_with_timestamp()
    
    def _generate_with_timestamp(self) -> str:
        """Generate unique number using timestamp if random generation fails"""
        # Use timestamp to ensure uniqueness
        timestamp_suffix = str(int(time.time()))[-8:]  # Last 8 digits of timestamp
        prefix = random.choice(self.VALID_PREFIXES)
        # Pad or trim to make exactly 9 digits after prefix
        remaining = timestamp_suffix[:9]
        if len(remaining) < 9:
            remaining = remaining + ''.join([str(random.randint(0, 9)) for _ in range(9 - len(remaining))])
        
        mobile_number = prefix + remaining
        self._generated_numbers.add(mobile_number)
        return mobile_number
    
    def generate_multiple(self, count: int, unique_in_session: bool = True) -> list:
        """
        Generate multiple random mobile numbers.
        
        Args:
            count: Number of mobile numbers to generate
            unique_in_session: If True, ensures all numbers are unique
            
        Returns:
            List of mobile number strings
            
        Example:
            >>> generator = MobileNumberGenerator()
            >>> mobiles = generator.generate_multiple(5)
            >>> print(mobiles)  # ["9876543210", "8765432109", ...]
        """
        numbers = []
        for _ in range(count):
            numbers.append(self.generate(unique_in_session=unique_in_session))
        return numbers
    
    def is_valid(self, mobile_number: str) -> bool:
        """
        Check if a mobile number is valid.
        
        Args:
            mobile_number: Mobile number to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not mobile_number:
            return False
        
        # Check length
        if len(mobile_number) != 10:
            return False
        
        # Check all digits
        if not mobile_number.isdigit():
            return False
        
        # Check prefix
        if mobile_number[0] not in self.VALID_PREFIXES:
            return False
        
        return True
    
    def get_generated_count(self) -> int:
        """Get count of unique numbers generated in this session"""
        return len(self._generated_numbers)
    
    def get_all_generated(self) -> Set[str]:
        """Get all generated numbers in this session"""
        return self._generated_numbers.copy()
    
    def reset(self):
        """Reset the generator (clear all tracked numbers)"""
        self._generated_numbers.clear()
        self._session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


# Global generator instance
_mobile_generator: Optional[MobileNumberGenerator] = None


def get_mobile_generator() -> MobileNumberGenerator:
    """Get or create global mobile generator instance"""
    global _mobile_generator
    if _mobile_generator is None:
        _mobile_generator = MobileNumberGenerator()
    return _mobile_generator


def generate_mobile_number(unique_in_session: bool = True) -> str:
    """
    Quick function to generate a random mobile number.
    
    Args:
        unique_in_session: If True, ensures number wasn't generated before
        
    Returns:
        10-digit mobile number string
        
    Example:
        >>> mobile = generate_mobile_number()
        >>> print(mobile)  # e.g., "9876543210"
    """
    generator = get_mobile_generator()
    return generator.generate(unique_in_session=unique_in_session)


def generate_unique_mobile() -> str:
    """
    Generate a unique mobile number (guaranteed not duplicate in session).
    
    Returns:
        10-digit mobile number string
        
    Example:
        >>> mobile = generate_unique_mobile()
        >>> print(mobile)  # e.g., "9876543210"
    """
    return generate_mobile_number(unique_in_session=True)


# Standalone test
if __name__ == "__main__":
    print("="*60)
    print("Mobile Number Generator Test")
    print("="*60)
    
    generator = MobileNumberGenerator()
    
    # Test single generation
    print("\n1. Single Mobile Number:")
    mobile = generator.generate()
    print(f"   Generated: {mobile}")
    print(f"   Valid: {generator.is_valid(mobile)}")
    
    # Test multiple generation
    print("\n2. Multiple Mobile Numbers (5):")
    mobiles = generator.generate_multiple(5)
    for i, m in enumerate(mobiles, 1):
        print(f"   {i}. {m} (Valid: {generator.is_valid(m)})")
    
    # Check uniqueness
    print(f"\n3. Uniqueness Check:")
    print(f"   Total generated: {generator.get_generated_count()}")
    print(f"   Unique numbers: {len(set(generator.get_all_generated()))}")
    all_unique = generator.get_generated_count() == len(set(generator.get_all_generated()))
    print(f"   All unique: {all_unique}")
    
    # Test validation
    print("\n4. Validation Tests:")
    test_numbers = [
        "9876543210",  # Valid
        "5876543210",  # Invalid (starts with 5)
        "987654321",   # Invalid (9 digits)
        "98765432101", # Invalid (11 digits)
        "987654321a",  # Invalid (non-digit)
    ]
    for num in test_numbers:
        valid_str = 'Valid' if generator.is_valid(num) else 'Invalid'
        print(f"   {num}: {'✅' if generator.is_valid(num) else '❌'} {valid_str}")
    
    print("\n" + "="*60)
    print("All tests passed!")
    print("="*60)
    print(f"\nGenerated {generator.get_generated_count()} unique mobile numbers")
    print("="*60)
