from fastapi import FastAPI, HTTPException, Request, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import os
import uuid
import json
import asyncio
from dotenv import load_dotenv

# Import our custom modules
from models import *
from auth import AuthManager, get_current_user, get_current_user_required, get_admin_user, get_seller_user

# Import AI and Stripe integrations
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Load environment variables
load_dotenv()

app = FastAPI(title="E-commerce API", description="Advanced E-commerce Platform with AI", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client["ecommerce"]

# Collections
users_collection = db["users"]
products_collection = db["products"]
orders_collection = db["orders"]
cart_collection = db["cart"]
reviews_collection = db["reviews"]
wishlist_collection = db["wishlist"]
coupons_collection = db["coupons"]
seller_profiles_collection = db["seller_profiles"]
payment_transactions_collection = db["payment_transactions"]
search_collection = db["search_queries"]

# Stripe integration
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")
stripe_checkout = None

# AI integration
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")
auth_manager = AuthManager()

# Helper Functions
async def generate_product_description(product_name: str, category: str, brand: str) -> str:
    """Generate AI-powered product description"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"product_desc_{str(uuid.uuid4())}",
            system_message="You are an expert product copywriter. Create engaging, detailed product descriptions that highlight benefits and features. Keep descriptions under 200 words and include key selling points."
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(
            text=f"Create a compelling product description for: {product_name} by {brand} in the {category} category. Focus on benefits, features, and what makes it special."
        )
        
        description = await chat.send_message(user_message)
        return description.strip()
    except Exception as e:
        return f"High-quality {product_name} from {brand}. Perfect for {category} enthusiasts."

async def smart_search(query: str, products: List[dict]) -> List[dict]:
    """AI-powered smart search"""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"search_{str(uuid.uuid4())}",
            system_message="You are a smart search assistant. Given a search query and list of products, return the product IDs that best match the query in order of relevance. Return only a JSON array of product IDs."
        ).with_model("openai", "gpt-4o")
        
        products_info = [{"id": p["id"], "name": p["name"], "description": p.get("description", ""), "category": p.get("category", ""), "brand": p.get("brand", ""), "tags": p.get("tags", [])} for p in products]
        
        user_message = UserMessage(
            text=f"Search query: '{query}'\n\nProducts: {json.dumps(products_info)}\n\nReturn only a JSON array of product IDs that match the query, ordered by relevance."
        )
        
        response = await chat.send_message(user_message)
        try:
            relevant_ids = json.loads(response.strip())
            return [p for p in products if p["id"] in relevant_ids]
        except:
            return products[:10]  # Fallback to first 10
    except Exception as e:
        return products[:10]

async def get_recommendations(user_id: Optional[str] = None, product_id: Optional[str] = None) -> List[str]:
    """Generate product recommendations"""
    try:
        context = ""
        if user_id:
            orders = list(orders_collection.find({"user_id": user_id}).sort("created_at", -1).limit(5))
            if orders:
                purchased_products = []
                for order in orders:
                    for item in order.get("items", []):
                        product = products_collection.find_one({"id": item["product_id"]})
                        if product:
                            purchased_products.append(f"{product['name']} ({product['category']})")
                context = f"User's recent purchases: {', '.join(purchased_products)}"
        
        if product_id:
            product = products_collection.find_one({"id": product_id})
            if product:
                context += f" Current product: {product['name']} in {product['category']} category"
        
        all_products = list(products_collection.find({"is_active": True}).limit(20))
        products_info = [{"id": p["id"], "name": p["name"], "category": p.get("category", ""), "brand": p.get("brand", ""), "price": p.get("price", 0)} for p in all_products]
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"recommendations_{str(uuid.uuid4())}",
            system_message="You are a product recommendation engine. Based on user context and available products, recommend 4-6 relevant products. Return only a JSON array of product IDs."
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(
            text=f"Context: {context}\n\nAvailable products: {json.dumps(products_info)}\n\nRecommend 4-6 products that would interest this user. Return only a JSON array of product IDs."
        )
        
        response = await chat.send_message(user_message)
        try:
            return json.loads(response.strip())
        except:
            return [p["id"] for p in all_products[:6]]
    except Exception as e:
        return []

def calculate_average_rating(product_id: str) -> tuple[float, int]:
    """Calculate average rating and review count for a product"""
    reviews = list(reviews_collection.find({"product_id": product_id, "is_approved": True}))
    if not reviews:
        return 0.0, 0
    
    total_rating = sum(review["rating"] for review in reviews)
    avg_rating = total_rating / len(reviews)
    return round(avg_rating, 1), len(reviews)

def apply_coupon(cart_total: float, coupon_code: str) -> tuple[float, str]:
    """Apply coupon discount to cart total"""
    try:
        coupon = coupons_collection.find_one({
            "code": coupon_code,
            "is_active": True
        })
        
        if not coupon:
            return 0.0, "Invalid coupon code"
        
        # Check expiry
        if coupon.get("expires_at") and datetime.now(timezone.utc) > coupon["expires_at"]:
            return 0.0, "Coupon has expired"
        
        # Check usage limit
        if coupon.get("usage_limit") and coupon.get("used_count", 0) >= coupon["usage_limit"]:
            return 0.0, "Coupon usage limit exceeded"
        
        # Check minimum order amount
        if coupon.get("min_order_amount") and cart_total < coupon["min_order_amount"]:
            return 0.0, f"Minimum order amount ${coupon['min_order_amount']:.2f} required"
        
        # Calculate discount
        if coupon["type"] == "percentage":
            discount = cart_total * (coupon["value"] / 100)
            if coupon.get("max_discount"):
                discount = min(discount, coupon["max_discount"])
        else:  # fixed
            discount = coupon["value"]
        
        discount = min(discount, cart_total)  # Don't exceed cart total
        return discount, "Coupon applied successfully"
        
    except Exception as e:
        return 0.0, "Error applying coupon"

# API Routes

@app.get("/")
async def root():
    return {"message": "Advanced E-commerce API is running!", "version": "2.0.0"}

# Authentication Routes
@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    try:
        # Check if user already exists
        existing_user = users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        hashed_password = auth_manager.get_password_hash(user_data.password)
        
        # Create user
        user_dict = UserInDB(
            email=user_data.email,
            hashed_password=hashed_password,
            name=user_data.name,
            phone=user_data.phone,
            role=user_data.role
        ).dict()
        
        users_collection.insert_one(user_dict)
        
        # Remove password from response
        user_dict.pop("hashed_password", None)
        user_dict.pop("_id", None)
        
        return UserResponse(**user_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login", response_model=Token)
async def login_user(user_data: UserLogin):
    try:
        # Find user
        user = users_collection.find_one({"email": user_data.email})
        if not user or not auth_manager.verify_password(user_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Create tokens
        access_token = auth_manager.create_access_token(
            data={"sub": user["id"], "email": user["email"], "role": user["role"]}
        )
        refresh_token = auth_manager.create_refresh_token(
            data={"sub": user["id"], "email": user["email"]}
        )
        
        return Token(access_token=access_token, refresh_token=refresh_token)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user_required)):
    try:
        user = users_collection.find_one({"id": current_user["user_id"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.pop("hashed_password", None)
        user.pop("_id", None)
        
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/auth/profile", response_model=UserResponse)
async def update_user_profile(user_update: UserUpdate, current_user = Depends(get_current_user_required)):
    try:
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        users_collection.update_one(
            {"id": current_user["user_id"]},
            {"$set": update_data}
        )
        
        updated_user = users_collection.find_one({"id": current_user["user_id"]})
        updated_user.pop("hashed_password", None)
        updated_user.pop("_id", None)
        
        return UserResponse(**updated_user)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Product Routes (Enhanced)
@app.post("/api/products", response_model=Product)
async def create_product(product: ProductCreate, current_user = Depends(get_current_user)):
    try:
        # Generate AI description
        ai_description = await generate_product_description(
            product.name, product.category, product.brand
        )
        
        product_data = product.dict()
        product_data["id"] = str(uuid.uuid4())
        product_data["ai_generated_description"] = ai_description
        product_data["created_at"] = datetime.now(timezone.utc)
        product_data["updated_at"] = datetime.now(timezone.utc)
        product_data["rating"] = 0.0
        product_data["reviews_count"] = 0
        product_data["is_active"] = True
        
        # Add seller_id if user is logged in
        if current_user:
            product_data["seller_id"] = current_user["user_id"]
        
        products_collection.insert_one(product_data)
        return Product(**product_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products", response_model=List[Product])
async def get_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    seller_id: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc"),
    limit: int = Query(20),
    current_user = Depends(get_current_user)
):
    try:
        # Build filter query
        filter_query = {"is_active": True}
        if category and category != "all":
            filter_query["category"] = {"$regex": category, "$options": "i"}
        if brand and brand != "all":
            filter_query["brand"] = {"$regex": brand, "$options": "i"}
        if seller_id:
            filter_query["seller_id"] = seller_id
        if min_price is not None or max_price is not None:
            price_filter = {}
            if min_price is not None:
                price_filter["$gte"] = min_price
            if max_price is not None:
                price_filter["$lte"] = max_price
            filter_query["price"] = price_filter
        
        # Get products
        sort_direction = -1 if sort_order == "desc" else 1
        products = list(products_collection.find(filter_query).sort(sort_by, sort_direction).limit(limit))
        
        # Convert MongoDB _id to string and remove it
        for product in products:
            product.pop("_id", None)
            # Update rating and review count
            avg_rating, review_count = calculate_average_rating(product["id"])
            product["rating"] = avg_rating
            product["reviews_count"] = review_count
        
        # Apply AI-powered search if search query provided
        if search:
            # Store search query for analytics
            search_collection.insert_one({
                "query": search,
                "results_count": len(products),
                "user_id": current_user["user_id"] if current_user else None,
                "timestamp": datetime.now(timezone.utc)
            })
            
            # Apply smart search
            products = await smart_search(search, products)
        
        return products
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    try:
        product = products_collection.find_one({"id": product_id, "is_active": True})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product.pop("_id", None)
        
        # Update rating and review count
        avg_rating, review_count = calculate_average_rating(product_id)
        product["rating"] = avg_rating
        product["reviews_count"] = review_count
        
        return Product(**product)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate, current_user = Depends(get_current_user_required)):
    try:
        # Check if product exists
        existing_product = products_collection.find_one({"id": product_id, "is_active": True})
        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if user owns the product or is admin
        if (existing_product.get("seller_id") != current_user["user_id"] and 
            current_user.get("role") != "admin"):
            raise HTTPException(status_code=403, detail="Not authorized to update this product")
        
        # Generate AI description if name, category, or brand changed
        update_data = {k: v for k, v in product_update.dict().items() if v is not None}
        
        ai_description = existing_product.get("ai_generated_description")
        if (update_data.get("name") != existing_product.get("name") or
            update_data.get("category") != existing_product.get("category") or
            update_data.get("brand") != existing_product.get("brand")):
            
            name = update_data.get("name", existing_product.get("name"))
            category = update_data.get("category", existing_product.get("category"))
            brand = update_data.get("brand", existing_product.get("brand"))
            ai_description = await generate_product_description(name, category, brand)
        
        update_data["ai_generated_description"] = ai_description
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        # Update in database
        products_collection.update_one(
            {"id": product_id},
            {"$set": update_data}
        )
        
        # Get updated product
        updated_product = products_collection.find_one({"id": product_id})
        updated_product.pop("_id", None)
        
        # Update rating and review count
        avg_rating, review_count = calculate_average_rating(product_id)
        updated_product["rating"] = avg_rating
        updated_product["reviews_count"] = review_count
        
        return Product(**updated_product)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str, current_user = Depends(get_current_user_required)):
    try:
        # Check if product exists
        existing_product = products_collection.find_one({"id": product_id, "is_active": True})
        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if user owns the product or is admin
        if (existing_product.get("seller_id") != current_user["user_id"] and 
            current_user.get("role") != "admin"):
            raise HTTPException(status_code=403, detail="Not authorized to delete this product")
        
        # Soft delete product
        products_collection.update_one(
            {"id": product_id},
            {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return {"message": "Product deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}/recommendations")
async def get_product_recommendations(product_id: str, current_user = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"] if current_user else None
        recommended_ids = await get_recommendations(user_id=user_id, product_id=product_id)
        
        recommended_products = []
        for rec_id in recommended_ids[:6]:
            product = products_collection.find_one({"id": rec_id, "is_active": True})
            if product:
                product.pop("_id", None)
                # Update rating and review count
                avg_rating, review_count = calculate_average_rating(rec_id)
                product["rating"] = avg_rating
                product["reviews_count"] = review_count
                recommended_products.append(product)
        
        return {"recommendations": recommended_products}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Review Routes
@app.post("/api/products/{product_id}/reviews", response_model=ReviewResponse)
async def create_review(product_id: str, review_data: ReviewCreate, current_user = Depends(get_current_user_required)):
    try:
        # Check if product exists
        product = products_collection.find_one({"id": product_id, "is_active": True})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if user already reviewed this product
        existing_review = reviews_collection.find_one({
            "product_id": product_id,
            "user_id": current_user["user_id"]
        })
        if existing_review:
            raise HTTPException(status_code=400, detail="You have already reviewed this product")
        
        # Get user info
        user = users_collection.find_one({"id": current_user["user_id"]})
        
        # Create review
        review_dict = Review(
            product_id=product_id,
            user_id=current_user["user_id"],
            rating=review_data.rating,
            comment=review_data.comment
        ).dict()
        
        reviews_collection.insert_one(review_dict)
        
        # Prepare response
        review_dict.pop("_id", None)
        review_response = ReviewResponse(
            id=review_dict["id"],
            product_id=review_dict["product_id"],
            user_name=user["name"],
            rating=review_dict["rating"],
            comment=review_dict["comment"],
            created_at=review_dict["created_at"],
            is_approved=review_dict["is_approved"]
        )
        
        return review_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}/reviews", response_model=List[ReviewResponse])
async def get_product_reviews(product_id: str, limit: int = Query(20), skip: int = Query(0)):
    try:
        reviews = list(reviews_collection.find({
            "product_id": product_id,
            "is_approved": True
        }).sort("created_at", -1).skip(skip).limit(limit))
        
        review_responses = []
        for review in reviews:
            review.pop("_id", None)
            user = users_collection.find_one({"id": review["user_id"]})
            
            review_response = ReviewResponse(
                id=review["id"],
                product_id=review["product_id"],
                user_name=user["name"] if user else "Anonymous",
                rating=review["rating"],
                comment=review["comment"],
                created_at=review["created_at"],
                is_approved=review["is_approved"]
            )
            review_responses.append(review_response)
        
        return review_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Wishlist Routes
@app.get("/api/wishlist")
async def get_user_wishlist(current_user = Depends(get_current_user_required)):
    try:
        wishlist = wishlist_collection.find_one({"user_id": current_user["user_id"]})
        if not wishlist:
            # Create empty wishlist
            wishlist_data = Wishlist(user_id=current_user["user_id"]).dict()
            wishlist_collection.insert_one(wishlist_data)
            wishlist = wishlist_data
        
        wishlist.pop("_id", None)
        
        # Get product details for wishlist items
        products = []
        for item in wishlist.get("items", []):
            product = products_collection.find_one({"id": item["product_id"], "is_active": True})
            if product:
                product.pop("_id", None)
                # Update rating and review count
                avg_rating, review_count = calculate_average_rating(product["id"])
                product["rating"] = avg_rating
                product["reviews_count"] = review_count
                products.append(product)
        
        return {"wishlist": wishlist, "products": products}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/wishlist/add/{product_id}")
async def add_to_wishlist(product_id: str, current_user = Depends(get_current_user_required)):
    try:
        # Check if product exists
        product = products_collection.find_one({"id": product_id, "is_active": True})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get or create wishlist
        wishlist = wishlist_collection.find_one({"user_id": current_user["user_id"]})
        if not wishlist:
            wishlist_data = Wishlist(user_id=current_user["user_id"]).dict()
            wishlist_collection.insert_one(wishlist_data)
            wishlist = wishlist_data
        
        # Check if product already in wishlist
        existing_items = wishlist.get("items", [])
        if any(item["product_id"] == product_id for item in existing_items):
            raise HTTPException(status_code=400, detail="Product already in wishlist")
        
        # Add to wishlist
        new_item = WishlistItem(product_id=product_id).dict()
        existing_items.append(new_item)
        
        wishlist_collection.update_one(
            {"user_id": current_user["user_id"]},
            {
                "$set": {
                    "items": existing_items,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return {"message": "Product added to wishlist"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/wishlist/remove/{product_id}")
async def remove_from_wishlist(product_id: str, current_user = Depends(get_current_user_required)):
    try:
        wishlist = wishlist_collection.find_one({"user_id": current_user["user_id"]})
        if not wishlist:
            raise HTTPException(status_code=404, detail="Wishlist not found")
        
        # Remove from wishlist
        existing_items = wishlist.get("items", [])
        updated_items = [item for item in existing_items if item["product_id"] != product_id]
        
        if len(updated_items) == len(existing_items):
            raise HTTPException(status_code=404, detail="Product not in wishlist")
        
        wishlist_collection.update_one(
            {"user_id": current_user["user_id"]},
            {
                "$set": {
                    "items": updated_items,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return {"message": "Product removed from wishlist"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cart Routes (Enhanced)
@app.post("/api/cart")
async def create_cart(current_user = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"] if current_user else None
        session_id = str(uuid.uuid4()) if not user_id else None
        
        cart_data = Cart(
            user_id=user_id,
            session_id=session_id
        ).dict()
        
        cart_collection.insert_one(cart_data)
        cart_data.pop("_id", None)
        return cart_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cart/{cart_id}")
async def get_cart(cart_id: str, current_user = Depends(get_current_user)):
    try:
        cart = cart_collection.find_one({"id": cart_id})
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        # Check if user owns the cart
        if (current_user and cart.get("user_id") != current_user["user_id"]):
            raise HTTPException(status_code=403, detail="Not authorized to access this cart")
        
        cart.pop("_id", None)
        return cart
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cart/{cart_id}/items")
async def add_to_cart(cart_id: str, product_id: str, quantity: int = 1, current_user = Depends(get_current_user)):
    try:
        # Get product
        product = products_collection.find_one({"id": product_id, "is_active": True})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check inventory
        if product["inventory"] < quantity:
            raise HTTPException(status_code=400, detail="Insufficient inventory")
        
        # Get cart
        cart = cart_collection.find_one({"id": cart_id})
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        # Check if user owns the cart
        if (current_user and cart.get("user_id") != current_user["user_id"]):
            raise HTTPException(status_code=403, detail="Not authorized to access this cart")
        
        # Check if item already exists in cart
        items = cart.get("items", [])
        existing_item = None
        for item in items:
            if item["product_id"] == product_id:
                existing_item = item
                break
        
        if existing_item:
            existing_item["quantity"] += quantity
        else:
            items.append({
                "product_id": product_id,
                "quantity": quantity,
                "price": product["price"]
            })
        
        # Calculate total
        total = sum(item["quantity"] * item["price"] for item in items)
        
        # Update cart
        cart_collection.update_one(
            {"id": cart_id},
            {
                "$set": {
                    "items": items,
                    "total": total,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        updated_cart = cart_collection.find_one({"id": cart_id})
        updated_cart.pop("_id", None)
        return updated_cart
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/cart/{cart_id}/items/{product_id}")
async def remove_from_cart(cart_id: str, product_id: str, current_user = Depends(get_current_user)):
    try:
        cart = cart_collection.find_one({"id": cart_id})
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        # Check if user owns the cart
        if (current_user and cart.get("user_id") != current_user["user_id"]):
            raise HTTPException(status_code=403, detail="Not authorized to access this cart")
        
        items = [item for item in cart.get("items", []) if item["product_id"] != product_id]
        total = sum(item["quantity"] * item["price"] for item in items)
        
        cart_collection.update_one(
            {"id": cart_id},
            {
                "$set": {
                    "items": items,
                    "total": total,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        updated_cart = cart_collection.find_one({"id": cart_id})
        updated_cart.pop("_id", None)
        return updated_cart
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Checkout and Payment Routes (Enhanced)
@app.post("/api/checkout/session")
async def create_checkout_session(request: CheckoutRequest, current_user = Depends(get_current_user)):
    try:
        # Get cart
        cart = cart_collection.find_one({"id": request.cart_id})
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        if not cart.get("items"):
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Initialize Stripe checkout
        global stripe_checkout
        if not stripe_checkout and STRIPE_API_KEY:
            webhook_url = f"{request.origin_url}/api/webhook/stripe"
            stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
        
        if not stripe_checkout:
            raise HTTPException(status_code=500, detail="Stripe not configured")
        
        # Calculate total
        total_amount = cart["total"]
        discount_amount = 0.0
        coupon_code = None
        
        # Apply coupon if provided
        if hasattr(request, 'coupon_code') and request.coupon_code:
            discount_amount, message = apply_coupon(total_amount, request.coupon_code)
            if discount_amount > 0:
                coupon_code = request.coupon_code
                total_amount -= discount_amount
        
        # Create success and cancel URLs
        success_url = f"{request.origin_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{request.origin_url}/checkout/cancel"
        
        # Create checkout session request
        checkout_request = CheckoutSessionRequest(
            amount=total_amount,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "cart_id": request.cart_id,
                "user_id": current_user["user_id"] if current_user else "guest",
                "session_id": cart.get("session_id", "guest"),
                "coupon_code": coupon_code or "",
                "discount_amount": str(discount_amount)
            }
        )
        
        # Create Stripe session
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create order
        order_items = []
        for item in cart["items"]:
            product = products_collection.find_one({"id": item["product_id"]})
            order_items.append({
                "product_id": item["product_id"],
                "seller_id": product.get("seller_id"),
                "quantity": item["quantity"],
                "price": item["price"],
                "product_name": product["name"] if product else "Unknown Product"
            })
        
        order_data = Order(
            user_id=current_user["user_id"] if current_user else None,
            items=order_items,
            total_amount=cart["total"],
            status=OrderStatus.PENDING,
            payment_session_id=session.session_id,
            shipping_address=Address(
                name="Default Address",
                street="123 Main St",
                city="City",
                state="State",
                postal_code="12345",
                country="US"
            )  # This should come from user input in a real app
        ).dict()
        
        orders_collection.insert_one(order_data)
        
        # Create payment transaction
        transaction_data = PaymentTransaction(
            session_id=session.session_id,
            order_id=order_data["id"],
            user_id=current_user["user_id"] if current_user else None,
            amount=total_amount,
            coupon_code=coupon_code,
            discount_amount=discount_amount,
            metadata=checkout_request.metadata
        ).dict()
        
        payment_transactions_collection.insert_one(transaction_data)
        
        return {
            "url": session.url,
            "session_id": session.session_id,
            "total_amount": total_amount,
            "discount_amount": discount_amount,
            "original_amount": cart["total"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/checkout/status/{session_id}")
async def get_checkout_status(session_id: str):
    try:
        if not stripe_checkout:
            raise HTTPException(status_code=500, detail="Stripe not configured")
        
        # Get status from Stripe
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update local transaction
        transaction = payment_transactions_collection.find_one({"session_id": session_id})
        if transaction:
            update_data = {
                "status": checkout_status.status,
                "payment_status": checkout_status.payment_status,
                "updated_at": datetime.now(timezone.utc)
            }
            
            payment_transactions_collection.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            
            # Update order status if payment successful
            if checkout_status.payment_status == "paid" and transaction.get("order_id"):
                orders_collection.update_one(
                    {"id": transaction["order_id"]},
                    {"$set": {"status": "processing"}}
                )
                
                # Update coupon usage count
                if transaction.get("coupon_code"):
                    coupons_collection.update_one(
                        {"code": transaction["coupon_code"]},
                        {"$inc": {"used_count": 1}}
                    )
        
        return {
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "amount_total": checkout_status.amount_total,
            "currency": checkout_status.currency
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    try:
        if not stripe_checkout:
            return {"status": "stripe not configured"}
        
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update transaction based on webhook
        if webhook_response.session_id:
            update_data = {
                "payment_status": webhook_response.payment_status,
                "updated_at": datetime.now(timezone.utc)
            }
            
            payment_transactions_collection.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": update_data}
            )
        
        return {"status": "success"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Order Routes (Enhanced)
@app.get("/api/orders")
async def get_user_orders(current_user = Depends(get_current_user_required)):
    try:
        orders = list(orders_collection.find({"user_id": current_user["user_id"]}).sort("created_at", -1))
        for order in orders:
            order.pop("_id", None)
        
        return {"orders": orders}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/{order_id}")
async def get_order_details(order_id: str, current_user = Depends(get_current_user_required)):
    try:
        order = orders_collection.find_one({"id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check if user owns the order or is admin
        if (order.get("user_id") != current_user["user_id"] and 
            current_user.get("role") != "admin"):
            raise HTTPException(status_code=403, detail="Not authorized to view this order")
        
        order.pop("_id", None)
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin Routes
@app.get("/api/admin/users")
async def get_all_users(current_user = Depends(get_admin_user), skip: int = 0, limit: int = 50):
    try:
        users = list(users_collection.find().skip(skip).limit(limit).sort("created_at", -1))
        for user in users:
            user.pop("hashed_password", None)
            user.pop("_id", None)
        
        return {"users": users}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/orders")
async def get_all_orders(current_user = Depends(get_admin_user), skip: int = 0, limit: int = 50):
    try:
        orders = list(orders_collection.find().skip(skip).limit(limit).sort("created_at", -1))
        for order in orders:
            order.pop("_id", None)
        
        return {"orders": orders}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/orders/{order_id}/status")
async def update_order_status(order_id: str, status: OrderStatus, current_user = Depends(get_admin_user)):
    try:
        order = orders_collection.find_one({"id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        orders_collection.update_one(
            {"id": order_id},
            {"$set": {"status": status.value, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return {"message": "Order status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Categories and filters
@app.get("/api/categories")
async def get_categories():
    try:
        categories = products_collection.distinct("category", {"is_active": True})
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/brands")
async def get_brands():
    try:
        brands = products_collection.distinct("brand", {"is_active": True})
        return {"brands": brands}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics
@app.get("/api/analytics/search")
async def get_search_analytics(current_user = Depends(get_admin_user)):
    try:
        recent_searches = list(search_collection.find().sort("timestamp", -1).limit(10))
        for search in recent_searches:
            search.pop("_id", None)
        
        return {"recent_searches": recent_searches}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)