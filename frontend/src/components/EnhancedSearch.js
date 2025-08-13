import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, Clock, TrendingUp, Package } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const EnhancedSearch = ({ className = "" }) => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [recentSearches, setRecentSearches] = useState([]);
  const [trendingSearches] = useState([
    'iPhone', 'Samsung Galaxy', 'MacBook', 'AirPods', 'PlayStation', 'Nintendo Switch'
  ]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(false);
  const searchRef = useRef(null);
  const dropdownRef = useRef(null);

  useEffect(() => {
    // Load recent searches from localStorage
    const saved = localStorage.getItem('recentSearches');
    if (saved) {
      setRecentSearches(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    // Click outside handler
    const handleClickOutside = (event) => {
      if (
        searchRef.current && 
        !searchRef.current.contains(event.target) &&
        dropdownRef.current && 
        !dropdownRef.current.contains(event.target)
      ) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    // Fetch suggestions when typing
    if (searchQuery.trim().length > 2) {
      const delayedSearch = setTimeout(fetchSuggestions, 300);
      return () => clearTimeout(delayedSearch);
    } else {
      setSuggestions([]);
    }
  }, [searchQuery]);

  const fetchSuggestions = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/products/search?q=${encodeURIComponent(searchQuery)}&limit=6`);
      const products = response.data.products || response.data || [];
      setSuggestions(products);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query = searchQuery) => {
    if (!query.trim()) return;
    
    // Add to recent searches
    const newRecentSearches = [query, ...recentSearches.filter(s => s !== query)].slice(0, 5);
    setRecentSearches(newRecentSearches);
    localStorage.setItem('recentSearches', JSON.stringify(newRecentSearches));
    
    // Navigate to catalog with search
    navigate(`/catalog?q=${encodeURIComponent(query)}`);
    setShowDropdown(false);
    setSearchQuery('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSearch();
  };

  const handleInputFocus = () => {
    setShowDropdown(true);
  };

  const handleClearRecentSearches = () => {
    setRecentSearches([]);
    localStorage.removeItem('recentSearches');
  };

  const handleProductSelect = (product) => {
    navigate(`/product/${product.id}`);
    setShowDropdown(false);
    setSearchQuery('');
  };

  return (
    <div className={`relative ${className}`} ref={searchRef}>
      {/* Search Input */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            type="text"
            placeholder="Search for products, brands, categories..."
            className="pl-10 pr-12 w-full"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={handleInputFocus}
          />
          {searchQuery && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="absolute right-1 top-1/2 transform -translate-y-1/2 p-1 h-8 w-8"
              onClick={() => setSearchQuery('')}
            >
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>
      </form>

      {/* Search Dropdown */}
      {showDropdown && (
        <Card 
          ref={dropdownRef}
          className="absolute top-full mt-2 w-full z-50 shadow-lg max-h-96 overflow-hidden"
        >
          <CardContent className="p-0">
            {/* Loading */}
            {loading && (
              <div className="p-4 flex items-center justify-center">
                <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                <span className="ml-2 text-sm text-gray-600">Searching...</span>
              </div>
            )}

            {/* Product Suggestions */}
            {suggestions.length > 0 && (
              <div className="border-b border-gray-200">
                <div className="p-3 bg-gray-50 border-b border-gray-100">
                  <h4 className="text-sm font-medium text-gray-700 flex items-center">
                    <Package className="h-4 w-4 mr-2" />
                    Products
                  </h4>
                </div>
                <div className="max-h-48 overflow-y-auto">
                  {suggestions.map((product) => (
                    <div
                      key={product.id}
                      className="flex items-center p-3 hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => handleProductSelect(product)}
                    >
                      <div className="w-10 h-10 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                        <img
                          src={product.image_url || `https://via.placeholder.com/40?text=${encodeURIComponent(product.name.charAt(0))}`}
                          alt={product.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="ml-3 flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {product.name}
                        </p>
                        <div className="flex items-center mt-1">
                          {product.category && (
                            <Badge variant="secondary" className="text-xs mr-2">
                              {product.category}
                            </Badge>
                          )}
                          <span className="text-sm font-semibold text-gray-900">
                            ${product.price}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Searches */}
            {recentSearches.length > 0 && !searchQuery && (
              <div className="border-b border-gray-200">
                <div className="p-3 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
                  <h4 className="text-sm font-medium text-gray-700 flex items-center">
                    <Clock className="h-4 w-4 mr-2" />
                    Recent Searches
                  </h4>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleClearRecentSearches}
                    className="text-xs text-gray-500 hover:text-gray-700"
                  >
                    Clear
                  </Button>
                </div>
                <div className="py-2">
                  {recentSearches.map((search, index) => (
                    <div
                      key={index}
                      className="px-3 py-2 hover:bg-gray-50 cursor-pointer flex items-center transition-colors"
                      onClick={() => handleSearch(search)}
                    >
                      <Clock className="h-3 w-3 text-gray-400 mr-3" />
                      <span className="text-sm text-gray-700">{search}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Trending Searches */}
            {!searchQuery && (
              <div>
                <div className="p-3 bg-gray-50 border-b border-gray-100">
                  <h4 className="text-sm font-medium text-gray-700 flex items-center">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Trending
                  </h4>
                </div>
                <div className="py-2">
                  {trendingSearches.map((search, index) => (
                    <div
                      key={index}
                      className="px-3 py-2 hover:bg-gray-50 cursor-pointer flex items-center transition-colors"
                      onClick={() => handleSearch(search)}
                    >
                      <TrendingUp className="h-3 w-3 text-gray-400 mr-3" />
                      <span className="text-sm text-gray-700">{search}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* No Results */}
            {searchQuery && suggestions.length === 0 && !loading && (
              <div className="p-6 text-center">
                <Package className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600">No products found for "{searchQuery}"</p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-2"
                  onClick={() => handleSearch()}
                >
                  Search in catalog
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default EnhancedSearch;