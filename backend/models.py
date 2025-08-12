from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from enum import Enum

# Enhanced User Models with Seller Support
class UserRole(str, Enum):
    CUSTOMER = "customer"
    SELLER = "seller"
    ADMIN = "admin"

class SellerApplication(BaseModel):
    business_name: str
    business_description: str
    business_email: str
    business_phone: str
    business_address: Dict[str, str]
    tax_id: Optional[str] = None
    website: Optional[str] = None
    social_media: Optional[Dict[str, str]] = {}

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    seller_application: Optional[SellerApplication] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    avatar: Optional[str] = None
    role: UserRole
    created_at: datetime
    is_active: bool = True

class UserInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    hashed_password: str
    name: str
    phone: Optional[str] = None
    avatar: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    addresses: List[Dict[str, Any]] = []

# Address Models
class Address(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "home"  # home, work, other
    name: str
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool = False

# Token Models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

# Product Models (Enhanced)
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    brand: str
    images: List[str] = []
    inventory: int
    tags: List[str] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    images: Optional[List[str]] = None
    inventory: Optional[int] = None
    tags: Optional[List[str]] = None

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    price: float
    category: str
    brand: str
    images: List[str] = []
    inventory: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    tags: List[str] = []
    ai_generated_description: Optional[str] = None
    seller_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

# Review Models
class ReviewCreate(BaseModel):
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str
    
class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    user_id: str
    rating: int
    comment: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_approved: bool = True

class ReviewResponse(BaseModel):
    id: str
    product_id: str
    user_name: str
    rating: int
    comment: str
    created_at: datetime
    is_approved: bool

# Wishlist Models
class WishlistItem(BaseModel):
    product_id: str
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Wishlist(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[WishlistItem] = []
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Order Models (Enhanced)
class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class OrderItem(BaseModel):
    product_id: str
    seller_id: Optional[str] = None
    quantity: int
    price: float
    product_name: str
    
class OrderCreate(BaseModel):
    items: List[OrderItem]
    shipping_address: Address
    total_amount: float
    
class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    items: List[OrderItem]
    total_amount: float
    shipping_address: Address
    status: OrderStatus = OrderStatus.PENDING
    payment_session_id: Optional[str] = None
    tracking_number: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Cart Models (Enhanced)
class CartItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class Cart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    items: List[CartItem] = []
    total: float = 0.0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Coupon Models
class CouponType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"

class CouponCreate(BaseModel):
    code: str
    type: CouponType
    value: float  # percentage (0-100) or fixed amount
    min_order_amount: Optional[float] = None
    max_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True

class Coupon(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    type: CouponType
    value: float
    min_order_amount: Optional[float] = None
    max_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    used_count: int = 0
    expires_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Payment Transaction (Enhanced)
class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    order_id: Optional[str] = None
    user_id: Optional[str] = None
    amount: float
    currency: str = "usd"
    status: str = "pending"  # pending, paid, failed, expired
    payment_status: str = "unpaid"
    coupon_code: Optional[str] = None
    discount_amount: Optional[float] = 0.0
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Seller Models
class SellerProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    business_name: str
    business_description: Optional[str] = None
    business_address: Optional[Address] = None
    commission_rate: float = 10.0  # percentage
    total_sales: float = 0.0
    total_commission: float = 0.0
    is_verified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SellerProfileCreate(BaseModel):
    business_name: str
    business_description: Optional[str] = None
    business_address: Optional[Address] = None

class SellerStats(BaseModel):
    total_products: int
    total_sales: float
    total_orders: int
    average_rating: float
    commission_earned: float