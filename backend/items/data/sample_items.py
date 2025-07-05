"""
Sample item data that matches the Item model exactly
"""

ELECTRONICS_ITEMS = [
    {
        'name': 'iPhone 15 Pro',
        'category': 'electronics',
        'price': 999.99,
        'summary': 'Latest iPhone with pro camera system and titanium design',
        'description': 'Advanced smartphone with A17 Pro chip, titanium design, and professional camera system. Features include ProRAW photography, 4K video recording, and all-day battery life with advanced computational photography.',
        'weight': 0.17,
        'dimensions': {'length': 14.67, 'width': 7.09, 'height': 0.83},
        'origin': 'China',
        'is_digital': False,
        'specs': {
            'Display': '6.1-inch Super Retina XDR',
            'Chip': 'A17 Pro',
            'Storage': '128GB',
            'Camera': '48MP Main',
            'Battery': 'Up to 23 hours video',
            'OS': 'iOS 17',
            'Materials': 'Titanium frame',
            'Water Resistance': 'IP68'
        }
    },
    {
        'name': 'MacBook Air M2',
        'category': 'electronics',
        'price': 1299.99,
        'summary': 'Powerful laptop with M2 chip for professionals and students',
        'description': 'Thin and light laptop with Apple M2 chip, perfect for work and creativity. Features 8-core CPU, 10-core GPU, and up to 18 hours of battery life. Includes MagSafe charging and two Thunderbolt ports.',
        'weight': 1.24,
        'dimensions': {'length': 30.41, 'width': 21.5, 'height': 1.13},
        'origin': 'China',
        'is_digital': False,
        'specs': {
            'Chip': 'Apple M2 8-core CPU',
            'Memory': '8GB unified memory',
            'Storage': '256GB SSD',
            'Display': '13.6-inch Liquid Retina',
            'Battery': 'Up to 18 hours',
            'Ports': '2x Thunderbolt, MagSafe 3',
            'Webcam': '1080p FaceTime HD',
            'Audio': '4-speaker sound system'
        }
    },
    {
        'name': 'Sony WH-1000XM5 Headphones',
        'category': 'electronics',
        'price': 399.99,
        'summary': 'Premium noise-canceling wireless headphones with 30-hour battery',
        'description': 'Industry-leading noise cancellation with exceptional sound quality. Features 30-hour battery life, quick charge capability, and multipoint Bluetooth connection for seamless device switching.',
        'weight': 0.25,
        'dimensions': {'length': 27.0, 'width': 19.0, 'height': 8.0},
        'origin': 'Malaysia',
        'is_digital': False,
        'specs': {
            'Driver': '30mm dome type',
            'Frequency_Response': '4Hz-40,000Hz',
            'Battery_Life': '30 hours with ANC',
            'Charging': 'USB-C quick charge',
            'Connectivity': 'Bluetooth 5.2',
            'Noise_Canceling': 'Industry-leading ANC',
            'Voice_Assistant': 'Alexa, Google Assistant',
            'Weight': '250g'
        }
    },
    {
        'name': 'Samsung Galaxy S24 Ultra',
        'category': 'electronics',
        'price': 1199.99,
        'summary': 'Ultimate Android flagship with S Pen and 200MP camera',
        'description': 'Premium Android smartphone with built-in S Pen, 200MP camera system, and Galaxy AI features. Includes titanium frame, 6.8-inch display, and all-day battery with fast charging.',
        'weight': 0.22,
        'dimensions': {'length': 16.26, 'width': 7.9, 'height': 0.86},
        'origin': 'South Korea',
        'is_digital': False,
        'specs': {
            'Display': '6.8-inch Dynamic AMOLED 2X',
            'Processor': 'Snapdragon 8 Gen 3',
            'RAM': '12GB',
            'Storage': '256GB',
            'Camera': '200MP Quad camera system',
            'S_Pen': 'Built-in S Pen',
            'Battery': '5000mAh with 45W fast charging',
            'OS': 'Android 14 with One UI 6.1'
        }
    },
    {
        'name': 'Dell XPS 13 Plus',
        'category': 'electronics',
        'price': 1399.99,
        'summary': 'Ultra-portable Windows laptop with OLED display option',
        'description': 'Compact and powerful Windows laptop with stunning 13.4-inch display, Intel 12th gen processors, and premium build quality. Perfect for professionals and content creators.',
        'weight': 1.26,
        'dimensions': {'length': 29.57, 'width': 19.86, 'height': 1.57},
        'origin': 'China',
        'is_digital': False,
        'specs': {
            'Processor': 'Intel Core i7-1260P',
            'RAM': '16GB LPDDR5',
            'Storage': '512GB NVMe SSD',
            'Display': '13.4-inch FHD+ InfinityEdge',
            'Graphics': 'Intel Iris Xe',
            'Ports': '2x Thunderbolt 4',
            'Battery': 'Up to 12 hours',
            'Build': 'CNC machined aluminum'
        }
    },
]

