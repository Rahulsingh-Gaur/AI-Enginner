Prompt 4

## Stage 4 (Email OTP Generation API)

**Context:** We have successfully automated the first three stages. We are now moving to **Stage 4** of our Python API automation: the **Email Send OTP API**.

### 1. Workflow Sequence

* This is the **4th API** in the chain.
* **Trigger:** This API should be called immediately after a successful response from the **Stage 3 (2FA API)**.

### 2. Dynamic Data Generation (Email Logic)

* **Requirement:** Generate a random email address for the request body.
* **Format:** Use the structure `{random_string}_@gmail.com`.
* **Logic:** The prefix should be a unique alphanumeric string or timestamp to ensure it remains unique for every execution, while keeping `@gmail.com` as the fixed suffix.

### 3. Request Details

* **API Name:** `Email Send OTP`
* **Method:** POST (assuming based on flow)
* **Body:** Include the generated random email ID.

### 4. Response Validation & Reporting

To pass this stage, the following must be verified:

* **HTTP Status Code:** `200`
* **JSON Response:** Match the key-value pair `"EMAIL": "OTP sent successfully"`.
* **Automation Summary:** Ensure the status of this validation (Pass/Fail) and the **generated email address** used are included in the final execution summary/log.

---

Python request 

import requests
import json

url = "https://service-uat.upstox.com/account-opening/v3/email/send-otp"

