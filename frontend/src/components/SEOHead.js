import React from 'react';
import { Helmet } from 'react-helmet-async';

const SEOHead = ({ 
  title,
  description, 
  keywords,
  focusKeyword,
  canonicalUrl,
  structuredData,
  ogImage,
  ogType = 'website',
  twitterCard = 'summary_large_image',
  noindex = false,
  location = 'Cameroon',
  propertyType,
  price
}) => {
  const siteName = 'Habitere';
  const defaultImage = 'https://habitere.com/og-image.jpg';
  const currentUrl = typeof window !== 'undefined' ? window.location.href : '';

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      
      {/* Focus Keyword for SEO */}
      <meta name="focus-keyword" content={focusKeyword} />
      
      {/* Canonical URL */}
      <link rel="canonical" href={canonicalUrl || currentUrl} />
      
      {/* Robots */}
      <meta name="robots" content={noindex ? 'noindex,nofollow' : 'index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1'} />
      
      {/* Open Graph Tags */}
      <meta property="og:locale" content="en_US" />
      <meta property="og:locale:alternate" content="fr_FR" />
      <meta property="og:type" content={ogType} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={canonicalUrl || currentUrl} />
      <meta property="og:site_name" content={siteName} />
      <meta property="og:image" content={ogImage || defaultImage} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:image:alt" content={title} />
      
      {/* Twitter Card Tags */}
      <meta name="twitter:card" content={twitterCard} />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={ogImage || defaultImage} />
      <meta name="twitter:image:alt" content={title} />
      
      {/* Geographic Tags for Cameroon SEO */}
      <meta name="geo.region" content="CM" />
      <meta name="geo.placename" content={location} />
      <meta name="ICBM" content="6.2088,12.1067" /> {/* Cameroon coordinates */}
      
      {/* Real Estate Specific Meta Tags */}
      {propertyType && <meta name="property:type" content={propertyType} />}
      {price && <meta name="property:price" content={price} />}
      <meta name="property:country" content="Cameroon" />
      <meta name="property:region" content={location} />
      
      {/* Language and Regional Tags */}
      <meta httpEquiv="content-language" content="en" />
      <meta name="language" content="English" />
      
      {/* Additional SEO Tags */}
      <meta name="author" content="Habitere" />
      <meta name="publisher" content="Habitere" />
      <meta name="copyright" content="© 2024 Habitere. All rights reserved." />
      <meta name="rating" content="general" />
      <meta name="distribution" content="global" />
      
      {/* Mobile and Responsive Tags */}
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta name="mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
      
      {/* Structured Data */}
      {structuredData && (
        <script type="application/ld+json">
          {JSON.stringify(structuredData)}
        </script>
      )}
      
      {/* Additional Cameroon-specific meta tags */}
      <meta name="cameroon-real-estate" content="true" />
      <meta name="african-property" content="cameroon" />
      <meta name="central-africa-real-estate" content="true" />
    </Helmet>
  );
};

export default SEOHead;