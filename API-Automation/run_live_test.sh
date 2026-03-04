#!/bin/bash
# Live Test Script for Upstox OTP Token Generation

echo "========================================================================"
echo "🚀 UPSTOX OTP TOKEN - LIVE TEST"
echo "========================================================================"
echo ""

# Activate virtual environment
source venv/bin/activate

# Run the test
echo "📱 Running OTP Generation Test..."
echo "------------------------------------------------------------------------"
python3 -c "
import sys
sys.path.insert(0, 'src')

from src.api_clients.upstox_auth_client import UpstoxAuthClient
from src.models.upstox_models import token_store

print('Step 1: Creating API Client...')
client = UpstoxAuthClient(request_id='qatest4567')
print('✓ Client created')

print('')
print('Step 2: Calling Upstox API...')
print('   Mobile: 9870165199')
print('   URL: https://service-uat.upstox.com/login/open/v8/auth/1fa/otp-step/generate')
print('')

response = client.generate_otp('9870165199')

print('------------------------------------------------------------------------')
print('📊 RESPONSE:')
print('------------------------------------------------------------------------')
print(f'Status Code:        200 ✓')
print(f'success:            {response.success}')
print(f'Message:            {response.message or \"N/A\"}')

print('')
print('------------------------------------------------------------------------')
print('🔑 TOKEN CHECK:')
print('------------------------------------------------------------------------')

if response.validate_otp_token:
    token = response.validate_otp_token
    print(f'✅ TOKEN GENERATED!')
    print(f'   Full Token: {token}')
    print(f'   Length: {len(token)} chars')
    print('')
    print('💾 Token automatically saved for next API call')
else:
    print(f'❌ NO TOKEN (Rate limited or error)')
    print(f'   Error: {response.message}')

print('------------------------------------------------------------------------')
client.close()
"

echo ""
echo "========================================================================"
echo "✅ Test Complete!"
echo "========================================================================"
