import React, { useState } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Separator } from './ui/separator';
import { Eye, EyeOff, Phone, Mail, MapPin, User, Shield, Check, X } from 'lucide-react';
import { useTranslation } from '../i18n/translations';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const EnhancedRegistration = ({ onClose, onSuccess }) => {
  const { t } = useTranslation();
  const [step, setStep] = useState(1); // 1: Form, 2: Verification
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  // Form data
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    phone: '',
    // Shipping address
    fullName: '',
    addressLine1: '',
    addressLine2: '',
    city: '',
    state: '',
    postalCode: '',
    country: 'US',
    addressPhone: ''
  });

  // Verification states
  const [verificationCodes, setVerificationCodes] = useState({
    email: '',
    phone: ''
  });
  
  const [verificationStatus, setVerificationStatus] = useState({
    email: { sent: false, verified: false, code: '' },
    phone: { sent: false, verified: false, code: '' }
  });

  const [userToken, setUserToken] = useState('');

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(''); // Clear error when user types
  };

  const handleVerificationCodeChange = (type, value) => {
    setVerificationCodes(prev => ({ ...prev, [type]: value }));
  };

  const validateForm = () => {
    if (!formData.email || !formData.password || !formData.name) {
      setError('Please fill in all required fields');
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }

    if (formData.phone && !/^\+?[\d\s\-\(\)]+$/.test(formData.phone)) {
      setError('Please enter a valid phone number');
      return false;
    }

    return true;
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    setError('');

    try {
      // Prepare shipping address if provided
      const shippingAddress = formData.fullName ? {
        full_name: formData.fullName,
        address_line_1: formData.addressLine1,
        address_line_2: formData.addressLine2,
        city: formData.city,
        state: formData.state,
        postal_code: formData.postalCode,
        country: formData.country,
        phone: formData.addressPhone,
        is_default: true
      } : null;

      const registrationData = {
        email: formData.email,
        password: formData.password,
        name: formData.name,
        phone: formData.phone || null,
        shipping_address: shippingAddress
      };

      const response = await api.post('/api/auth/register-enhanced', registrationData);
      
      setUserToken(response.data.access_token);
      
      // Update verification status based on what was sent
      const newStatus = { ...verificationStatus };
      if (response.data.verification_sent.email) {
        newStatus.email = { 
          sent: true, 
          verified: false, 
          code: response.data.verification_sent.email.dev_code || '' 
        };
      }
      if (response.data.verification_sent.phone) {
        newStatus.phone = { 
          sent: true, 
          verified: false, 
          code: response.data.verification_sent.phone.dev_code || '' 
        };
      }
      setVerificationStatus(newStatus);

      setMessage(response.data.message);
      setStep(2); // Move to verification step

    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSendVerification = async (type) => {
    setLoading(true);
    setError('');

    try {
      const endpoint = type === 'email' ? '/api/auth/send-email-verification' : '/api/auth/send-phone-verification';
      const payload = type === 'email' 
        ? { email: formData.email }
        : { phone: formData.phone };

      const response = await api.post(endpoint, payload);
      
      setVerificationStatus(prev => ({
        ...prev,
        [type]: { 
          sent: true, 
          verified: false, 
          code: response.data.dev_code || '' 
        }
      }));

      setMessage(`Verification code sent to your ${type}`);

    } catch (error) {
      setError(error.response?.data?.detail || `Failed to send ${type} verification`);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async (type) => {
    if (!verificationCodes[type]) {
      setError('Please enter the verification code');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const endpoint = type === 'email' ? '/api/auth/verify-email' : '/api/auth/verify-phone';
      const payload = type === 'email'
        ? { email: formData.email, code: verificationCodes[type] }
        : { phone: formData.phone, code: verificationCodes[type] };

      await api.post(endpoint, payload);

      setVerificationStatus(prev => ({
        ...prev,
        [type]: { ...prev[type], verified: true }
      }));

      // Update user verification status in backend
      const updateData = {};
      updateData[`${type}_verified`] = true;
      
      await api.post('/api/auth/update-verification-status', null, {
        params: updateData,
        headers: { Authorization: `Bearer ${userToken}` }
      });

      setMessage(`${type.charAt(0).toUpperCase() + type.slice(1)} verified successfully!`);

      // Check if both verifications are done or if we can proceed
      const bothDone = (
        (!formData.email || verificationStatus.email.verified || type === 'email') &&
        (!formData.phone || verificationStatus.phone.verified || type === 'phone')
      );

      if (bothDone) {
        setTimeout(() => {
          onSuccess && onSuccess({
            token: userToken,
            message: 'Registration completed successfully!'
          });
        }, 1500);
      }

    } catch (error) {
      setError(error.response?.data?.detail || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSkipVerification = () => {
    onSuccess && onSuccess({
      token: userToken,
      message: 'Registration completed! You can verify your contacts later.'
    });
  };

  if (step === 1) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">
            {t('signup')} - Enhanced Registration
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleRegister} className="space-y-6">
            {error && (
              <Alert className="border-red-200 bg-red-50">
                <AlertDescription className="text-red-700">{error}</AlertDescription>
              </Alert>
            )}

            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg flex items-center">
                <User className="h-5 w-5 mr-2" />
                Personal Information
              </h3>
              
              <div>
                <Label htmlFor="email">{t('email')} *</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  required
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="name">{t('fullName')} *</Label>
                <Input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  required
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="phone">{t('phone')} (Optional)</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  placeholder="+1 (555) 123-4567"
                  className="mt-1"
                />
              </div>

              <div className="relative">
                <Label htmlFor="password">Password *</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    required
                    className="mt-1 pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-1 h-8 w-8 p-0"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <div>
                <Label htmlFor="confirmPassword">Confirm Password *</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                  required
                  className="mt-1"
                />
              </div>
            </div>

            <Separator />

            {/* Shipping Address */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg flex items-center">
                <MapPin className="h-5 w-5 mr-2" />
                Shipping Address (Optional)
              </h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="fullName">Full Name</Label>
                  <Input
                    id="fullName"
                    type="text"
                    value={formData.fullName}
                    onChange={(e) => handleInputChange('fullName', e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="addressPhone">Phone</Label>
                  <Input
                    id="addressPhone"
                    type="tel"
                    value={formData.addressPhone}
                    onChange={(e) => handleInputChange('addressPhone', e.target.value)}
                    className="mt-1"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="addressLine1">Address Line 1</Label>
                <Input
                  id="addressLine1"
                  type="text"
                  value={formData.addressLine1}
                  onChange={(e) => handleInputChange('addressLine1', e.target.value)}
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="addressLine2">Address Line 2</Label>
                <Input
                  id="addressLine2"
                  type="text"
                  value={formData.addressLine2}
                  onChange={(e) => handleInputChange('addressLine2', e.target.value)}
                  className="mt-1"
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    type="text"
                    value={formData.city}
                    onChange={(e) => handleInputChange('city', e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="state">State</Label>
                  <Input
                    id="state"
                    type="text"
                    value={formData.state}
                    onChange={(e) => handleInputChange('state', e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="postalCode">Postal Code</Label>
                  <Input
                    id="postalCode"
                    type="text"
                    value={formData.postalCode}
                    onChange={(e) => handleInputChange('postalCode', e.target.value)}
                    className="mt-1"
                  />
                </div>
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </Button>
          </form>
        </CardContent>
      </Card>
    );
  }

  // Step 2: Verification
  return (
    <Card className="w-full max-w-lg mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-center flex items-center justify-center">
          <Shield className="h-6 w-6 mr-2" />
          Verify Your Account
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {message && (
          <Alert className="border-green-200 bg-green-50">
            <AlertDescription className="text-green-700">{message}</AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert className="border-red-200 bg-red-50">
            <AlertDescription className="text-red-700">{error}</AlertDescription>
          </Alert>
        )}

        {/* Email Verification */}
        {formData.email && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Mail className="h-5 w-5 mr-2" />
                <span className="font-medium">Email Verification</span>
              </div>
              {verificationStatus.email.verified && (
                <Check className="h-5 w-5 text-green-600" />
              )}
            </div>
            
            <p className="text-sm text-gray-600">
              We sent a code to {formData.email}
            </p>
            
            {verificationStatus.email.code && (
              <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                <p className="text-sm text-yellow-800">
                  <strong>Development Code:</strong> {verificationStatus.email.code}
                </p>
              </div>
            )}

            {!verificationStatus.email.verified && (
              <div className="space-y-2">
                <Input
                  type="text"
                  placeholder="Enter email verification code"
                  value={verificationCodes.email}
                  onChange={(e) => handleVerificationCodeChange('email', e.target.value)}
                  maxLength={6}
                />
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleVerifyCode('email')}
                    disabled={loading || !verificationCodes.email}
                    className="flex-1"
                  >
                    Verify Email
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleSendVerification('email')}
                    disabled={loading}
                  >
                    Resend
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Phone Verification */}
        {formData.phone && (
          <div className="space-y-3">
            <Separator />
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Phone className="h-5 w-5 mr-2" />
                <span className="font-medium">Phone Verification</span>
              </div>
              {verificationStatus.phone.verified && (
                <Check className="h-5 w-5 text-green-600" />
              )}
            </div>
            
            <p className="text-sm text-gray-600">
              We sent a code to {formData.phone}
            </p>
            
            {verificationStatus.phone.code && (
              <div className="bg-green-50 border border-green-200 rounded p-3">
                <p className="text-sm text-green-800">
                  <strong>Development Code:</strong> {verificationStatus.phone.code}
                </p>
              </div>
            )}

            {!verificationStatus.phone.verified && (
              <div className="space-y-2">
                <Input
                  type="text"
                  placeholder="Enter SMS verification code"
                  value={verificationCodes.phone}
                  onChange={(e) => handleVerificationCodeChange('phone', e.target.value)}
                  maxLength={6}
                />
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleVerifyCode('phone')}
                    disabled={loading || !verificationCodes.phone}
                    className="flex-1"
                  >
                    Verify Phone
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleSendVerification('phone')}
                    disabled={loading}
                  >
                    Resend
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}

        <Separator />

        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleSkipVerification}
            className="flex-1"
          >
            Skip for Now
          </Button>
          {(!formData.email || verificationStatus.email.verified) && 
           (!formData.phone || verificationStatus.phone.verified) && (
            <Button
              onClick={handleSkipVerification}
              className="flex-1 bg-green-600 hover:bg-green-700"
            >
              Complete Registration
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default EnhancedRegistration;