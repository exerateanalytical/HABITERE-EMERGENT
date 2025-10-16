export const PROPERTY_CATEGORIES = [
  {
    "sector": "Residential Properties",
    "icon": "🏠",
    "categories": [
      "Houses for Sale",
      "Houses for Rent",
      "Apartments / Flats for Sale",
      "Apartments / Flats for Rent",
      "Duplexes",
      "Bungalows",
      "Condominiums",
      "Townhouses",
      "Studios / Self-Contained Units",
      "Serviced Apartments",
      "Villas",
      "Mansions",
      "Penthouses",
      "Shared Apartments",
      "Short Let Apartments",
      "Student Accommodation",
      "Senior Living / Retirement Homes",
      "Vacation Homes / Holiday Houses"
    ]
  },
  {
    "sector": "Commercial Properties",
    "icon": "🏢",
    "categories": [
      "Office Spaces for Rent",
      "Office Spaces for Sale",
      "Shops / Retail Stores",
      "Shopping Malls / Complexes",
      "Warehouses",
      "Industrial Buildings",
      "Factories / Manufacturing Plants",
      "Cold Storage Facilities",
      "Co-working Spaces",
      "Showrooms",
      "Restaurants / Cafes",
      "Bars / Lounges",
      "Petrol Stations",
      "Car Dealerships / Auto Garages"
    ]
  },
  {
    "sector": "Land & Agricultural Properties",
    "icon": "🌾",
    "categories": [
      "Residential Land / Plots",
      "Commercial Land",
      "Industrial Land",
      "Mixed-Use Land",
      "Agricultural Land / Farmland",
      "Ranches",
      "Vineyards",
      "Estates / Development Land",
      "Waterfront Land",
      "Forest Land",
      "Mining Land / Quarry Sites"
    ]
  },
  {
    "sector": "Hospitality & Lodging",
    "icon": "🏨",
    "categories": [
      "Hotels",
      "Motels",
      "Resorts",
      "Lodges",
      "Guest Houses",
      "Bed & Breakfasts",
      "Hostels",
      "Serviced Apartments",
      "Holiday Homes",
      "Chalets / Cabins",
      "Campsites",
      "Safari Lodges"
    ]
  },
  {
    "sector": "Event & Leisure Properties",
    "icon": "🎉",
    "categories": [
      "Event Venues / Halls",
      "Conference Centers",
      "Banquet Halls",
      "Wedding Venues",
      "Outdoor Event Spaces",
      "Beach Houses",
      "Recreational Parks",
      "Golf Resorts",
      "Sports Complexes / Arenas"
    ]
  },
  {
    "sector": "Industrial & Special Use",
    "icon": "🏭",
    "categories": [
      "Factories",
      "Warehouses",
      "Workshops",
      "Power Plants",
      "Data Centers",
      "Storage Units",
      "Truck Yards",
      "Recycling Facilities"
    ]
  },
  {
    "sector": "Development & Investment",
    "icon": "📈",
    "categories": [
      "Real Estate Projects (Under Construction)",
      "Off-Plan Properties",
      "Housing Estates",
      "Mixed-Use Developments",
      "Property Portfolios",
      "REIT Listings (Real Estate Investment Trusts)"
    ]
  },
  {
    "sector": "Other / Niche Property Types",
    "icon": "🏘️",
    "categories": [
      "Tiny Homes",
      "Modular Homes",
      "Container Homes",
      "Mobile Homes / Caravans",
      "Floating Homes / Houseboats",
      "Religious Buildings",
      "Schools / Educational Buildings",
      "Hospitals / Clinics",
      "Government Buildings",
      "Military / Security Properties"
    ]
  }
];

// Helper function to get all categories as a flat list
export const getAllCategories = () => {
  const allCategories = [];
  PROPERTY_CATEGORIES.forEach(sector => {
    sector.categories.forEach(category => {
      allCategories.push({
        value: category,
        label: category,
        sector: sector.sector
      });
    });
  });
  return allCategories;
};

// Helper function to get sector by category
export const getSectorByCategory = (category) => {
  for (const sector of PROPERTY_CATEGORIES) {
    if (sector.categories.includes(category)) {
      return sector.sector;
    }
  }
  return null;
};

// Helper function to check if category exists
export const isValidCategory = (category) => {
  return getAllCategories().some(cat => cat.value === category);
};
