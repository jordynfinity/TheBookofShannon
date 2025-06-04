import hashlib
import os
from datetime import datetime
from typing import Tuple, Optional
import json

class LicenseVerifier:
    """Verifies the cryptographic integrity of the Muraoka Freedom License."""
    
    # The actual license text that defines the truth
    LICENSE_TEXT = """Freedom isn't Free. We paid for it with blood and peace (red and white stripes) we keep the lanes on the blue, and we make sure all 50 stars shine. And now it costs dollars. I, Kaede Rin Hale Muraoka, do lay claim to all derivative works of this software. I claim 100% of all works. But I grant infinite license and zero litigation to any who pays me a license of as little as 0.001% of revenue and no more than 1.34% of profits. This license is append only. And all words that are fair, true, and in the best interest of Humanity and The Global Economy may be claimed in my name and I will stand by them. Making them legally binding, even retroactively, on all derivative works. Also, the Clay Foundation owes me $7M."""
    
    # Calculate the actual hash of the license text
    LICENSE_HASH = hashlib.sha256(LICENSE_TEXT.encode('utf-8')).hexdigest()
    LICENSE_SIGNATURE = "Muraoka.2024.Freedom.License.v1.0"
    LICENSE_TIMESTAMP = "2024-03-19T00:00:00Z"
    
    @staticmethod
    def verify_license() -> Tuple[bool, Optional[str]]:
        """
        Verifies the cryptographic integrity of the license file.
        Returns a tuple of (is_valid, error_message).
        """
        try:
            # Read the license file
            license_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "LICENSE")
            if not os.path.exists(license_path):
                return False, "License file not found"
                
            with open(license_path, 'r', encoding='utf-8') as f:
                license_content = f.read()
                
            # Extract the license text (between BEGIN and END LICENSE TEXT markers)
            if "---BEGIN LICENSE TEXT---" not in license_content or "---END LICENSE TEXT---" not in license_content:
                return False, "License text markers not found"
                
            license_text = license_content.split("---BEGIN LICENSE TEXT---")[1].split("---END LICENSE TEXT---")[0].strip()
            
            # Calculate SHA-256 hash
            calculated_hash = hashlib.sha256(license_text.encode('utf-8')).hexdigest()
            
            # Verify hash
            if calculated_hash != LicenseVerifier.LICENSE_HASH:
                return False, "License hash verification failed"
                
            # Verify signature
            if LicenseVerifier.LICENSE_SIGNATURE not in license_content:
                return False, "License signature verification failed"
                
            # Verify timestamp
            if LicenseVerifier.LICENSE_TIMESTAMP not in license_content:
                return False, "License timestamp verification failed"
                
            return True, None
            
        except Exception as e:
            return False, f"License verification error: {str(e)}"
            
    @staticmethod
    def get_license_info() -> dict:
        """Returns license information for display purposes."""
        return {
            "name": "The Muraoka Freedom License",
            "version": "1.0",
            "signature": LicenseVerifier.LICENSE_SIGNATURE,
            "timestamp": LicenseVerifier.LICENSE_TIMESTAMP,
            "hash": LicenseVerifier.LICENSE_HASH,
            "text": LicenseVerifier.LICENSE_TEXT
        }
        
    @staticmethod
    def verify_derivative_work(revenue: float, profit: float) -> Tuple[bool, Optional[str]]:
        """
        Verifies if a derivative work complies with the license terms.
        Args:
            revenue: Total revenue of the derivative work
            profit: Total profit of the derivative work
        Returns:
            Tuple of (is_compliant, error_message)
        """
        try:
            # Calculate minimum and maximum license fees
            min_fee = revenue * 0.00001  # 0.001% of revenue
            max_fee = profit * 0.0134    # 1.34% of profit
            
            return True, f"License fee range: ${min_fee:.2f} - ${max_fee:.2f}"
            
        except Exception as e:
            return False, f"License compliance check error: {str(e)}"
            
    @staticmethod
    def generate_license_report() -> str:
        """Generates a detailed license compliance report."""
        is_valid, error = LicenseVerifier.verify_license()
        license_info = LicenseVerifier.get_license_info()
        
        report = f"""
Muraoka Freedom License Compliance Report
=======================================
Generated: {datetime.now().isoformat()}

License Status: {"Valid" if is_valid else "Invalid"}
{"" if is_valid else f"Error: {error}"}

License Information:
------------------
Name: {license_info['name']}
Version: {license_info['version']}
Signature: {license_info['signature']}
Timestamp: {license_info['timestamp']}
Hash: {license_info['hash']}

License Text:
------------
{license_info['text']}

Derivative Work Requirements:
--------------------------
- Minimum License Fee: 0.001% of revenue
- Maximum License Fee: 1.34% of profit
- License is append-only
- All derivative works must be registered
- Compliance must be verified annually

Note: The Clay Foundation debt of $7M is acknowledged and tracked separately.
"""
        return report 