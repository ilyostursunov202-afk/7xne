import requests
import sys
import json
import time
from datetime import datetime
import uuid

class EcommerceAPITester:
    def __init__(self, base_url="https://3db9a099-f08d-4056-bd05-8842cd5b7fe1.preview.emergentagent.com"):
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
                response = self.session.put(url, json=data, params=params, headers=headers)

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

            try:
                return success, response.json() if response.text and response.status_code < 500 else {}
            except:
                return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root endpoint"""
        return self.run_test("Root Endpoint", "GET", "/", 200)[0]

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
            params={"is_active": False},
            auth_required=True
        )[0]
        
        # Test unblocking user
        success2 = self.run_test(
            "Admin Unblock User",
            "PUT",
            f"/api/admin/users/{self.user_id}/status",
            200,
            params={"is_active": True},
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
        
        # Test changing role to seller (send as query parameter)
        success1 = self.run_test(
            "Admin Change User Role to Seller",
            "PUT",
            f"/api/admin/users/{self.user_id}/role",
            200,
            params={"role": "seller"},
            auth_required=True
        )[0]
        
        # Test changing role back to customer
        success2 = self.run_test(
            "Admin Change User Role to Customer",
            "PUT",
            f"/api/admin/users/{self.user_id}/role",
            200,
            params={"role": "customer"},
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
        success1 = self.run_test(
            "Change Password",
            "PUT",
            "/api/profile/password",
            200,
            params={"old_password": "password123", "new_password": "newpassword123"},
            auth_required=True
        )[0]
        
        # Change password back for other tests
        success2 = self.run_test(
            "Change Password Back",
            "PUT",
            "/api/profile/password",
            200,
            params={"old_password": "newpassword123", "new_password": "password123"},
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
            params={"language": "ru"},
            auth_required=True
        )[0]
        
        # Test setting language back to English
        success2 = self.run_test(
            "Set Language to English",
            "PUT",
            "/api/profile/language",
            200,
            params={"language": "en"},
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

    # ENHANCED REGISTRATION AND VERIFICATION TESTS
    def test_send_email_verification(self):
        """Test sending email verification code"""
        email_data = {
            "email": "test.verification@example.com"
        }
        
        success, response = self.run_test(
            "Send Email Verification",
            "POST",
            "/api/auth/send-email-verification",
            200,
            data=email_data
        )
        
        if success and 'dev_code' in response:
            # Store the verification code for later use
            self.email_verification_code = response['dev_code']
            print(f"   Email verification code: {self.email_verification_code}")
        
        return success

    def test_verify_email_code(self):
        """Test verifying email with code"""
        if not hasattr(self, 'email_verification_code'):
            print("⚠️  Skipping email verification test - no verification code available")
            return False
        
        verify_data = {
            "email": "test.verification@example.com",
            "code": self.email_verification_code
        }
        
        return self.run_test(
            "Verify Email Code",
            "POST",
            "/api/auth/verify-email",
            200,
            data=verify_data
        )[0]

    def test_send_phone_verification(self):
        """Test sending phone verification code (mock mode)"""
        phone_data = {
            "phone": "+1234567890"
        }
        
        success, response = self.run_test(
            "Send Phone Verification",
            "POST",
            "/api/auth/send-phone-verification",
            200,
            data=phone_data
        )
        
        if success and 'dev_code' in response:
            # Store the verification code for later use
            self.phone_verification_code = response['dev_code']
            print(f"   Phone verification code: {self.phone_verification_code}")
        
        return success

    def test_verify_phone_code(self):
        """Test verifying phone with code"""
        if not hasattr(self, 'phone_verification_code'):
            print("⚠️  Skipping phone verification test - no verification code available")
            return False
        
        verify_data = {
            "phone": "+1234567890",
            "code": self.phone_verification_code
        }
        
        return self.run_test(
            "Verify Phone Code",
            "POST",
            "/api/auth/verify-phone",
            200,
            data=verify_data
        )[0]

    def test_enhanced_registration(self):
        """Test enhanced user registration with email, phone, and shipping address"""
        timestamp = str(int(time.time()))
        
        registration_data = {
            "email": f"enhanced.user.{timestamp}@example.com",
            "password": "SecurePassword123!",
            "name": "Enhanced Test User",
            "phone": f"+1555{timestamp[-6:]}",
            "role": "customer",
            "shipping_address": {
                "full_name": "Enhanced Test User",
                "address_line_1": "123 Test Street",
                "address_line_2": "Apt 4B",
                "city": "Test City",
                "state": "CA",
                "postal_code": "90210",
                "country": "US",
                "phone": f"+1555{timestamp[-6:]}",
                "is_default": True
            }
        }
        
        success, response = self.run_test(
            "Enhanced Registration",
            "POST",
            "/api/auth/register-enhanced",
            200,
            data=registration_data
        )
        
        if success:
            # Store user data for other tests
            if 'access_token' in response:
                self.enhanced_user_token = response['access_token']
                print(f"   Enhanced user registered successfully")
            
            if 'user' in response:
                self.enhanced_user_id = response['user']['id']
                self.enhanced_user_email = response['user']['email']
                print(f"   User ID: {self.enhanced_user_id}")
                print(f"   Email verified: {response['user'].get('email_verified', False)}")
                print(f"   Phone verified: {response['user'].get('phone_verified', False)}")
            
            # Check verification codes were sent
            if 'verification_sent' in response:
                verification = response['verification_sent']
                if verification.get('email') and 'dev_code' in verification['email']:
                    self.enhanced_email_code = verification['email']['dev_code']
                    print(f"   Email verification code: {self.enhanced_email_code}")
                
                if verification.get('phone') and 'dev_code' in verification['phone']:
                    self.enhanced_phone_code = verification['phone']['dev_code']
                    print(f"   Phone verification code: {self.enhanced_phone_code}")
        
        return success

    def test_enhanced_user_email_verification(self):
        """Test verifying email for enhanced registered user"""
        if not hasattr(self, 'enhanced_email_code') or not hasattr(self, 'enhanced_user_email'):
            print("⚠️  Skipping enhanced user email verification - missing data")
            return False
        
        verify_data = {
            "email": self.enhanced_user_email,
            "code": self.enhanced_email_code
        }
        
        success = self.run_test(
            "Enhanced User Email Verification",
            "POST",
            "/api/auth/verify-email",
            200,
            data=verify_data
        )[0]
        
        if success:
            # Update verification status
            self.test_update_verification_status(email_verified=True)
        
        return success

    def test_update_verification_status(self, email_verified=None, phone_verified=None):
        """Test updating user verification status"""
        if not hasattr(self, 'enhanced_user_token'):
            print("⚠️  Skipping verification status update - no enhanced user token")
            return False
        
        params = {}
        if email_verified is not None:
            params['email_verified'] = email_verified
        if phone_verified is not None:
            params['phone_verified'] = phone_verified
        
        # Set the token for this request
        old_token = self.access_token
        self.access_token = self.enhanced_user_token
        
        success = self.run_test(
            "Update Verification Status",
            "POST",
            "/api/auth/update-verification-status",
            200,
            params=params,
            auth_required=True
        )[0]
        
        # Restore original token
        self.access_token = old_token
        
        return success

    def test_forgot_password_email(self):
        """Test forgot password with email"""
        if not hasattr(self, 'enhanced_user_email'):
            # Use a test email
            test_email = "testuser@example.com"
        else:
            test_email = self.enhanced_user_email
        
        forgot_data = {
            "identifier": test_email,
            "method": "email"
        }
        
        success, response = self.run_test(
            "Forgot Password - Email",
            "POST",
            "/api/auth/forgot-password",
            200,
            data=forgot_data
        )
        
        if success and 'dev_code' in response:
            self.password_reset_code = response['dev_code']
            self.password_reset_identifier = test_email
            print(f"   Password reset code: {self.password_reset_code}")
        
        return success

    def test_reset_password(self):
        """Test password reset with verification code"""
        if not hasattr(self, 'password_reset_code') or not hasattr(self, 'password_reset_identifier'):
            print("⚠️  Skipping password reset test - no reset code available")
            return False
        
        reset_data = {
            "identifier": self.password_reset_identifier,
            "code": self.password_reset_code,
            "new_password": "NewSecurePassword123!"
        }
        
        return self.run_test(
            "Reset Password",
            "POST",
            "/api/auth/reset-password",
            200,
            data=reset_data
        )[0]

    def test_enhanced_registration_duplicate_email(self):
        """Test enhanced registration with duplicate email (should fail)"""
        registration_data = {
            "email": "testuser@example.com",  # Existing email
            "password": "SecurePassword123!",
            "name": "Duplicate Test User",
            "phone": "+1555999999",
            "role": "customer"
        }
        
        return self.run_test(
            "Enhanced Registration - Duplicate Email",
            "POST",
            "/api/auth/register-enhanced",
            400,  # Should fail with 400
            data=registration_data
        )[0]

    def test_invalid_verification_codes(self):
        """Test verification with invalid codes"""
        # Test invalid email verification
        invalid_email_data = {
            "email": "test.verification@example.com",
            "code": "000000"  # Invalid code
        }
        
        success1 = self.run_test(
            "Invalid Email Verification Code",
            "POST",
            "/api/auth/verify-email",
            400,  # Should fail
            data=invalid_email_data
        )[0]
        
        # Test invalid phone verification
        invalid_phone_data = {
            "phone": "+1234567890",
            "code": "000000"  # Invalid code
        }
        
        success2 = self.run_test(
            "Invalid Phone Verification Code",
            "POST",
            "/api/auth/verify-phone",
            400,  # Should fail
            data=invalid_phone_data
        )[0]
        
        return success1 and success2

    def test_verification_flow_complete(self):
        """Test complete verification flow: register -> verify email -> verify phone"""
        print("\n🔄 Testing Complete Enhanced Registration and Verification Flow...")
        
        timestamp = str(int(time.time()))
        
        # Step 1: Enhanced Registration
        registration_data = {
            "email": f"flow.test.{timestamp}@example.com",
            "password": "FlowTestPassword123!",
            "name": "Flow Test User",
            "phone": f"+1555{timestamp[-6:]}",
            "role": "customer",
            "shipping_address": {
                "full_name": "Flow Test User",
                "address_line_1": "456 Flow Street",
                "city": "Flow City",
                "state": "NY",
                "postal_code": "10001",
                "country": "US",
                "is_default": True
            }
        }
        
        success1, reg_response = self.run_test(
            "Flow Registration",
            "POST",
            "/api/auth/register-enhanced",
            200,
            data=registration_data
        )
        
        if not success1:
            print("❌ Registration failed - aborting flow test")
            return False
        
        # Extract verification codes
        email_code = None
        phone_code = None
        user_email = registration_data["email"]
        user_phone = registration_data["phone"]
        
        if 'verification_sent' in reg_response:
            verification = reg_response['verification_sent']
            if verification.get('email') and 'dev_code' in verification['email']:
                email_code = verification['email']['dev_code']
            if verification.get('phone') and 'dev_code' in verification['phone']:
                phone_code = verification['phone']['dev_code']
        
        print(f"   Registration successful - Email: {user_email}, Phone: {user_phone}")
        print(f"   Email code: {email_code}, Phone code: {phone_code}")
        
        # Step 2: Verify Email
        success2 = True
        if email_code:
            verify_email_data = {
                "email": user_email,
                "code": email_code
            }
            
            success2, _ = self.run_test(
                "Flow Email Verification",
                "POST",
                "/api/auth/verify-email",
                200,
                data=verify_email_data
            )
        
        # Step 3: Verify Phone
        success3 = True
        if phone_code:
            verify_phone_data = {
                "phone": user_phone,
                "code": phone_code
            }
            
            success3, _ = self.run_test(
                "Flow Phone Verification",
                "POST",
                "/api/auth/verify-phone",
                200,
                data=verify_phone_data
            )
        
        # Overall success
        flow_success = success1 and success2 and success3
        
        if flow_success:
            print("✅ Complete enhanced registration and verification flow test passed!")
            self.tests_passed += 1
        else:
            print("❌ Enhanced registration and verification flow test failed!")
        
        return flow_success

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
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    # Admin Panel Extension test summary
    print("\n🔍 ADMIN PANEL EXTENSION FUNCTIONALITY SUMMARY:")
    print("   - Admin Authentication: ✅ if admin login test passed")
    print("   - Enhanced User Management:")
    print("     • User Search & Filter: ✅ if search tests passed")
    print("     • Block/Unblock Users: ✅ if status update tests passed")
    print("     • Change User Roles: ✅ if role update tests passed")
    print("   - Admin Statistics: ✅ if statistics endpoint test passed")
    print("   - Action Logging: ✅ if action logs tests passed")
    print("   - Enhanced Profile Management:")
    print("     • Get/Update Profile: ✅ if profile tests passed")
    print("     • Change Password: ✅ if password change tests passed")
    print("     • Language Preference: ✅ if language tests passed")
    print("     • Avatar Upload: ✅ if avatar tests passed")
    print("   - Existing Functionality: ✅ if wishlist and other tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())