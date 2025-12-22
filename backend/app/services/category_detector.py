"""
Category detection service for automatically categorizing products based on keywords.

Uses keyword matching to assign categories to products that don't have them.
"""

import re
from typing import Optional


class CategoryDetector:
    """
    Detects product categories based on name and description keywords.
    """

    # Category keyword mappings
    CATEGORY_KEYWORDS = {
        "Produce": [
            "apple", "banana", "orange", "grape", "berry", "strawberry", "blueberry", "raspberry",
            "lettuce", "spinach", "kale", "carrot", "potato", "onion", "tomato", "cucumber",
            "pepper", "broccoli", "cauliflower", "celery", "avocado", "lemon", "lime",
            "peach", "pear", "plum", "cherry", "melon", "watermelon", "cantaloupe",
            "cabbage", "zucchini", "squash", "mushroom", "garlic", "ginger", "herbs",
            "salad", "organic", "fresh", "produce", "fruit", "vegetable", "veggie"
        ],
        "Meat": [
            "chicken", "beef", "pork", "turkey", "lamb", "fish", "salmon", "tuna",
            "ground", "steak", "roast", "chops", "wings", "thighs", "breast",
            "bacon", "ham", "sausage", "deli", "meat", "protein", "fresh meat",
            "ribeye", "sirloin", "tenderloin", "brisket", "ribs", "drumstick"
        ],
        "Dairy": [
            "milk", "cheese", "yogurt", "butter", "cream", "sour cream", "cottage cheese",
            "cheddar", "mozzarella", "parmesan", "swiss", "brie", "goat cheese",
            "ice cream", "frozen yogurt", "dairy", "lactose", "organic milk",
            "almond milk", "oat milk", "coconut milk", "eggs", "egg"
        ],
        "Bakery": [
            "bread", "buns", "rolls", "bagels", "muffins", "croissant", "pastry",
            "cake", "cookies", "pie", "tart", "donut", "danish", "scone",
            "bakery", "fresh baked", "artisan", "sourdough", "whole grain",
            "gluten free", "baguette", "focaccia", "pretzel"
        ],
        "Frozen": [
            "frozen", "ice cream", "frozen yogurt", "frozen fruit", "frozen vegetables",
            "frozen meals", "frozen pizza", "frozen chicken", "frozen fish",
            "ice", "popsicle", "sorbet", "gelato", "frozen berries", "frozen peas"
        ],
        "Pantry": [
            "pasta", "rice", "beans", "lentils", "quinoa", "oats", "cereal",
            "flour", "sugar", "salt", "pepper", "spices", "oil", "vinegar",
            "sauce", "dressing", "condiment", "canned", "jarred", "dried",
            "nuts", "seeds", "honey", "syrup", "jam", "jelly", "peanut butter"
        ],
        "Snacks": [
            "chips", "crackers", "popcorn", "pretzels", "nuts", "trail mix",
            "granola", "energy bar", "protein bar", "candy", "chocolate",
            "gum", "mints", "cookies", "snack", "treats", "jerky"
        ],
        "Beverages": [
            "water", "juice", "soda", "pop", "coffee", "tea", "energy drink",
            "sports drink", "kombucha", "smoothie", "beer", "wine", "alcohol",
            "sparkling", "coconut water", "drink", "beverage", "bottle", "can"
        ],
        "Health & Beauty": [
            "shampoo", "conditioner", "soap", "lotion", "cream", "deodorant",
            "toothpaste", "toothbrush", "vitamins", "supplements", "medicine",
            "bandages", "first aid", "beauty", "cosmetics", "skincare", "haircare"
        ],
        "Pet Food": [
            "dog food", "cat food", "pet food", "dog treats", "cat treats",
            "pet treats", "dog", "cat", "pet", "kibble", "wet food", "dry food"
        ]
    }

    @classmethod
    def detect_category(cls, name: str, description: Optional[str] = None) -> Optional[str]:
        """
        Detect category based on product name and description.

        Args:
            name: Product name
            description: Product description (optional)

        Returns:
            Detected category name or None if no match found
        """
        # Combine name and description for analysis
        text_to_analyze = name.lower()
        if description:
            text_to_analyze += " " + description.lower()

        # Score each category based on keyword matches
        category_scores = {}
        
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = len(re.findall(pattern, text_to_analyze))
                score += matches
            
            if score > 0:
                category_scores[category] = score

        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return "Other"  # Default category

    @classmethod
    def get_available_categories(cls) -> list[str]:
        """
        Get list of all available categories.

        Returns:
            List of category names
        """
        return list(cls.CATEGORY_KEYWORDS.keys()) + ["Other"]