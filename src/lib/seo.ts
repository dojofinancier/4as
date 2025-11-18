/**
 * SEO utility functions
 */

/**
 * Truncates a string to a maximum length, adding ellipsis if truncated
 */
export function truncateText(text: string, maxLength: number): string {
  if (!text || text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - 3) + '...';
}

/**
 * Truncates title to SEO-friendly length (≤60 chars)
 */
export function truncateTitle(title: string): string {
  return truncateText(title, 60);
}

/**
 * Truncates meta description to SEO-friendly length (≤155 chars)
 */
export function truncateMetaDescription(description: string): string {
  return truncateText(description, 155);
}

/**
 * Generates Organization schema for Carré d'As Tutorat
 */
export function getOrganizationSchema(baseUrl: string) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: "Carré d'As Tutorat",
    url: baseUrl,
    logo: {
      '@type': 'ImageObject',
      url: `${baseUrl}/dark_logo_high.png`,
    },
  };
}

/**
 * Generates BreadcrumbList schema
 */
export function getBreadcrumbSchema(items: Array<{ name: string; url: string }>) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };
}

