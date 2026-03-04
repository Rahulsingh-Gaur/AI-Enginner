#!/usr/bin/env python3
"""
Stage Handlers - Individual API stage implementations
Extracted from auto_run_full_flow.py for better modularity
"""
import logging
from datetime import datetime
from typing import Tuple, Dict, Any

from src.api_clients.upstox_auth_client import UpstoxAuthClient
from src.models.upstox_models import token_store

logger = logging.getLogger(__name__)


class StageResult:
    """Result of a stage execution"""
    def __init__(self, success: bool, message: str = "", details: dict = None):
        self.success = success
        self.message = message
        self.details = details or {}


class StageManager:
    """Manages all 5 stages of the authentication flow"""
    
    def __init__(self, client: UpstoxAuthClient, mobile_number: str, email: str, otp: str = "123789"):
        self.client = client
        self.mobile_number = mobile_number
        self.email = email
        self.otp = otp
        self.results: list = []
    
    def run_stage1_generate_otp(self) -> StageResult:
        """Stage 1: Generate OTP"""
        logger.info("\n📌 STAGE 1: Generate OTP")
        
        response = self.client.generate_otp(self.mobile_number, save_token=True)
        success = response.success
        
        self._record_result(1, "Generate OTP", success, 200, response.message)
        logger.info(f"   Status: {'✅ PASS' if success else '❌ FAIL'}")
        
        if not success:
            return StageResult(False, "Stage 1 Failed: Generate OTP")
        
        return StageResult(True, response.message, {
            "token": response.validate_otp_token[:30] + "..." if response.validate_otp_token else None
        })
    
    def run_stage2_verify_otp(self) -> StageResult:
        """Stage 2: Verify OTP"""
        logger.info("\n📌 STAGE 2: Verify OTP")
        
        response = self.client.verify_otp(
            otp=self.otp,
            mobile_number=self.mobile_number,
            save_profile_id=True
        )
        
        is_valid, error_msg = response.validate_success_response()
        
        self._record_result(2, "Verify OTP", is_valid, 200, response.message, {
            "user_type": response.user_type,
            "profile_id": response.profile_id
        })
        
        logger.info(f"   Status: {'✅ PASS' if is_valid else '❌ FAIL'}")
        logger.info(f"   Profile ID: {response.profile_id}")
        logger.info(f"   User Type: {response.user_type}")
        
        if not is_valid:
            return StageResult(False, f"Stage 2 Failed: {error_msg}")
        
        return StageResult(True, "OTP verified", {
            "user_type": response.user_type,
            "profile_id": response.profile_id
        })
    
    def run_stage3_two_fa(self) -> StageResult:
        """Stage 3: 2FA Authentication"""
        logger.info("\n📌 STAGE 3: 2FA Authentication")
        
        response = self.client.two_factor_auth(otp=self.otp)
        is_valid, error_msg = response.validate_success_response()
        
        self._record_result(3, "2FA Authentication", is_valid, 200, "2FA Successful", {
            "redirect_uri": response.redirect_uri,
            "user_type": response.user_type,
            "customer_status": response.customer_status
        })
        
        logger.info(f"   Status: {'✅ PASS' if is_valid else '❌ FAIL'}")
        logger.info(f"   Redirect URI: {response.redirect_uri}")
        logger.info(f"   Customer Status: {response.customer_status}")
        
        if not is_valid:
            return StageResult(False, f"Stage 3 Failed: {error_msg}")
        
        return StageResult(True, "2FA successful", {
            "redirect_uri": response.redirect_uri,
            "customer_status": response.customer_status
        })
    
    def run_stage4_email_send_otp(self) -> StageResult:
        """Stage 4: Email Send OTP"""
        logger.info("\n📌 STAGE 4: Email Send OTP")
        
        response = self.client.email_send_otp(email=self.email)
        is_valid, error_msg = response.validate_success_response()
        
        self._record_result(4, "Email Send OTP", is_valid, 200, response.message, {
            "email_used": self.email
        })
        
        logger.info(f"   Status: {'✅ PASS' if is_valid else '❌ FAIL'}")
        logger.info(f"   Email: {self.email}")
        logger.info(f"   Response: {response.message}")
        
        if not is_valid:
            return StageResult(False, f"Stage 4 Failed: {error_msg}")
        
        return StageResult(True, response.message, {"email": self.email})
    
    def run_stage5_email_verify_otp(self) -> StageResult:
        """Stage 5: Email Verify OTP"""
        logger.info("\n📌 STAGE 5: Email Verify OTP")
        
        response = self.client.email_verify_otp(email=self.email, otp=self.otp)
        is_valid, error_msg = response.validate_success_response()
        
        self._record_result(5, "Email Verify OTP", is_valid, 200, response.message, {
            "email_verified": self.email
        })
        
        logger.info(f"   Status: {'✅ PASS' if is_valid else '❌ FAIL'}")
        logger.info(f"   Email Verified: {self.email}")
        logger.info(f"   Response: {response.message}")
        
        if not is_valid:
            return StageResult(False, f"Stage 5 Failed: {error_msg}")
        
        return StageResult(True, response.message, {"email": self.email})
    
    def _record_result(self, stage: int, api_name: str, status: bool, 
                       status_code: int, message: str, details: dict = None):
        """Record API result for reporting"""
        self.results.append({
            "stage": stage,
            "api_name": api_name,
            "status": "PASS" if status else "FAIL",
            "status_code": status_code,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        })
    
    def get_results(self) -> list:
        """Get all recorded results"""
        return self.results
