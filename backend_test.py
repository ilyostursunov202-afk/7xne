import requests
import sys
import json
from datetime import datetime
import uuid

class EcommerceAPITester:
    def __init__(self, base_url="https://d80afeaf-a107-473e-99e9-b5d4d91b17c9.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.cart_id = None
        self.product_id = None
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {method} {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params)
            elif method == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method == 'DELETE':
                response = self.session.delete(url)
            elif method == 'PUT':
                response = self.session.put(url, json=data)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(response_data) > 0:
                        print(f"   Response keys: {list(response_data.keys())}")
                    elif isinstance(response_data, list) and len(response_data) > 0:
                        print(f"   Response: List with {len(response_data)} items")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            return success, response.json() if response.text and response.status_code < 500 else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root endpoint"""
        return self.run_test("Root Endpoint", "GET", "/", 200)

    def test_create_product(self):
        """Test creating a product"""
        product_data = {
            "name": f"Test Product {datetime.now().strftime('%H%M%S')}",
            "description": "A test product for API testing",
            "price": 29.99,
            "category": "Electronics",
            "brand": "TestBrand",
            "images": ["https://via.placeholder.com/300"],
            "inventory": 10,
            "tags": ["test", "electronics"]
        }
        
        success, response = self.run_test(
            "Create Product",
            "POST",
            "/api/products",
            200,
            data=product_data
        )
        
        if success and 'id' in response:
            self.product_id = response['id']
            print(f"   Created product ID: {self.product_id}")
        
        return success

    def test_get_products(self):
        """Test getting products list"""
        return self.run_test("Get Products", "GET", "/api/products", 200)

    def test_get_products_with_filters(self):
        """Test getting products with filters"""
        params = {
            "category": "Electronics",
            "limit": 5
        }
        return self.run_test("Get Products with Filters", "GET", "/api/products", 200, params=params)

    def test_search_products(self):
        """Test product search"""
        params = {
            "search": "test",
            "limit": 5
        }
        return self.run_test("Search Products", "GET", "/api/products", 200, params=params)

    def test_get_product_detail(self):
        """Test getting product details"""
        if not self.product_id:
            print("⚠️  Skipping product detail test - no product ID available")
            return False
            
        return self.run_test(
            "Get Product Detail",
            "GET",
            f"/api/products/{self.product_id}",
            200
        )

    def test_get_product_recommendations(self):
        """Test getting product recommendations"""
        if not self.product_id:
            print("⚠️  Skipping recommendations test - no product ID available")
            return False
            
        return self.run_test(
            "Get Product Recommendations",
            "GET",
            f"/api/products/{self.product_id}/recommendations",
            200
        )

    def test_create_cart(self):
        """Test creating a cart"""
        success, response = self.run_test("Create Cart", "POST", "/api/cart", 200)
        
        if success and 'id' in response:
            self.cart_id = response['id']
            print(f"   Created cart ID: {self.cart_id}")
        
        return success

    def test_get_cart(self):
        """Test getting cart details"""
        if not self.cart_id:
            print("⚠️  Skipping get cart test - no cart ID available")
            return False
            
        return self.run_test("Get Cart", "GET", f"/api/cart/{self.cart_id}", 200)

    def test_add_to_cart(self):
        """Test adding item to cart"""
        if not self.cart_id or not self.product_id:
            print("⚠️  Skipping add to cart test - missing cart or product ID")
            return False
            
        params = {
            "product_id": self.product_id,
            "quantity": 2
        }
        
        return self.run_test(
            "Add to Cart",
            "POST",
            f"/api/cart/{self.cart_id}/items",
            200,
            params=params
        )

    def test_remove_from_cart(self):
        """Test removing item from cart"""
        if not self.cart_id or not self.product_id:
            print("⚠️  Skipping remove from cart test - missing cart or product ID")
            return False
            
        return self.run_test(
            "Remove from Cart",
            "DELETE",
            f"/api/cart/{self.cart_id}/items/{self.product_id}",
            200
        )

    def test_get_categories(self):
        """Test getting categories"""
        return self.run_test("Get Categories", "GET", "/api/categories", 200)

    def test_get_brands(self):
        """Test getting brands"""
        return self.run_test("Get Brands", "GET", "/api/brands", 200)

    def test_checkout_session_creation(self):
        """Test creating checkout session (without completing payment)"""
        if not self.cart_id:
            print("⚠️  Skipping checkout test - no cart ID available")
            return False
            
        # First add an item to cart for checkout
        if self.product_id:
            params = {"product_id": self.product_id, "quantity": 1}
            self.session.post(f"{self.base_url}/api/cart/{self.cart_id}/items", params=params)
        
        checkout_data = {
            "cart_id": self.cart_id,
            "origin_url": "https://test.example.com"
        }
        
        success, response = self.run_test(
            "Create Checkout Session",
            "POST",
            "/api/checkout/session",
            200,
            data=checkout_data
        )
        
        if success and 'url' in response:
            print(f"   Stripe checkout URL created: {response['url'][:50]}...")
        
        return success

    def test_get_orders(self):
        """Test getting orders"""
        return self.run_test("Get Orders", "GET", "/api/orders", 200)

def main():
    print("🚀 Starting E-commerce API Tests")
    print("=" * 50)
    
    tester = EcommerceAPITester()
    
    # Test sequence
    test_methods = [
        tester.test_root_endpoint,
        tester.test_create_product,
        tester.test_get_products,
        tester.test_get_products_with_filters,
        tester.test_search_products,
        tester.test_get_product_detail,
        tester.test_get_product_recommendations,
        tester.test_get_categories,
        tester.test_get_brands,
        tester.test_create_cart,
        tester.test_get_cart,
        tester.test_add_to_cart,
        tester.test_get_cart,  # Test cart after adding item
        tester.test_remove_from_cart,
        tester.test_checkout_session_creation,
        tester.test_get_orders
    ]
    
    # Run all tests
    for test_method in test_methods:
        try:
            test_method()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            tester.tests_run += 1
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())