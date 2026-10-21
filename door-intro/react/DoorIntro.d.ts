import type { FC } from 'react';

export interface DoorIntroOptions {
  preset?: 'neutral' | 'opendoors' | string;
  brandName?: string;
  logoUrl?: string;
  logoAlt?: string;
  logoHeight?: number;
  imageUrl?: string;
  imageSrcset?: string;
  imageSizes?: string;
  imageAlt?: string;
  imagePosition?: string;
  imageTimeout?: number;
  welcomeText?: string;
  revealText?: string;
  primaryColor?: string;
  accentColor?: string;
  accentColor2?: string;
  textColor?: string;
  doorColor?: string;
  doorStyle?: 'classic' | 'modern' | 'glass';
  showHandles?: boolean;
  showFrame?: boolean;
  fontDisplay?: string;
  fontBody?: string;
  duration?: number;
  playMode?: 'session' | 'once' | 'always' | 'manual';
  storageKey?: string;
  urlParam?: string;
  reducedMotion?: 'fade' | 'skip';
  skipForBots?: boolean;
  skipButton?: boolean;
  skipLabel?: string;
  clickToSkip?: boolean;
  skipOnScroll?: boolean;
  replayButton?: 'floating' | 'none';
  replayLabel?: string;
  replayPosition?: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right';
  replaySelector?: string;
  soundUrl?: string;
  soundLabel?: string;
  zIndex?: number;
  onStart?: () => void;
  onComplete?: (reason: 'complete' | 'skip') => void;
}

export interface DoorIntroProps extends DoorIntroOptions {
  /** Play even if the visitor has already seen the intro. */
  force?: boolean;
}

declare const DoorIntro: FC<DoorIntroProps>;
export default DoorIntro;
export function replayDoorIntro(): void;
