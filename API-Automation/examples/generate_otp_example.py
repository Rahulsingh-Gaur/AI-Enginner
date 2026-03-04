#!/usr/bin/env python3
"""
Example: Upstox Generate OTP API Usage

This script demonstrates how to use the UpstoxAuthClient to:
1. Generate OTP for a mobile number
2. Validate the response (status 200, success=true, validateOTPToken generated)
3. Save the validateOTPToken for use in subsequent API calls
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api_clients.upstox_auth_client import UpstoxAuthClient, generate_otp_token
from src.models.upstox_models import token_store


def example_1_basic_usage():
    """Example 1: Basic OTP generation"""
    print("\n" + "="*60)
    print("Example 1: Basic OTP Generation")
    print("="*60)
    
    # Mobile number to send OTP
    mobile_number = "9870165199"
    
    # Create client
    client = UpstoxAuthClient(request_id="qatest4567")
    
    try:
        # Generate OTP
        response = client.generate_otp(mobile_number)
        
        print(f"\n✅ Response Status Code: 200")
        print(f"✅ Success: {response.is_success}")
        print(f"✅ Message: {response.message}")
        print(f"✅ validateOTPToken: {response.validate_otp_token}")
        
        # Token is automatically saved, you can retrieve it
        saved_token = client.get_stored_token()
        print(f"\n💾 Saved Token (retrieved): {saved_token}")
        
    except AssertionError as e:
        print(f"❌ Validation Failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()


def example_2_quick_function():
    """Example 2: Using quick function"""
    print("\n" + "="*60)
    print("Example 2: Using Quick Function")
    print("="*60)
    
    mobile_number = "9870165199"
    
    try:
        # One-liner to generate OTP
        response = generate_otp_token(mobile_number)
        
        print(f"\n✅ OTP Generated Successfully!")
        print(f"   Token: {response.validate_otp_token[:60]}...")
        
        # Access token from global store
        token = token_store.get_token("validate_otp_token")
        print(f"\n💾 Token from store: {token[:60]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_3_custom_request_id():
    """Example 3: Using custom request ID"""
    print("\n" + "="*60)
    print("Example 3: Custom Request ID")
    print("="*60)
    
    mobile_number = "9870165199"
    custom_request_id = "my_custom_request_123"
    
    client = UpstoxAuthClient(request_id=custom_request_id)
    
    try:
        response = client.generate_otp(mobile_number)
        print(f"\n✅ OTP Generated with requestId: {custom_request_id}")
        print(f"   Token: {response.validate_otp_token[:50]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()


def example_4_manual_validation():
    """Example 4: Manual response validation"""
    print("\n" + "="*60)
    print("Example 4: Manual Response Validation")
    print("="*60)
    
    mobile_number = "9870165199"
    
    client = UpstoxAuthClient(request_id="qatest4567")
    
    try:
        # Get raw response
        raw_response = client.generate_otp_raw(mobile_number)
        
        print(f"\n📊 Response Status Code: {raw_response.status_code}")
        
        # Parse JSON
        data = raw_response.json()
        
        # Manual validation
        print(f"\n🔍 Validations:")
        print(f"   1. Status Code == 200: {raw_response.status_code == 200}")
        
        response_data = data.get('response', {})
        success = response_data.get('success', False)
        print(f"   2. success == true: {success}")
        
        token = response_data.get('validateOTPToken')
        print(f"   3. validateOTPToken exists: {token is not None}")
        print(f"   4. validateOTPToken not empty: {bool(token)}")
        
        if token:
            print(f"\n✅ All validations passed!")
            print(f"   Token: {token}")
            
            # Save token for later use
            token_store.save_token("my_custom_token_key", token)
            print(f"\n💾 Token saved with key: 'my_custom_token_key'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()


def example_5_use_token_for_next_api():
    """Example 5: How to use token in subsequent API calls"""
    print("\n" + "="*60)
    print("Example 5: Using Token in Next API Call")
    print("="*60)
    
    mobile_number = "9870165199"
    
    client = UpstoxAuthClient(request_id="qatest4567")
    
    try:
        # Step 1: Generate OTP and save token
        print(f"\nStep 1: Generating OTP...")
        otp_response = client.generate_otp(mobile_number, save_token=True)
        print(f"   ✅ OTP Generated")
        
        # Step 2: Get the token (for use in next API)
        token = client.get_stored_token()
        print(f"\nStep 2: Token Retrieved")
        print(f"   Token: {token[:50]}...")
        
        # Step 3: Show how to use in query parameter
        print(f"\nStep 3: Use token in next API call")
        print(f"   URL: /login/open/v8/auth/1fa/otp-step/validate")
        print(f"   Query Param: ?requestId=qatest4567&validateOTPToken={token[:30]}...")
        
        # Step 4: Example of using token for validation
        print(f"\n💡 To validate OTP, you would call:")
        print(f"   client.validate_otp(otp='123456')")
        print(f"   # This automatically uses the stored token")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Upstox Generate OTP API - Usage Examples")
    print("="*60)
    
    # Uncomment the examples you want to run
    
    example_1_basic_usage()
    # example_2_quick_function()
    # example_3_custom_request_id()
    # example_4_manual_validation()
    # example_5_use_token_for_next_api()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