CLOTHING_ITEMS = [
    {
        'name': 'Nike Air Max 90',
        'category': 'clothing',
        'price': 119.99,
        'summary': 'Classic running shoes with visible Air cushioning',
        'description': 'Iconic running shoes that defined a generation. Features visible Air cushioning in the heel, durable construction with leather and textile upper, and timeless design that works with any outfit.',
        'weight': 0.8,
        'dimensions': {'length': 32.0, 'width': 12.0, 'height': 12.0},
        'origin': 'Vietnam',
        'is_digital': False,
        'specs': {
            'Upper_Material': 'Leather and textile',
            'Sole_Type': 'Rubber with visible Air cushioning',
            'Closure': 'Lace-up',
            'Style': 'Low-top running shoe',
            'Heel_Type': 'Visible Air Max cushioning',
            'Toe_Style': 'Round toe',
            'Care_Instructions': 'Spot clean with damp cloth',
            'Season': 'All seasons'
        }
    },
    {
        'name': 'Levi\'s 501 Original Jeans',
        'category': 'clothing',
        'price': 89.99,
        'summary': 'The original straight leg jeans since 1873',
        'description': 'The classic straight-leg jeans that started it all. Made from 100% cotton denim with authentic button fly closure. A timeless design that never goes out of style and gets better with age.',
        'weight': 0.6,
        'dimensions': {'length': 107.0, 'width': 35.0, 'height': 2.0},
        'origin': 'Mexico',
        'is_digital': False,
        'specs': {
            'Material': '100% Cotton denim',
            'Fit': 'Straight leg',
            'Rise': 'Mid-rise',
            'Closure': 'Button fly',
            'Pockets': '5-pocket styling',
            'Wash': 'Stone wash',
            'Care': 'Machine wash cold, tumble dry low',
            'Weight': '14.75 oz denim'
        }
    },
    {
        'name': 'Champion Reverse Weave Hoodie',
        'category': 'clothing',
        'price': 65.99,
        'summary': 'Premium cotton blend hoodie with reverse weave construction',
        'description': 'Classic pullover hoodie with Champion\'s signature reverse weave construction that resists shrinkage. Features kangaroo pocket, adjustable drawstring hood, and comfortable cotton blend fabric.',
        'weight': 0.7,
        'dimensions': {'length': 70.0, 'width': 55.0, 'height': 3.0},
        'origin': 'Honduras',
        'is_digital': False,
        'specs': {
            'Material': '82% Cotton, 18% Polyester',
            'Construction': 'Reverse Weave',
            'Fit': 'Regular fit',
            'Hood': 'Adjustable drawstring',
            'Pockets': 'Front kangaroo pocket',
            'Cuffs': 'Ribbed cuffs and hem',
            'Care': 'Machine wash warm',
            'Features': 'Shrinkage resistant'
        }
    },
    {
        'name': 'Adidas Ultraboost 23',
        'category': 'clothing',
        'price': 189.99,
        'summary': 'Premium running shoes with Boost midsole technology',
        'description': 'High-performance running shoes featuring responsive Boost midsole, Primeknit+ upper for adaptive fit, and Continental rubber outsole for superior traction. Designed for runners who demand the best.',
        'weight': 0.31,
        'dimensions': {'length': 33.0, 'width': 13.0, 'height': 11.0},
        'origin': 'Vietnam',
        'is_digital': False,
        'specs': {
            'Midsole_Technology': 'Boost energy return',
            'Upper_Material': 'Primeknit+ adaptive fit',
            'Outsole': 'Continental rubber',
            'Drop': '10mm heel-to-toe drop',
            'Support': 'Neutral running shoe',
            'Closure': 'Lace-up',
            'Purpose': 'Road running',
            'Cushioning': 'Maximum cushioning'
        }
    },
]

