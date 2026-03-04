Prompt 5

---

## Improved Prompt: Stage 5 (Email OTP Verification API)

**Context:** We are now at **Stage 5** of our Python API automation. This stage involves verifying the OTP sent to the email address generated in the previous step.

### 1. Workflow Sequence

* **Step 4 (Pre-requisite):** Email Send OTP API (Generates a dynamic email).
* **Step 5 (Current):** **Email Verify OTP API**. This must trigger only after Step 4 returns a success message.

### 2. Request Configuration

* **API Name:** `Email Verify OTP`
* **Dynamic Dependency:** Retrieve and use the exact **Email ID** that was generated and used in **Stage 4**.
* **Hardcoded Input:** Set the `otp` value to `123789`.
* **Payload Structure:**

```json
{
  "email": "<dynamic_email_from_stage_4>",
  "otp": "123789"
}

```

### 3. Success Validation Criteria

The automation script must validate the following to confirm a successful verification:

* **HTTP Status Code:** `200 OK`
* **JSON Response Body:** Must exactly match `{"EMAIL": "OTP verified successfully"}`.

### 4. Reporting & Summary

Upon completion of this API call:

* Update the **Execution Summary** with the final Status Code.
* Log the full **API Response** for Stage 5.
* Confirm that the email used in Stage 5 matches the email from Stage 4.

---

### Key Improvements Made:

* **Data Persistence:** Emphasized that the script must "remember" the email from Stage 4. If you hardcode `aahulsingh121@gmail.com` in the script, the test will fail because Stage 4 generates a *random* email every time.
* **Structural Clarity:** Organized the requirements into Request, Validation, and Reporting for better code architecture.
* **Eliminated Ambiguity:** Clarified that the "Existing enter email id" refers to the dynamic variable from the previous stage.

**Would you like me to write the Python logic that handles passing the email variable from the Stage 4 function to this Stage 5 function?**