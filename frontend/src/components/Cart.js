import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ShoppingCart, Plus, Minus, X, CreditCard, Truck } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Separator } from './ui/separator';
import { Skeleton } from './ui/skeleton';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const CartPage = ({ cart, updateCartQuantity, removeFromCart }) => {
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProductDetails = async () => {
      if (!cart?.items) return;
      
      try {
        setLoading(true);
        const productPromises = cart.items.map(item =>
          api.get(`/api/products/${item.product_id}`)
        );
        
        const responses = await Promise.all(productPromises);
        const productMap = {};
        responses.forEach(response => {
          productMap[response.data.id] = response.data;
        });
        
        setProducts(productMap);
      } catch (error) {
        console.error('Error fetching product details:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProductDetails();
  }, [cart]);

  const handleCheckout = async () => {
    if (!cart?.id) return;
    
    try {
      setLoading(true);
      const originUrl = window.location.origin;
      
      const response = await api.post('/api/checkout/session', {
        cart_id: cart.id,
        origin_url: originUrl
      });
      
      // Redirect to Stripe Checkout
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
      alert('Failed to create checkout session. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!cart) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ShoppingCart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Loading cart...</h2>
        </div>
      </div>
    );
  }

  if (!cart.items || cart.items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold mb-8">Shopping Cart</h1>
          
          <div className="text-center py-12">
            <ShoppingCart className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Your cart is empty</h3>
            <p className="text-gray-600 mb-6">Add some products to get started</p>
            <Button onClick={() => navigate('/search')} className="bg-blue-600 hover:bg-blue-700 text-white">
              Continue Shopping
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold mb-8">Shopping Cart</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Cart Items ({cart.items.length})</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {cart.items.map((item) => {
                  const product = products[item.product_id];
                  if (!product) {
                    return (
                      <div key={item.product_id} className="flex items-center space-x-4 p-4 border rounded-lg">
                        <Skeleton className="w-16 h-16 rounded" />
                        <div className="flex-1">
                          <Skeleton className="h-4 mb-2" />
                          <Skeleton className="h-3 w-1/2" />
                        </div>
                      </div>
                    );
                  }

                  return (
                    <div key={item.product_id} className="flex items-center space-x-4 p-4 border rounded-lg">
                      <div 
                        className="w-16 h-16 bg-gray-100 rounded overflow-hidden cursor-pointer"
                        onClick={() => navigate(`/product/${item.product_id}`)}
                      >
                        {product.images?.[0] ? (
                          <img
                            src={product.images[0]}
                            alt={product.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <ShoppingCart className="h-6 w-6 text-gray-400" />
                          </div>
                        )}
                      </div>
                      
                      <div className="flex-1">
                        <h3 
                          className="font-semibold cursor-pointer hover:text-blue-600"
                          onClick={() => navigate(`/product/${item.product_id}`)}
                        >
                          {product.name}
                        </h3>
                        <p className="text-sm text-gray-600">{product.brand}</p>
                        <p className="text-sm font-medium text-blue-600">
                          ${item.price.toFixed(2)} each
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => updateCartQuantity(item.product_id, item.quantity - 1)}
                          disabled={loading}
                        >
                          <Minus className="h-4 w-4" />
                        </Button>
                        <span className="px-3 py-1 border rounded min-w-[40px] text-center">
                          {item.quantity}
                        </span>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => updateCartQuantity(item.product_id, item.quantity + 1)}
                          disabled={loading}
                        >
                          <Plus className="h-4 w-4" />
                        </Button>
                      </div>
                      
                      <div className="text-right">
                        <p className="font-semibold">
                          ${(item.price * item.quantity).toFixed(2)}
                        </p>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFromCart(item.product_id)}
                          disabled={loading}
                          className="text-red-600 hover:text-red-700"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>

          {/* Order Summary */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Order Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span>Subtotal:</span>
                  <span>${cart.total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Shipping:</span>
                  <span className="text-green-600">Free</span>
                </div>
                <div className="flex justify-between">
                  <span>Tax:</span>
                  <span>${(cart.total * 0.08).toFixed(2)}</span>
                </div>
                <Separator />
                <div className="flex justify-between text-lg font-bold">
                  <span>Total:</span>
                  <span>${(cart.total * 1.08).toFixed(2)}</span>
                </div>
                
                <Button
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                  size="lg"
                  onClick={handleCheckout}
                  disabled={loading}
                >
                  {loading ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Processing...</span>
                    </div>
                  ) : (
                    <>
                      <CreditCard className="h-5 w-5 mr-2" />
                      Proceed to Checkout
                    </>
                  )}
                </Button>
                
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => navigate('/search')}
                >
                  Continue Shopping
                </Button>

                {/* Trust Indicators */}
                <div className="pt-4 border-t">
                  <div className="flex items-center space-x-2 text-sm text-gray-600 mb-2">
                    <Truck className="h-4 w-4" />
                    <span>Free shipping on orders over $50</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <CreditCard className="h-4 w-4" />
                    <span>Secure checkout with Stripe</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage;