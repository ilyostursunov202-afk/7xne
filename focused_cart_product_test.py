#!/usr/bin/env python3
"""
Focused test for cart and product functionality as requested in the review.
Tests the specific endpoints mentioned in the review request.
"""

import requests
import json
from datetime import datetime

class FocusedAPITester:
    def __init__(self, base_url="https://vendormarket.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.cart_id = None
        self.product_id = None
        self.test_results = []

    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })

    def test_product_endpoints(self):
        """Test all product-related endpoints"""
        print("\n🛍️  TESTING PRODUCT ENDPOINTS")
        print("=" * 40)
        
        # 1. GET /api/products (list products)
        try:
            response = self.session.get(f"{self.base_url}/api/products")
            success = response.status_code == 200
            products = response.json() if success else []
            details = f"Status: {response.status_code}, Products found: {len(products)}"
            self.log_test("GET /api/products", success, details)
            
            # Store a product ID for later tests
            if success and products:
                self.product_id = products[0]['id']
                print(f"    Using product ID: {self.product_id}")
        except Exception as e:
            self.log_test("GET /api/products", False, f"Error: {str(e)}")

        # 2. Create a test product first
        try:
            product_data = {
                "name": f"Cart Test Product {datetime.now().strftime('%H%M%S')}",
                "description": "Product specifically for cart testing",
                "price": 49.99,
                "category": "Test Category",
                "brand": "TestBrand",
                "images": ["https://via.placeholder.com/300"],
                "inventory": 20,
                "tags": ["test", "cart"]
            }
            
            response = self.session.post(f"{self.base_url}/api/products", json=product_data)
            success = response.status_code == 200
            if success:
                created_product = response.json()
                self.product_id = created_product['id']
                details = f"Status: {response.status_code}, Created product ID: {self.product_id}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
            self.log_test("POST /api/products (create test product)", success, details)
        except Exception as e:
            self.log_test("POST /api/products (create test product)", False, f"Error: {str(e)}")

        # 3. GET /api/products/{product_id} (get single product)
        if self.product_id:
            try:
                response = self.session.get(f"{self.base_url}/api/products/{self.product_id}")
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                if success:
                    product = response.json()
                    details += f", Product: {product.get('name', 'Unknown')}, Price: ${product.get('price', 0)}"
                self.log_test("GET /api/products/{product_id}", success, details)
            except Exception as e:
                self.log_test("GET /api/products/{product_id}", False, f"Error: {str(e)}")

        # 4. GET /api/categories
        try:
            response = self.session.get(f"{self.base_url}/api/categories")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                categories = response.json().get('categories', [])
                details += f", Categories found: {len(categories)}"
            self.log_test("GET /api/categories", success, details)
        except Exception as e:
            self.log_test("GET /api/categories", False, f"Error: {str(e)}")

        # 5. GET /api/brands
        try:
            response = self.session.get(f"{self.base_url}/api/brands")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                brands = response.json().get('brands', [])
                details += f", Brands found: {len(brands)}"
            self.log_test("GET /api/brands", success, details)
        except Exception as e:
            self.log_test("GET /api/brands", False, f"Error: {str(e)}")

    def test_cart_endpoints(self):
        """Test all cart-related endpoints"""
        print("\n🛒 TESTING CART ENDPOINTS")
        print("=" * 40)
        
        # 1. POST /api/cart (create cart)
        try:
            response = self.session.post(f"{self.base_url}/api/cart")
            success = response.status_code == 200
            if success:
                cart = response.json()
                self.cart_id = cart['id']
                details = f"Status: {response.status_code}, Cart ID: {self.cart_id}"
            else:
                details = f"Status: {response.status_code}, Error: {response.text[:100]}"
            self.log_test("POST /api/cart", success, details)
        except Exception as e:
            self.log_test("POST /api/cart", False, f"Error: {str(e)}")

        # 2. GET /api/cart/{cart_id} (get cart)
        if self.cart_id:
            try:
                response = self.session.get(f"{self.base_url}/api/cart/{self.cart_id}")
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                if success:
                    cart = response.json()
                    details += f", Items: {len(cart.get('items', []))}, Total: ${cart.get('total', 0)}"
                self.log_test("GET /api/cart/{cart_id}", success, details)
            except Exception as e:
                self.log_test("GET /api/cart/{cart_id}", False, f"Error: {str(e)}")

        # 3. POST /api/cart/{cart_id}/items (add item to cart)
        if self.cart_id and self.product_id:
            try:
                params = {
                    "product_id": self.product_id,
                    "quantity": 2
                }
                response = self.session.post(f"{self.base_url}/api/cart/{self.cart_id}/items", params=params)
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                if success:
                    cart = response.json()
                    details += f", Items after add: {len(cart.get('items', []))}, Total: ${cart.get('total', 0)}"
                else:
                    details += f", Error: {response.text[:100]}"
                self.log_test("POST /api/cart/{cart_id}/items", success, details)
            except Exception as e:
                self.log_test("POST /api/cart/{cart_id}/items", False, f"Error: {str(e)}")

        # 4. Verify cart has items after adding
        if self.cart_id:
            try:
                response = self.session.get(f"{self.base_url}/api/cart/{self.cart_id}")
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                if success:
                    cart = response.json()
                    items_count = len(cart.get('items', []))
                    details += f", Items in cart: {items_count}, Total: ${cart.get('total', 0)}"
                    success = items_count > 0  # Verify cart actually has items
                self.log_test("GET /api/cart/{cart_id} (verify items added)", success, details)
            except Exception as e:
                self.log_test("GET /api/cart/{cart_id} (verify items added)", False, f"Error: {str(e)}")

        # 5. DELETE /api/cart/{cart_id}/items/{product_id} (remove item from cart)
        if self.cart_id and self.product_id:
            try:
                response = self.session.delete(f"{self.base_url}/api/cart/{self.cart_id}/items/{self.product_id}")
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                if success:
                    cart = response.json()
                    details += f", Items after remove: {len(cart.get('items', []))}, Total: ${cart.get('total', 0)}"
                else:
                    details += f", Error: {response.text[:100]}"
                self.log_test("DELETE /api/cart/{cart_id}/items/{product_id}", success, details)
            except Exception as e:
                self.log_test("DELETE /api/cart/{cart_id}/items/{product_id}", False, f"Error: {str(e)}")

    def test_scenarios(self):
        """Test the specific scenarios mentioned in the review"""
        print("\n🎯 TESTING SPECIFIC SCENARIOS")
        print("=" * 40)
        
        # Scenario: Create a new cart, add product, remove product
        scenario_success = True
        
        # Create new cart for scenario
        try:
            response = self.session.post(f"{self.base_url}/api/cart")
            if response.status_code == 200:
                scenario_cart_id = response.json()['id']
                self.log_test("Scenario: Create new cart", True, f"Cart ID: {scenario_cart_id}")
            else:
                scenario_success = False
                self.log_test("Scenario: Create new cart", False, f"Status: {response.status_code}")
                return
        except Exception as e:
            scenario_success = False
            self.log_test("Scenario: Create new cart", False, f"Error: {str(e)}")
            return

        # Add product to cart
        if self.product_id:
            try:
                params = {"product_id": self.product_id, "quantity": 1}
                response = self.session.post(f"{self.base_url}/api/cart/{scenario_cart_id}/items", params=params)
                success = response.status_code == 200
                if success:
                    cart = response.json()
                    items_count = len(cart.get('items', []))
                    self.log_test("Scenario: Add product to cart", True, f"Items: {items_count}")
                else:
                    scenario_success = False
                    self.log_test("Scenario: Add product to cart", False, f"Status: {response.status_code}")
            except Exception as e:
                scenario_success = False
                self.log_test("Scenario: Add product to cart", False, f"Error: {str(e)}")

        # Remove product from cart
        if self.product_id:
            try:
                response = self.session.delete(f"{self.base_url}/api/cart/{scenario_cart_id}/items/{self.product_id}")
                success = response.status_code == 200
                if success:
                    cart = response.json()
                    items_count = len(cart.get('items', []))
                    self.log_test("Scenario: Remove product from cart", True, f"Items remaining: {items_count}")
                else:
                    scenario_success = False
                    self.log_test("Scenario: Remove product from cart", False, f"Status: {response.status_code}")
            except Exception as e:
                scenario_success = False
                self.log_test("Scenario: Remove product from cart", False, f"Error: {str(e)}")

        # Get product details
        if self.product_id:
            try:
                response = self.session.get(f"{self.base_url}/api/products/{self.product_id}")
                success = response.status_code == 200
                if success:
                    product = response.json()
                    self.log_test("Scenario: Get product details", True, f"Product: {product.get('name')}")
                else:
                    scenario_success = False
                    self.log_test("Scenario: Get product details", False, f"Status: {response.status_code}")
            except Exception as e:
                scenario_success = False
                self.log_test("Scenario: Get product details", False, f"Error: {str(e)}")

        # List available products
        try:
            response = self.session.get(f"{self.base_url}/api/products")
            success = response.status_code == 200
            if success:
                products = response.json()
                self.log_test("Scenario: List available products", True, f"Products available: {len(products)}")
            else:
                scenario_success = False
                self.log_test("Scenario: List available products", False, f"Status: {response.status_code}")
        except Exception as e:
            scenario_success = False
            self.log_test("Scenario: List available products", False, f"Error: {str(e)}")

        return scenario_success

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 FOCUSED CART & PRODUCT API TESTING")
        print("=" * 50)
        
        self.test_product_endpoints()
        self.test_cart_endpoints()
        self.test_scenarios()
        
        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Cart and Product functionality is working correctly.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed.")
            print("\nFailed tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['details']}")
            return False

def main():
    tester = FocusedAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())