/**
 * Logo Component with optimized loading
 */
import { OptimizedImage } from './OptimizedImage';

interface LogoProps {
  className?: string;
  href?: string;
}

export function Logo({ className = 'h-10 sm:h-12 w-auto', href = '/' }: LogoProps) {
  const logo = (
    <OptimizedImage
      src="/dark_logo_high.png"
      alt="Carré d'As Tutorat"
      className={className}
      loading="eager"
      priority={true}
      sizes="(max-width: 640px) 40px, 48px"
    />
  );

  if (href) {
    return <a href={href}>{logo}</a>;
  }

  return logo;
}

