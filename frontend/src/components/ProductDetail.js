import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Star, Heart, ShoppingCart, Plus, Minus, Truck, Shield, ArrowLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Skeleton } from './ui/skeleton';
import { Separator } from './ui/separator';
import { ReviewForm, ReviewList } from './Reviews';

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

const ProductDetailPage = ({ addToCart, wishlist, onToggleWishlist }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        setLoading(true);
        const [productRes, reviewsRes, recommendationsRes] = await Promise.all([
          api.get(`/api/products/${id}`),
          api.get(`/api/products/${id}/reviews`),
          api.get(`/api/products/${id}/recommendations`)
        ]);
        
        setProduct(productRes.data);
        setReviews(reviewsRes.data);
        setRecommendations(recommendationsRes.data.recommendations);
      } catch (error) {
        console.error('Error fetching product:', error);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchProduct();
    }
  }, [id]);

  const handleReviewSubmitted = async () => {
    try {
      const response = await api.get(`/api/products/${id}/reviews`);
      setReviews(response.data);
      
      // Refetch product to update rating
      const productResponse = await api.get(`/api/products/${id}`);
      setProduct(productResponse.data);
    } catch (error) {
      console.error('Error refreshing reviews:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Skeleton className="aspect-square rounded-lg" />
            <div className="space-y-4">
              <Skeleton className="h-8 w-3/4" />
              <Skeleton className="h-6 w-1/2" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Product not found</h2>
          <p className="text-gray-600 mb-4">The product you're looking for doesn't exist.</p>
          <Button onClick={() => navigate('/search')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Products
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <div className="flex items-center space-x-2 text-sm text-gray-600 mb-6">
          <Button variant="ghost" size="sm" onClick={() => navigate('/')}>
            Home
          </Button>
          <span>/</span>
          <Button variant="ghost" size="sm" onClick={() => navigate('/search')}>
            Products
          </Button>
          <span>/</span>
          <span className="text-gray-900">{product.name}</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Product Images */}
          <div className="space-y-4">
            <div className="aspect-square overflow-hidden rounded-lg bg-white border">
              {product.images && product.images.length > 0 ? (
                <img
                  src={product.images[selectedImage]}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-100">
                  <ShoppingCart className="h-24 w-24 text-gray-400" />
                </div>
              )}
            </div>
            
            {product.images && product.images.length > 1 && (
              <div className="flex space-x-2">
                {product.images.map((image, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedImage(index)}
                    className={`w-20 h-20 rounded-lg overflow-hidden border-2 ${
                      selectedImage === index ? 'border-blue-600' : 'border-gray-200'
                    }`}
                  >
                    <img
                      src={image}
                      alt={`${product.name} ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Product Info */}
          <div className="space-y-6">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <Badge variant="secondary">{product.category}</Badge>
                <Badge variant="outline">{product.brand}</Badge>
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-4">{product.name}</h1>
              
              <div className="flex items-center space-x-4 mb-4">
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`h-5 w-5 ${
                        i < Math.floor(product.rating) 
                          ? 'text-yellow-400 fill-current' 
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-gray-600">
                  {product.rating.toFixed(1)} ({product.reviews_count} reviews)
                </span>
              </div>

              <div className="flex items-baseline space-x-2 mb-6">
                <span className="text-3xl font-bold text-blue-600">
                  ${product.price.toFixed(2)}
                </span>
                {product.inventory > 0 ? (
                  <span className="text-green-600 font-medium">In Stock ({product.inventory} available)</span>
                ) : (
                  <span className="text-red-600 font-medium">Out of Stock</span>
                )}
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Description</h3>
              <p className="text-gray-700 mb-4">
                {product.ai_generated_description || product.description}
              </p>
              
              {product.tags && product.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {product.tags.map((tag, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <label className="font-medium">Quantity:</label>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    disabled={quantity <= 1}
                  >
                    <Minus className="h-4 w-4" />
                  </Button>
                  <span className="px-4 py-2 border rounded-md min-w-[60px] text-center">
                    {quantity}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setQuantity(Math.min(product.inventory, quantity + 1))}
                    disabled={quantity >= product.inventory}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="flex space-x-4">
                <Button
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                  size="lg"
                  onClick={() => addToCart(product.id, quantity)}
                  disabled={product.inventory === 0}
                >
                  <ShoppingCart className="h-5 w-5 mr-2" />
                  Add to Cart
                </Button>
                <Button 
                  variant="outline" 
                  size="lg"
                  onClick={() => onToggleWishlist(product.id)}
                  className={isWishlisted ? 'text-red-600 border-red-600' : ''}
                >
                  <Heart className={`h-5 w-5 ${isWishlisted ? 'fill-current' : ''}`} />
                </Button>
              </div>
            </div>

            <div className="border-t pt-6">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <Truck className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <p className="text-sm font-medium">Free Shipping</p>
                  <p className="text-xs text-gray-600">On orders over $50</p>
                </div>
                <div>
                  <Shield className="h-8 w-8 text-green-600 mx-auto mb-2" />
                  <p className="text-sm font-medium">Secure Payment</p>
                  <p className="text-xs text-gray-600">100% protected</p>
                </div>
                <div>
                  <Star className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
                  <p className="text-sm font-medium">Top Quality</p>
                  <p className="text-xs text-gray-600">Premium products</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-16">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Reviews Section */}
            <div>
              <h2 className="text-2xl font-bold mb-6">Customer Reviews</h2>
              <div className="space-y-6">
                <ReviewForm productId={product.id} onReviewSubmitted={handleReviewSubmitted} />
                <ReviewList reviews={reviews} />
              </div>
            </div>

            {/* Recommendations */}
            {recommendations.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold mb-6">You might also like</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {recommendations.slice(0, 4).map((rec) => (
                    <Card key={rec.id} className="cursor-pointer" onClick={() => navigate(`/product/${rec.id}`)}>
                      <CardHeader className="p-0">
                        <div className="aspect-square overflow-hidden rounded-t-lg bg-gray-100">
                          {rec.images?.[0] ? (
                            <img
                              src={rec.images[0]}
                              alt={rec.name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center">
                              <ShoppingCart className="h-8 w-8 text-gray-400" />
                            </div>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="p-4">
                        <h3 className="font-semibold text-sm mb-2">{rec.name}</h3>
                        <div className="flex items-center space-x-2 mb-2">
                          <div className="flex items-center">
                            {[...Array(5)].map((_, i) => (
                              <Star
                                key={i}
                                className={`h-3 w-3 ${
                                  i < Math.floor(rec.rating) 
                                    ? 'text-yellow-400 fill-current' 
                                    : 'text-gray-300'
                                }`}
                              />
                            ))}
                          </div>
                          <span className="text-xs text-gray-500">({rec.reviews_count})</span>
                        </div>
                        <p className="text-lg font-bold text-blue-600">
                          ${rec.price.toFixed(2)}
                        </p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailPage;