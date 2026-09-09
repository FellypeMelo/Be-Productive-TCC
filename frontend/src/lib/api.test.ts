import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from './api';

vi.stubGlobal('fetch', vi.fn());

describe('API client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('includes auth token in request headers', async () => {
    localStorage.setItem('auth_token', 'test-token');
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ success: true, data: { id_usuario: 1 } }),
    });

    await api.getUser(1);

    const callArgs = (global.fetch as any).mock.calls[0][1];
    expect(callArgs.headers.Authorization).toBe('Bearer test-token');
  });

  it('handles 401 by clearing auth storage', async () => {
    localStorage.setItem('auth_token', 'stale');
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    await expect(api.getUser(1)).rejects.toThrow();
    expect(localStorage.getItem('auth_token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  it('getFeed returns FeedResponse shape', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve({
        success: true,
        data: {
          content_ids: [1, 2],
          scores: { '1': 0.9, '2': 0.8 },
          items: [
            { id_conteudo: 1, titulo: 'Content 1', categoria: 'PRODUTIVIDADE', tipo_de_midia: 'VIDEO', autor_id: 1, data_publicacao: '2026-01-01', score_de_qualidade: 0.9, corpo: '', tags_relevantes: '' },
            { id_conteudo: 2, titulo: 'Content 2', categoria: 'ENTRETENIMENTO', tipo_de_midia: 'AUDIO', autor_id: 2, data_publicacao: '2026-01-01', score_de_qualidade: 0.8, corpo: '', tags_relevantes: '' },
          ],
          friction_level: 'mild',
        },
      }),
    });

    const result = await api.getFeed(1);

    expect(result.content_ids).toEqual([1, 2]);
    expect(result.friction_level).toBe('mild');
    expect(result.items).toHaveLength(2);
  });

  it('getFeed passes category and topic_id query params', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve({
        success: true,
        data: { content_ids: [], scores: {}, items: [], friction_level: 'none' },
      }),
    });

    await api.getFeed(1, 'PRODUTIVIDADE', 42);

    const url = (global.fetch as any).mock.calls[0][0];
    expect(url).toContain('category=PRODUTIVIDADE');
    expect(url).toContain('topic_id=42');
  });

  it('getFeed sends only the binary protection order', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve({
        success: true,
        data: { content_ids: [], scores: {}, items: [], friction_level: 'high' },
      }),
    });

    await api.getFeed(1, undefined, undefined, 20, false, undefined, true);

    const url = (global.fetch as any).mock.calls[0][0];
    expect(url).toContain('protective_mode_active=true');
    expect(url).not.toContain('v_scroll');
    expect(url).not.toContain('v_alt');
  });

  it('non-auth endpoint 401 throws error', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    await expect(api.getUser(1)).rejects.toThrow();
  });
});
