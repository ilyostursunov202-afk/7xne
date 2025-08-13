import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { Search, Filter, Grid, List, SortAsc, SortDesc, Star, Heart, ShoppingCart, Package, Smartphone, Laptop, Headphones, Camera, Watch, Gamepad2, Tv, Speaker, Tablet, Monitor, Keyboard, Mouse, Printer, Router, Flashlight } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardFooter } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { useTranslation } from '../i18n/translations';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const CatalogPage = ({ addToCart, wishlist = [], onToggleWishlist }) => {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid');
  
  // Search and filter states
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || '');
  const [selectedBrand, setSelectedBrand] = useState(searchParams.get('brand') || '');
  const [priceRange, setPriceRange] = useState(searchParams.get('price') || '');
  const [sortBy, setSortBy] = useState(searchParams.get('sort') || 'name');
  const [minRating, setMinRating] = useState(searchParams.get('rating') || '');

  // Electronics categories with icons
  const electronicsCategories = [
    { id: 'smartphones', name: 'Smartphones', icon: Smartphone, nameRu: 'Смартфоны' },
    { id: 'laptops', name: 'Laptops & Computers', icon: Laptop, nameRu: 'Ноутбуки и компьютеры' },
    { id: 'headphones', name: 'Headphones & Audio', icon: Headphones, nameRu: 'Наушники и аудио' },
    { id: 'cameras', name: 'Cameras & Photography', icon: Camera, nameRu: 'Камеры и фотография' },
    { id: 'smartwatches', name: 'Smart Watches', icon: Watch, nameRu: 'Умные часы' },
    { id: 'gaming', name: 'Gaming & Consoles', icon: Gamepad2, nameRu: 'Игры и консоли' },
    { id: 'tv-entertainment', name: 'TV & Entertainment', icon: Tv, nameRu: 'ТВ и развлечения' },
    { id: 'speakers', name: 'Speakers & Sound', icon: Speaker, nameRu: 'Колонки и звук' },
    { id: 'tablets', name: 'Tablets & E-readers', icon: Tablet, nameRu: 'Планшеты и электронные книги' },
    { id: 'monitors', name: 'Monitors & Displays', icon: Monitor, nameRu: 'Мониторы и дисплеи' },
    { id: 'accessories', name: 'Accessories', icon: Package, nameRu: 'Аксессуары' },
    { id: 'smart-home', name: 'Smart Home', icon: Router, nameRu: 'Умный дом' }
  ];

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    updateURL();
    fetchProducts();
  }, [searchQuery, selectedCategory, selectedBrand, priceRange, sortBy, minRating]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [productsRes, categoriesRes, brandsRes] = await Promise.all([
        api.get('/api/products/search?limit=50'),  // Use search endpoint for consistency
        api.get('/api/categories'),
        api.get('/api/brands')
      ]);
      
      setProducts(productsRes.data.products || productsRes.data || []);
      setCategories(categoriesRes.data.categories || []);
      setBrands(brandsRes.data.brands || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append('q', searchQuery);
      if (selectedCategory) params.append('category', selectedCategory);
      if (selectedBrand) params.append('brand', selectedBrand);
      if (priceRange) params.append('price_range', priceRange);
      if (sortBy) params.append('sort', sortBy);
      if (minRating) params.append('min_rating', minRating);
      
      const response = await api.get(`/api/products/search?${params.toString()}`);
      setProducts(response.data.products || response.data || []);
    } catch (error) {
      console.error('Error fetching products:', error);
      setProducts([]);
    }
  };

  const updateURL = () => {
    const params = new URLSearchParams();
    if (searchQuery) params.append('q', searchQuery);
    if (selectedCategory) params.append('category', selectedCategory);
    if (selectedBrand) params.append('brand', selectedBrand);
    if (priceRange) params.append('price', priceRange);
    if (sortBy) params.append('sort', sortBy);
    if (minRating) params.append('rating', minRating);
    
    setSearchParams(params);
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedCategory('');
    setSelectedBrand('');
    setPriceRange('');
    setSortBy('name');
    setMinRating('');
    setSearchParams({});
  };

  const isWishlisted = (productId) => {
    return Array.isArray(wishlist) && wishlist.some(item => 
      (typeof item === 'string' ? item : item.id || item.product_id) === productId
    );
  };

  const handleAddToCart = async (product) => {
    if (addToCart) {
      await addToCart(product.id, 1);
    }
  };

  const getCategoryIcon = (categoryName) => {
    const category = electronicsCategories.find(cat => 
      cat.name.toLowerCase().includes(categoryName.toLowerCase()) ||
      categoryName.toLowerCase().includes(cat.id)
    );
    return category ? category.icon : Package;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Electronics Catalog</h1>
              <p className="text-gray-600 mt-2">Discover the latest in technology and electronics</p>
            </div>
            
            {/* Enhanced Search */}
            <div className="flex flex-col sm:flex-row gap-3 lg:w-1/2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  type="text"
                  placeholder="Search for products, brands, models..."
                  className="pl-10 pr-4"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Button
                onClick={fetchProducts}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                <Search className="h-4 w-4 mr-2" />
                Search
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar Filters */}
          <div className="lg:w-1/4">
            <Card className="sticky top-4">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900 flex items-center">
                    <Filter className="h-4 w-4 mr-2" />
                    Filters
                  </h3>
                  <Button variant="ghost" size="sm" onClick={handleClearFilters}>
                    Clear All
                  </Button>
                </div>
              </div>
              
              <div className="p-6 space-y-6">
                {/* Categories */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Category
                  </label>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {electronicsCategories.map((category) => {
                      const IconComponent = category.icon;
                      return (
                        <div
                          key={category.id}
                          className={`flex items-center p-2 rounded-lg cursor-pointer transition-colors ${
                            selectedCategory === category.id
                              ? 'bg-blue-50 text-blue-700 border border-blue-200'
                              : 'hover:bg-gray-50'
                          }`}
                          onClick={() => setSelectedCategory(selectedCategory === category.id ? '' : category.id)}
                        >
                          <IconComponent className="h-4 w-4 mr-3 text-gray-500" />
                          <span className="text-sm">{category.name}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <Separator />

                {/* Brands */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Brand
                  </label>
                  <Select value={selectedBrand} onValueChange={setSelectedBrand}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Brands" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All Brands</SelectItem>
                      {brands.map((brand) => (
                        <SelectItem key={brand} value={brand}>
                          {brand}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <Separator />

                {/* Price Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Price Range
                  </label>
                  <Select value={priceRange} onValueChange={setPriceRange}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Prices" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All Prices</SelectItem>
                      <SelectItem value="0-50">$0 - $50</SelectItem>
                      <SelectItem value="50-100">$50 - $100</SelectItem>
                      <SelectItem value="100-250">$100 - $250</SelectItem>
                      <SelectItem value="250-500">$250 - $500</SelectItem>
                      <SelectItem value="500-1000">$500 - $1,000</SelectItem>
                      <SelectItem value="1000+">$1,000+</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Separator />

                {/* Rating */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Minimum Rating
                  </label>
                  <Select value={minRating} onValueChange={setMinRating}>
                    <SelectTrigger>
                      <SelectValue placeholder="Any Rating" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Any Rating</SelectItem>
                      <SelectItem value="4">4+ Stars</SelectItem>
                      <SelectItem value="3">3+ Stars</SelectItem>
                      <SelectItem value="2">2+ Stars</SelectItem>
                      <SelectItem value="1">1+ Stars</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:w-3/4">
            {/* Toolbar */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
              <div className="flex items-center gap-4">
                <span className="text-gray-600">
                  {products.length} products found
                </span>
                {(searchQuery || selectedCategory || selectedBrand || priceRange || minRating) && (
                  <Button variant="outline" size="sm" onClick={handleClearFilters}>
                    Clear Filters
                  </Button>
                )}
              </div>
              
              <div className="flex items-center gap-4">
                {/* Sort */}
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="name">Name A-Z</SelectItem>
                    <SelectItem value="name_desc">Name Z-A</SelectItem>
                    <SelectItem value="price">Price Low-High</SelectItem>
                    <SelectItem value="price_desc">Price High-Low</SelectItem>
                    <SelectItem value="rating">Best Rating</SelectItem>
                    <SelectItem value="newest">Newest</SelectItem>
                  </SelectContent>
                </Select>

                {/* View Toggle */}
                <div className="flex border border-gray-300 rounded-lg">
                  <Button
                    variant={viewMode === 'grid' ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('grid')}
                    className="rounded-r-none"
                  >
                    <Grid className="h-4 w-4" />
                  </Button>
                  <Button
                    variant={viewMode === 'list' ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('list')}
                    className="rounded-l-none"
                  >
                    <List className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>

            {/* Products Grid/List */}
            {products.length === 0 ? (
              <div className="text-center py-12">
                <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No products found</h3>
                <p className="text-gray-500">Try adjusting your search or filters</p>
              </div>
            ) : (
              <div className={viewMode === 'grid' 
                ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
                : 'space-y-4'
              }>
                {products.map((product) => {
                  const IconComponent = getCategoryIcon(product.category || '');
                  return (
                    <Card 
                      key={product.id} 
                      className={`group cursor-pointer hover:shadow-lg transition-all duration-200 ${
                        viewMode === 'list' ? 'flex flex-row' : ''
                      }`}
                    >
                      <div className={viewMode === 'list' ? 'w-48 flex-shrink-0' : ''}>
                        <div className="aspect-square bg-gray-100 rounded-t-lg overflow-hidden">
                          <img
                            src={product.image_url || `https://via.placeholder.com/300?text=${encodeURIComponent(product.name)}`}
                            alt={product.name}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                          />
                        </div>
                      </div>
                      
                      <div className={`p-4 flex-1 ${viewMode === 'list' ? 'flex flex-col justify-between' : ''}`}>
                        <div>
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center">
                              <IconComponent className="h-4 w-4 text-gray-400 mr-2" />
                              <Badge variant="secondary" className="text-xs">
                                {product.category}
                              </Badge>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                onToggleWishlist && onToggleWishlist(product.id);
                              }}
                              className="p-1"
                            >
                              <Heart className={`h-4 w-4 ${
                                isWishlisted(product.id) 
                                  ? 'fill-red-500 text-red-500' 
                                  : 'text-gray-400 hover:text-red-500'
                              }`} />
                            </Button>
                          </div>
                          
                          <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                            {product.name}
                          </h3>
                          
                          {product.brand && (
                            <p className="text-sm text-gray-600 mb-2">{product.brand}</p>
                          )}
                          
                          <div className="flex items-center mb-2">
                            <div className="flex items-center">
                              {[...Array(5)].map((_, i) => (
                                <Star
                                  key={i}
                                  className={`h-3 w-3 ${
                                    i < Math.floor(product.rating || 0)
                                      ? 'text-yellow-400 fill-current'
                                      : 'text-gray-300'
                                  }`}
                                />
                              ))}
                            </div>
                            <span className="text-xs text-gray-500 ml-2">
                              ({product.reviews_count || 0})
                            </span>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between mt-4">
                          <div>
                            <span className="text-lg font-bold text-gray-900">
                              ${product.price}
                            </span>
                            {product.original_price && product.original_price > product.price && (
                              <span className="text-sm text-gray-500 line-through ml-2">
                                ${product.original_price}
                              </span>
                            )}
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <Link to={`/product/${product.id}`}>
                              <Button variant="outline" size="sm">
                                View
                              </Button>
                            </Link>
                            <Button
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleAddToCart(product);
                              }}
                              className="bg-blue-600 hover:bg-blue-700"
                            >
                              <ShoppingCart className="h-4 w-4 mr-1" />
                              Add
                            </Button>
                          </div>
                        </div>
                      </div>
                    </Card>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CatalogPage;