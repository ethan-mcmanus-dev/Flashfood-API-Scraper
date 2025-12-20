/**
 * Main dashboard page displaying deals and filters.
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { productApi, preferenceApi } from '../api/client';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAuth } from '../contexts/AuthContext';
import { DealCard } from '../components/deals/DealCard';
import { DealFilters } from '../components/deals/DealFilters';
import { Navbar } from '../components/layout/Navbar';
import type { Product, WebSocketMessage } from '../types';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [city, setCity] = useState('calgary');
  const [category, setCategory] = useState('');
  const [minDiscount, setMinDiscount] = useState(0);
  const [search, setSearch] = useState('');
  const [notification, setNotification] = useState<string | null>(null);

  const token = localStorage.getItem('access_token');

  // Fetch user preferences
  const { data: preferences } = useQuery({
    queryKey: ['preferences'],
    queryFn: preferenceApi.getPreferences,
  });

  // Set city from preferences when loaded
  useEffect(() => {
    if (preferences) {
      setCity(preferences.city);
    }
  }, [preferences]);

  // Fetch products with filters
  const {
    data: products = [],
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['products', city, category, minDiscount, search],
    queryFn: () =>
      productApi.listProducts({
        city: city || undefined,
        category: category || undefined,
        min_discount: minDiscount || undefined,
        search: search || undefined,
        limit: 100,
      }),
  });

  // WebSocket for real-time updates (temporarily disabled to prevent connection loop)
  const { lastMessage } = useWebSocket(null, {
    onMessage: (message: WebSocketMessage) => {
      if (message.type === 'new_deals') {
        setNotification(message.message);
        refetch(); // Refresh products

        // Clear notification after 5 seconds
        setTimeout(() => setNotification(null), 5000);
      }
    },
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.full_name || user?.email}!
          </h1>
          <p className="mt-2 text-gray-600">
            Discover amazing deals from Flashfood stores near you
          </p>
        </div>

        {/* Real-time Notification */}
        {notification && (
          <div className="mb-6 bg-primary-50 border border-primary-200 text-primary-800 px-4 py-3 rounded-lg flex items-center">
            <span className="text-2xl mr-3">🆕</span>
            <span className="font-medium">{notification}</span>
          </div>
        )}

        {/* Filters */}
        <DealFilters
          city={city}
          category={category}
          minDiscount={minDiscount}
          search={search}
          onCityChange={setCity}
          onCategoryChange={setCategory}
          onMinDiscountChange={setMinDiscount}
          onSearchChange={setSearch}
        />

        {/* Products Grid */}
        <div className="mt-8">
          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-xl text-gray-500">No deals found</p>
              <p className="mt-2 text-gray-400">
                Try adjusting your filters or check back later
              </p>
            </div>
          ) : (
            <>
              <div className="flex justify-between items-center mb-4">
                <p className="text-sm text-gray-600">
                  Found {products.length} {products.length === 1 ? 'deal' : 'deals'}
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {products.map((product) => (
                  <DealCard key={product.id} product={product} />
                ))}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
};
