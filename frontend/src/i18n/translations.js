// Multi-language support for English and Russian
export const translations = {
  en: {
    // Common
    loading: "Loading...",
    save: "Save",
    cancel: "Cancel",
    delete: "Delete",
    edit: "Edit",
    add: "Add",
    search: "Search",
    filter: "Filter",
    
    // Navigation
    home: "Home",
    products: "Products",
    cart: "Cart",
    wishlist: "Wishlist",
    profile: "Profile",
    orders: "Order History",
    admin: "Admin Panel",
    logout: "Logout",
    login: "Login",
    signup: "Sign Up",
    
    // Admin Panel
    dashboard: "Dashboard",
    users: "Users",
    sellers: "Sellers",
    coupons: "Coupons",
    statistics: "Statistics",
    userManagement: "User Management",
    totalUsers: "Total Users",
    activeUsers: "Active Users",
    totalOrders: "Total Orders",
    totalRevenue: "Total Revenue",
    topProducts: "Top Selling Products",
    recentOrders: "Recent Orders",
    recentActions: "Recent Admin Actions",
    blockUser: "Block User",
    activateUser: "Activate User",
    changeRole: "Change Role",
    viewDetails: "View Details",
    
    // Profile
    profileSettings: "Profile Settings",
    personalInfo: "Personal Information",
    fullName: "Full Name",
    email: "Email",
    phone: "Phone",
    avatar: "Avatar",
    language: "Language",
    changePassword: "Change Password",
    currentPassword: "Current Password",
    newPassword: "New Password",
    confirmPassword: "Confirm Password",
    uploadAvatar: "Upload Avatar",
    
    // User roles
    customer: "Customer",
    seller: "Seller",
    admin: "Admin",
    
    // Status
    active: "Active",
    blocked: "Blocked",
    pending: "Pending",
    approved: "Approved",
    rejected: "Rejected",
    
    // Messages
    userBlocked: "User blocked successfully",
    userActivated: "User activated successfully",
    roleChanged: "User role updated successfully",
    profileUpdated: "Profile updated successfully",
    passwordChanged: "Password changed successfully",
    avatarUploaded: "Avatar uploaded successfully",
    languageChanged: "Language preference updated",
    
    // Products
    addToCart: "Add to Cart",
    addToWishlist: "Add to Wishlist",
    inStock: "In Stock",
    outOfStock: "Out of Stock",
    price: "Price",
    category: "Category",
    brand: "Brand",
    rating: "Rating",
    reviews: "Reviews",
    
    // Cart & Checkout
    shoppingCart: "Shopping Cart",
    proceedToCheckout: "Proceed to Checkout",
    continueShopping: "Continue Shopping",
    removeFromCart: "Remove from Cart",
    quantity: "Quantity",
    subtotal: "Subtotal",
    shipping: "Shipping",
    tax: "Tax",
    total: "Total"
  },
  ru: {
    // Common
    loading: "Загрузка...",
    save: "Сохранить",
    cancel: "Отмена",
    delete: "Удалить",
    edit: "Редактировать",
    add: "Добавить",
    search: "Поиск",
    filter: "Фильтр",
    
    // Navigation
    home: "Главная",
    products: "Товары",
    cart: "Корзина",
    wishlist: "Избранное",
    profile: "Профиль",
    orders: "История заказов",
    admin: "Панель администратора",
    logout: "Выйти",
    login: "Войти",
    signup: "Регистрация",
    
    // Admin Panel
    dashboard: "Панель управления",
    users: "Пользователи",
    sellers: "Продавцы",
    coupons: "Купоны",
    statistics: "Статистика",
    userManagement: "Управление пользователями",
    totalUsers: "Всего пользователей",
    activeUsers: "Активные пользователи",
    totalOrders: "Всего заказов",
    totalRevenue: "Общая выручка",
    topProducts: "Популярные товары",
    recentOrders: "Последние заказы",
    recentActions: "Последние действия администратора",
    blockUser: "Заблокировать пользователя",
    activateUser: "Активировать пользователя",
    changeRole: "Изменить роль",
    viewDetails: "Просмотреть детали",
    
    // Profile
    profileSettings: "Настройки профиля",
    personalInfo: "Личная информация",
    fullName: "Полное имя",
    email: "Электронная почта",
    phone: "Телефон",
    avatar: "Аватар",
    language: "Язык",
    changePassword: "Изменить пароль",
    currentPassword: "Текущий пароль",
    newPassword: "Новый пароль",
    confirmPassword: "Подтвердить пароль",
    uploadAvatar: "Загрузить аватар",
    
    // User roles
    customer: "Покупатель",
    seller: "Продавец",
    admin: "Администратор",
    
    // Status
    active: "Активен",
    blocked: "Заблокирован",
    pending: "Ожидает",
    approved: "Одобрен",
    rejected: "Отклонен",
    
    // Messages
    userBlocked: "Пользователь успешно заблокирован",
    userActivated: "Пользователь успешно активирован",
    roleChanged: "Роль пользователя успешно обновлена",
    profileUpdated: "Профиль успешно обновлен",
    passwordChanged: "Пароль успешно изменен",
    avatarUploaded: "Аватар успешно загружен",
    languageChanged: "Языковые предпочтения обновлены",
    
    // Products
    addToCart: "Добавить в корзину",
    addToWishlist: "Добавить в избранное",
    inStock: "В наличии",
    outOfStock: "Нет в наличии",
    price: "Цена",
    category: "Категория",
    brand: "Бренд",
    rating: "Рейтинг",
    reviews: "Отзывы",
    
    // Cart & Checkout
    shoppingCart: "Корзина покупок",
    proceedToCheckout: "Перейти к оформлению",
    continueShopping: "Продолжить покупки",
    removeFromCart: "Удалить из корзины",
    quantity: "Количество",
    subtotal: "Подытог",
    shipping: "Доставка",
    tax: "Налог",
    total: "Итого"
  }
};

// Language context and hook
import React, { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('en');
  
  useEffect(() => {
    // Load language from localStorage or user profile
    const savedLanguage = localStorage.getItem('language') || 'en';
    setCurrentLanguage(savedLanguage);
  }, []);
  
  const changeLanguage = (lang) => {
    setCurrentLanguage(lang);
    localStorage.setItem('language', lang);
  };
  
  const t = (key) => {
    return translations[currentLanguage]?.[key] || key;
  };
  
  return (
    <LanguageContext.Provider value={{ currentLanguage, changeLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useTranslation = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within LanguageProvider');
  }
  return context;
};