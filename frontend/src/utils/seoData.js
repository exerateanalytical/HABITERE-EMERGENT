// Comprehensive SEO data for Cameroon real estate platform
export const cameroonRegions = [
  'Yaoundé', 'Douala', 'Bafoussam', 'Bamenda', 'Garoua', 'Maroua', 
  'Ngaoundéré', 'Bertoua', 'Ebolowa', 'Kribi'
];

export const cameroonNeighborhoods = {
  'Yaoundé': [
    'Bastos', 'Odza', 'Biyem Assi', 'Omnisport', 'Mimboman', 'Ngousso', 
    'Tsinga', 'Etoa Meki', 'Mokolo', 'Emana', 'Nkol Eton', 'Simbock'
  ],
  'Douala': [
    'Akwa', 'Bonaberi', 'Bonamoussadi', 'Bonapriso', 'Deido', 'Logpom',
    'New Bell', 'Bali', 'Makepe', 'Kotto', 'Ndogpassi'
  ],
  'Bafoussam': [
    'Famla', 'Djeleng', 'Tougang', 'Kingstown', 'Banengo'
  ],
  'Bamenda': [
    'Commercial Avenue', 'Up Station', 'Ntarikon', 'Nkwen', 'Santa Barbara'
  ]
};

export const propertyTypes = {
  'maison': {
    fr: 'Maison',
    en: 'House',
    keywords: ['maison', 'house', 'villa', 'résidence', 'demeure']
  },
  'appartement': {
    fr: 'Appartement', 
    en: 'Apartment',
    keywords: ['appartement', 'apartment', 'studio', 'duplex', 'penthouse']
  },
  'terrain': {
    fr: 'Terrain',
    en: 'Land',
    keywords: ['terrain', 'land', 'lot', 'parcelle', 'lotissement']
  },
  'commercial': {
    fr: 'Commercial',
    en: 'Commercial',
    keywords: ['bureau', 'office', 'magasin', 'shop', 'entrepôt', 'warehouse']
  }
};

export const transactionTypes = {
  'rent': {
    fr: 'à louer',
    en: 'for rent',
    keywords: ['louer', 'rent', 'location', 'rental', 'lease']
  },
  'sale': {
    fr: 'à vendre',
    en: 'for sale', 
    keywords: ['vendre', 'sale', 'buy', 'purchase', 'acheter']
  }
};

// Top Cameroon real estate keywords
export const topKeywords = [
  // French keywords (Yaoundé focus)
  'maison à louer yaoundé',
  'maison à vendre yaoundé',
  'appartement à louer yaoundé',
  'maison à louer bastos yaoundé',
  'maison à louer odza yaoundé', 
  'villa à louer yaoundé',
  'terrain à vendre yaoundé',
  'immobilier yaoundé cameroun',
  
  // English keywords (Douala focus)
  'house for rent douala cameroon',
  'house for sale douala cameroon', 
  'apartment for rent douala',
  'houses for rent bonamoussadi douala',
  'real estate douala cameroon',
  'property for sale cameroon',
  
  // General Cameroon keywords
  'real estate cameroon',
  'immobilier cameroun',
  'property cameroon',
  'houses for sale cameroon',
  'land for sale cameroon',
  'commercial property cameroon'
];

// Generate SEO metadata for different page types
export const generateSEOData = (pageType, data = {}) => {
  const { 
    location = 'Cameroon',
    propertyType = 'property',
    transactionType = 'rent',
    neighborhood = '',
    price = '',
    bedrooms = '',
    area = ''
  } = data;

  const seoTemplates = {
    homepage: {
      title: "Habitere - Real Estate & Property Platform in Cameroon | Houses, Apartments & Land",
      description: "Find houses, apartments & land for rent and sale in Yaoundé, Douala & all Cameroon regions. Verified properties, professional services, secure MTN MoMo payments. #1 real estate platform in Cameroon.",
      keywords: "real estate cameroon, maison à louer yaoundé, house for rent douala, property cameroon, appartement yaoundé, immobilier cameroun, habitere",
      focusKeyword: "real estate cameroon"
    },
    
    properties: {
      title: `Properties for Rent & Sale in ${location} | Houses, Apartments & Land - Habitere`,
      description: `Browse ${data.count || '1000+'} verified properties in ${location}. Find houses, apartments & land for rent and sale. Best prices, verified listings, secure payments with MTN MoMo.`,
      keywords: `properties ${location.toLowerCase()}, maison à louer ${location.toLowerCase()}, house for rent ${location.toLowerCase()}, real estate ${location.toLowerCase()}, immobilier ${location.toLowerCase()}`,
      focusKeyword: `properties ${location.toLowerCase()}`
    },
    
    propertyDetail: {
      title: `${data.title || `${propertyType} ${transactionType} ${location}`} | ${price ? price + ' XAF' : 'Habitere'}`,
      description: `${data.title || `Beautiful ${propertyType} ${transactionType} in ${location}${neighborhood ? ' ' + neighborhood : ''}`}. ${bedrooms ? bedrooms + ' bedrooms, ' : ''}${area ? area + 'm², ' : ''}Verified listing, professional photos, secure booking.`,
      keywords: `${propertyType} ${transactionType} ${location.toLowerCase()}${neighborhood ? ' ' + neighborhood.toLowerCase() : ''}, ${propertyType === 'maison' ? 'maison' : 'house'} ${transactionType === 'rent' ? 'à louer' : 'for sale'} ${location.toLowerCase()}`,
      focusKeyword: `${propertyType} ${transactionType} ${location.toLowerCase()}`
    },
    
    services: {
      title: `Professional Services in ${location} | Construction, Plumbing, Electrical - Habitere`,
      description: `Connect with verified professionals in ${location}. Construction, plumbing, electrical, cleaning & more. Licensed experts, secure payments, 24/7 support across Cameroon.`,
      keywords: `professional services ${location.toLowerCase()}, construction ${location.toLowerCase()}, plumbing ${location.toLowerCase()}, electrical services cameroon, home services ${location.toLowerCase()}`,
      focusKeyword: `professional services ${location.toLowerCase()}`
    },
    
    serviceDetail: {
      title: `${data.title || `Professional ${data.category || 'Service'} in ${location}`} | Habitere`,
      description: `${data.title || `Expert ${data.category || 'service'} professional in ${location}`}. ${data.rating ? `${data.rating}★ rated, ` : ''}Verified, licensed, insured. Book securely with MTN MoMo payments.`,
      keywords: `${data.category || 'service'} ${location.toLowerCase()}, professional ${data.category || 'service'} cameroon, ${data.title ? data.title.toLowerCase() : ''}`,
      focusKeyword: `${data.category || 'service'} ${location.toLowerCase()}`
    }
  };

  return seoTemplates[pageType] || seoTemplates.homepage;
};

