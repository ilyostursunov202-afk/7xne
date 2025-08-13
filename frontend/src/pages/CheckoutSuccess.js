import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import axios from 'axios';

const CheckoutSuccess = () => {
  const [searchParams] = useSearchParams();
  const [paymentStatus, setPaymentStatus] = useState('checking');
  const [orderDetails, setOrderDetails] = useState(null);
  const [error, setError] = useState('');
  const sessionId = searchParams.get('session_id');

  const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.VITE_BACKEND_URL;

  const pollPaymentStatus = async (attempts = 0) => {
    const maxAttempts = 10;
    const pollInterval = 2000; // 2 seconds

    if (attempts >= maxAttempts) {
      setError('Payment status check timed out. Please check your email for confirmation.');
      setPaymentStatus('timeout');
      return;
    }

    try {
      const response = await axios.get(`${backendUrl}/api/checkout/status/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      });

      const data = response.data;
      
      if (data.payment_status === 'paid') {
        setPaymentStatus('success');
        setOrderDetails(data);
        return;
      } else if (data.status === 'expired') {
        setPaymentStatus('expired');
        setError('Payment session expired. Please try again.');
        return;
      }

      // If payment is still pending, continue polling
      setPaymentStatus('processing');
      setTimeout(() => pollPaymentStatus(attempts + 1), pollInterval);
    } catch (error) {
      console.error('Error checking payment status:', error);
      setError('Error checking payment status. Please try again.');
      setPaymentStatus('error');
    }
  };

  useEffect(() => {
    if (sessionId) {
      pollPaymentStatus();
    } else {
      setError('No session ID found in URL');
      setPaymentStatus('error');
    }
  }, [sessionId]);

  const renderContent = () => {
    switch (paymentStatus) {
      case 'checking':
      case 'processing':
        return (
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              {paymentStatus === 'checking' ? 'Checking payment status...' : 'Payment is being processed...'}
            </h2>
            <p className="text-gray-600">Please wait while we confirm your payment.</p>
          </div>
        );

      case 'success':
        return (
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
              <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Payment Successful!</h2>
            <p className="text-gray-600 mb-6">Thank you for your purchase. Your order has been confirmed.</p>
            
            {orderDetails && (
              <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left">
                <h3 className="font-semibold text-lg mb-3">Order Summary</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Session ID:</span>
                    <span className="font-mono text-sm">{sessionId.slice(0, 20)}...</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Amount:</span>
                    <span className="font-semibold">
                      ${(orderDetails.amount_total / 100).toFixed(2)} {orderDetails.currency?.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Status:</span>
                    <span className="text-green-600 font-semibold">Paid</span>
                  </div>
                </div>
              </div>
            )}
            
            <div className="space-y-3">
              <Link 
                to="/orders" 
                className="w-full inline-flex justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                View My Orders
              </Link>
              <Link 
                to="/" 
                className="w-full inline-flex justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Continue Shopping
              </Link>
            </div>
          </div>
        );

      case 'expired':
      case 'error':
      case 'timeout':
        return (
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
              <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Payment Issue</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            
            <div className="space-y-3">
              <Link 
                to="/cart" 
                className="w-full inline-flex justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Return to Cart
              </Link>
              <Link 
                to="/contact" 
                className="w-full inline-flex justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Contact Support
              </Link>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
        {renderContent()}
      </div>
    </div>
  );
};

export default CheckoutSuccess;