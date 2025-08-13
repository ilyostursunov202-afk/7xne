import React, { useState } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Separator } from './ui/separator';
import { Mail, Phone, Eye, EyeOff, ArrowLeft, Shield, Key } from 'lucide-react';
import { useTranslation } from '../i18n/translations';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const ForgotPassword = ({ onClose, onSuccess }) => {
  const { t } = useTranslation();
  const [step, setStep] = useState(1); // 1: Enter identifier, 2: Enter code & new password
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const [formData, setFormData] = useState({
    identifier: '', // email or phone
    method: 'email', // 'email' or 'sms'
    code: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [devCode, setDevCode] = useState(''); // For development

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(''); // Clear error when user types
  };

  const detectIdentifierType = (identifier) => {
    return identifier.includes('@') ? 'email' : 'phone';
  };

  const handleSendResetCode = async (e) => {
    e.preventDefault();
    
    if (!formData.identifier.trim()) {
      setError('Please enter your email or phone number');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const detectedMethod = detectIdentifierType(formData.identifier);
      const requestData = {
        identifier: formData.identifier,
        method: formData.method || detectedMethod
      };

      const response = await api.post('/api/auth/forgot-password', requestData);
      
      setDevCode(response.data.dev_code || '');
      setMessage(response.data.message);
      setStep(2);

    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to send reset code');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();

    if (!formData.code.trim()) {
      setError('Please enter the verification code');
      return;
    }

    if (!formData.newPassword || formData.newPassword.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    if (formData.newPassword !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const requestData = {
        identifier: formData.identifier,
        code: formData.code,
        new_password: formData.newPassword
      };

      await api.post('/api/auth/reset-password', requestData);
      
      setMessage('Password reset successful! You can now log in with your new password.');
      
      setTimeout(() => {
        onSuccess && onSuccess('Password reset completed successfully!');
      }, 2000);

    } catch (error) {
      setError(error.response?.data?.detail || 'Password reset failed');
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    setLoading(true);
    setError('');

    try {
      const detectedMethod = detectIdentifierType(formData.identifier);
      const requestData = {
        identifier: formData.identifier,
        method: formData.method || detectedMethod
      };

      const response = await api.post('/api/auth/forgot-password', requestData);
      
      setDevCode(response.data.dev_code || '');
      setMessage('Verification code resent successfully');

    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to resend code');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToStep1 = () => {
    setStep(1);
    setError('');
    setMessage('');
    setFormData(prev => ({ ...prev, code: '', newPassword: '', confirmPassword: '' }));
  };

  if (step === 1) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center flex items-center justify-center">
            <Key className="h-6 w-6 mr-2" />
            {t('forgotPassword') || 'Forgot Password'}
          </CardTitle>
          <p className="text-center text-gray-600 text-sm">
            Enter your email or phone number to receive a password reset code
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSendResetCode} className="space-y-4">
            {error && (
              <Alert className="border-red-200 bg-red-50">
                <AlertDescription className="text-red-700">{error}</AlertDescription>
              </Alert>
            )}

            <div>
              <Label htmlFor="identifier">Email or Phone Number</Label>
              <Input
                id="identifier"
                type="text"
                value={formData.identifier}
                onChange={(e) => handleInputChange('identifier', e.target.value)}
                placeholder="Enter your email or phone number"
                required
                className="mt-1"
              />
            </div>

            {/* Method Selection */}
            {formData.identifier && !formData.identifier.includes('@') && (
              <div className="space-y-2">
                <Label>Preferred Method</Label>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant={formData.method === 'sms' ? 'default' : 'outline'}
                    onClick={() => handleInputChange('method', 'sms')}
                    className="flex-1"
                  >
                    <Phone className="h-4 w-4 mr-2" />
                    SMS
                  </Button>
                  <Button
                    type="button"
                    variant={formData.method === 'email' ? 'default' : 'outline'}
                    onClick={() => handleInputChange('method', 'email')}
                    className="flex-1"
                  >
                    <Mail className="h-4 w-4 mr-2" />
                    Email
                  </Button>
                </div>
              </div>
            )}

            <Button
              type="submit"
              disabled={loading || !formData.identifier}
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {loading ? 'Sending...' : 'Send Reset Code'}
            </Button>

            <div className="text-center">
              <Button
                type="button"
                variant="link"
                onClick={onClose}
                className="text-sm"
              >
                Back to Login
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    );
  }

  // Step 2: Enter code and new password
  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-center flex items-center justify-center">
          <Shield className="h-6 w-6 mr-2" />
          Reset Password
        </CardTitle>
        <p className="text-center text-gray-600 text-sm">
          Enter the verification code and your new password
        </p>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleResetPassword} className="space-y-4">
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

          {/* Show development code */}
          {devCode && (
            <Alert className="border-blue-200 bg-blue-50">
              <AlertDescription className="text-blue-700">
                <strong>Development Code:</strong> {devCode}
              </AlertDescription>
            </Alert>
          )}

          <div>
            <Label htmlFor="identifier-display">Sent to:</Label>
            <div className="flex items-center mt-1 p-2 bg-gray-50 rounded border">
              {formData.identifier.includes('@') ? (
                <Mail className="h-4 w-4 mr-2 text-gray-500" />
              ) : (
                <Phone className="h-4 w-4 mr-2 text-gray-500" />
              )}
              <span className="text-sm text-gray-700">{formData.identifier}</span>
            </div>
          </div>

          <div>
            <Label htmlFor="code">Verification Code</Label>
            <Input
              id="code"
              type="text"
              value={formData.code}
              onChange={(e) => handleInputChange('code', e.target.value)}
              placeholder="Enter 6-digit code"
              maxLength={6}
              required
              className="mt-1"
            />
          </div>

          <Separator />

          <div>
            <Label htmlFor="newPassword">New Password</Label>
            <div className="relative">
              <Input
                id="newPassword"
                type={showPassword ? "text" : "password"}
                value={formData.newPassword}
                onChange={(e) => handleInputChange('newPassword', e.target.value)}
                placeholder="Enter new password"
                required
                minLength={6}
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
            <p className="text-xs text-gray-500 mt-1">Must be at least 6 characters long</p>
          </div>

          <div>
            <Label htmlFor="confirmPassword">Confirm New Password</Label>
            <Input
              id="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
              placeholder="Confirm new password"
              required
              className="mt-1"
            />
          </div>

          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleBackToStep1}
              className="flex items-center"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <Button
              type="submit"
              disabled={loading || !formData.code || !formData.newPassword}
              className="flex-1 bg-green-600 hover:bg-green-700"
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </Button>
          </div>

          <div className="text-center">
            <Button
              type="button"
              variant="link"
              onClick={handleResendCode}
              disabled={loading}
              className="text-sm"
            >
              Didn't receive the code? Resend
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default ForgotPassword;