// Generate structured data (JSON-LD) for better SEO
export const generateStructuredData = (type, data) => {
  const baseData = {
    "@context": "https://schema.org",
    "address": {
      "@type": "PostalAddress",
      "addressCountry": "CM",
      "addressRegion": data.region || "Centre",
      "addressLocality": data.location || "Yaoundé"
    }
  };

  const schemas = {
    RealEstateAgent: {
      ...baseData,
      "@type": "RealEstateAgent",
      "name": "Habitere",
      "description": "Leading real estate platform in Cameroon",
      "url": "https://habitere.com",
      "telephone": "+27675668211",
      "areaServed": "Cameroon",
      "serviceType": ["Real Estate Sales", "Property Rental", "Property Management"]
    },
    
    Residence: {
      ...baseData,
      "@type": "Residence",
      "name": data.title,
      "description": data.description,
      "numberOfRooms": data.bedrooms,
      "floorSize": {
        "@type": "QuantitativeValue",
        "value": data.area_sqm,
        "unitCode": "MTK"
      },
      "offers": {
        "@type": "Offer",
        "price": data.price,
        "priceCurrency": "XAF",
        "availability": "InStock"
      }
    },
    
    Service: {
      ...baseData,
      "@type": "Service",
      "name": data.title,
      "description": data.description,
      "provider": {
        "@type": "Organization",
        "name": data.provider_name || "Professional Service Provider"
      },
      "areaServed": data.location,
      "serviceType": data.category
    }
  };

  return schemas[type] || schemas.RealEstateAgent;
};

// Regional SEO data for all Cameroon regions
export const regionalSEO = {
  'Yaoundé': {
    keywords: [
      'maison à louer yaoundé', 'appartement yaoundé', 'villa yaoundé',
      'immobilier yaoundé', 'bastos yaoundé', 'odza yaoundé', 'mimboman yaoundé'
    ],
    description: "Capital city properties - premium residential and commercial real estate"
  },
  'Douala': {
    keywords: [
      'house for rent douala', 'apartment douala', 'real estate douala',
      'bonaberi douala', 'akwa douala', 'bonamoussadi douala'
    ],
    description: "Economic capital properties - modern apartments and commercial spaces"
  },
  'Bafoussam': {
    keywords: [
      'maison bafoussam', 'terrain bafoussam', 'immobilier bafoussam',
      'propriété bafoussam', 'location bafoussam'
    ],
    description: "West Region properties - residential homes and agricultural land"
  },
  'Bamenda': {
    keywords: [
      'house bamenda', 'property bamenda', 'real estate bamenda',
      'land bamenda', 'rental bamenda'
    ],
    description: "Northwest Region properties - mountain view homes and land"
  },
  'Garoua': {
    keywords: [
      'maison garoua', 'terrain garoua', 'immobilier garoua',
      'propriété garoua nord', 'location garoua'
    ],
    description: "North Region properties - spacious homes and commercial land"
  }
};

// Real estate company keywords
export const realEstateCompanyKeywords = [
  'agence immobilière cameroun',
  'real estate company cameroon', 
  'promoteur immobilier yaoundé',
  'property developer douala',
  'immobilier professionnel cameroun',
  'courtier immobilier yaoundé',
  'real estate agent douala',
  'société immobilière cameroun',
  'gestionnaire immobilier yaoundé',
  'property management cameroon'
];

export default {
  generateSEOData,
  generateStructuredData,
  cameroonRegions,
  topKeywords,
  regionalSEO,
  realEstateCompanyKeywords
};