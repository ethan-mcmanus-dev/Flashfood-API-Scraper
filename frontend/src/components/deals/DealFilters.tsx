/**
 * Deal filters component for filtering products.
 */

import React from 'react';

interface DealFiltersProps {
  city: string;
  category: string;
  minDiscount: number;
  search: string;
  onCityChange: (city: string) => void;
  onCategoryChange: (category: string) => void;
  onMinDiscountChange: (discount: number) => void;
  onSearchChange: (search: string) => void;
}

const CITIES = [
  { value: 'calgary', label: 'Calgary' },
  { value: 'vancouver', label: 'Vancouver' },
  { value: 'toronto', label: 'Toronto' },
  { value: 'edmonton', label: 'Edmonton' },
  { value: 'waterloo', label: 'Waterloo/Kitchener' },
];

export const DealFilters: React.FC<DealFiltersProps> = ({
  city,
  category,
  minDiscount,
  search,
  onCityChange,
  onCategoryChange,
  onMinDiscountChange,
  onSearchChange,
}) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* City Filter */}
        <div>
          <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-1">
            City
          </label>
          <select
            id="city"
            value={city}
            onChange={(e) => onCityChange(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Cities</option>
            {CITIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </div>

        {/* Category Filter */}
        <div>
          <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
            Category
          </label>
          <select
            id="category"
            value={category}
            onChange={(e) => onCategoryChange(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Categories</option>
            <option value="Produce">Produce</option>
            <option value="Bakery">Bakery</option>
            <option value="Meat">Meat</option>
            <option value="Dairy">Dairy</option>
            <option value="Deli">Deli</option>
            <option value="Prepared Foods">Prepared Foods</option>
          </select>
        </div>

        {/* Minimum Discount Filter */}
        <div>
          <label htmlFor="minDiscount" className="block text-sm font-medium text-gray-700 mb-1">
            Min. Discount: {minDiscount}%
          </label>
          <input
            type="range"
            id="minDiscount"
            min="0"
            max="90"
            step="10"
            value={minDiscount}
            onChange={(e) => onMinDiscountChange(Number(e.target.value))}
            className="block w-full"
          />
        </div>

        {/* Search Filter */}
        <div>
          <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
            Search
          </label>
          <input
            type="text"
            id="search"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search products..."
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>
    </div>
  );
};
