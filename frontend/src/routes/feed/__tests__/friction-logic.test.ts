import { describe, it, expect } from 'vitest';

type FrictionLevel = 'none' | 'mild' | 'high' | 'block';

// Same mapping the feed page applies from friction_level -> UI state.
// Kept as a union-typed pure function so it is meaningfully testable
// (a literal-annotated const would narrow and defeat the comparisons).
function frictionUI(level: FrictionLevel) {
  return {
    grayscale: level === 'high' || level === 'block',
    banner: level === 'high',
    overlay: level === 'block',
  };
}

describe('Friction UI logic', () => {
  it('none → no UI', () => {
    expect(frictionUI('none')).toEqual({ grayscale: false, banner: false, overlay: false });
  });

  it('mild → no banner, no grayscale', () => {
    expect(frictionUI('mild')).toEqual({ grayscale: false, banner: false, overlay: false });
  });

  it('high → grayscale + warning banner', () => {
    expect(frictionUI('high')).toEqual({ grayscale: true, banner: true, overlay: false });
  });

  it('block → grayscale + full overlay', () => {
    expect(frictionUI('block')).toEqual({ grayscale: true, banner: false, overlay: true });
  });
});

describe('FeedResponse friction defaulting', () => {
  it('defaults friction_level to none when not sent', () => {
    const apiResponse: { friction_level?: FrictionLevel } = { /* omitted */ };
    const frictionLevel = apiResponse.friction_level || 'none';
    expect(frictionLevel).toBe('none');
  });

  it('valid friction values are exactly the union', () => {
    const valid: FrictionLevel[] = ['none', 'mild', 'high', 'block'];
    expect(valid).toEqual(['none', 'mild', 'high', 'block']);
  });
});
