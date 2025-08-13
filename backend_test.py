import requests
import sys
import json
from datetime import datetime
import uuid

class EcommerceAPITester:
    def __init__(self, base_url="https://shopfix-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.cart_id = None
        self.product_id = None
        self.access_token = None
        self.admin_token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, auth_required=False):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {method} {url}")
        
        # Set authorization header if auth is required and we have a token
        headers = {}
        if auth_required:
            # Use admin token if available, otherwise use regular token
            token = self.admin_token if hasattr(self, 'admin_token') and self.admin_token else self.access_token
            if token:
                headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)

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
        return self.run_test("Get Orders", "GET", "/api/orders", 200, auth_required=True)

    def test_user_login(self):
        """Test user authentication with testuser@example.com"""
        login_data = {
            "email": "testuser@example.com",
            "password": "password123"
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "/api/auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.access_token = response['access_token']
            print(f"   Login successful - Token obtained")
            
            # Get user info to get user_id
            user_success, user_response = self.run_test(
                "Get Current User Info",
                "GET",
                "/api/auth/me",
                200,
                auth_required=True
            )
            
            if user_success and 'id' in user_response:
                self.user_id = user_response['id']
                print(f"   User ID: {self.user_id}")
        
        return success

    def test_get_wishlist(self):
        """Test getting user's wishlist"""
        if not self.access_token:
            print("⚠️  Skipping wishlist test - not authenticated")
            return False
            
        return self.run_test(
            "Get User Wishlist",
            "GET",
            "/api/wishlist",
            200,
            auth_required=True
        )

    def test_add_to_wishlist(self):
        """Test adding product to wishlist"""
        if not self.access_token or not self.product_id:
            print("⚠️  Skipping add to wishlist test - missing auth or product ID")
            return False
            
        return self.run_test(
            "Add Product to Wishlist",
            "POST",
            f"/api/wishlist/add/{self.product_id}",
            200,
            auth_required=True
        )

    def test_remove_from_wishlist(self):
        """Test removing product from wishlist"""
        if not self.access_token or not self.product_id:
            print("⚠️  Skipping remove from wishlist test - missing auth or product ID")
            return False
            
        return self.run_test(
            "Remove Product from Wishlist",
            "DELETE",
            f"/api/wishlist/remove/{self.product_id}",
            200,
            auth_required=True
        )

    def test_wishlist_flow(self):
        """Test complete wishlist flow: add -> verify -> remove -> verify"""
        print("\n🔄 Testing Complete Wishlist Flow...")
        
        if not self.access_token or not self.product_id:
            print("⚠️  Skipping wishlist flow test - missing auth or product ID")
            return False
        
        # Step 1: Get initial wishlist
        success1, initial_wishlist = self.run_test(
            "Get Initial Wishlist",
            "GET",
            "/api/wishlist",
            200,
            auth_required=True
        )
        
        initial_count = len(initial_wishlist.get('wishlist', {}).get('items', [])) if success1 else 0
        print(f"   Initial wishlist items: {initial_count}")
        
        # Step 2: Add product to wishlist
        success2, add_response = self.run_test(
            "Add to Wishlist (Flow)",
            "POST",
            f"/api/wishlist/add/{self.product_id}",
            200,
            auth_required=True
        )
        
        # Step 3: Verify product was added
        success3, updated_wishlist = self.run_test(
            "Verify Product Added",
            "GET",
            "/api/wishlist",
            200,
            auth_required=True
        )
        
        added_count = len(updated_wishlist.get('wishlist', {}).get('items', [])) if success3 else 0
        print(f"   Wishlist items after add: {added_count}")
        
        # Check if product is in wishlist
        product_in_wishlist = False
        if success3 and 'wishlist' in updated_wishlist:
            items = updated_wishlist['wishlist'].get('items', [])
            product_in_wishlist = any(item.get('product_id') == self.product_id for item in items)
            print(f"   Product {self.product_id} in wishlist: {product_in_wishlist}")
        
        # Step 4: Remove product from wishlist
        success4, remove_response = self.run_test(
            "Remove from Wishlist (Flow)",
            "DELETE",
            f"/api/wishlist/remove/{self.product_id}",
            200,
            auth_required=True
        )
        
        # Step 5: Verify product was removed
        success5, final_wishlist = self.run_test(
            "Verify Product Removed",
            "GET",
            "/api/wishlist",
            200,
            auth_required=True
        )
        
        final_count = len(final_wishlist.get('wishlist', {}).get('items', [])) if success5 else 0
        print(f"   Final wishlist items: {final_count}")
        
        # Check if product is no longer in wishlist
        product_removed = True
        if success5 and 'wishlist' in final_wishlist:
            items = final_wishlist['wishlist'].get('items', [])
            product_removed = not any(item.get('product_id') == self.product_id for item in items)
            print(f"   Product {self.product_id} removed from wishlist: {product_removed}")
        
        # Overall success
        flow_success = all([success1, success2, success3, success4, success5, product_in_wishlist, product_removed])
        
        if flow_success:
            print("✅ Complete wishlist flow test passed!")
            self.tests_passed += 1
        else:
            print("❌ Wishlist flow test failed!")
        
        return flow_success

    # NEW ADMIN PANEL TESTS
    def test_admin_login(self):
        """Test admin authentication"""
        login_data = {
            "email": "admin@marketplace.com",
            "password": "admin123"
        }
        
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "/api/auth/login",
            200,
            data=login_data
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"   Admin login successful - Token obtained")
        
        return success

    def test_admin_user_search(self):
        """Test admin user search functionality"""
        if not hasattr(self, 'admin_token') or not self.admin_token:
            print("⚠️  Skipping admin user search test - not authenticated as admin")
            return False
        
        # Test basic search
        success1 = self.run_test(
            "Admin User Search - All Users",
            "GET",
            "/api/admin/users/search",
            200,
            auth_required=True
        )[0]
        
        # Test search with query
        params = {"q": "test", "limit": 10}
        success2 = self.run_test(
            "Admin User Search - With Query",
            "GET",
            "/api/admin/users/search",
            200,
            params=params,
            auth_required=True
        )[0]
        
        # Test search with role filter
        params = {"role": "customer", "limit": 10}
        success3 = self.run_test(
            "Admin User Search - Role Filter",
            "GET",
            "/api/admin/users/search",
            200,
            params=params,
            auth_required=True
        )[0]
        
        # Test search with status filter
        params = {"status": "active", "limit": 10}
        success4 = self.run_test(
            "Admin User Search - Status Filter",
            "GET",
            "/api/admin/users/search",
            200,
            params=params,
            auth_required=True
        )[0]
        
        return all([success1, success2, success3, success4])

    def test_admin_user_status_update(self):
        """Test admin user status update (block/unblock)"""
        if not hasattr(self, 'admin_token') or not self.admin_token:
            print("⚠️  Skipping admin user status test - not authenticated as admin")
            return False
        
        if not self.user_id:
            print("⚠️  Skipping admin user status test - no regular user ID available")
            return False
        
        # Test blocking user
        success1 = self.run_test(
            "Admin Block User",
            "PUT",
            f"/api/admin/users/{self.user_id}/status",
            200,
            data={"is_active": False},
            auth_required=True
        )[0]
        
        # Test unblocking user
        success2 = self.run_test(
            "Admin Unblock User",
            "PUT",
            f"/api/admin/users/{self.user_id}/status",
            200,
            data={"is_active": True},
            auth_required=True
        )[0]
        
        return success1 and success2

    def test_admin_user_role_update(self):
        """Test admin user role update"""
        if not hasattr(self, 'admin_token') or not self.admin_token:
            print("⚠️  Skipping admin user role test - not authenticated as admin")
            return False
        
        if not self.user_id:
            print("⚠️  Skipping admin user role test - no regular user ID available")
            return False
        
        # Test changing role to seller
        success1 = self.run_test(
            "Admin Change User Role to Seller",
            "PUT",
            f"/api/admin/users/{self.user_id}/role",
            200,
            data={"role": "seller"},
            auth_required=True
        )[0]
        
        # Test changing role back to customer
        success2 = self.run_test(
            "Admin Change User Role to Customer",
            "PUT",
            f"/api/admin/users/{self.user_id}/role",
            200,
            data={"role": "customer"},
            auth_required=True
        )[0]
        
        return success1 and success2

    def test_admin_statistics(self):
        """Test admin statistics endpoint"""
        if not hasattr(self, 'admin_token') or not self.admin_token:
            print("⚠️  Skipping admin statistics test - not authenticated as admin")
            return False
        
        success, response = self.run_test(
            "Admin Statistics",
            "GET",
            "/api/admin/statistics",
            200,
            auth_required=True
        )
        
        if success:
            expected_keys = ['user_stats', 'order_stats', 'product_stats', 'top_products', 'recent_orders', 'website_stats']
            has_all_keys = all(key in response for key in expected_keys)
            if has_all_keys:
                print(f"   ✅ Statistics response contains all expected sections")
            else:
                print(f"   ⚠️  Missing some expected keys in statistics response")
        
        return success

    def test_admin_action_logs(self):
        """Test admin action logs endpoint"""
        if not hasattr(self, 'admin_token') or not self.admin_token:
            print("⚠️  Skipping admin action logs test - not authenticated as admin")
            return False
        
        # Test getting all action logs
        success1 = self.run_test(
            "Admin Action Logs - All",
            "GET",
            "/api/admin/action-logs",
            200,
            auth_required=True
        )[0]
        
        # Test getting action logs with filter
        params = {"action_type": "user_status_update", "limit": 10}
        success2 = self.run_test(
            "Admin Action Logs - Filtered",
            "GET",
            "/api/admin/action-logs",
            200,
            params=params,
            auth_required=True
        )[0]
        
        return success1 and success2

    def test_profile_management(self):
        """Test profile management endpoints"""
        if not self.access_token:
            print("⚠️  Skipping profile management test - not authenticated")
            return False
        
        # Test get profile
        success1, profile = self.run_test(
            "Get User Profile",
            "GET",
            "/api/profile",
            200,
            auth_required=True
        )
        
        # Test update profile
        profile_data = {
            "name": "Updated Test User",
            "phone": "+1234567890"
        }
        success2 = self.run_test(
            "Update User Profile",
            "PUT",
            "/api/profile",
            200,
            data=profile_data,
            auth_required=True
        )[0]
        
        return success1 and success2

    def test_password_change(self):
        """Test password change endpoint"""
        if not self.access_token:
            print("⚠️  Skipping password change test - not authenticated")
            return False
        
        # Test password change
        password_data = {
            "old_password": "password123",
            "new_password": "newpassword123"
        }
        success1 = self.run_test(
            "Change Password",
            "PUT",
            "/api/profile/password",
            200,
            data=password_data,
            auth_required=True
        )[0]
        
        # Change password back for other tests
        password_data_back = {
            "old_password": "newpassword123",
            "new_password": "password123"
        }
        success2 = self.run_test(
            "Change Password Back",
            "PUT",
            "/api/profile/password",
            200,
            data=password_data_back,
            auth_required=True
        )[0]
        
        return success1 and success2

    def test_language_preference(self):
        """Test language preference update"""
        if not self.access_token:
            print("⚠️  Skipping language preference test - not authenticated")
            return False
        
        # Test setting language to Russian
        success1 = self.run_test(
            "Set Language to Russian",
            "PUT",
            "/api/profile/language",
            200,
            data={"language": "ru"},
            auth_required=True
        )[0]
        
        # Test setting language back to English
        success2 = self.run_test(
            "Set Language to English",
            "PUT",
            "/api/profile/language",
            200,
            data={"language": "en"},
            auth_required=True
        )[0]
        
        return success1 and success2

    def test_avatar_upload_error_handling(self):
        """Test avatar upload error handling (without actual file)"""
        if not self.access_token:
            print("⚠️  Skipping avatar upload test - not authenticated")
            return False
        
        # This will test the endpoint exists but expect an error since we're not sending a file
        success, response = self.run_test(
            "Avatar Upload Error Handling",
            "POST",
            "/api/profile/avatar",
            422,  # Expect validation error for missing file
            auth_required=True
        )
        
        return success

    def test_avatar_file_serving(self):
        """Test avatar file serving endpoint"""
        # Test with a non-existent file (should return 404)
        success = self.run_test(
            "Avatar File Serving - Not Found",
            "GET",
            "/api/uploads/avatars/nonexistent.jpg",
            404
        )[0]
        
        return success

