# Gemini.md - Project Constitution

> This is the **law**. Data schemas, behavioral rules, and architectural invariants.

---

## Data Schema

### Input Shape
```json
{
  "url": "string (default: https://upstox.com/)",
  "mobile_number": "string (default: 9552931377)"
}
```

### Output Shape (Payload)
No output payload - local browser automation only.

**Side Effects:**
- Chrome browser opens
- Navigates to specified URL
- Finds Sign In button using XPath
- Clicks Sign In button
- Enters mobile number in login form
- Handles Cloudflare checkbox conditionally (if present)
- Clicks "Get OTP" button when enabled
- Browser remains open (manual close required)

---

## Behavioral Rules

### System Behavior
- Open browser in visible mode (not headless)
- Navigate directly to target URL
- Handle Cloudflare checkbox only if present (conditional logic)
- Wait for "Get OTP" button to be enabled before clicking
- Keep browser open (do not auto-close)
- Use human-like delays between actions

### Constraints
- Requires Chrome browser installed on system
- Requires internet connectivity to load https://upstox.com/
- Selenium WebDriver must be available
- "Get OTP" button must be enabled before clicking

---

## Architectural Invariants

### Golden Rules
1. If logic changes, update the SOP before updating code
2. All environment variables in `.env`
3. All intermediate files in `.tmp/`

---

## Maintenance Log

| Date | Change | Reason |
|------|--------|--------|
| 2026-02-07 | Initialized project | Project start |
| 2026-02-07 | Discovery complete, Blueprint approved | User provided requirements |
| 2026-02-07 | Data Schema defined | Selenium automation task |
| 2026-02-07 | Tool built | `browser_automation.py` ready for execution |
| 2026-02-07 | Project complete | Successfully executed browser automation |
| 2026-02-07 | Requirements updated | Added Get OTP button, conditional Cloudflare handling |