BOOKS_ITEMS = [
    {
        'name': 'Clean Code by Robert Martin',
        'category': 'books',
        'price': 42.99,
        'summary': 'A handbook of agile software craftsmanship',
        'description': 'Essential reading for any developer who wants to write better code. Learn the principles of clean code, meaningful names, functions, and best practices for professional software development.',
        'weight': 0.68,
        'dimensions': {'length': 23.5, 'width': 17.8, 'height': 3.2},
        'origin': 'USA',
        'is_digital': False,
        'specs': {
            'Pages': '464 pages',
            'Publisher': 'Prentice Hall',
            'Publication_Year': '2008',
            'Language': 'English',
            'ISBN_13': '978-0132350884',
            'Format': 'Paperback',
            'Edition': '1st Edition',
            'Category': 'Programming'
        }
    },
    {
        'name': 'Python Crash Course 3rd Edition',
        'category': 'books',
        'price': 39.99,
        'summary': 'A hands-on introduction to programming with Python',
        'description': 'Learn Python programming through practical projects. Perfect for beginners who want to start coding quickly. Includes web development with Django and data visualization projects.',
        'weight': 0.79,
        'dimensions': {'length': 25.4, 'width': 17.8, 'height': 3.8},
        'origin': 'USA',
        'is_digital': False,
        'specs': {
            'Pages': '552 pages',
            'Publisher': 'No Starch Press',
            'Publication_Year': '2023',
            'Language': 'English',
            'ISBN_13': '978-1718502703',
            'Format': 'Paperback',
            'Edition': '3rd Edition',
            'Level': 'Beginner'
        }
    },
    {
        'name': 'Complete Python Programming Course',
        'category': 'books',
        'price': 79.99,
        'summary': 'Comprehensive digital Python course with certificates',
        'description': 'Complete digital course covering Python from basics to advanced topics. Includes 40+ hours of video lectures, hands-on exercises, real-world projects, and completion certificates.',
        'weight': 0,
        'dimensions': {},
        'origin': 'Digital Content',
        'is_digital': True,
        'specs': {
            'Duration': '40+ hours of content',
            'Format': 'Video lectures + PDF materials',
            'Language': 'English',
            'Access': 'Lifetime access',
            'Certificate': 'Completion certificate included',
            'Projects': '15+ hands-on projects',
            'Level': 'Beginner to Advanced',
            'Platform': 'Online learning platform'
        }
    },
    {
        'name': 'The Pragmatic Programmer 20th Anniversary',
        'category': 'books',
        'price': 49.99,
        'summary': 'Your journey to mastery in software development',
        'description': 'Classic programming book updated for modern development. Teaches practical approaches to software development, debugging techniques, and career advice for programmers.',
        'weight': 0.52,
        'dimensions': {'length': 23.0, 'width': 15.5, 'height': 2.8},
        'origin': 'USA',
        'is_digital': False,
        'specs': {
            'Pages': '352 pages',
            'Publisher': 'Addison-Wesley Professional',
            'Publication_Year': '2019',
            'Language': 'English',
            'ISBN_13': '978-0135957059',
            'Format': 'Paperback',
            'Edition': '20th Anniversary Edition',
            'Authors': 'David Thomas, Andrew Hunt'
        }
    },
]

