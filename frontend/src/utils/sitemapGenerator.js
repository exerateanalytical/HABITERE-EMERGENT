// Sitemap generator for Habitere platform
import { cameroonRegions, cameroonNeighborhoods } from './seoData';

export const generateSitemapUrls = () => {
  const baseUrl = process.env.REACT_APP_FRONTEND_URL || 'https://habitere.com';
  const currentDate = new Date().toISOString().split('T')[0];
  
  const urls = [];
  
  // Main pages
  const mainPages = [
    { url: '', priority: '1.0', changefreq: 'daily' },
    { url: '/properties', priority: '0.9', changefreq: 'hourly' },
    { url: '/services', priority: '0.9', changefreq: 'hourly' },
    { url: '/dashboard', priority: '0.8', changefreq: 'daily' },
    { url: '/profile', priority: '0.6', changefreq: 'weekly' }
  ];
  
  mainPages.forEach(page => {
    urls.push({
      loc: `${baseUrl}${page.url}`,
      lastmod: currentDate,
      changefreq: page.changefreq,
      priority: page.priority
    });
  });
  
  // Regional property pages
  cameroonRegions.forEach(region => {
    // Properties by region
    urls.push({
      loc: `${baseUrl}/properties?location=${encodeURIComponent(region.toLowerCase())}`,
      lastmod: currentDate,
      changefreq: 'daily',
      priority: '0.8'
    });
    
    // Services by region  
    urls.push({
      loc: `${baseUrl}/services?location=${encodeURIComponent(region.toLowerCase())}`,
      lastmod: currentDate,
      changefreq: 'daily',
      priority: '0.8'
    });
    
    // Neighborhood-specific pages for major cities
    if (cameroonNeighborhoods[region]) {
      cameroonNeighborhoods[region].forEach(neighborhood => {
        urls.push({
          loc: `${baseUrl}/properties?location=${encodeURIComponent(region.toLowerCase())}&neighborhood=${encodeURIComponent(neighborhood.toLowerCase())}`,
          lastmod: currentDate,
          changefreq: 'daily', 
          priority: '0.7'
        });
      });
    }
  });
  
  // Property type specific pages
  const propertyTypes = ['maison', 'appartement', 'terrain', 'commercial'];
  const transactionTypes = ['rent', 'sale'];
  
  propertyTypes.forEach(type => {
    transactionTypes.forEach(transaction => {
      urls.push({
        loc: `${baseUrl}/properties?type=${type}&transaction=${transaction}`,
        lastmod: currentDate,
        changefreq: 'daily',
        priority: '0.7'
      });
    });
  });
  
  // Service category pages
  const serviceCategories = [
    'construction', 'plumbing', 'electrical', 'cleaning', 
    'painting', 'carpentry', 'architecture', 'interior'
  ];
  
  serviceCategories.forEach(category => {
    urls.push({
      loc: `${baseUrl}/services?category=${category}`,
      lastmod: currentDate,
      changefreq: 'daily',
      priority: '0.7'
    });
  });
  
  return urls;
};

export const generateSitemapXML = () => {
  const urls = generateSitemapUrls();
  
  let xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`;

  urls.forEach(url => {
    xml += `
  <url>
    <loc>${url.loc}</loc>
    <lastmod>${url.lastmod}</lastmod>
    <changefreq>${url.changefreq}</changefreq>
    <priority>${url.priority}</priority>
  </url>`;
  });
  
  xml += `
</urlset>`;
  
  return xml;
};

// Generate robots.txt content
export const generateRobotsTxt = () => {
  const baseUrl = process.env.REACT_APP_FRONTEND_URL || 'https://habitere.com';
  
  return `User-agent: *
Allow: /

# Important pages
Allow: /properties
Allow: /services
Allow: /properties?*
Allow: /services?*

# Disallow sensitive areas
Disallow: /dashboard
Disallow: /profile
Disallow: /auth/
Disallow: /api/

# Sitemap location
Sitemap: ${baseUrl}/sitemap.xml

# Crawl delay for better server performance
Crawl-delay: 1`;
};

export default {
  generateSitemapUrls,
  generateSitemapXML,
  generateRobotsTxt
};