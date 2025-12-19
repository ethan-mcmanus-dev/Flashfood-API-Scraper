/**
 * Deal card component displaying product information.
 */

import React from 'react';
import { format, parseISO } from 'date-fns';
import type { Product } from '../../types';

interface DealCardProps {
  product: Product;
}

export const DealCard: React.FC<DealCardProps> = ({ product }) => {
  const savings = product.original_price
    ? product.original_price - product.discount_price
    : 0;

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300">
      {/* Product Image */}
      {product.image_url ? (
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-48 object-cover"
        />
      ) : (
        <div className="w-full h-48 bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center">
          <span className="text-4xl">🍽️</span>
        </div>
      )}

      {/* Discount Badge */}
      {product.discount_percent && product.discount_percent > 0 && (
        <div className="absolute top-2 right-2 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold shadow-lg">
          {product.discount_percent}% OFF
        </div>
      )}

      {/* Product Info */}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {product.name}
        </h3>

        {product.description && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
            {product.description}
          </p>
        )}

        {/* Price */}
        <div className="flex items-baseline mb-3">
          <span className="text-2xl font-bold text-primary-600">
            ${product.discount_price.toFixed(2)}
          </span>
          {product.original_price && (
            <>
              <span className="ml-2 text-sm text-gray-500 line-through">
                ${product.original_price.toFixed(2)}
              </span>
              <span className="ml-2 text-sm font-medium text-green-600">
                Save ${savings.toFixed(2)}
              </span>
            </>
          )}
        </div>

        {/* Store Info */}
        <div className="border-t border-gray-200 pt-3">
          <p className="text-sm font-medium text-gray-900">
            {product.store_name}
          </p>
          <p className="text-xs text-gray-500">{product.store_city}</p>

          {/* Quantity */}
          <div className="mt-2 flex items-center justify-between">
            <span className="text-xs text-gray-500">
              {product.quantity_available} available
            </span>

            {/* Expiry Date */}
            {product.expiry_date && (
              <span className="text-xs text-gray-500">
                Exp: {format(parseISO(product.expiry_date), 'MMM d')}
              </span>
            )}
          </div>

          {/* Category Badge */}
          {product.category && (
            <span className="inline-block mt-2 px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded">
              {product.category}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