HOME_GARDEN_ITEMS = [
    {
        'name': 'Cuisinart Programmable Coffee Maker',
        'category': 'home_garden',
        'price': 149.99,
        'summary': 'Smart 12-cup programmable drip coffee maker with auto shut-off',
        'description': 'Brew the perfect cup every morning with this programmable coffee maker. Features 12-cup glass carafe, programmable timer, auto shut-off, and brew strength control for customized coffee experience.',
        'weight': 4.1,
        'dimensions': {'length': 21.8, 'width': 23.1, 'height': 33.7},
        'origin': 'China',
        'is_digital': False,
        'specs': {
            'Capacity': '12 cups (1.8 liters)',
            'Power': '1050 watts',
            'Material': 'Stainless steel and plastic',
            'Features': 'Programmable 24-hour timer',
            'Auto_Shutoff': '2-hour auto shut-off',
            'Carafe': 'Glass carafe with ergonomic handle',
            'Filter': 'Permanent gold-tone filter',
            'Warranty': '3-year limited warranty'
        }
    },
    {
        'name': 'Air Purifying Plant Collection',
        'category': 'home_garden',
        'price': 89.99,
        'summary': 'Set of 5 NASA-approved air-purifying plants with decorative pots',
        'description': 'Beautiful collection of low-maintenance indoor plants scientifically proven to purify air. Includes Snake plant, Pothos, Spider plant, Rubber tree, and Peace lily with matching ceramic pots.',
        'weight': 3.2,
        'dimensions': {'length': 45.0, 'width': 35.0, 'height': 25.0},
        'origin': 'Netherlands',
        'is_digital': False,
        'specs': {
            'Plant_Count': '5 different species',
            'Pot_Material': 'Glazed ceramic',
            'Care_Level': 'Low maintenance',
            'Light_Requirements': 'Low to medium indirect light',
            'Watering': 'Weekly watering',
            'Air_Purifying': 'NASA Clean Air Study approved',
            'Pet_Safe': 'Mixed (care required)',
            'Pot_Size': '6-inch diameter pots'
        }
    },
    {
        'name': 'Shark Robot Vacuum Cleaner',
        'category': 'home_garden',
        'price': 329.99,
        'summary': 'Smart robotic vacuum with app control and self-emptying base',
        'description': 'Intelligent robot vacuum that maps your home for efficient cleaning. Features app control, voice commands, automatic dirt disposal, and works on both carpets and hard floors.',
        'weight': 3.8,
        'dimensions': {'length': 34.5, 'width': 34.5, 'height': 9.6},
        'origin': 'China',
        'is_digital': False,
        'specs': {
            'Battery_Life': '120 minutes runtime',
            'Navigation': 'Smart mapping technology',
            'Connectivity': 'WiFi and app control',
            'Voice_Control': 'Alexa and Google Assistant',
            'Auto_Empty': 'Self-emptying base included',
            'Suction_Power': '2000Pa strong suction',
            'Floor_Types': 'Carpet and hard floors',
            'Warranty': '2-year limited warranty'
        }
    },
    {
        'name': 'Ninja Digital Air Fryer',
        'category': 'home_garden',
        'price': 129.99,
        'summary': 'Digital air fryer for healthy cooking with 75% less fat',
        'description': 'Cook crispy, delicious food with little to no oil using rapid air circulation technology. Features digital controls, multiple cooking functions, and dishwasher-safe parts for easy cleanup.',
        'weight': 5.2,
        'dimensions': {'length': 35.8, 'width': 27.4, 'height': 33.2},
        'origin': 'China',
        'is_digital': False,
        'specs': {
            'Capacity': '4.2 quart (4L) basket',
            'Power': '1550 watts',
            'Temperature_Range': '105°F to 400°F (40°C to 204°C)',
            'Timer': '1 to 60 minutes',
            'Functions': 'Air fry, roast, reheat, dehydrate',
            'Control': 'Digital touch display',
            'Cleanup': 'Dishwasher-safe parts',
            'Cooking_Time': 'Up to 75% faster'
        }
    },
]

