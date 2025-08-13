import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useTranslation } from '../i18n/translations';
import { Globe } from 'lucide-react';
import axios from 'axios';

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

const LanguageSwitcher = ({ className = "" }) => {
  const { currentLanguage, changeLanguage } = useTranslation();

  const updateLanguagePreference = async (language) => {
    try {
      const token = localStorage.getItem('accessToken');
      if (token) {
        // Update language preference on server if user is logged in
        await api.put('/api/profile/language', null, {
          params: { language }
        });
      }
    } catch (error) {
      console.error('Failed to update language preference:', error);
      // Continue anyway - language will still work locally
    }
  };

  const handleLanguageChange = async (language) => {
    changeLanguage(language);
    await updateLanguagePreference(language);
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <Globe className="h-4 w-4 text-gray-600" />
      <Select value={currentLanguage} onValueChange={handleLanguageChange}>
        <SelectTrigger className="w-20 h-8 text-sm">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="en">EN</SelectItem>
          <SelectItem value="ru">RU</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
};

export default LanguageSwitcher;