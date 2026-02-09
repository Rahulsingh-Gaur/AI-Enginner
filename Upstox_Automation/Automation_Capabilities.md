# 🚀 Upstox Automation Capabilities

> **Living Document** - Track all automation milestones and features  
> **Last Updated:** 2026-02-08 (Email Screen Added)  
> **Project:** Upstox Web Automation

---
## 📊 Checklist Status Overview
 Find Sign In Button | ✅ | Multiple XPath strategies |
| Click Sign In Button | ✅ | Opens login popup/new tab |
| Mobile Number Input | ✅ | Enters "9552931377" |
| Cloudflare Handling | ✅ | Conditional checkbox click |
| Get OTP Button | ✅ | Waits for enable, then clicks |
||

## 📊 Quick Status Overview

| Category | Status | Milestones |
|----------|--------|------------|
| Authentication | 🟡 In Progress | 3/4 Complete |
| Onboarding | ✅ Complete | 1/1 Complete |
| Trading | ⚪ Not Started | 0/5 Complete |
| Portfolio | ⚪ Not Started | 0/3 Complete |
| Data Extraction | ⚪ Not Started | 0/2 Complete |

**Legend:** ✅ Complete | 🟡 In Progress | ⚪ Not Started | 🔴 Blocked

---

## 🔐 1. Authentication & Login

### Milestone 1.1: Basic Login Flow
| Item | Status | Details |
|------|--------|---------|
| Open Chrome Browser | ✅ | With anti-detection measures |
| Navigate to upstox.com | ✅ | URL: https://upstox.com/ |
| Find Sign In Button | ✅ | Multiple XPath strategies |
| Click Sign In Button | ✅ | Opens login popup/new tab |
| Mobile Number Input | ✅ | Enters "9552931377" |
| Cloudflare Handling | ✅ | Conditional checkbox click |
| Get OTP Button | ✅ | Waits for enable, then clicks |
| Keep Browser Open | ✅ | Manual verification mode |

**Test Status:** ✅ PASS  
**File:** `tools/browser_automation.py` → `open_browser_and_login()`

---

### Milestone 1.2: Email Authentication Screen (Conditional)
| Item | Status | Details |
|------|--------|---------|
| Detect Email Screen | ✅ | Check for "What's your email address?" label |
| Conditional Handling | ✅ | Skip if not found (one-time only) |
| Enter Email Address | ✅ | Input: Anujathakur259@gmail.com |
| Click Continue Button | ✅ | Wait for enabled, then click |
| Handle Multiple XPaths | ✅ | Fallback strategies for elements |

**Test Status:** 🟡 READY FOR TEST  
**File:** `tools/browser_automation.py` → `handle_email_screen()`  
**Note:** This screen appears only once for new users after mobile OTP

---

### Milestone 1.3: Full Login Flow with OTP Wait
| Item | Status | Details |
|------|--------|---------|
| Complete Login Steps | ✅ | All from 1.1 |
| Pause for Manual OTP | ✅ | User enters OTP manually |
| Handle Email Screen | ✅ | Conditional step added |
| Auto-detect Login Success | ⚪ | Detect successful login |
| Session Persistence | ⚪ | Save cookies/session |

**Test Status:** 🟡 PARTIAL  
**File:** `tools/browser_automation.py` → `run_full_flow()`

---

### Milestone 1.3: Automated OTP (Future)
| Item | Status | Details |
|------|--------|---------|
| SMS Integration | ⚪ | Read OTP from SMS/Email |
| Auto-enter OTP | ⚪ | Fill 6-digit code automatically |
| TOTP Support | ⚪ | Time-based OTP for 2FA |

**Test Status:** ⚪ NOT STARTED  
**Note:** Requires SMS gateway integration

---

## 📝 2. Onboarding Flow

### Milestone 2.1: Personal Information Form
| Item | Status | Details |
|------|--------|---------|
| Navigate to Onboarding | ✅ | URL: /onboarding/personal-info |
| Select Marital Status | ✅ | Single / Married |
| Select Trading Experience | ✅ | <1 year to >25 years |
| Select Occupation | ✅ | Private, Govt, Business, etc. |
| Select Annual Income | ✅ | Below ₹1L to Above ₹25L |
| Click Continue | ✅ | Proceeds to next step |

**Test Status:** ✅ PASS  
**File:** `tools/browser_automation.py` → `fill_onboarding_form()`

---

### Milestone 2.2: Bank Details (Future)
| Item | Status | Details |
|------|--------|---------|
| Enter Bank Account Number | ⚪ | Valid account number |
| Select Bank Name | ⚪ | Dropdown selection |
| Enter IFSC Code | ⚪ | Auto-fill from bank |
| Upload Cancelled Cheque | ⚪ | File upload handling |
| Verify Bank Details | ⚪ | Penny drop verification |

**Test Status:** ⚪ NOT STARTED

---

### Milestone 2.3: Document Upload (Future)
| Item | Status | Details |
|------|--------|---------|
| Upload PAN Card | ⚪ | Image/PDF upload |
| Upload Aadhaar Front | ⚪ | Image upload |
| Upload Aadhaar Back | ⚪ | Image upload |
| Upload Signature | ⚪ | Draw or upload |
| Upload Photo | ⚪ | Webcam capture or upload |

**Test Status:** ⚪ NOT STARTED

---

### Milestone 2.4: e-Sign & IPV (Future)
| Item | Status | Details |
|------|--------|---------|
| Aadhaar e-Sign | ⚪ | OTP-based signing |
| In-Person Verification | ⚪ | Video recording |
| Nominee Details | ⚪ | Add nominee info |

**Test Status:** ⚪ NOT STARTED

---

## 💹 3. Trading Operations

### Milestone 3.1: Market Data Viewing
| Item | Status | Details |
|------|--------|---------|
| View Market Watch | ⚪ | Nifty 50, Sensex |
| Search Scrip | ⚪ | Find stocks by name/symbol |
| View Stock Details | ⚪ | LTP, OHLC, Volume |
| View Charts | ⚪ | Candlestick patterns |
| Add to Watchlist | ⚪ | Create custom watchlists |

**Test Status:** ⚪ NOT STARTED

---

### Milestone 3.2: Order Placement
| Item | Status | Details |
|------|--------|---------|
| Place Buy Order (CNC) | ⚪ | Cash & Carry delivery |
| Place Buy Order (MIS) | ⚪ | Intraday margin |
| Place Sell Order | ⚪ | Exit positions |
| Modify Order | ⚪ | Change price/qty |
| Cancel Order | ⚪ | Cancel pending orders |
| Order Validation | ⚪ | Check margin requirements |

**Test Status:** ⚪ NOT STARTED

---

### Milestone 3.3: Order Types
| Item | Status | Details |
|------|--------|---------|
| Market Order | ⚪ | Execute at market price |
| Limit Order | ⚪ | Execute at set price |
| Stop Loss Order | ⚪ | SL & SL-M orders |
| Cover Order (CO) | ⚪ | Stop loss + target |
| Bracket Order (BO) | ⚪ | Entry, SL, Target |
| GTT Order | ⚪ | Good Till Triggered |

**Test Status:** ⚪ NOT STARTED

---

### Milestone 3.4: Option Trading
| Item | Status | Details |
|------|--------|---------|
| View Option Chain | ⚪ | Calls & Puts |
| Place Option Buy | ⚪ | CE/PE contracts |
| Place Option Sell | ⚪ | Write options |
| Strategy Builder | ⚪ | Multi-leg strategies |

**Test Status:** ⚪ NOT STARTED

---

### Milestone 3.5: Mutual Funds (Future)
| Item | Status | Details |
|------|--------|---------|
| Browse Funds | ⚪ | Explore MF categories |
| Place SIP Order | ⚪ | Systematic Investment |
| Place Lumpsum Order | ⚪ | One-time investment |
| Redeem Units | ⚪ | Sell MF units |

**Test Status:** ⚪ NOT STARTED

---

## 📊 4. Portfolio & Holdings

### Milestone 4.1: Portfolio View
| Item | Status | Details |
|------|--------|---------|
| View Holdings | ⚪ | All stocks held |
| View Positions | ⚪ | Open intraday positions |
| P&L Calculation | ⚪ | Realized & Unrealized |
| Day's P&L | ⚪ | Today's profit/loss |

**Test Status:** ⚪ NOT STARTED

---

### Milestone 4.2: Funds Management
| Item | Status | Details |
|------|--------|---------|
| Check Available Balance | ⚪ | Withdrawable amount |
| Check Used Margin | ⚪ | Blocked for positions |
| Add Funds (View) | ⚪ | UPI, Netbanking options |
| Withdraw Funds (View) | ⚪ | Withdrawal request |

**Test Status:** ⚪ NOT STARTED

---

### Milestone 4.3: Trade History
| Item | Status | Details |
|------|--------|---------|
| View Order Book | ⚪ | All orders placed |
| View Trade Book | ⚪ | Executed trades |
| Download Contract Note | ⚪ | Daily trade summary |
| Filter by Date | ⚪ | Historical data |

**Test Status:** ⚪ NOT STARTED

---

## 📤 5. Data Extraction & Reporting

### Milestone 5.1: Screenshot Capture
| Item | Status | Details |
|------|--------|---------|
| Full Page Screenshot | ✅ | Save as PNG |
| Element Screenshot | ⚪ | Specific component |
| Error Screenshots | ✅ | Auto-save on failure |
| Timestamped Files | ✅ | Organized by datetime |

**Test Status:** ✅ PASS  
**Location:** `.tmp/` folder

---

### Milestone 5.2: Data Export
| Item | Status | Details |
|------|--------|---------|
| Export Holdings to CSV | ⚪ | Stock-wise data |
| Export Orders to CSV | ⚪ | Order history |
| Export P&L to Excel | ⚪ | Tax reporting format |
| Scrape Real-time Prices | ⚪ | Live market data |

**Test Status:** ⚪ NOT STARTED

---

### Milestone 5.3: Reports Generation (Future)
| Item | Status | Details |
|------|--------|---------|
| Daily P&L Report | ⚪ | Automated email/pdf |
| Weekly Summary | ⚪ | Performance metrics |
| Tax Report (FY) | ⚪ | Capital gains report |

**Test Status:** ⚪ NOT STARTED

---

## ⚙️ 6. Advanced Features

### Milestone 6.1: Configuration Management
| Item | Status | Details |
|------|--------|---------|
| Environment Variables | ⚪ | .env for credentials |
| Config File Support | ⚪ | JSON/YAML settings |
| Multiple User Profiles | ⚪ | Switch accounts easily |

**Test Status:** ⚪ NOT STARTED

---

### Milestone 6.2: Headless Mode
| Item | Status | Details |
|------|--------|---------|
| Run Without UI | ⚪ | --headless option |
| Background Execution | ⚪ | No browser window |
| Docker Support | ⚪ | Containerized execution |

**Test Status:** ⚪ NOT STARTED

---

### Milestone 6.3: Notifications
| Item | Status | Details |
|------|--------|---------|
| Email Alerts | ⚪ | SMTP integration |
| Telegram Bot | ⚪ | Bot notifications |
| Slack Webhooks | ⚪ | Channel notifications |
| SMS Alerts | ⚪ | Twilio integration |

**Test Status:** ⚪ NOT STARTED

---

## 📋 How to Update This Document

When adding new automation features:

1. **Add new milestone** under appropriate category
2. **Mark items as:**
   - `⚪ Not Started` - Planned but not implemented
   - `🟡 In Progress` - Currently being developed
   - `✅ Complete` - Implemented and tested
   - `🔴 Blocked` - Cannot proceed (add reason)
3. **Update "Last Updated"** date at top
4. **Update Quick Status Overview** table

---

## 🎯 Next Priorities

Based on current status, recommended next steps:

1. 🟡 **Test Milestone 1.2** - Email authentication screen (NEW)
2. ✅ **Complete Milestone 1.3** - Auto-detect login success
3. 🟡 **Start Milestone 3.1** - Market data viewing
4. ⚪ **Plan Milestone 2.2** - Bank details automation
5. ⚪ **Research Milestone 6.1** - Config management

---

## 📞 Quick Reference

| File | Purpose |
|------|---------|
| `tools/browser_automation.py` | Main automation script |
| `task_plan.md` | Project goals & test cases |
| `selenium_browser_automation.md` | Technical SOP |
| `Automation_Capabilities.md` | **This file** |

---

*Document created by KIMI CLI | Maintain this file as automation grows*
