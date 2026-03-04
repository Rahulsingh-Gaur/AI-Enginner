## Improved Prompt

**Subject: Implementation of OTP Verification API Logic**

Kimi, please help me develop the Code logic in python for the **Verify OTP API**. This is the second step in our login flow. Please follow these requirements:

### 1. API Integration & Input

* **Dependency:** Retrieve the `validate_otp_token` generated from the previous **Generate OTP API**.
* **Request:** Call the `Verify OTP` endpoint using:
* `validate_otp_token` (from the previous step)
* `otp`: Use `123789` as the default value.



### 2. Success Validation (Happy Path)

If the API call is successful, validate the following in the response:

* `success`: Must be `true`.
* `message`: Must match `"Your OTP has been successfully verified."`
* `userType`: Must be `"LEAD"`.
* `isSecretPinSet`: Must be `false`.
* **Data Extraction:** Verify that `profileId` is a **numeric** value and store it for use in subsequent API calls.

### 3. Error Handling & Retry Logic

Handle the scenario where the session expires or validation fails:

* **Specific Error Catch:** If the API returns error code `1017076` (*"Your session to validate otp has expired, please try again."*).
* **Fallback Mechanism:** If the above error occurs OR any of the success validations fail:
1. Automatically re-call the **Generate OTP API**.
2. Capture the new `validate_otp_token`.
3. Retry the **Verify OTP API** with the new token.

Base URL https://service-uat.upstox.com
End point :/login/open/v4/auth/1fa/otp-totp/verify?requestId=qatest4567

import requests
import json

url = "https://service-uat.upstox.com/login/open/v4/auth/1fa/otp-totp/verify?requestId=qatest4567"

payload = json.dumps({
  "data": {
    "validateOtpToken": "ll1FA-0c5844fedb744ed8d1ef1ec700581d8f96c36423d636785600117a1dd6a51df6",
    "otp": "123789"
  }
})
headers = {
  'X-Device-Details': 'platform=WEB|deviceId=someAlphanumericDeviceId|osName=iOS|osVersion=13.5.1|appVersion=2.3.14|imei=000000000000|network=net|memory=mem|modelName=iPhone101|manufacturer=Apple',
  'Content-Type': 'application/json',
  'Cookie': 'auth_identity_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI2NjFjODEyZmEzNDA2YWExZjk0ZTdlZmE2MDQzYjI0OSIsImV4cCI6MTc3MTU4NzY3N30.rBxljOuNe_SlKaex2nsD0qOyB-gmjrBxxqHYbyVIY1w; auth_identity_token_expiry=1771587676539; profile_id_web=3820874; __cf_bm=PMoMDTuvsUmDSz2LAQm7XX0.HFM5l1r4no8IXCL4R48-1771501274-1.0.1.1-gyykOgyHRlW0G5MLNf0lOtgLFXa.q5c8bJQmZR0qDQXoBMwXwMK1CAuuupVWBDcpXppspeRhj0pllg4WvgPfrO4B0qmJ4Ehs4LAVA8z1ZhM; _cfuvid=wxFrLvEeEXct0FuEEdbtXMj4FyQ9nTbL_HKnaZTiKHw-1771492556398-0.0.1.1-604800000'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
