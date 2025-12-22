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
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300">
      {/* Product Info */}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {product.name}
        </h3>

        {product.description && (
          <p className="text-sm text-gray-600 mb-3">
            {product.description}
          </p>
        )}

        {/* Price */}
        <div className="flex items-baseline mb-3">
          <span className="text-2xl font-bold text-primary-600">
            ${product.discount_price.toFixed(2)}
          </span>
          {product.original_price && product.original_price > product.discount_price && (
            <>
              <span className="ml-2 text-sm text-gray-500 line-through">
                ${product.original_price.toFixed(2)}
              </span>
              <span className="ml-2 text-sm font-medium text-green-600">
                Save ${(product.original_price - product.discount_price).toFixed(2)}
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

            {/* Expiry/Pickup Date */}
            {product.expiry_date && (
              <span className="text-xs text-gray-500">
                Pickup by: {format(parseISO(product.expiry_date), 'MMM d')}
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