payload = json.dumps({
  "email": "aahulsingh121@gmail.com"
})
headers = {
  'X-profile-id': '3809733',
  'Content-Type': 'application/json',
  'requestId': 'requestId',
  'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxMDEwMDMxIiwianRpIjoiR18xU09ma292RW0tenhRZ1c0TTVINHRoMkdFIiwiaWF0IjoxNjcyMjA5OTYxLCJleHAiOjE2NzIyOTYzNjEsImlzcyI6ImxvZ2luLXNlcnZpY2UiLCJzY29wZSI6W10sImNsaWVudF9pZCI6Ik9CRC13UVFzNlNjeDlxZEpVN2FxQ0kwMHRub2siLCJrZXlfaWQiOiJpZHQtYWJkZTk5NzktOGNhMS00MDhjLWIxZDEtNjJlMmY0MGM1MTdmIiwicmVmcmVzaF90b2tlbl9pZCI6IjRkN1dMLVZtd0lrSEh1cGpjU3laWGp6SUxUdyIsInR5cGUiOiJhY2Nlc3NfdG9rZW4iLCJyb2xlIjoiQ1VTVE9NRVIiLCJ1c2VyX3R5cGUiOiJDVVNUT01FUiIsInVzZXJfaWQiOiI1REJZV04iLCJ2ZXJzaW9uIjoiVjIifQ.auxqHU5WkdlFB9FkxE04KKjiT7ABdu58bpAhODYe1tWneiRS9aUCrf-oLA5kMtKyqLqhwtrXcp6u6WZJBKRmAHzVBh2ZmbqguQ1SU56oITdIdUGYU6Rn_kJoqnNfaXdbadqWgZLZJMnWOHsoV-kdWXnVOJ1EyhI6upYvY_F-DL-OriUHPNyjlLcs0ooQj0Mnp__Ro7q89SNqVPYX6GbANnEhhqgVt8KvjoY6DRTEBqRjB_j50l2RzvxbFQ5EQJd3nq98wjKwT5mMZoWKNor4yMDYn2Y-TBxcEkyOmGGZpdQ15csK4GFvMH-Bs7w0NfUacDnOJgXiT7f9L-xn8OflUA',
  'Cookie': 'access_token=eyJ0eXAiOiJKV1QiLCJraWQiOiJpZHQtYWJkZTk5NzktOGNhMS00MDhjLWIxZDEtNjJlMmY0MGM1MTdmIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzODIxNTQxIiwianRpIjoiNXdhQURKVGhIYkNyUHgwVGtpT0lyME8wTTdBIiwiaWF0IjoxNzcxNTE0OTU1LCJleHAiOjE3NzE1MTg1NTUsImlzcyI6ImxvZ2luLXNlcnZpY2UiLCJzY29wZSI6W10sImNsaWVudF9pZCI6IlBXMy1LZDZwdlRQSWNpUGJQeGRGNVMzRkF4ODgiLCJrZXlfaWQiOiJpZHQtYWJkZTk5NzktOGNhMS00MDhjLWIxZDEtNjJlMmY0MGM1MTdmIiwicmVmcmVzaF90b2tlbl9pZCI6Ii1xVTBXUGJtc0d4aGNXZTVSUjlPTW5QVFl6dyIsInR5cGUiOiJhY2Nlc3NfdG9rZW4iLCJyb2xlIjoiTEVBRCIsInVzZXJfdHlwZSI6IkxFQUQiLCJ2ZXJzaW9uIjoiVjIiLCJwbGFuIjoiQkFTSUMifQ.LKoxORJXkM6548yEn3uD7nBThfCbHQ90ETl9PuyCie3Kc36QQ4itpXUj3oEtNUg6QHvtZif-PglnrGLAi2cYuQEaJEWvgJosGmGbWkr64zG7BJZa2M2ARErD-TMCScjAHEgqn6iioBh0lnijK5dWcCjcVgSlC7Y3q_Nsf2BVyzzEK0OpiNsQ4zePN74LMuJLzA_mlFRdqrN8DX9dSR8g1tuzBBZrfE3qtn3TrRmqF1Je-3bhwY7q3SV_HUoK6yJY-Z3R3cNTKwMgZE5eSXMsnPxpXAvxwdI75GLUR-QdPoPCLfprzrMNrOwsBg0LcssHRhZ9UV7nLpjNCpg8StgMEQ; auth_identity_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI2NWQ1MjhiZGFkYmRiZTUyNDQ2Mzc2ZGQzZTQ5ZWM2OSIsImV4cCI6MTc3MTYwMTM1NH0.OAXUsydnSmEz-cZoy0XEajn5us959787KrYdEefyAEU; auth_identity_token_expiry=1771601353708; customer_status=NEW; profile_id_web=3821541; refresh_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzODIxNTQxIiwianRpIjoiLXFVMFdQYm1zR3hoY1dlNVJSOU9NblBUWXp3IiwiaWF0IjoxNzcxNTE0OTU1LCJleHAiOjE3NzE2MDEzNTUsImlzcyI6ImxvZ2luLXNlcnZpY2UiLCJzY29wZSI6W10sImNsaWVudF9pZCI6IlBXMy1LZDZwdlRQSWNpUGJQeGRGNVMzRkF4ODgiLCJrZXlfaWQiOiJpZHQtYWJkZTk5NzktOGNhMS00MDhjLWIxZDEtNjJlMmY0MGM1MTdmIiwiYXRpIjoiNXdhQURKVGhIYkNyUHgwVGtpT0lyME8wTTdBIiwicmVmcmVzaF90b2tlbl9pZCI6Ii1xVTBXUGJtc0d4aGNXZTVSUjlPTW5QVFl6dyIsInR5cGUiOiJyZWZyZXNoX3Rva2VuIiwicm9sZSI6IkxFQUQiLCJ1c2VyX3R5cGUiOiJMRUFEIiwidmVyc2lvbiI6IlYyIiwicGxhbiI6IkJBU0lDIn0.M-gKf6dH97vHRHNwQqA-9HZ3ChQIulhu0yTfvCOR3ErtPBnDPi5wgryyZstgn5ZrEfynuWVXTWDnHr3OLF_PWZ_2qUlCvHpg6k_xUZVroP9tMQtUFxc7TApuiQtVrnUhWPKGvv-rzUmcU1y7V7QWDjT-Vnv6IuQ-Uh4TIKMqhzcLh-sQkfMZ_pVABI3Co94B0gQDYPvTW2oBOvlVU3G41mxPSJGD1KE7qJnhmGQ2V5XzmyuyKsdqbDz8ctpGEriW0qPLZHsK3I6joG-Yq1mOsUrgrD5eJBzvOGxsqAgrFmNn-7JsAaeL3zd-wDP58w0xiDpLnyizLu2F8neTS1yXkA; __cf_bm=OpEFK48xlrCNbg6hzJA0Le3HU1pG4ChiERVavUI8hCg-1771514948-1.0.1.1-oTKfrSzk.OswKkWgwGC0ac9SXNpUALMpSJu1wXt7fMvBst8ub2_kFcJe7idSU1TdKfyOJkH4kU217UFwA7Wp.3dqLkiyC05YmDHbZbyGF88; _cfuvid=wxFrLvEeEXct0FuEEdbtXMj4FyQ9nTbL_HKnaZTiKHw-1771492556398-0.0.1.1-604800000'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