def main():
    print("🚀 Starting E-commerce API Tests - Admin Panel Extension Focus")
    print("=" * 70)
    
    tester = EcommerceAPITester()
    
    # Test sequence - Admin Panel Extension focused
    test_methods = [
        # Basic functionality tests
        tester.test_root_endpoint,
        tester.test_create_product,
        tester.test_get_products,
        tester.test_get_categories,
        tester.test_get_brands,
        tester.test_create_cart,
        tester.test_get_cart,
        tester.test_add_to_cart,
        tester.test_remove_from_cart,
        
        # Regular user authentication and profile tests
        tester.test_user_login,
        tester.test_profile_management,
        tester.test_password_change,
        tester.test_language_preference,
        tester.test_avatar_upload_error_handling,
        tester.test_avatar_file_serving,
        
        # Admin authentication and new admin panel tests
        tester.test_admin_login,
        tester.test_admin_user_search,
        tester.test_admin_user_status_update,
        tester.test_admin_user_role_update,
        tester.test_admin_statistics,
        tester.test_admin_action_logs,
        
        # Wishlist tests (existing functionality)
        tester.test_get_wishlist,
        tester.test_add_to_wishlist,
        tester.test_remove_from_wishlist,
        tester.test_wishlist_flow,
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
    
    # Specific wishlist test summary
    print("\n🔍 WISHLIST FUNCTIONALITY SUMMARY:")
    print("   - User Authentication: ✅ if login test passed")
    print("   - Get Wishlist: ✅ if wishlist retrieval worked")
    print("   - Add to Wishlist: ✅ if product addition worked")
    print("   - Remove from Wishlist: ✅ if product removal worked")
    print("   - Complete Flow: ✅ if full add/remove cycle worked")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())