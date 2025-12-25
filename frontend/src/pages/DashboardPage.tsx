/**
 * Main dashboard page displaying personalized deals based on user preferences.
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { productApi, preferenceApi } from '../api/client';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAuth } from '../contexts/AuthContext';
import { DealCard } from '../components/deals/DealCard';
import { Navbar } from '../components/layout/Navbar';
import type { WebSocketMessage } from '../types';

export const DashboardPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const [notification, setNotification] = useState<string | null>(null);

  // Fetch user preferences
  const { data: preferences } = useQuery({
    queryKey: ['preferences'],
    queryFn: preferenceApi.getPreferences,
  });

  // Fetch products using preferences
  const {
    data: products = [],
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['products', 'preferences', search],
    queryFn: () =>
      productApi.listProducts({
        search: search || undefined,
        limit: 100,
        use_preferences: true, // Use user preferences for filtering
      }),
  });

  // WebSocket for real-time updates (temporarily disabled to prevent connection loop)
  const { } = useWebSocket(null, {
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
            Your personalized deals based on your preferences
          </p>
          {preferences && (
            <div className="mt-4 text-sm text-gray-500">
              Showing deals from {preferences.city} • 
              {preferences.selected_store_ids?.length > 0 
                ? ` ${preferences.selected_store_ids.length} selected stores • `
                : ' All stores • '
              }
              {preferences.min_discount_percent > 0 
                ? `${preferences.min_discount_percent}%+ discount`
                : 'Any discount'
              }
            </div>
          )}
        </div>

        {/* Real-time Notification */}
        {notification && (
          <div className="mb-6 bg-primary-50 border border-primary-200 text-primary-800 px-4 py-3 rounded-lg flex items-center">
            <span className="text-2xl mr-3">🆕</span>
            <span className="font-medium">{notification}</span>
          </div>
        )}

        {/* Search Only */}
        <div className="mb-6">
          <div className="max-w-md">
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
              Search deals
            </label>
            <input
              type="text"
              id="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search for specific items..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>

        {/* Products Grid */}
        <div className="mt-8">
          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-xl text-gray-500">No deals found matching your preferences</p>
              <p className="mt-2 text-gray-400">
                Try updating your preferences or check back later
              </p>
              <div className="mt-4">
                <a
                  href="/preferences"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
                >
                  Update My Preferences
                </a>
              </div>
            </div>
          ) : (
            <>
              <div className="flex justify-between items-center mb-4">
                <p className="text-sm text-gray-600">
                  Found {products.length} {products.length === 1 ? 'deal' : 'deals'} matching your preferences
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
