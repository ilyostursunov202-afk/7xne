#!/usr/bin/env python3
"""
Detailed Add to Cart Functionality Test
Focus: Verify backend API response structure for cart operations
"""

import requests
import json
import sys
from datetime import datetime

class AddToCartTester:
    def __init__(self):
        self.base_url = "https://shopfix-2.preview.emergentagent.com"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.cart_id = None
        self.product_id = None
        self.test_results = []

    def log_result(self, test_name, success, details):
        """Log test result with details"""
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n{status} {test_name}")
        print(f"Details: {details}")

    def create_test_product(self):
        """Create a test product for cart testing"""
        print("\n🔍 Step 1: Creating test product...")
        
        product_data = {
            "name": f"Cart Test Product {datetime.now().strftime('%H%M%S')}",
            "description": "Product specifically for testing Add to Cart functionality",
            "price": 49.99,
            "category": "Test Category",
            "brand": "TestBrand",
            "images": ["https://via.placeholder.com/300x300?text=Test+Product"],
            "inventory": 100,
            "tags": ["test", "cart", "api"]
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/products", json=product_data)
            
            if response.status_code == 200:
                product = response.json()
                self.product_id = product['id']
                self.log_result(
                    "Create Test Product", 
                    True, 
                    f"Product created with ID: {self.product_id}, Price: ${product['price']}"
                )
                return True
            else:
                self.log_result(
                    "Create Test Product", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Create Test Product", False, f"Exception: {str(e)}")
            return False

    def create_test_cart(self):
        """Create a test cart and get cart ID"""
        print("\n🔍 Step 2: Creating test cart...")
        
        try:
            response = self.session.post(f"{self.base_url}/api/cart")
            
            if response.status_code == 200:
                cart = response.json()
                self.cart_id = cart['id']
                
                # Verify initial cart structure
                expected_keys = ['id', 'user_id', 'session_id', 'items', 'total', 'updated_at']
                missing_keys = [key for key in expected_keys if key not in cart]
                
                if missing_keys:
                    self.log_result(
                        "Create Test Cart", 
                        False, 
                        f"Missing keys in cart response: {missing_keys}"
                    )
                    return False
                
                # Verify initial state
                if cart['items'] != [] or cart['total'] != 0:
                    self.log_result(
                        "Create Test Cart", 
                        False, 
                        f"Cart not empty initially. Items: {cart['items']}, Total: {cart['total']}"
                    )
                    return False
                
                self.log_result(
                    "Create Test Cart", 
                    True, 
                    f"Cart created with ID: {self.cart_id}. Initial state: empty items array, total: 0"
                )
                return True
            else:
                self.log_result(
                    "Create Test Cart", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Create Test Cart", False, f"Exception: {str(e)}")
            return False

    def add_item_to_cart(self, quantity=2):
        """Add item to cart using POST /api/cart/{cart_id}/items"""
        print(f"\n🔍 Step 3: Adding {quantity} items to cart...")
        
        if not self.cart_id or not self.product_id:
            self.log_result("Add Item to Cart", False, "Missing cart_id or product_id")
            return False
        
        try:
            # Add item to cart
            params = {
                "product_id": self.product_id,
                "quantity": quantity
            }
            
            response = self.session.post(
                f"{self.base_url}/api/cart/{self.cart_id}/items", 
                params=params
            )
            
            if response.status_code == 200:
                cart = response.json()
                
                # Detailed verification of response structure
                expected_keys = ['id', 'user_id', 'session_id', 'items', 'total', 'updated_at']
                missing_keys = [key for key in expected_keys if key not in cart]
                
                if missing_keys:
                    self.log_result(
                        "Add Item to Cart", 
                        False, 
                        f"Missing keys in response: {missing_keys}"
                    )
                    return False
                
                # Verify items array is populated
                if not cart['items'] or len(cart['items']) == 0:
                    self.log_result(
                        "Add Item to Cart", 
                        False, 
                        f"Items array is empty after adding item. Full response: {json.dumps(cart, indent=2)}"
                    )
                    return False
                
                # Verify item structure
                item = cart['items'][0]
                expected_item_keys = ['product_id', 'quantity', 'price']
                missing_item_keys = [key for key in expected_item_keys if key not in item]
                
                if missing_item_keys:
                    self.log_result(
                        "Add Item to Cart", 
                        False, 
                        f"Missing keys in item: {missing_item_keys}. Item: {item}"
                    )
                    return False
                
                # Verify item data
                if item['product_id'] != self.product_id:
                    self.log_result(
                        "Add Item to Cart", 
                        False, 
                        f"Product ID mismatch. Expected: {self.product_id}, Got: {item['product_id']}"
                    )
                    return False
                
                if item['quantity'] != quantity:
                    self.log_result(
                        "Add Item to Cart", 
                        False, 
                        f"Quantity mismatch. Expected: {quantity}, Got: {item['quantity']}"
                    )
                    return False
                
                # Verify total calculation
                expected_total = item['price'] * item['quantity']
                if abs(cart['total'] - expected_total) > 0.01:  # Allow for floating point precision
                    self.log_result(
                        "Add Item to Cart", 
                        False, 
                        f"Total calculation incorrect. Expected: {expected_total}, Got: {cart['total']}"
                    )
                    return False
                
                self.log_result(
                    "Add Item to Cart", 
                    True, 
                    f"Item added successfully. Items array populated with 1 item. Product: {item['product_id']}, Quantity: {item['quantity']}, Price: ${item['price']}, Total: ${cart['total']}"
                )
                return True
            else:
                self.log_result(
                    "Add Item to Cart", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Add Item to Cart", False, f"Exception: {str(e)}")
            return False

    def verify_cart_contents(self):
        """Verify cart contents by getting the cart: GET /api/cart/{cart_id}"""
        print("\n🔍 Step 4: Verifying cart contents...")
        
        if not self.cart_id:
            self.log_result("Verify Cart Contents", False, "Missing cart_id")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/api/cart/{self.cart_id}")
            
            if response.status_code == 200:
                cart = response.json()
                
                # Print full cart structure for analysis
                print(f"\n📋 FULL CART RESPONSE STRUCTURE:")
                print(json.dumps(cart, indent=2, default=str))
                
                # Verify cart structure
                expected_keys = ['id', 'user_id', 'session_id', 'items', 'total', 'updated_at']
                missing_keys = [key for key in expected_keys if key not in cart]
                
                if missing_keys:
                    self.log_result(
                        "Verify Cart Contents", 
                        False, 
                        f"Missing keys: {missing_keys}"
                    )
                    return False
                
                # Verify items array is populated
                if not cart['items'] or len(cart['items']) == 0:
                    self.log_result(
                        "Verify Cart Contents", 
                        False, 
                        f"Items array is empty. Cart: {cart}"
                    )
                    return False
                
                # Verify item details
                item = cart['items'][0]
                if item['product_id'] != self.product_id:
                    self.log_result(
                        "Verify Cart Contents", 
                        False, 
                        f"Product ID mismatch in retrieved cart"
                    )
                    return False
                
                self.log_result(
                    "Verify Cart Contents", 
                    True, 
                    f"Cart retrieved successfully. Contains {len(cart['items'])} item(s), Total: ${cart['total']}"
                )
                return True
            else:
                self.log_result(
                    "Verify Cart Contents", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Verify Cart Contents", False, f"Exception: {str(e)}")
            return False

    def test_multiple_items(self):
        """Test adding multiple different items to cart"""
        print("\n🔍 Step 5: Testing multiple items in cart...")
        
        # Create second product
        product_data = {
            "name": f"Second Cart Test Product {datetime.now().strftime('%H%M%S')}",
            "description": "Second product for testing multiple items",
            "price": 19.99,
            "category": "Test Category",
            "brand": "TestBrand",
            "images": ["https://via.placeholder.com/300x300?text=Test+Product+2"],
            "inventory": 50,
            "tags": ["test", "cart", "api", "second"]
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/products", json=product_data)
            if response.status_code != 200:
                self.log_result("Test Multiple Items", False, "Failed to create second product")
                return False
            
            second_product_id = response.json()['id']
            
            # Add second product to cart
            params = {
                "product_id": second_product_id,
                "quantity": 1
            }
            
            response = self.session.post(
                f"{self.base_url}/api/cart/{self.cart_id}/items", 
                params=params
            )
            
            if response.status_code == 200:
                cart = response.json()
                
                # Verify we now have 2 items
                if len(cart['items']) != 2:
                    self.log_result(
                        "Test Multiple Items", 
                        False, 
                        f"Expected 2 items, got {len(cart['items'])}"
                    )
                    return False
                
                # Verify total calculation for multiple items
                expected_total = sum(item['price'] * item['quantity'] for item in cart['items'])
                if abs(cart['total'] - expected_total) > 0.01:
                    self.log_result(
                        "Test Multiple Items", 
                        False, 
                        f"Total calculation incorrect for multiple items. Expected: {expected_total}, Got: {cart['total']}"
                    )
                    return False
                
                self.log_result(
                    "Test Multiple Items", 
                    True, 
                    f"Multiple items added successfully. Cart contains {len(cart['items'])} items, Total: ${cart['total']}"
                )
                return True
            else:
                self.log_result(
                    "Test Multiple Items", 
                    False, 
                    f"Failed to add second item. Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Test Multiple Items", False, f"Exception: {str(e)}")
            return False

    def test_quantity_update(self):
        """Test adding same product again (should update quantity)"""
        print("\n🔍 Step 6: Testing quantity update...")
        
        try:
            # Add same product again
            params = {
                "product_id": self.product_id,
                "quantity": 1
            }
            
            response = self.session.post(
                f"{self.base_url}/api/cart/{self.cart_id}/items", 
                params=params
            )
            
            if response.status_code == 200:
                cart = response.json()
                
                # Find our original product in the cart
                original_item = None
                for item in cart['items']:
                    if item['product_id'] == self.product_id:
                        original_item = item
                        break
                
                if not original_item:
                    self.log_result(
                        "Test Quantity Update", 
                        False, 
                        "Original product not found in cart after quantity update"
                    )
                    return False
                
                # Should now have quantity 3 (2 + 1)
                if original_item['quantity'] != 3:
                    self.log_result(
                        "Test Quantity Update", 
                        False, 
                        f"Quantity not updated correctly. Expected: 3, Got: {original_item['quantity']}"
                    )
                    return False
                
                self.log_result(
                    "Test Quantity Update", 
                    True, 
                    f"Quantity updated successfully. Product {self.product_id} now has quantity: {original_item['quantity']}"
                )
                return True
            else:
                self.log_result(
                    "Test Quantity Update", 
                    False, 
                    f"Failed to update quantity. Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Test Quantity Update", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive Add to Cart functionality test"""
        print("🚀 COMPREHENSIVE ADD TO CART FUNCTIONALITY TEST")
        print("=" * 60)
        print("Focus: Backend API response structure and cart state management")
        print("=" * 60)
        
        # Run test sequence
        tests = [
            self.create_test_product,
            self.create_test_cart,
            self.add_item_to_cart,
            self.verify_cart_contents,
            self.test_multiple_items,
            self.test_quantity_update
        ]
        
        all_passed = True
        for test in tests:
            if not test():
                all_passed = False
                # Continue with other tests even if one fails
        
        # Final verification
        if self.cart_id:
            print(f"\n🔍 FINAL CART STATE VERIFICATION:")
            try:
                response = self.session.get(f"{self.base_url}/api/cart/{self.cart_id}")
                if response.status_code == 200:
                    final_cart = response.json()
                    print(f"📋 FINAL CART STRUCTURE:")
                    print(json.dumps(final_cart, indent=2, default=str))
                    
                    print(f"\n📊 FINAL CART SUMMARY:")
                    print(f"   Cart ID: {final_cart['id']}")
                    print(f"   Items Count: {len(final_cart['items'])}")
                    print(f"   Total Amount: ${final_cart['total']}")
                    print(f"   Items Array Populated: {'✅ YES' if final_cart['items'] else '❌ NO'}")
                    
                    if final_cart['items']:
                        print(f"   Items Details:")
                        for i, item in enumerate(final_cart['items'], 1):
                            print(f"     Item {i}: Product {item['product_id']}, Qty: {item['quantity']}, Price: ${item['price']}")
            except Exception as e:
                print(f"   Error getting final cart state: {e}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed_count = sum(1 for result in self.test_results if result['success'])
        total_count = len(self.test_results)
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {result['test']}")
        
        print(f"\n📈 OVERALL RESULT: {passed_count}/{total_count} tests passed")
        
        if all_passed:
            print("🎉 ALL TESTS PASSED - Add to Cart functionality is working correctly!")
            print("✅ Backend API returns proper cart structure with populated items array")
            print("✅ Total calculation is accurate")
            print("✅ Cart state persists correctly")
        else:
            print("⚠️  SOME TESTS FAILED - Issues found in Add to Cart functionality")
            failed_tests = [r['test'] for r in self.test_results if not r['success']]
            print(f"❌ Failed tests: {', '.join(failed_tests)}")
        
        return all_passed

def main():
    tester = AddToCartTester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())