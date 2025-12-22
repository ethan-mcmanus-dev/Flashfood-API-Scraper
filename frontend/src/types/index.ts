/**
 * TypeScript type definitions for the Flashfood Tracker application.
 */

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface Store {
  id: number;
  external_id: string;
  name: string;
  address: string | null;
  city: string;
  latitude: number;
  longitude: number;
  created_at: string;
  updated_at: string;
  distance_km?: number;
}

export interface Product {
  id: number;
  store_id: number;
  external_id: string;
  name: string;
  description: string | null;
  category: string | null;
  original_price: number | null;
  discount_price: number;
  discount_percent: number | null;
  quantity_available: number;
  expiry_date: string | null;
  image_url: string | null;
  first_seen: string;
  last_seen: string;
  store_name?: string;
  store_address?: string | null;
  store_city?: string;
}

export interface ProductWithHistory extends Product {
  price_history: PriceHistoryPoint[];
}

export interface PriceHistoryPoint {
  price: number;
  quantity_available: number;
  recorded_at: string;
}

export interface UserPreference {
  id: number;
  user_id: number;
  city: string;
  max_distance_km: number;
  selected_store_ids: number[];
  email_notifications: boolean;
  web_push_notifications: boolean;
  notify_new_deals: boolean;
  notify_price_drops: boolean;
  min_discount_percent: number;
  favorite_categories: string[];
  notification_start_time: string; // Time in HH:MM format
  notification_end_time: string;   // Time in HH:MM format
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string; // Email
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface WebSocketMessage {
  type: 'new_deals' | 'price_drop' | 'connection' | 'error';
  count?: number;
  message: string;
  timestamp: string;
  data?: unknown;
}
