import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Users, 
  Package, 
  ShoppingBag, 
  DollarSign, 
  Settings,
  Plus,
  Edit,
  Trash2,
  Check,
  X,
  Clock,
  AlertCircle,
  Tag
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { Skeleton } from './ui/skeleton';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';

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

const AdminPanel = () => {
  const [sellers, setSellers] = useState([]);
  const [coupons, setCoupons] = useState([]);
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCouponModal, setShowCouponModal] = useState(false);
  const [showProductModal, setShowProductModal] = useState(false);
  const [editingCoupon, setEditingCoupon] = useState(null);
  const [editingProduct, setEditingProduct] = useState(null);
  
  const [couponForm, setCouponForm] = useState({
    code: '',
    type: 'percentage',
    value: '',
    scope: 'global',
    scope_value: '',
    min_order_amount: '',
    max_discount: '',
    usage_limit: '',
    usage_per_user: '',
    description: '',
    is_active: true
  });

  const [productForm, setProductForm] = useState({
    name: '',
    description: '',
    price: '',
    category: '',
    brand: '',
    inventory: '',
    images: '',
    tags: ''
  });

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      const [sellersRes, couponsRes, productsRes, ordersRes] = await Promise.all([
        api.get('/api/admin/sellers'),
        api.get('/api/admin/coupons'),
        api.get('/api/products?limit=50'),
        api.get('/api/admin/orders')
      ]);
      
      setSellers(sellersRes.data.sellers);
      setCoupons(couponsRes.data.coupons);
      setProducts(productsRes.data);
      setOrders(ordersRes.data.orders);
    } catch (error) {
      console.error('Error fetching admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSellerStatusUpdate = async (sellerId, status) => {
    try {
      await api.put(`/api/admin/sellers/${sellerId}/status`, null, {
        params: { status }
      });
      
      // Update local state
      setSellers(sellers.map(seller => 
        seller.user_id === sellerId ? { ...seller, status } : seller
      ));
      
      alert(`Seller ${status} successfully`);
    } catch (error) {
      console.error('Error updating seller status:', error);
      alert('Failed to update seller status');
    }
  };

  const handleCouponSubmit = async (e) => {
    e.preventDefault();
    try {
      const couponData = {
        ...couponForm,
        value: parseFloat(couponForm.value),
        min_order_amount: couponForm.min_order_amount ? parseFloat(couponForm.min_order_amount) : null,
        max_discount: couponForm.max_discount ? parseFloat(couponForm.max_discount) : null,
        usage_limit: couponForm.usage_limit ? parseInt(couponForm.usage_limit) : null,
        usage_per_user: couponForm.usage_per_user ? parseInt(couponForm.usage_per_user) : null
      };

      if (editingCoupon) {
        await api.put(`/api/admin/coupons/${editingCoupon.id}`, couponData);
      } else {
        await api.post('/api/admin/coupons', couponData);
      }

      setShowCouponModal(false);
      setEditingCoupon(null);
      resetCouponForm();
      fetchAdminData();
    } catch (error) {
      console.error('Error saving coupon:', error);
      alert(error.response?.data?.detail || 'Failed to save coupon');
    }
  };

  const handleEditCoupon = (coupon) => {
    setEditingCoupon(coupon);
    setCouponForm({
      code: coupon.code,
      type: coupon.type,
      value: coupon.value.toString(),
      scope: coupon.scope,
      scope_value: coupon.scope_value || '',
      min_order_amount: coupon.min_order_amount?.toString() || '',
      max_discount: coupon.max_discount?.toString() || '',
      usage_limit: coupon.usage_limit?.toString() || '',
      usage_per_user: coupon.usage_per_user?.toString() || '',
      description: coupon.description || '',
      is_active: coupon.is_active
    });
    setShowCouponModal(true);
  };

  const handleDeleteCoupon = async (couponId) => {
    if (!confirm('Are you sure you want to delete this coupon?')) return;
    
    try {
      await api.delete(`/api/admin/coupons/${couponId}`);
      setCoupons(coupons.filter(c => c.id !== couponId));
    } catch (error) {
      console.error('Error deleting coupon:', error);
      alert('Failed to delete coupon');
    }
  };

  const resetCouponForm = () => {
    setCouponForm({
      code: '',
      type: 'percentage',
      value: '',
      scope: 'global',
      scope_value: '',
      min_order_amount: '',
      max_discount: '',
      usage_limit: '',
      usage_per_user: '',
      description: '',
      is_active: true
    });
  };

  const resetProductForm = () => {
    setProductForm({
      name: '',
      description: '',
      price: '',
      category: '',
      brand: '',
      inventory: '',
      images: '',
      tags: ''
    });
  };

  const handleProductSubmit = async (e) => {
    e.preventDefault();
    try {
      const productData = {
        ...productForm,
        price: parseFloat(productForm.price),
        inventory: parseInt(productForm.inventory),
        images: productForm.images.split('\n').filter(url => url.trim()),
        tags: productForm.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };

      if (editingProduct) {
        await api.put(`/api/products/${editingProduct.id}`, productData);
      } else {
        await api.post('/api/products', productData);
      }

      setShowProductModal(false);
      setEditingProduct(null);
      resetProductForm();
      fetchAdminData();
      alert(`Product ${editingProduct ? 'updated' : 'created'} successfully!`);
    } catch (error) {
      console.error('Error saving product:', error);
      alert(error.response?.data?.detail || 'Failed to save product');
    }
  };

  const handleEditProduct = (product) => {
    setEditingProduct(product);
    setProductForm({
      name: product.name,
      description: product.description || '',
      price: product.price.toString(),
      category: product.category || '',
      brand: product.brand || '',
      inventory: product.inventory.toString(),
      images: (product.images || []).join('\n'),
      tags: (product.tags || []).join(', ')
    });
    setShowProductModal(true);
  };

  const handleDeleteProduct = async (productId) => {
    if (!confirm('Are you sure you want to delete this product?')) return;
    
    try {
      await api.delete(`/api/products/${productId}`);
      setProducts(products.filter(p => p.id !== productId));
      alert('Product deleted successfully!');
    } catch (error) {
      console.error('Error deleting product:', error);
      alert('Failed to delete product');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'suspended': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Skeleton className="h-8 w-48 mb-8" />
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <Skeleton className="h-8 w-16 mb-2" />
                  <Skeleton className="h-4 w-24" />
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-gray-900">{sellers.length}</p>
                  <p className="text-sm text-gray-600">Total Sellers</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Package className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-gray-900">{products.length}</p>
                  <p className="text-sm text-gray-600">Total Products</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <ShoppingBag className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-gray-900">{orders.length}</p>
                  <p className="text-sm text-gray-600">Total Orders</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <Tag className="h-6 w-6 text-yellow-600" />
                </div>
                <div className="ml-4">
                  <p className="text-2xl font-bold text-gray-900">{coupons.length}</p>
                  <p className="text-sm text-gray-600">Active Coupons</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="sellers" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="sellers">Sellers</TabsTrigger>
            <TabsTrigger value="products">Products</TabsTrigger>
            <TabsTrigger value="orders">Orders</TabsTrigger>
            <TabsTrigger value="coupons">Coupons</TabsTrigger>
          </TabsList>

          <TabsContent value="sellers" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Seller Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {sellers.map((seller) => (
                    <div key={seller.user_id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4 className="font-semibold">{seller.business_name}</h4>
                          <p className="text-sm text-gray-600">
                            {seller.user_name} ({seller.user_email})
                          </p>
                        </div>
                        <Badge className={getStatusColor(seller.status)}>
                          {seller.status.toUpperCase()}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                        <div>
                          <span className="text-gray-500">Commission:</span>
                          <p className="font-medium">{seller.commission_rate}%</p>
                        </div>
                        <div>
                          <span className="text-gray-500">Total Sales:</span>
                          <p className="font-medium">${seller.total_sales?.toFixed(2) || '0.00'}</p>
                        </div>
                        <div>
                          <span className="text-gray-500">Products:</span>
                          <p className="font-medium">{seller.total_products || 0}</p>
                        </div>
                        <div>
                          <span className="text-gray-500">Joined:</span>
                          <p className="font-medium">{new Date(seller.created_at).toLocaleDateString()}</p>
                        </div>
                      </div>

                      <div className="flex space-x-2">
                        {seller.status === 'pending' && (
                          <>
                            <Button 
                              size="sm" 
                              className="bg-green-600 hover:bg-green-700 text-white"
                              onClick={() => handleSellerStatusUpdate(seller.user_id, 'approved')}
                            >
                              <Check className="h-4 w-4 mr-1" />
                              Approve
                            </Button>
                            <Button 
                              size="sm" 
                              variant="destructive"
                              onClick={() => handleSellerStatusUpdate(seller.user_id, 'rejected')}
                            >
                              <X className="h-4 w-4 mr-1" />
                              Reject
                            </Button>
                          </>
                        )}
                        {seller.status === 'approved' && (
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleSellerStatusUpdate(seller.user_id, 'suspended')}
                          >
                            Suspend
                          </Button>
                        )}
                        {seller.status === 'suspended' && (
                          <Button 
                            size="sm" 
                            className="bg-green-600 hover:bg-green-700 text-white"
                            onClick={() => handleSellerStatusUpdate(seller.user_id, 'approved')}
                          >
                            Reactivate
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                  {sellers.length === 0 && (
                    <div className="text-center py-8">
                      <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No sellers registered yet</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="products" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Product Management ({products.length})</CardTitle>
                  <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Product
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse border border-gray-300">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="border border-gray-300 px-4 py-3 text-left">Image</th>
                        <th className="border border-gray-300 px-4 py-3 text-left">Name</th>
                        <th className="border border-gray-300 px-4 py-3 text-left">Category</th>
                        <th className="border border-gray-300 px-4 py-3 text-left">Price</th>
                        <th className="border border-gray-300 px-4 py-3 text-left">Stock</th>
                        <th className="border border-gray-300 px-4 py-3 text-left">Rating</th>
                        <th className="border border-gray-300 px-4 py-3 text-left">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {products.map((product) => (
                        <tr key={product.id} className="hover:bg-gray-50">
                          <td className="border border-gray-300 px-4 py-3">
                            <div className="w-12 h-12 bg-gray-100 rounded-md overflow-hidden">
                              {product.images?.[0] ? (
                                <img
                                  src={product.images[0]}
                                  alt={product.name}
                                  className="w-full h-full object-cover"
                                />
                              ) : (
                                <Package className="h-6 w-6 text-gray-400 m-3" />
                              )}
                            </div>
                          </td>
                          <td className="border border-gray-300 px-4 py-3">
                            <div className="font-medium line-clamp-2">{product.name}</div>
                            <div className="text-sm text-gray-600">{product.brand}</div>
                          </td>
                          <td className="border border-gray-300 px-4 py-3">
                            <Badge variant="secondary">{product.category}</Badge>
                          </td>
                          <td className="border border-gray-300 px-4 py-3">
                            <span className="font-semibold">${product.price?.toFixed(2)}</span>
                          </td>
                          <td className="border border-gray-300 px-4 py-3">
                            <span className={
                              product.inventory > 10 ? 'text-green-600' :
                              product.inventory > 0 ? 'text-yellow-600' : 'text-red-600'
                            }>
                              {product.inventory}
                            </span>
                          </td>
                          <td className="border border-gray-300 px-4 py-3">
                            <div className="flex items-center">
                              <span className="font-medium">{product.rating?.toFixed(1) || '0.0'}</span>
                              <span className="text-sm text-gray-500 ml-1">
                                ({product.reviews_count || 0})
                              </span>
                            </div>
                          </td>
                          <td className="border border-gray-300 px-4 py-3">
                            <div className="flex space-x-2">
                              <Button variant="outline" size="sm">
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button variant="outline" size="sm" className="text-red-600">
                                <Trash2 className="h-4 w-4" />
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
          </TabsContent>

          <TabsContent value="orders" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Order Management ({orders.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {orders.slice(0, 10).map((order) => (
                    <div key={order.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4 className="font-semibold">Order #{order.id.slice(0, 8)}</h4>
                          <p className="text-sm text-gray-600">
                            {new Date(order.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold">${order.total_amount?.toFixed(2)}</p>
                          <Badge className={`text-xs ${
                            order.status === 'delivered' ? 'bg-green-100 text-green-800' :
                            order.status === 'shipped' ? 'bg-blue-100 text-blue-800' :
                            order.status === 'processing' ? 'bg-purple-100 text-purple-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {order.status}
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="text-sm text-gray-600 mb-3">
                        {order.items?.length} items • Total: ${order.total_amount?.toFixed(2)}
                      </div>

                      <div className="flex justify-end space-x-2">
                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                        <select 
                          className="px-3 py-1 border border-gray-300 rounded text-sm"
                          value={order.status}
                          onChange={(e) => {
                            // Handle status update
                            console.log('Update order status:', e.target.value);
                          }}
                        >
                          <option value="pending">Pending</option>
                          <option value="processing">Processing</option>
                          <option value="shipped">Shipped</option>
                          <option value="delivered">Delivered</option>
                          <option value="cancelled">Cancelled</option>
                        </select>
                      </div>
                    </div>
                  ))}
                  {orders.length === 0 && (
                    <div className="text-center py-8">
                      <ShoppingBag className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No orders yet</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="coupons" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Coupon Management ({coupons.length})</CardTitle>
                  <Button 
                    onClick={() => {
                      resetCouponForm();
                      setEditingCoupon(null);
                      setShowCouponModal(true);
                    }}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Coupon
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {coupons.map((coupon) => (
                    <div key={coupon.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4 className="font-semibold text-lg">{coupon.code}</h4>
                          <p className="text-sm text-gray-600">{coupon.description}</p>
                        </div>
                        <div className="text-right">
                          <Badge className={coupon.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                            {coupon.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                        <div>
                          <span className="text-gray-500">Type:</span>
                          <p className="font-medium capitalize">{coupon.type}</p>
                        </div>
                        <div>
                          <span className="text-gray-500">Value:</span>
                          <p className="font-medium">
                            {coupon.type === 'percentage' ? `${coupon.value}%` : `$${coupon.value}`}
                          </p>
                        </div>
                        <div>
                          <span className="text-gray-500">Used:</span>
                          <p className="font-medium">
                            {coupon.used_count}/{coupon.usage_limit || '∞'}
                          </p>
                        </div>
                        <div>
                          <span className="text-gray-500">Min Order:</span>
                          <p className="font-medium">
                            {coupon.min_order_amount ? `$${coupon.min_order_amount}` : 'None'}
                          </p>
                        </div>
                      </div>

                      <div className="flex space-x-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleEditCoupon(coupon)}
                        >
                          <Edit className="h-4 w-4 mr-1" />
                          Edit
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          className="text-red-600"
                          onClick={() => handleDeleteCoupon(coupon.id)}
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          Delete
                        </Button>
                      </div>
                    </div>
                  ))}
                  {coupons.length === 0 && (
                    <div className="text-center py-8">
                      <Tag className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No coupons created yet</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Coupon Modal */}
        <Dialog open={showCouponModal} onOpenChange={setShowCouponModal}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>
                {editingCoupon ? 'Edit Coupon' : 'Create New Coupon'}
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCouponSubmit} className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="code">Coupon Code *</Label>
                  <Input
                    id="code"
                    value={couponForm.code}
                    onChange={(e) => setCouponForm({...couponForm, code: e.target.value.toUpperCase()})}
                    placeholder="WELCOME20"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="type">Type *</Label>
                  <Select value={couponForm.type} onValueChange={(value) => setCouponForm({...couponForm, type: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="percentage">Percentage</SelectItem>
                      <SelectItem value="fixed">Fixed Amount</SelectItem>
                      <SelectItem value="free_shipping">Free Shipping</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="value">
                    {couponForm.type === 'percentage' ? 'Percentage (%)' : 'Amount ($)'} *
                  </Label>
                  <Input
                    id="value"
                    type="number"
                    step="0.01"
                    value={couponForm.value}
                    onChange={(e) => setCouponForm({...couponForm, value: e.target.value})}
                    placeholder={couponForm.type === 'percentage' ? '20' : '10.00'}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="scope">Scope</Label>
                  <Select value={couponForm.scope} onValueChange={(value) => setCouponForm({...couponForm, scope: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="global">Global</SelectItem>
                      <SelectItem value="category">Category</SelectItem>
                      <SelectItem value="product">Product</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="min_order_amount">Min Order Amount ($)</Label>
                  <Input
                    id="min_order_amount"
                    type="number"
                    step="0.01"
                    value={couponForm.min_order_amount}
                    onChange={(e) => setCouponForm({...couponForm, min_order_amount: e.target.value})}
                    placeholder="50.00"
                  />
                </div>
                <div>
                  <Label htmlFor="max_discount">Max Discount ($)</Label>
                  <Input
                    id="max_discount"
                    type="number"
                    step="0.01"
                    value={couponForm.max_discount}
                    onChange={(e) => setCouponForm({...couponForm, max_discount: e.target.value})}
                    placeholder="100.00"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="usage_limit">Usage Limit</Label>
                  <Input
                    id="usage_limit"
                    type="number"
                    value={couponForm.usage_limit}
                    onChange={(e) => setCouponForm({...couponForm, usage_limit: e.target.value})}
                    placeholder="100"
                  />
                </div>
                <div>
                  <Label htmlFor="usage_per_user">Usage Per User</Label>
                  <Input
                    id="usage_per_user"
                    type="number"
                    value={couponForm.usage_per_user}
                    onChange={(e) => setCouponForm({...couponForm, usage_per_user: e.target.value})}
                    placeholder="1"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={couponForm.description}
                  onChange={(e) => setCouponForm({...couponForm, description: e.target.value})}
                  placeholder="Welcome discount for new users"
                  rows="3"
                />
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={couponForm.is_active}
                  onChange={(e) => setCouponForm({...couponForm, is_active: e.target.checked})}
                />
                <Label htmlFor="is_active">Active</Label>
              </div>

              <div className="flex justify-end space-x-4">
                <Button 
                  type="button" 
                  variant="outline"
                  onClick={() => setShowCouponModal(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white">
                  {editingCoupon ? 'Update Coupon' : 'Create Coupon'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default AdminPanel;