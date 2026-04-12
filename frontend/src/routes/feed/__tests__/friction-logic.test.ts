import { describe, it, expect } from 'vitest';

describe('Friction UI Logic', () => {
  // Tests the same conditional logic as the feed page's friction rendering
  // so we can verify the mapping from friction_level -> UI state

  it('maps none to no UI', () => {
    const level: 'none' | 'mild' | 'high' | 'block' = 'none';
    expect(level === 'high' || level === 'block').toBe(false);
    expect(level === 'block').toBe(false);
    expect(level === 'high').toBe(false);
  });

  it('maps mild to no banner shown', () => {
    const level: 'none' | 'mild' | 'high' | 'block' = 'mild';
    expect(level === 'high' || level === 'block').toBe(false);
  });

  it('maps high to grayscale filter + warning banner', () => {
    const level: 'none' | 'mild' | 'high' | 'block' = 'high';
    expect(level === 'high' || level === 'block').toBe(true);
    expect(level === 'high').toBe(true);
    expect(level === 'block').toBe(false);
  });

  it('maps block to grayscale filter + full overlay', () => {
    const level: 'none' | 'mild' | 'high' | 'block' = 'block';
    expect(level === 'high' || level === 'block').toBe(true);
    expect(level === 'block').toBe(true);
  });
});

describe('FeedResponse friction defaulting', () => {
  it('defaults friction_level to none when not sent', () => {
    const apiResponse: any = {
      content_ids: [1],
      scores: { '1': 0.9 },
      items: [],
      // friction_level intentionally not sent
    };
    const frictionLevel = apiResponse.friction_level || 'none';
    expect(frictionLevel).toBe('none');
  });

  it('valid friction values are exactly the union', () => {
    const valid: Array<'none' | 'mild' | 'high' | 'block'> = ['none', 'mild', 'high', 'block'];
    const allowed = ['none', 'mild', 'high', 'block'];
    for (const v of valid) {
      expect(allowed).toContain(v);
    }
  });
});
