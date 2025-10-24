#!/usr/bin/env python3

import requests
import json
import io
from PIL import Image

class ErrorScenarioTester:
    def __init__(self, base_url="https://habitere-inventory.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Habitere-Error-Test/1.0'
        })

    def test_image_upload_missing_entity_type(self):
        """Test image upload without entity_type parameter"""
        try:
            test_image = Image.new('RGB', (100, 100), color='blue')
            img_bytes = io.BytesIO()
            test_image.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            files = {
                'files': ('test_image.jpg', img_bytes, 'image/jpeg')
            }
            # Missing entity_type in data
            data = {
                'entity_id': 'test-property-id'
            }
            
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{self.api_url}/upload/images",
                files=files,
                data=data,
                headers=headers
            )
            
            print(f"Missing entity_type test: Status {response.status_code}")
            if response.status_code != 401:  # If not auth error, check for validation error
                print(f"Response: {response.text[:200]}")
            return True
        except Exception as e:
            print(f"Error in missing entity_type test: {e}")
            return False

    def test_mtn_momo_missing_phone(self):
        """Test MTN MoMo payment without phone number"""
        try:
            payment_data = {
                "amount": "1000",
                "currency": "EUR",
                "external_id": "test-payment-123",
                "payer_message": "Test payment",
                "payee_note": "Test transaction"
                # Missing phone number
            }
            
            response = self.session.post(
                f"{self.api_url}/payments/mtn-momo",
                json=payment_data
            )
            
            print(f"Missing phone test: Status {response.status_code}")
            if response.status_code not in [401, 422]:  # If not auth or validation error
                print(f"Response: {response.text[:200]}")
            return True
        except Exception as e:
            print(f"Error in missing phone test: {e}")
            return False

    def test_mtn_momo_invalid_amount(self):
        """Test MTN MoMo payment with invalid amount"""
        try:
            payment_data = {
                "amount": "-100",  # Negative amount
                "currency": "EUR",
                "external_id": "test-payment-123",
                "payer_message": "Test payment",
                "payee_note": "Test transaction",
                "phone": "237123456789"
            }
            
            response = self.session.post(
                f"{self.api_url}/payments/mtn-momo",
                json=payment_data
            )
            
            print(f"Invalid amount test: Status {response.status_code}")
            if response.status_code not in [401, 422, 400]:
                print(f"Response: {response.text[:200]}")
            return True
        except Exception as e:
            print(f"Error in invalid amount test: {e}")
            return False

    def test_image_endpoint_invalid_entity_type(self):
        """Test getting images with invalid entity type"""
        try:
            response = self.session.get(f"{self.api_url}/images/invalid_type/some-id")
            print(f"Invalid entity type test: Status {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {len(data)} images found")
            return True
        except Exception as e:
            print(f"Error in invalid entity type test: {e}")
            return False

    def test_mtn_momo_callback_malformed(self):
        """Test MTN MoMo callback with malformed data"""
        try:
            # Missing required fields
            callback_data = {
                "status": "SUCCESSFUL"
                # Missing referenceId
            }
            
            response = self.session.post(
                f"{self.api_url}/payments/mtn-momo/callback",
                json=callback_data
            )
            
            print(f"Malformed callback test: Status {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {data}")
            elif response.status_code == 400:
                print("Properly rejected malformed callback")
            return True
        except Exception as e:
            print(f"Error in malformed callback test: {e}")
            return False

    def run_error_tests(self):
        """Run all error scenario tests"""
        print("🔍 Testing Error Scenarios...")
        print("=" * 50)
        
        print("\n📸 Image Upload Error Tests:")
        self.test_image_upload_missing_entity_type()
        self.test_image_endpoint_invalid_entity_type()
        
        print("\n💳 MTN MoMo Error Tests:")
        self.test_mtn_momo_missing_phone()
        self.test_mtn_momo_invalid_amount()
        self.test_mtn_momo_callback_malformed()
        
        print("\n✅ Error scenario testing completed")

if __name__ == "__main__":
    tester = ErrorScenarioTester()
    tester.run_error_tests()