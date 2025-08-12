from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import os
import uuid
from dotenv import load_dotenv
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import asyncio

# Load environment variables
load_dotenv()

app = FastAPI(title="E-commerce API", description="Modern E-commerce Platform with AI")

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
products_collection = db["products"]
users_collection = db["users"]
orders_collection = db["orders"]
cart_collection = db["cart"]
payment_transactions_collection = db["payment_transactions"]
search_collection = db["search_queries"]

# Stripe integration
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")
stripe_checkout = None

# AI integration
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")

# Pydantic models
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    brand: str
    images: List[str] = []
    inventory: int
    tags: List[str] = []

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    items: List[CartItem]
    total: float
    status: str = "pending"  # pending, paid, shipped, delivered, cancelled
    payment_session_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CheckoutRequest(BaseModel):
    cart_id: str
    origin_url: str

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    amount: float
    currency: str = "usd"
    status: str = "pending"  # pending, paid, failed, expired
    payment_status: str = "unpaid"
    user_id: Optional[str] = None
    order_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# AI Helper Functions
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
        # Get user's order history or current product context
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
        
        all_products = list(products_collection.find().limit(20))
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

# API Routes

@app.get("/")
async def root():
    return {"message": "E-commerce API is running!"}

# Product routes
@app.post("/api/products", response_model=Product)
async def create_product(product: ProductCreate):
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
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc"),
    limit: int = Query(20)
):
    try:
        # Build filter query
        filter_query = {}
        if category:
            filter_query["category"] = {"$regex": category, "$options": "i"}
        if brand:
            filter_query["brand"] = {"$regex": brand, "$options": "i"}
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
        
        # Apply AI-powered search if search query provided
        if search:
            # Store search query for analytics
            search_collection.insert_one({
                "query": search,
                "results_count": len(products),
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
        product = products_collection.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product.pop("_id", None)
        return Product(**product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}/recommendations")
async def get_product_recommendations(product_id: str, user_id: Optional[str] = Query(None)):
    try:
        recommended_ids = await get_recommendations(user_id=user_id, product_id=product_id)
        
        recommended_products = []
        for product_id in recommended_ids[:6]:
            product = products_collection.find_one({"id": product_id})
            if product:
                product.pop("_id", None)
                recommended_products.append(product)
        
        return {"recommendations": recommended_products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cart routes
@app.post("/api/cart")
async def create_cart(user_id: Optional[str] = None, session_id: Optional[str] = None):
    try:
        if not user_id and not session_id:
            session_id = str(uuid.uuid4())
        
        cart_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": session_id,
            "items": [],
            "total": 0.0,
            "updated_at": datetime.now(timezone.utc)
        }
        
        cart_collection.insert_one(cart_data)
        cart_data.pop("_id", None)
        return cart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cart/{cart_id}")
async def get_cart(cart_id: str):
    try:
        cart = cart_collection.find_one({"id": cart_id})
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        cart.pop("_id", None)
        return cart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cart/{cart_id}/items")
async def add_to_cart(cart_id: str, product_id: str, quantity: int = 1):
    try:
        # Get product
        product = products_collection.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get cart
        cart = cart_collection.find_one({"id": cart_id})
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
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
async def remove_from_cart(cart_id: str, product_id: str):
    try:
        cart = cart_collection.find_one({"id": cart_id})
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
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

# Checkout and Payment routes
@app.post("/api/checkout/session")
async def create_checkout_session(request: CheckoutRequest):
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
                "user_id": cart.get("user_id", ""),
                "session_id": cart.get("session_id", "")
            }
        )
        
        # Create Stripe session
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create order
        order_data = {
            "id": str(uuid.uuid4()),
            "user_id": cart.get("user_id"),
            "session_id": cart.get("session_id"),
            "items": cart["items"],
            "total": total_amount,
            "status": "pending",
            "payment_session_id": session.session_id,
            "created_at": datetime.now(timezone.utc)
        }
        orders_collection.insert_one(order_data)
        
        # Create payment transaction
        transaction_data = {
            "id": str(uuid.uuid4()),
            "session_id": session.session_id,
            "amount": total_amount,
            "currency": "usd",
            "status": "pending",
            "payment_status": "unpaid",
            "user_id": cart.get("user_id"),
            "order_id": order_data["id"],
            "metadata": checkout_request.metadata,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        payment_transactions_collection.insert_one(transaction_data)
        
        return {
            "url": session.url,
            "session_id": session.session_id
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
                    {"$set": {"status": "paid"}}
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

# Orders routes
@app.get("/api/orders")
async def get_orders(user_id: Optional[str] = Query(None), session_id: Optional[str] = Query(None)):
    try:
        filter_query = {}
        if user_id:
            filter_query["user_id"] = user_id
        elif session_id:
            filter_query["session_id"] = session_id
        
        orders = list(orders_collection.find(filter_query).sort("created_at", -1))
        for order in orders:
            order.pop("_id", None)
        
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Categories and filters
@app.get("/api/categories")
async def get_categories():
    try:
        categories = products_collection.distinct("category")
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/brands")
async def get_brands():
    try:
        brands = products_collection.distinct("brand")
        return {"brands": brands}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics
@app.get("/api/analytics/search")
async def get_search_analytics():
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