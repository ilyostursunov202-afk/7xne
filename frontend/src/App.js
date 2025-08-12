import React, { useState, useEffect, createContext, useContext, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation, useSearchParams, Link } from 'react-router-dom';
import axios from 'axios';
import { Search, ShoppingCart, Filter, Star, Heart, User, Menu, Plus, Minus, CreditCard, Truck, Shield, ArrowRight, Grid, List, SortAsc, X } from 'lucide-react';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from './components/ui/sheet';
import { Separator } from './components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Alert, AlertDescription } from './components/ui/alert';
import { Skeleton } from './components/ui/skeleton';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './components/ui/dialog';
import './App.css';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Context for global state
const AppContext = createContext();

const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

const AppProvider = ({ children }) => {
  const [cart, setCart] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cartCount, setCartCount] = useState(0);
  
  // Initialize cart
  useEffect(() => {
    const initCart = async () => {
      try {
        let cartId = localStorage.getItem('cartId');
        if (!cartId) {
          const response = await api.post('/api/cart');
          cartId = response.data.id;
          localStorage.setItem('cartId', cartId);
          setCart(response.data);
        } else {
          const response = await api.get(`/api/cart/${cartId}`);
          setCart(response.data);
        }
      } catch (error) {
        console.error('Error initializing cart:', error);
        // Create new cart if existing one fails
        try {
          const response = await api.post('/api/cart');
          localStorage.setItem('cartId', response.data.id);
          setCart(response.data);
        } catch (createError) {
          console.error('Error creating new cart:', createError);
        }
      }
    };
    
    initCart();
  }, []);

  // Update cart count when cart changes
  useEffect(() => {
    if (cart?.items) {
      const count = cart.items.reduce((sum, item) => sum + item.quantity, 0);
      setCartCount(count);
    }
  }, [cart]);

  const addToCart = async (productId, quantity = 1) => {
    if (!cart) return;
    
    try {
      setLoading(true);
      const response = await api.post(`/api/cart/${cart.id}/items`, null, {
        params: { product_id: productId, quantity }
      });
      setCart(response.data);
    } catch (error) {
      console.error('Error adding to cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeFromCart = async (productId) => {
    if (!cart) return;
    
    try {
      setLoading(true);
      const response = await api.delete(`/api/cart/${cart.id}/items/${productId}`);
      setCart(response.data);
    } catch (error) {
      console.error('Error removing from cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateCartQuantity = async (productId, quantity) => {
    if (!cart) return;
    
    if (quantity === 0) {
      await removeFromCart(productId);
      return;
    }
    
    try {
      setLoading(true);
      // Remove existing item first
      await removeFromCart(productId);
      // Add with new quantity
      await addToCart(productId, quantity);
    } catch (error) {
      console.error('Error updating cart quantity:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppContext.Provider value={{
      cart,
      setCart,
      user,
      setUser,
      loading,
      setLoading,
      cartCount,
      addToCart,
      removeFromCart,
      updateCartQuantity
    }}>
      {children}
    </AppContext.Provider>
  );
};

// Header Component
const Header = () => {
  const { cartCount } = useAppContext();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-2 rounded-lg">
              <ShoppingCart className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              MarketPlace
            </span>
          </Link>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="flex-1 max-w-xl mx-8">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                type="text"
                placeholder="Search products, brands, categories..."
                className="pl-10 pr-4 w-full"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </form>

          {/* Navigation */}
          <div className="flex items-center space-x-6">
            <Button variant="ghost" size="sm" className="hidden md:flex items-center space-x-2">
              <User className="h-4 w-4" />
              <span>Account</span>
            </Button>
            
            <Button 
              variant="ghost" 
              size="sm" 
              className="relative flex items-center space-x-2"
              onClick={() => navigate('/cart')}
            >
              <ShoppingCart className="h-4 w-4" />
              <span className="hidden md:inline">Cart</span>
              {cartCount > 0 && (
                <Badge className="absolute -top-2 -right-2 bg-blue-600 text-white text-xs min-w-[20px] h-5 flex items-center justify-center rounded-full">
                  {cartCount}
                </Badge>
              )}
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

// Product Card Component
const ProductCard = ({ product, onAddToCart }) => {
  const [imageError, setImageError] = useState(false);
  const navigate = useNavigate();

  return (
    <Card className="group cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-[1.02]">
      <CardHeader className="p-0">
        <div 
          className="aspect-square overflow-hidden rounded-t-lg bg-gray-100"
          onClick={() => navigate(`/product/${product.id}`)}
        >
          {product.images && product.images.length > 0 && !imageError ? (
            <img
              src={product.images[0]}
              alt={product.name}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
              onError={() => setImageError(true)}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
              <div className="text-center">
                <ShoppingCart className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-500">{product.name}</p>
              </div>
            </div>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="p-4" onClick={() => navigate(`/product/${product.id}`)}>
        <div className="space-y-2">
          <div className="flex items-start justify-between">
            <h3 className="font-semibold text-sm line-clamp-2 flex-1">{product.name}</h3>
            <Button variant="ghost" size="sm" className="p-1 ml-2">
              <Heart className="h-4 w-4" />
            </Button>
          </div>
          
          <p className="text-xs text-gray-600 line-clamp-2">
            {product.ai_generated_description || product.description}
          </p>
          
          <div className="flex items-center space-x-2">
            <div className="flex items-center">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`h-3 w-3 ${
                    i < Math.floor(product.rating) 
                      ? 'text-yellow-400 fill-current' 
                      : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-xs text-gray-500">
              ({product.reviews_count})
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            <Badge variant="secondary" className="text-xs">
              {product.category}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {product.brand}
            </Badge>
          </div>
        </div>
      </CardContent>
      
      <CardFooter className="p-4 pt-0">
        <div className="flex items-center justify-between w-full">
          <div className="flex flex-col">
            <span className="text-lg font-bold text-blue-600">
              ${product.price.toFixed(2)}
            </span>
            {product.inventory > 0 ? (
              <span className="text-xs text-green-600">In Stock</span>
            ) : (
              <span className="text-xs text-red-600">Out of Stock</span>
            )}
          </div>
          
          <Button
            onClick={(e) => {
              e.stopPropagation();
              onAddToCart(product.id);
            }}
            disabled={product.inventory === 0}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Plus className="h-4 w-4 mr-1" />
            Add
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
};

// Home Page Component
const HomePage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const { addToCart } = useAppContext();

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get('/api/products?limit=12');
        setProducts(response.data);
        setFeaturedProducts(response.data.slice(0, 4));
      } catch (error) {
        console.error('Error fetching products:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <Card key={i}>
                <CardHeader className="p-0">
                  <Skeleton className="aspect-square rounded-t-lg" />
                </CardHeader>
                <CardContent className="p-4">
                  <Skeleton className="h-4 mb-2" />
                  <Skeleton className="h-3 mb-4 w-3/4" />
                  <div className="flex space-x-2">
                    <Skeleton className="h-5 w-16" />
                    <Skeleton className="h-5 w-16" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Discover Amazing Products
            </h1>
            <p className="text-xl md:text-2xl mb-8 opacity-90">
              AI-powered shopping experience with smart recommendations
            </p>
            <div className="flex justify-center space-x-4">
              <Button className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3 text-lg">
                Shop Now
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600 px-8 py-3 text-lg">
                Learn More
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Truck className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Fast Delivery</h3>
              <p className="text-gray-600">Free shipping on orders over $50</p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Shield className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Secure Payment</h3>
              <p className="text-gray-600">100% secure payment processing</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Star className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">AI Recommendations</h3>
              <p className="text-gray-600">Smart product suggestions just for you</p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Featured Products</h2>
            <p className="text-gray-600">Discover our handpicked selection</p>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={addToCart}
              />
            ))}
          </div>

          <div className="text-center mt-12">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white">
              <Link to="/search" className="flex items-center">
                View All Products
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

// Search/Products Page Component
const SearchPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState({
    search: searchParams.get('q') || '',
    category: searchParams.get('category') || '',
    brand: searchParams.get('brand') || '',
    minPrice: searchParams.get('min_price') || '',
    maxPrice: searchParams.get('max_price') || '',
    sortBy: searchParams.get('sort_by') || 'created_at',
    sortOrder: searchParams.get('sort_order') || 'desc'
  });
  const [viewMode, setViewMode] = useState('grid');
  const { addToCart } = useAppContext();

  useEffect(() => {
    const fetchFilters = async () => {
      try {
        const [categoriesRes, brandsRes] = await Promise.all([
          api.get('/api/categories'),
          api.get('/api/brands')
        ]);
        setCategories(categoriesRes.data.categories);
        setBrands(brandsRes.data.brands);
      } catch (error) {
        console.error('Error fetching filters:', error);
      }
    };

    fetchFilters();
  }, []);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams();
        
        Object.entries(filters).forEach(([key, value]) => {
          if (value) {
            if (key === 'minPrice') params.append('min_price', value);
            else if (key === 'maxPrice') params.append('max_price', value);
            else if (key === 'sortBy') params.append('sort_by', value);
            else if (key === 'sortOrder') params.append('sort_order', value);
            else params.append(key, value);
          }
        });

        const response = await api.get(`/api/products?${params.toString()}&limit=24`);
        setProducts(response.data);
      } catch (error) {
        console.error('Error fetching products:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [filters]);

  const handleFilterChange = (key, value) => {
    const newFilters = { 
      ...filters, 
      [key]: value === 'all' ? '' : value 
    };
    setFilters(newFilters);
    
    const newSearchParams = new URLSearchParams();
    Object.entries(newFilters).forEach(([k, v]) => {
      if (v && v !== 'all') newSearchParams.set(k, v);
    });
    setSearchParams(newSearchParams);
  };

  const clearFilters = () => {
    const clearedFilters = {
      search: '',
      category: '',
      brand: '',
      minPrice: '',
      maxPrice: '',
      sortBy: 'created_at',
      sortOrder: 'desc'
    };
    setFilters(clearedFilters);
    setSearchParams(new URLSearchParams());
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              {filters.search ? `Search results for "${filters.search}"` : 'All Products'}
            </h1>
            <p className="text-gray-600">
              {products.length} {products.length === 1 ? 'product' : 'products'} found
            </p>
          </div>
          
          <div className="flex items-center space-x-4 mt-4 md:mt-0">
            <div className="flex items-center space-x-2">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
            
            <Select value={filters.sortBy} onValueChange={(value) => handleFilterChange('sortBy', value)}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="created_at">Newest First</SelectItem>
                <SelectItem value="price">Price: Low to High</SelectItem>
                <SelectItem value="name">Name: A to Z</SelectItem>
                <SelectItem value="rating">Highest Rated</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <div className="lg:w-1/4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Filters</CardTitle>
                  <Button variant="ghost" size="sm" onClick={clearFilters}>
                    <X className="h-4 w-4 mr-1" />
                    Clear
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Search */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Search</label>
                  <Input
                    placeholder="Search products..."
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                  />
                </div>

                {/* Category */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Category</label>
                  <Select value={filters.category || undefined} onValueChange={(value) => handleFilterChange('category', value || '')}>
                    <SelectTrigger>
                      <SelectValue placeholder="All categories" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All categories</SelectItem>
                      {categories.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Brand */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Brand</label>
                  <Select value={filters.brand || undefined} onValueChange={(value) => handleFilterChange('brand', value === 'all' ? '' : value || '')}>
                    <SelectTrigger>
                      <SelectValue placeholder="All brands" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All brands</SelectItem>
                      {brands.map((brand) => (
                        <SelectItem key={brand} value={brand}>
                          {brand}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Price Range */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Price Range</label>
                  <div className="flex space-x-2">
                    <Input
                      type="number"
                      placeholder="Min"
                      value={filters.minPrice}
                      onChange={(e) => handleFilterChange('minPrice', e.target.value)}
                    />
                    <Input
                      type="number"
                      placeholder="Max"
                      value={filters.maxPrice}
                      onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Products Grid */}
          <div className="lg:w-3/4">
            {loading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(9)].map((_, i) => (
                  <Card key={i}>
                    <CardHeader className="p-0">
                      <Skeleton className="aspect-square rounded-t-lg" />
                    </CardHeader>
                    <CardContent className="p-4">
                      <Skeleton className="h-4 mb-2" />
                      <Skeleton className="h-3 mb-4 w-3/4" />
                      <div className="flex space-x-2">
                        <Skeleton className="h-5 w-16" />
                        <Skeleton className="h-5 w-16" />
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : products.length === 0 ? (
              <div className="text-center py-12">
                <ShoppingCart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No products found</h3>
                <p className="text-gray-600 mb-4">Try adjusting your search or filters</p>
                <Button onClick={clearFilters}>Clear all filters</Button>
              </div>
            ) : (
              <div className={`grid gap-6 ${
                viewMode === 'grid' 
                  ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3' 
                  : 'grid-cols-1'
              }`}>
                {products.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onAddToCart={addToCart}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Product Detail Page Component
const ProductDetailPage = () => {
  const location = useLocation();
  const id = location.pathname.split('/').pop();
  const [product, setProduct] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);
  const { addToCart } = useAppContext();

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const [productRes, recommendationsRes] = await Promise.all([
          api.get(`/api/products/${id}`),
          api.get(`/api/products/${id}/recommendations`)
        ]);
        
        setProduct(productRes.data);
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
          <Link to="/search">
            <Button>Browse Products</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
                <Button variant="outline" size="lg">
                  <Heart className="h-5 w-5" />
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

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div className="mt-16">
            <h2 className="text-2xl font-bold mb-8">You might also like</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {recommendations.slice(0, 4).map((rec) => (
                <ProductCard
                  key={rec.id}
                  product={rec}
                  onAddToCart={addToCart}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Cart Page Component
const CartPage = () => {
  const { cart, updateCartQuantity, removeFromCart } = useAppContext();
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
                      <div className="w-16 h-16 bg-gray-100 rounded overflow-hidden">
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
                        <h3 className="font-semibold">{product.name}</h3>
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
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

// Checkout Success Page Component
const CheckoutSuccessPage = () => {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    if (!sessionId) {
      navigate('/cart');
      return;
    }

    const pollPaymentStatus = async (attempts = 0) => {
      const maxAttempts = 5;
      const pollInterval = 2000; // 2 seconds

      if (attempts >= maxAttempts) {
        setStatus({ error: 'Payment status check timed out. Please check your email for confirmation.' });
        setLoading(false);
        return;
      }

      try {
        const response = await api.get(`/api/checkout/status/${sessionId}`);
        const data = response.data;
        
        if (data.payment_status === 'paid') {
          setStatus({ success: true, data });
          setLoading(false);
          // Clear cart
          localStorage.removeItem('cartId');
          return;
        } else if (data.status === 'expired') {
          setStatus({ error: 'Payment session expired. Please try again.' });
          setLoading(false);
          return;
        }

        // If payment is still pending, continue polling
        if (attempts === 0) setLoading(false); // Stop loading after first check
        setTimeout(() => pollPaymentStatus(attempts + 1), pollInterval);
      } catch (error) {
        console.error('Error checking payment status:', error);
        setStatus({ error: 'Error checking payment status. Please try again.' });
        setLoading(false);
      }
    };

    pollPaymentStatus();
  }, [searchParams, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Processing Payment</h2>
          <p className="text-gray-600">Please wait while we confirm your payment...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full">
        <Card>
          <CardContent className="text-center py-12">
            {status?.success ? (
              <>
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <ShoppingCart className="h-8 w-8 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Payment Successful!</h2>
                <p className="text-gray-600 mb-6">
                  Thank you for your purchase. Your order has been confirmed.
                </p>
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <p className="text-sm text-gray-600 mb-1">Order Total</p>
                  <p className="text-2xl font-bold text-green-600">
                    ${((status.data.amount_total || 0) / 100).toFixed(2)}
                  </p>
                </div>
                <div className="space-y-3">
                  <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white">
                    View Orders
                  </Button>
                  <Button variant="outline" className="w-full" onClick={() => navigate('/')}>
                    Continue Shopping
                  </Button>
                </div>
              </>
            ) : (
              <>
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <X className="h-8 w-8 text-red-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Payment Failed</h2>
                <p className="text-gray-600 mb-6">
                  {status?.error || 'There was an issue processing your payment.'}
                </p>
                <div className="space-y-3">
                  <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white" onClick={() => navigate('/cart')}>
                    Try Again
                  </Button>
                  <Button variant="outline" className="w-full" onClick={() => navigate('/')}>
                    Back to Home
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Admin Panel Component
const AdminPanel = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    category: '',
    brand: '',
    inventory: '',
    images: [''],
    tags: []
  });

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/products?limit=50');
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const productData = {
        ...formData,
        price: parseFloat(formData.price),
        inventory: parseInt(formData.inventory),
        tags: formData.tags.filter(tag => tag.trim() !== '')
      };

      if (editingProduct) {
        // Update existing product
        await api.put(`/api/products/${editingProduct.id}`, productData);
      } else {
        // Create new product
        await api.post('/api/products', productData);
      }

      await fetchProducts();
      setShowAddForm(false);
      setEditingProduct(null);
      resetForm();
    } catch (error) {
      console.error('Error saving product:', error);
      alert('Failed to save product. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      description: product.description,
      price: product.price.toString(),
      category: product.category,
      brand: product.brand,
      inventory: product.inventory.toString(),
      images: product.images.length > 0 ? product.images : [''],
      tags: product.tags || []
    });
    setShowAddForm(true);
  };

  const handleDelete = async (productId) => {
    if (!confirm('Are you sure you want to delete this product?')) return;
    
    try {
      setLoading(true);
      await api.delete(`/api/products/${productId}`);
      await fetchProducts();
    } catch (error) {
      console.error('Error deleting product:', error);
      alert('Failed to delete product. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      price: '',
      category: '',
      brand: '',
      inventory: '',
      images: [''],
      tags: []
    });
  };

  const addImageUrl = () => {
    setFormData(prev => ({
      ...prev,
      images: [...prev.images, '']
    }));
  };

  const updateImageUrl = (index, url) => {
    setFormData(prev => ({
      ...prev,
      images: prev.images.map((img, i) => i === index ? url : img)
    }));
  };

  const removeImageUrl = (index) => {
    setFormData(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }));
  };

  const addTag = () => {
    setFormData(prev => ({
      ...prev,
      tags: [...prev.tags, '']
    }));
  };

  const updateTag = (index, tag) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.map((t, i) => i === index ? tag : t)
    }));
  };

  const removeTag = (index) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter((_, i) => i !== index)
    }));
  };

  if (loading && products.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex justify-center items-center h-64">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Product Management</h1>
            <p className="text-gray-600 mt-1">Manage your e-commerce products</p>
          </div>
          <Button 
            onClick={() => {
              setShowAddForm(true);
              setEditingProduct(null);
              resetForm();
            }}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Plus className="h-5 w-5 mr-2" />
            Add Product
          </Button>
        </div>

        {/* Add/Edit Form */}
        {showAddForm && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>
                {editingProduct ? 'Edit Product' : 'Add New Product'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Product Name *
                    </label>
                    <Input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData(prev => ({...prev, name: e.target.value}))}
                      placeholder="Enter product name"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Price *
                    </label>
                    <Input
                      type="number"
                      step="0.01"
                      value={formData.price}
                      onChange={(e) => setFormData(prev => ({...prev, price: e.target.value}))}
                      placeholder="0.00"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Category *
                    </label>
                    <Input
                      type="text"
                      value={formData.category}
                      onChange={(e) => setFormData(prev => ({...prev, category: e.target.value}))}
                      placeholder="e.g., Electronics, Fashion"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Brand *
                    </label>
                    <Input
                      type="text"
                      value={formData.brand}
                      onChange={(e) => setFormData(prev => ({...prev, brand: e.target.value}))}
                      placeholder="e.g., Apple, Nike"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Inventory *
                    </label>
                    <Input
                      type="number"
                      value={formData.inventory}
                      onChange={(e) => setFormData(prev => ({...prev, inventory: e.target.value}))}
                      placeholder="0"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description *
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({...prev, description: e.target.value}))}
                    placeholder="Enter product description"
                    required
                    rows="3"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Image URLs */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Product Images
                  </label>
                  {formData.images.map((image, index) => (
                    <div key={index} className="flex items-center space-x-2 mb-2">
                      <Input
                        type="url"
                        value={image}
                        onChange={(e) => updateImageUrl(index, e.target.value)}
                        placeholder="https://example.com/image.jpg"
                        className="flex-1"
                      />
                      {formData.images.length > 1 && (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => removeImageUrl(index)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  ))}
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={addImageUrl}
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Add Image URL
                  </Button>
                </div>

                {/* Tags */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags
                  </label>
                  {formData.tags.map((tag, index) => (
                    <div key={index} className="flex items-center space-x-2 mb-2">
                      <Input
                        type="text"
                        value={tag}
                        onChange={(e) => updateTag(index, e.target.value)}
                        placeholder="Tag name"
                        className="flex-1"
                      />
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => removeTag(index)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={addTag}
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Add Tag
                  </Button>
                </div>

                <div className="flex justify-end space-x-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowAddForm(false);
                      setEditingProduct(null);
                      resetForm();
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {loading ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        <span>Saving...</span>
                      </div>
                    ) : (
                      editingProduct ? 'Update Product' : 'Create Product'
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Products Table */}
        <Card>
          <CardHeader>
            <CardTitle>Products ({products.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="border border-gray-300 px-4 py-3 text-left">Image</th>
                    <th className="border border-gray-300 px-4 py-3 text-left">Name</th>
                    <th className="border border-gray-300 px-4 py-3 text-left">Category</th>
                    <th className="border border-gray-300 px-4 py-3 text-left">Brand</th>
                    <th className="border border-gray-300 px-4 py-3 text-left">Price</th>
                    <th className="border border-gray-300 px-4 py-3 text-left">Inventory</th>
                    <th className="border border-gray-300 px-4 py-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((product) => (
                    <tr key={product.id} className="hover:bg-gray-50">
                      <td className="border border-gray-300 px-4 py-3">
                        <div className="w-16 h-16 bg-gray-100 rounded-md overflow-hidden">
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
                      </td>
                      <td className="border border-gray-300 px-4 py-3">
                        <div className="font-medium">{product.name}</div>
                        <div className="text-sm text-gray-600 line-clamp-2">
                          {product.ai_generated_description || product.description}
                        </div>
                      </td>
                      <td className="border border-gray-300 px-4 py-3">
                        <Badge variant="secondary">{product.category}</Badge>
                      </td>
                      <td className="border border-gray-300 px-4 py-3">
                        <Badge variant="outline">{product.brand}</Badge>
                      </td>
                      <td className="border border-gray-300 px-4 py-3">
                        <span className="font-semibold text-green-600">
                          ${product.price.toFixed(2)}
                        </span>
                      </td>
                      <td className="border border-gray-300 px-4 py-3">
                        <span className={`font-medium ${
                          product.inventory > 10 ? 'text-green-600' : 
                          product.inventory > 0 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {product.inventory}
                        </span>
                      </td>
                      <td className="border border-gray-300 px-4 py-3">
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(product)}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(product.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            Delete
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Checkout Cancel Page Component  
const CheckoutCancelPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full">
        <Card>
          <CardContent className="text-center py-12">
            <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <X className="h-8 w-8 text-yellow-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Checkout Cancelled</h2>
            <p className="text-gray-600 mb-6">
              Your payment was cancelled. Your cart items have been saved.
            </p>
            <div className="space-y-3">
              <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white" onClick={() => navigate('/cart')}>
                Back to Cart
              </Button>
              <Button variant="outline" className="w-full" onClick={() => navigate('/')}>
                Continue Shopping
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <Router>
      <AppProvider>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/product/:id" element={<ProductDetailPage />} />
              <Route path="/cart" element={<CartPage />} />
              <Route path="/checkout/success" element={<CheckoutSuccessPage />} />
              <Route path="/checkout/cancel" element={<CheckoutCancelPage />} />
            </Routes>
          </main>
        </div>
      </AppProvider>
    </Router>
  );
}

export default App;