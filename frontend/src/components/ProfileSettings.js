import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Separator } from './ui/separator';
import { Camera, Save, Lock, User, Globe, Upload } from 'lucide-react';
import { useTranslation } from '../i18n/translations';
import LanguageSwitcher from './LanguageSwitcher';

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

const ProfileSettings = ({ user, onUserUpdate }) => {
  const { t } = useTranslation();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);
  
  // Profile form state
  const [profileForm, setProfileForm] = useState({
    name: '',
    email: '',
    phone: ''
  });
  
  // Password form state
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/profile');
      setProfile(response.data);
      setProfileForm({
        name: response.data.name || '',
        email: response.data.email || '',
        phone: response.data.phone || ''
      });
    } catch (error) {
      setError('Failed to load profile');
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    try {
      const response = await api.put('/api/profile', profileForm);
      setProfile(response.data);
      
      // Update user in parent component and localStorage
      if (onUserUpdate) {
        onUserUpdate(response.data);
      }
      localStorage.setItem('user', JSON.stringify(response.data));
      
      setMessage(t('profileUpdated'));
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setError('New passwords do not match');
      setLoading(false);
      return;
    }

    if (passwordForm.newPassword.length < 6) {
      setError('New password must be at least 6 characters long');
      setLoading(false);
      return;
    }

    try {
      await api.put('/api/profile/password', null, {
        params: {
          old_password: passwordForm.currentPassword,
          new_password: passwordForm.newPassword
        }
      });
      
      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      
      setMessage(t('passwordChanged'));
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file');
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5MB');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      setMessage('');
      setError('');

      const response = await api.post('/api/profile/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Update profile with new avatar
      const updatedProfile = { ...profile, avatar: response.data.avatar_url };
      setProfile(updatedProfile);
      
      if (onUserUpdate) {
        onUserUpdate(updatedProfile);
      }
      localStorage.setItem('user', JSON.stringify(updatedProfile));
      
      setMessage(t('avatarUploaded'));
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to upload avatar');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !profile) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{t('profileSettings')}</h1>
          <p className="text-gray-600 mt-2">Manage your account settings and preferences</p>
        </div>

        {message && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <AlertDescription className="text-green-700">{message}</AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertDescription className="text-red-700">{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Profile Overview */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <User className="h-5 w-5 mr-2" />
                  Profile Overview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Avatar Section */}
                <div className="text-center">
                  <div className="relative inline-block">
                    <Avatar className="w-24 h-24">
                      <AvatarImage 
                        src={profile?.avatar} 
                        alt={profile?.name} 
                        className="object-cover"
                      />
                      <AvatarFallback className="text-2xl">
                        {profile?.name?.charAt(0)?.toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <Button
                      variant="outline"
                      size="sm"
                      className="absolute bottom-0 right-0 rounded-full p-2"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <Camera className="h-4 w-4" />
                    </Button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarUpload}
                      className="hidden"
                    />
                  </div>
                  <p className="text-sm text-gray-600 mt-2">
                    Click the camera icon to upload a new avatar
                  </p>
                </div>

                <Separator />

                {/* Basic Info */}
                <div className="space-y-3">
                  <div>
                    <Label className="text-sm font-medium text-gray-600">{t('fullName')}</Label>
                    <p className="text-gray-900">{profile?.name}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-600">{t('email')}</Label>
                    <p className="text-gray-900">{profile?.email}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-600">Role</Label>
                    <p className="text-gray-900 capitalize">{profile?.role}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-600">Member Since</Label>
                    <p className="text-gray-900">
                      {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                </div>

                <Separator />

                {/* Language Switcher */}
                <div>
                  <Label className="text-sm font-medium text-gray-600 mb-2 block">{t('language')}</Label>
                  <LanguageSwitcher className="justify-start" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Settings Forms */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="profile" className="space-y-6">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="profile" className="flex items-center">
                  <User className="h-4 w-4 mr-2" />
                  {t('personalInfo')}
                </TabsTrigger>
                <TabsTrigger value="password" className="flex items-center">
                  <Lock className="h-4 w-4 mr-2" />
                  {t('changePassword')}
                </TabsTrigger>
              </TabsList>

              <TabsContent value="profile">
                <Card>
                  <CardHeader>
                    <CardTitle>{t('personalInfo')}</CardTitle>
                    <p className="text-sm text-gray-600">
                      Update your personal information and contact details
                    </p>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleProfileSubmit} className="space-y-6">
                      <div>
                        <Label htmlFor="name">{t('fullName')} *</Label>
                        <Input
                          id="name"
                          type="text"
                          value={profileForm.name}
                          onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                          required
                          className="mt-1"
                        />
                      </div>

                      <div>
                        <Label htmlFor="email">{t('email')} *</Label>
                        <Input
                          id="email"
                          type="email"
                          value={profileForm.email}
                          onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                          required
                          className="mt-1"
                          disabled // Email usually shouldn't be changed easily
                        />
                        <p className="text-sm text-gray-500 mt-1">
                          Contact support to change your email address
                        </p>
                      </div>

                      <div>
                        <Label htmlFor="phone">{t('phone')}</Label>
                        <Input
                          id="phone"
                          type="tel"
                          value={profileForm.phone}
                          onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                          className="mt-1"
                          placeholder="+1 (555) 123-4567"
                        />
                      </div>

                      <Button type="submit" disabled={loading} className="w-full">
                        <Save className="h-4 w-4 mr-2" />
                        {loading ? t('loading') : t('save')}
                      </Button>
                    </form>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="password">
                <Card>
                  <CardHeader>
                    <CardTitle>{t('changePassword')}</CardTitle>
                    <p className="text-sm text-gray-600">
                      Update your password to keep your account secure
                    </p>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handlePasswordSubmit} className="space-y-6">
                      <div>
                        <Label htmlFor="currentPassword">{t('currentPassword')} *</Label>
                        <Input
                          id="currentPassword"
                          type="password"
                          value={passwordForm.currentPassword}
                          onChange={(e) => setPasswordForm({ ...passwordForm, currentPassword: e.target.value })}
                          required
                          className="mt-1"
                        />
                      </div>

                      <div>
                        <Label htmlFor="newPassword">{t('newPassword')} *</Label>
                        <Input
                          id="newPassword"
                          type="password"
                          value={passwordForm.newPassword}
                          onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                          required
                          minLength="6"
                          className="mt-1"
                        />
                        <p className="text-sm text-gray-500 mt-1">
                          Password must be at least 6 characters long
                        </p>
                      </div>

                      <div>
                        <Label htmlFor="confirmPassword">{t('confirmPassword')} *</Label>
                        <Input
                          id="confirmPassword"
                          type="password"
                          value={passwordForm.confirmPassword}
                          onChange={(e) => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
                          required
                          minLength="6"
                          className="mt-1"
                        />
                      </div>

                      <Button type="submit" disabled={loading} className="w-full">
                        <Lock className="h-4 w-4 mr-2" />
                        {loading ? t('loading') : t('changePassword')}
                      </Button>
                    </form>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileSettings;