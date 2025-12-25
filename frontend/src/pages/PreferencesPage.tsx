/**
 * User preferences page for managing notification settings and deal filters.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { preferenceApi, storeApi } from '../api/client';
import { Navbar } from '../components/layout/Navbar';
import type { UserPreference, Store } from '../types';

export const PreferencesPage: React.FC = () => {
  const navigate = useNavigate();
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Form state
  const [selectedCity, setSelectedCity] = useState('calgary');
  const [selectedStoreIds, setSelectedStoreIds] = useState<number[]>([]);
  const [minDiscount, setMinDiscount] = useState(0);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [webPushNotifications, setWebPushNotifications] = useState(false);
  const [favoriteCategories, setFavoriteCategories] = useState<string[]>([]);
  const [notificationStartTime, setNotificationStartTime] = useState('05:00');
  const [notificationEndTime, setNotificationEndTime] = useState('22:00');

  // Available categories (you can expand this list)
  const availableCategories = [
    'Produce', 'Meat', 'Dairy', 'Bakery', 'Frozen', 'Pantry', 
    'Snacks', 'Beverages', 'Health & Beauty', 'Pet Food', 'Other'
  ];

  // Available cities
  const availableCities = [
    'calgary', 'toronto', 'vancouver', 'edmonton', 'waterloo'
  ];

  useEffect(() => {
    loadPreferencesAndStores();
  }, [selectedCity]); // Reload stores when city changes

  const loadPreferencesAndStores = async () => {
    try {
      setLoading(true);
      
      // Load user preferences
      const userPrefs = await preferenceApi.getPreferences();
      setPreferences(userPrefs);
      
      // Set form state from preferences
      setSelectedCity(userPrefs.city || 'calgary');
      setSelectedStoreIds(userPrefs.selected_store_ids || []);
      setMinDiscount(userPrefs.min_discount_percent || 0);
      setEmailNotifications(userPrefs.email_notifications);
      setWebPushNotifications(userPrefs.web_push_notifications || false);
      setFavoriteCategories(userPrefs.favorite_categories || []);
      setNotificationStartTime(userPrefs.notification_start_time || '05:00');
      setNotificationEndTime(userPrefs.notification_end_time || '22:00');

      // Load available stores for the selected city
      const storeList = await storeApi.listStores({ city: selectedCity });
      setStores(storeList);
      
    } catch (error) {
      console.error('Failed to load preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      await preferenceApi.updatePreferences({
        city: selectedCity,
        selected_store_ids: selectedStoreIds,
        min_discount_percent: minDiscount,
        email_notifications: emailNotifications,
        web_push_notifications: webPushNotifications,
        favorite_categories: favoriteCategories,
        notification_start_time: notificationStartTime,
        notification_end_time: notificationEndTime,
      });

      // Show success message or redirect
      navigate('/dashboard');
      
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setSaving(false);
    }
  };

  const toggleStoreSelection = (storeId: number) => {
    setSelectedStoreIds(prev => 
      prev.includes(storeId) 
        ? prev.filter(id => id !== storeId)
        : [...prev, storeId]
    );
  };

  const toggleCategory = (category: string) => {
    setFavoriteCategories(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Deal Preferences</h1>
          <p className="mt-2 text-gray-600">
            Customize your notification settings and choose which deals you want to see
          </p>
        </div>

        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Notification Settings</h2>
          </div>
          
          <div className="p-6 space-y-6">
            {/* City Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                City
              </label>
              <select
                value={selectedCity}
                onChange={(e) => {
                  setSelectedCity(e.target.value);
                  setSelectedStoreIds([]); // Clear selected stores when city changes
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              >
                {availableCities.map(city => (
                  <option key={city} value={city}>
                    {city.charAt(0).toUpperCase() + city.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Minimum Discount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Discount: {minDiscount}%
              </label>
              <input
                type="range"
                min="0"
                max="80"
                value={minDiscount}
                onChange={(e) => setMinDiscount(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0%</span>
                <span>80%</span>
              </div>
            </div>

            {/* Notification Types */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-gray-700">Notification Methods</h3>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={emailNotifications}
                  onChange={(e) => setEmailNotifications(e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">Email notifications</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={webPushNotifications}
                  onChange={(e) => setWebPushNotifications(e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">Browser push notifications</span>
              </label>
            </div>

            {/* Notification Hours */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start notifications at
                </label>
                <input
                  type="time"
                  value={notificationStartTime}
                  onChange={(e) => setNotificationStartTime(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stop notifications at
                </label>
                <input
                  type="time"
                  value={notificationEndTime}
                  onChange={(e) => setNotificationEndTime(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>

            {/* Favorite Categories */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">Categories I Want</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {availableCategories.map(category => (
                  <label key={category} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={favoriteCategories.includes(category)}
                      onChange={() => toggleCategory(category)}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">{category}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Store Selection */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">
                Stores to Monitor in {selectedCity.charAt(0).toUpperCase() + selectedCity.slice(1)} ({selectedStoreIds.length} selected)
              </h3>
              <div className="max-h-64 overflow-y-auto border border-gray-200 rounded-md">
                {stores.map(store => (
                  <label key={store.id} className="flex items-center p-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0">
                    <input
                      type="checkbox"
                      checked={selectedStoreIds.includes(store.id)}
                      onChange={() => toggleStoreSelection(store.id)}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <div className="ml-3">
                      <div className="text-sm font-medium text-gray-900">{store.name}</div>
                      <div className="text-xs text-gray-500">{store.address}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
              <button
                onClick={() => navigate('/dashboard')}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700 disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Preferences'}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};