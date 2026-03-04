#!/usr/bin/env python3
"""
Example: Complete Upstox Login Flow (Generate OTP → Verify OTP)

This example demonstrates the complete 2-step login process:
1. Generate OTP for mobile number
2. Verify OTP and get profileId

Includes auto-retry on session expiry.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api_clients.upstox_auth_client import (
    UpstoxAuthClient, 
    complete_login_flow,
    generate_otp_token,
    verify_otp_token
)
from src.models.upstox_models import token_store


def example_1_step_by_step():
    """
    Example 1: Step-by-step manual flow
    
    Shows each step explicitly with error handling.
    """
    print("\n" + "="*70)
    print("Example 1: Step-by-Step Login Flow")
    print("="*70)
    
    # Configuration
    mobile_number = "9870165199"
    otp = "123789"
    request_id = "qatest4567"
    
    print(f"\n📱 Mobile Number: {mobile_number}")
    print(f"🔐 OTP: {otp}")
    print(f"🆔 Request ID: {request_id}")
    
    # Create client
    client = UpstoxAuthClient(request_id=request_id)
    
    try:
        # Step 1: Generate OTP
        print("\n" + "-"*70)
        print("STEP 1: Generate OTP")
        print("-"*70)
        
        generate_response = client.generate_otp(mobile_number, save_token=True)
        
        if not generate_response.validate_otp_token:
            print(f"❌ Failed to generate OTP: {generate_response.message}")
            return
        
        token = generate_response.validate_otp_token
        print(f"✅ OTP Generated Successfully!")
        print(f"   Token: {token[:60]}...")
        print(f"   Message: {generate_response.message}")
        
        # Step 2: Verify OTP
        print("\n" + "-"*70)
        print("STEP 2: Verify OTP")
        print("-"*70)
        
        # Option A: Simple verification (no auto-retry)
        # verify_response = client.verify_otp(otp=otp, auto_retry=False)
        
        # Option B: Verification with auto-retry on session expiry
        verify_response = client.verify_otp(
            otp=otp,
            mobile_number=mobile_number,  # Required for auto-retry
            auto_retry=True,              # Automatically regenerate OTP if session expired
            save_profile_id=True          # Save profileId to token_store
        )
        
        # Check if successful
        if not verify_response.success:
            print(f"❌ Verification failed: {verify_response.message}")
            print(f"   Error Code: {verify_response.error_code}")
            return
        
        # Validate all fields
        is_valid, error_msg = verify_response.validate_success_response()
        
        if not is_valid:
            print(f"❌ Validation failed: {error_msg}")
            return
        
        print(f"✅ OTP Verified Successfully!")
        print(f"   Message: {verify_response.message}")
        print(f"   User Type: {verify_response.user_type}")
        print(f"   Is Secret Pin Set: {verify_response.is_secret_pin_set}")
        print(f"   Profile ID: {verify_response.profile_id}")
        
        # Show stored data
        print("\n" + "-"*70)
        print("STORED DATA")
        print("-"*70)
        
        stored_token = client.get_stored_token()
        stored_profile_id = client.get_stored_profile_id()
        
        print(f"✓ Token stored: {stored_token[:50] if stored_token else 'None'}...")
        print(f"✓ Profile ID stored: {stored_profile_id}")
        
        print("\n" + "="*70)
        print("✅ COMPLETE FLOW SUCCESSFUL!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


def example_2_one_liner():
    """
    Example 2: One-liner complete flow
    
    Uses the complete_login_flow function for simplicity.
    """
    print("\n" + "="*70)
    print("Example 2: One-Liner Complete Flow")
    print("="*70)
    
    mobile_number = "9870165199"
    otp = "123789"
    
    print(f"\n📱 Mobile: {mobile_number}")
    print(f"🔐 OTP: {otp}")
    print(f"\n🚀 Executing complete flow...")
    
    try:
        # One function does everything!
        result = complete_login_flow(
            mobile_number=mobile_number,
            otp=otp,
            request_id="qatest4567"
        )
        
        print("\n" + "-"*70)
        print("RESULTS:")
        print("-"*70)
        print(f"✅ Flow completed successfully!")
        print(f"   Token: {result['token'][:50]}...")
        print(f"   Profile ID: {result['profile_id']}")
        print(f"   Generate Response: success={result['generate_response'].success}")
        print(f"   Verify Response: success={result['verify_response'].success}")
        
        print("\n" + "="*70)
        print("✅ ONE-LINER FLOW SUCCESSFUL!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_3_separate_functions():
    """
    Example 3: Using standalone functions
    
    Shows how to use the quick standalone functions.
    """
    print("\n" + "="*70)
    print("Example 3: Standalone Functions")
    print("="*70)
    
    mobile_number = "9870165199"
    otp = "123789"
    
    try:
        # Step 1: Generate OTP
        print("\n📱 Step 1: Generate OTP")
        generate_response = generate_otp_token(mobile_number)
        
        if not generate_response.validate_otp_token:
            print(f"❌ Failed: {generate_response.message}")
            return
        
        print(f"✅ Token: {generate_response.validate_otp_token[:50]}...")
        
        # Step 2: Verify OTP
        print("\n🔐 Step 2: Verify OTP")
        verify_response = verify_otp_token(
            otp=otp,
            mobile_number=mobile_number,  # For auto-retry
            auto_retry=True
        )
        
        if verify_response.success:
            print(f"✅ Verified!")
            print(f"   Profile ID: {verify_response.profile_id}")
        else:
            print(f"❌ Failed: {verify_response.message}")
        
        # Show all stored data
        print("\n💾 Stored Data:")
        print(f"   Tokens: {token_store.all_tokens}")
        print(f"   User Data: {token_store.all_user_data}")
        
        print("\n" + "="*70)
        print("✅ STANDALONE FUNCTIONS SUCCESSFUL!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def example_4_error_handling_demo():
    """
    Example 4: Error handling demonstration
    
    Shows what happens when errors occur.
    """
    print("\n" + "="*70)
    print("Example 4: Error Handling Demo")
    print("="*70)
    
    print("\n🔍 Simulating error scenarios...")
    
    # Scenario 1: Session Expired
    print("\nScenario 1: Session Expired (Error 1017076)")
    print("-"*70)
    print("When this error occurs, the code will:")
    print("  1. Detect error code 1017076")
    print("  2. Automatically call generate_otp()")
    print("  3. Get new validate_otp_token")
    print("  4. Retry verify_otp() with new token")
    print("  5. All happens automatically with auto_retry=True")
    
    # Scenario 2: Validation Failure
    print("\nScenario 2: Response Validation Failure")
    print("-"*70)
    print("If response doesn't match expected format:")
    print("  • success must be True")
    print("  • message must be 'Your OTP has been successfully verified.'")
    print("  • userType must be 'LEAD'")
    print("  • isSecretPinSet must be False")
    print("  • profileId must be numeric")
    print("\nWith auto_retry=True, it will regenerate OTP and retry.")
    
    print("\n" + "="*70)
    print("✅ Error handling demo complete")
    print("="*70)


def example_5_store_management():
    """
    Example 5: Token and profileId management
    
    Shows how to manage stored data.
    """
    print("\n" + "="*70)
    print("Example 5: Token Store Management")
    print("="*70)
    
    # Clear everything first
    token_store.clear_all()
    print("\n🗑️  Cleared all stored data")
    
    # Simulate storing data
    print("\n💾 Saving mock data...")
    token_store.save_token("validate_otp_token", "ll1FA-mock-token-123456")
    token_store.save_user_data("profile_id", 3820874)
    
    # Retrieve
    print("\n📤 Retrieving stored data...")
    token = token_store.get_token("validate_otp_token")
    profile_id = token_store.get_user_data("profile_id")
    
    print(f"   Token: {token}")
    print(f"   Profile ID: {profile_id}")
    
    # Show all
    print("\n📋 All stored data:")
    all_data = {
        "tokens": token_store.all_tokens,
        "user_data": token_store.all_user_data
    }
    print(f"   {all_data}")
    
    # Clear specific
    print("\n🗑️  Clearing profile_id only...")
    token_store.clear_user_data("profile_id")
    print(f"   Profile ID after clear: {token_store.get_user_data('profile_id')}")
    print(f"   Token still exists: {token_store.get_token('validate_otp_token') is not None}")
    
    # Clear all
    print("\n🗑️  Clearing all data...")
    token_store.clear_all()
    print(f"   All tokens: {token_store.all_tokens}")
    print(f"   All user data: {token_store.all_user_data}")
    
    print("\n" + "="*70)
    print("✅ Store management demo complete")
    print("="*70)


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("Upstox Complete Login Flow - Usage Examples")
    print("="*70)
    
    # Uncomment the examples you want to run
    
    # example_1_step_by_step()      # Detailed step-by-step
    # example_2_one_liner()         # Quick one-liner
    # example_3_separate_functions() # Standalone functions
    example_4_error_handling_demo() # Error handling demo
    example_5_store_management()    # Store management
    
    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