SPORTS_FITNESS_ITEMS = [
    {
        'name': 'Liforme Yoga Mat',
        'category': 'sports_fitness',
        'price': 139.99,
        'summary': 'Premium eco-friendly yoga mat with alignment guides',
        'description': 'Professional-grade yoga mat made from natural rubber with unique alignment marker system. Provides superior grip, cushioning, and stability for all yoga practices.',
        'weight': 2.5,
        'dimensions': {'length': 185.0, 'width': 68.0, 'height': 0.45},
        'origin': 'United Kingdom',
        'is_digital': False,
        'specs': {
            'Material': 'Natural rubber with eco-polyurethane top',
            'Thickness': '4.2mm professional thickness',
            'Grip': 'Superior wet and dry grip',
            'Alignment_System': 'Unique alignment marker system',
            'Eco_Friendly': 'Biodegradable and recyclable',
            'Size': '185cm x 68cm',
            'Care': 'Wipe clean with damp cloth',
            'Warranty': 'Lifetime guarantee'
        }
    },
    {
        'name': 'PowerBlock Elite Dumbbells',
        'category': 'sports_fitness',
        'price': 649.99,
        'summary': 'Adjustable dumbbell system replacing 16 pairs of weights',
        'description': 'Space-saving adjustable dumbbell set that replaces 16 pairs of traditional dumbbells. Quick weight changes from 3-24kg per hand with expandable design for home gym setups.',
        'weight': 19.0,
        'dimensions': {'length': 30.5, 'width': 15.2, 'height': 15.2},
        'origin': 'USA',
        'is_digital': False,
        'specs': {
            'Weight_Range': '3-24kg per dumbbell',
            'Adjustment_System': 'Magnetic pin system',
            'Material': 'Steel construction',
            'Expandable': 'Expandable to 39kg with add-ons',
            'Space_Saving': 'Replaces 16 pairs of dumbbells',
            'Handle': 'Ergonomic steel handle',
            'Stand': 'Optional stand available separately',
            'Warranty': '10-year home warranty'
        }
    },
    {
        'name': 'Resistance Bands Pro Set',
        'category': 'sports_fitness',
        'price': 34.99,
        'summary': 'Professional resistance training kit with 5 resistance levels',
        'description': 'Complete resistance bands set with multiple resistance levels from light to extra heavy. Includes door anchor, handles, ankle straps, and comprehensive workout guide for full-body training.',
        'weight': 1.1,
        'dimensions': {'length': 30.0, 'width': 20.0, 'height': 8.0},
        'origin': 'Malaysia',
        'is_digital': False,
        'specs': {
            'Resistance_Levels': '5 levels: Light, Medium, Heavy, X-Heavy, XX-Heavy',
            'Material': '100% natural latex',
            'Handles': 'Comfortable foam handles',
            'Door_Anchor': 'Heavy-duty door anchor included',
            'Ankle_Straps': 'Padded ankle straps',
            'Max_Resistance': 'Up to 68kg total resistance',
            'Exercise_Guide': 'Digital workout guide included',
            'Storage': 'Convenient carrying bag'
        }
    },
    {
        'name': 'Garmin Forerunner 255',
        'category': 'sports_fitness',
        'price': 349.99,
        'summary': 'Advanced GPS running watch with health monitoring',
        'description': 'Comprehensive GPS running watch with built-in sports apps, health monitoring, and smart features. Tracks running dynamics, recovery, and provides personalized training guidance.',
        'weight': 0.05,
        'dimensions': {'length': 4.6, 'width': 4.6, 'height': 1.25},
        'origin': 'Taiwan',
        'is_digital': False,
        'specs': {
            'Display': '1.3-inch MIP color display',
            'Battery_Life': 'Up to 14 days smartwatch mode',
            'GPS': 'Multi-GNSS satellite systems',
            'Water_Rating': '5 ATM water resistance',
            'Health_Features': 'Heart rate, sleep, stress tracking',
            'Sports_Apps': '30+ built-in sports apps',
            'Smart_Features': 'Notifications, music storage',
            'Training': 'Daily suggested workouts'
        }
    },
]

# Combine all items into one comprehensive list
ALL_SAMPLE_ITEMS = (
    ELECTRONICS_ITEMS + 
    CLOTHING_ITEMS + 
    BOOKS_ITEMS + 
    HOME_GARDEN_ITEMS + 
    SPORTS_FITNESS_ITEMS
)

# Optional: Export categories for reference
AVAILABLE_CATEGORIES = [
    'electronics',
    'clothing', 
    'books',
    'home_garden',
    'sports_fitness'
]