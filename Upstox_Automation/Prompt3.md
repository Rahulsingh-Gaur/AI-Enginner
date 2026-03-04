
Prompt 3

## Improved Prompt: Stage 3 (2FA Authentication API)

**Context:** We are now at **Stage 3** of our Python API automation suite. We need to integrate the **2FA Authentication API** as the third call in our end-to-end flow.

### 1. Workflow Sequence

1. **Step 1:** Generate OTP (Provides `validate_otp_token`).
2. **Step 2:** Verify OTP (Previous stage).
3. **Step 3 (Current):** Execute **2FA Authentication API** immediately after the OTP Verification is successful.

### 2. Request Configuration

* **API Name for Reference:** `2FA API`
* **Dependencies:** Retrieve the `validate_otp_token` generated from the **Generate OTP API** (Step 1).
* **Payload Requirements:**
* `validate_otp_token`: Use the dynamic token from the previous step.
* `otp`: Hardcode this value to `123789`.



### 3. Response Validation (Success Criteria)

The automation script must validate the following parameters to mark the test as **PASSED**:

* **HTTP Status Code:** `200`
* **JSON Fields:**
* `success`: `true`
* `redirectUri`: `"https://uat-pro.upstox.com"`
* `userType`: `"LEAD"`
* `customerStatus`: `"NEW"`



### 4. Integration Logic

Please ensure this API call is chained correctly so that if Step 1 or Step 2 fails, the `2FA API` is not triggered. Store the response for potential use in the next stage of the funnel.

---
Python Request
import requests
import json

url = "https://service-uat.upstox.com/login/open/v1/auth/leads/2fa?requestId=qatest4567&client_id=PW3-Kd6pvTPIciPbPxdF5S3FAx88&redirect_uri=https://uat-pro.upstox.com"

payload = json.dumps({
  "data": {
    "validateOtpToken": "ll1FA-cb1e388065e996d227d4ca7bd47f5c4dd64f1a8085a9e28afef5940d1bad07dc",
    "otp": "123789"
  }
})
headers = {
  'X-Device-Details': 'platform=WEB|deviceId=someAlphanumericDeviceId|osName=iOS|osVersion=13.5.1|appVersion=2.3.14|imei=000000000000|network=net|memory=mem|modelName=iPhone101|manufacturer=Apple',
  'Content-Type': 'application/json',
  'Cookie': 'access_token=eyJ0eXAiOiJKV1QiLCJraWQiOiJpZHQtYWJkZTk5NzktOGNhMS00MDhjLWIxZDEtNjJlMmY0MGM1MTdmIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzODIxNTMyIiwianRpIjoiWW05R0JKMUFISmZNRDBockMyYXRHV1YwaXEwIiwiaWF0IjoxNzcxNTA4NzYzLCJleHAiOjE3NzE1MTIzNjMsImlzcyI6ImxvZ2luLXNlcnZpY2UiLCJzY29wZSI6W10sImNsaWVudF9pZCI6IlBXMy1LZDZwdlRQSWNpUGJQeGRGNVMzRkF4ODgiLCJrZXlfaWQiOiJpZHQtYWJkZTk5NzktOGNhMS00MDhjLWIxZDEtNjJlMmY0MGM1MTdmIiwicmVmcmVzaF90b2tlbl9pZCI6IkF2M2xveTJ6NTMtSW1mLUEwZGRrTTFISkg2VSIsInR5cGUiOiJhY2Nlc3NfdG9rZW4iLCJyb2xlIjoiTEVBRCIsInVzZXJfdHlwZSI6IkxFQUQiLCJ2ZXJzaW9uIjoiVjIiLCJwbGFuIjoiQkFTSUMifQ.CfQSyCk_tZigt-F4VK-LzTP4FmE0nL4418gn_Tl7Sa3lG_NbVeqInAeZnsIhJ6Z_O-FslTm2qFJJOjs3jhFiHU6zlm9XsFQUN70lTR3kymLbhDPXX4lwlJhVIfdx6eoXzgwE-_XUm4zmEirapsQRI-Bhi7vQlb0sm8lNZtlU2UxiZNJsWplLrAEnxrHnuTADoU_r2CknsmWudJ4ShGF3fS9xVofXA5yPWWGQt7fmqtulLcJNUnRN-F1XRqrO4S-DkX5qEC-NbIkbrpOvQ36SH8uLR2ArdYGxvdylNF1XC5TC6kqlS9Ew4tygrWWVTo96g3Er2zK6g6nt86MELqycvg; auth_identity_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJlODg2YWRlMTM5ZWI1MDk0ZGRmZDQ5ODM2Yzg2ZDAzMiIsImV4cCI6MTc3MTU5NTE1OX0.d39Hmi1d-3Jb3_rh9zje5VtdxLOV8z8qza73wUkHDSE; auth_identity_token_expiry=1771595158365; customer_status=NEW; profile_id_web=3821532; refresh_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzODIxNTMyIiwianRpIjoiQXYzbG95Mno1My1JbWYtQTBkZGtNMUhKSDZVIiwiaWF0IjoxNzcxNTA4NzYzLCJleHAiOjE3NzE1OTUxNjMsImlzcyI6ImxvZ2luLXNlcnZpY2UiLCJzY29wZSI6W10sImNsaWVudF9pZCI6IlBXMy1LZDZwdlRQSWNpUGJQeGRGNVMzRkF4ODgiLCJrZXlfaWQiOiJpZHQtYWJkZTk5NzktOGNhMS00MDhjLWIxZDEtNjJlMmY0MGM1MTdmIiwiYXRpIjoiWW05R0JKMUFISmZNRDBockMyYXRHV1YwaXEwIiwicmVmcmVzaF90b2tlbl9pZCI6IkF2M2xveTJ6NTMtSW1mLUEwZGRrTTFISkg2VSIsInR5cGUiOiJyZWZyZXNoX3Rva2VuIiwicm9sZSI6IkxFQUQiLCJ1c2VyX3R5cGUiOiJMRUFEIiwidmVyc2lvbiI6IlYyIiwicGxhbiI6IkJBU0lDIn0.krq7NnshcPrS_9witz7UaTAwwccTSeI2OriSWwLeKfFzvhn8_W5yX0WBDTU4YcwxxEMLmIMaX1godD73cb9RCh6keIguYeyV4COaOWyLZP23OL80DlEmwdv4TwaikD4tl49fJuWpf4ckNARt4SS0QULlelg3goML25OdOwB78DDX-XX4gYexqx3nCoUeZs-sZdpoGtc80n10pWf_NWLcXFJQ80LhJXtcJPuHCzwi0dvg-1vxbCToyt4SMEi-I1TJeAsfNL7f1a6ISe2ofWgyKiepoDX-aJykVQPzw9zckD0fJbtz8-fdgyekUI-Zn8niwwJhpc-dU7AgVNlXy5aETQ; __cf_bm=N5Rkl2QQPb7m3oa4.l1yp7te1fEOq2AFNzlnH0PC7gw-1771508755-1.0.1.1-g1YBFH7a6B.sfzp6wm_4R9.b3l1MmGwwAvM9DJyCZPuIE5OeGbJ0WzglbN7ThS3x.k.ElD8K1A2CMLvkVGJHA0Uf2iCx5GUEbUbgQ2_xF6U; _cfuvid=wxFrLvEeEXct0FuEEdbtXMj4FyQ9nTbL_HKnaZTiKHw-1771492556398-0.0.1.1-604800000'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
