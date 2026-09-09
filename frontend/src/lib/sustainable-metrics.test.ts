import { describe, expect, it } from 'vitest';
import { LocalReserveAccumulator } from './sustainable-metrics';

describe('LocalReserveAccumulator', () => {
    it('calculates normalized reserve AUC locally', () => {
        const metrics = new LocalReserveAccumulator();
        metrics.observe(1, 10);
        metrics.observe(0.5, 10);
        expect(metrics.snapshot(123).normalized_reserve_auc).toBe(0.75);
        expect(metrics.snapshot(123).observed_seconds).toBe(20);
    });

    it('rejects malformed snapshots', () => {
        const metrics = new LocalReserveAccumulator();
        expect(metrics.restore({ version: 1, observed_seconds: 1, normalized_reserve_auc: 2, updated_at: 1 })).toBe(false);
    });
});
