/**
 * Optimized Image Component
 * Supports WebP with PNG fallback, lazy loading, and proper sizes attribute
 */

interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  sizes?: string;
  loading?: 'lazy' | 'eager';
  priority?: boolean;
}

export function OptimizedImage({
  src,
  alt,
  className = '',
  width,
  height,
  sizes = '(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw',
  loading = 'lazy',
  priority = false,
}: OptimizedImageProps) {
  // Convert PNG to WebP path
  const getWebPSrc = (originalSrc: string) => {
    if (originalSrc.startsWith('http')) {
      // External URL - return as is
      return originalSrc;
    }
    // Convert /path/to/image.png to /path/to/image.webp
    return originalSrc.replace(/\.(png|jpg|jpeg)$/i, '.webp');
  };

  const webpSrc = getWebPSrc(src);
  const isWebP = webpSrc !== src;

  // For logo images, we'll use eager loading since they're above the fold
  const loadStrategy = priority ? 'eager' : loading;

  return (
    <picture>
      {isWebP && (
        <source srcSet={webpSrc} type="image/webp" />
      )}
      <img
        src={src}
        alt={alt}
        className={className}
        width={width}
        height={height}
        sizes={sizes}
        loading={loadStrategy}
        decoding="async"
      />
    </picture>
  );
}

