// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1';

interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: {
        message: string;
    };
}

// Generic fetch wrapper
async function fetchApi<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
        (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers,
    });

    // Handle 401 — but NOT for auth endpoints (login/register return 401 for bad credentials)
    if (response.status === 401 && !endpoint.startsWith('/auth/')) {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
            window.location.href = '/login';
        }
        throw new Error('Session expired. Please log in again.');
    }

    // Safely parse JSON (guards against non-JSON responses)
    let json: ApiResponse<T>;
    try {
        json = await response.json();
    } catch {
        const text = await response.text().catch(() => 'Unknown error');
        throw new Error(text || `Request failed with status ${response.status}`);
    }

    if (!response.ok || !json.success) {
        throw new Error(json.error?.message || 'API request failed');
    }

    return json.data as T;
}

// API methods
export const api = {
    // Auth
    login: (email: string, senha: string) =>
        fetchApi<{ token: string; user: User }>('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, senha }),
        }),

    register: (nome: string, email: string, senha: string) =>
        fetchApi<User>('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ nome, email, senha }),
        }),

    // Users
    getUser: (id: number) => fetchApi<User>(`/users/${id}`),

    updateUser: (id: number, nome: string) =>
        fetchApi<User>(`/users/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ nome }),
        }),

    selectTopics: (userId: number, topicIds: number[]) =>
        fetchApi<{ success: boolean }>(`/users/${userId}/topics`, {
            method: 'POST',
            body: JSON.stringify({ topic_ids: topicIds }),
        }),

    getUserTopics: (userId: number) =>
        fetchApi<Topic[]>(`/users/${userId}/topics`).then(data => data || []),

    // Content
    getFeed: (userId: number, category?: string, topicId?: number, limit = 20) => {
        const params = new URLSearchParams({
            user_id: userId.toString(),
            limit: limit.toString(),
        });
        if (category) params.set('category', category);
        if (topicId) params.set('topic_id', topicId.toString());
        return fetchApi<Content[]>(`/feed?${params}`).then(data => data || []);
    },

    getContent: (id: number) => fetchApi<Content>(`/content/${id}`),

    createContent: (data: CreateContentInput) =>
        fetchApi<Content>('/content', {
            method: 'POST',
            body: JSON.stringify(data),
        }),

    submitFeedback: (contentId: number, userId: number, type: string) =>
        fetchApi<{ success: boolean }>(`/content/${contentId}/feedback`, {
            method: 'POST',
            body: JSON.stringify({ user_id: userId, type }),
        }),

    reportContent: (contentId: number, userId: number, motivo: string, detalhes: string) =>
        fetchApi<{ success: boolean }>(`/content/${contentId}/report`, {
            method: 'POST',
            body: JSON.stringify({ user_id: userId, motivo, detalhes }),
        }),

    // Focus
    createGoal: (data: CreateGoalInput) =>
        fetchApi<FocusGoal[]>('/focus/goals', {
            method: 'POST',
            body: JSON.stringify(data),
        }),

    listGoals: (userId: number) =>
        fetchApi<FocusGoal[]>(`/focus/goals?user_id=${userId}`).then(data => data || []),

    listActiveSessions: (userId: number) =>
        fetchApi<Session[]>(`/focus/sessions?user_id=${userId}&active=true`).then(data => data || []),

    getSessionGoals: (sessionId: number) =>
        fetchApi<FocusGoal[]>(`/focus/sessions/${sessionId}/goals`).then(data => data || []),

    startSession: (userId: number, goalIds: number[], modoAbsoluto: boolean) =>
        fetchApi<Session>('/focus/sessions', {
            method: 'POST',
            body: JSON.stringify({ user_id: userId, goal_ids: goalIds, modo_absoluto: modoAbsoluto }),
        }),

    endSession: (sessionId: number, data: EndSessionInput) =>
        fetchApi<Session>(`/focus/sessions/${sessionId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        }),

    getSessionReport: (sessionId: number) =>
        fetchApi<SessionReport>(`/focus/sessions/${sessionId}/report`),

    // Communities (UC04)
    listCommunities: () => fetchApi<Community[]>('/communities').then(data => data || []),

    joinCommunity: (id: number) =>
        fetchApi<{ success: boolean }>(`/communities/${id}/join`, { method: 'POST' }),

    leaveCommunity: (id: number) =>
        fetchApi<{ success: boolean }>(`/communities/${id}/leave`, { method: 'POST' }),

    getMyCommunities: () => fetchApi<Community[]>('/communities/me').then(data => data || []),

    // Settings (UC17)
    getSettings: (userId: number) => fetchApi<UserSettings>(`/users/${userId}/settings`),

    updateSettings: (userId: number, settings: UserSettings) =>
        fetchApi<UserSettings>(`/users/${userId}/settings`, {
            method: 'PUT',
            body: JSON.stringify(settings)
        }),
};

// Types
export interface Community {
    id_comunidade: number;
    nome_comunidade: string;
    topico_principal_id: number;
    regras_de_moderacao: string;
}

export interface UserSettings {
    id_usuario: number;
    sugestao_saudavel_ativa: boolean;
    personalizacao_ativa: boolean;
    notificacao_foco_ativa: boolean;
}
export interface User {
    id_usuario: number;
    nome: string;
    email: string;
    estado_emocional_inferido: string;
}

export interface Topic {
    id_topico: number;
    nome_topico: string;
    descricao: string;
}

export interface Content {
    id_conteudo: number;
    titulo: string;
    corpo: string;
    midia_url?: string;
    tipo_de_midia: 'TEXTO' | 'VIDEO' | 'AUDIO';
    categoria: 'PRODUTIVIDADE' | 'ENTRETENIMENTO';
    autor_id: number;
    data_publicacao: string;
    score_de_qualidade: number;
    tags_relevantes: string;
    topics?: Topic[];
}

export interface CreateContentInput {
    titulo: string;
    corpo: string;
    midia_url?: string;
    tipo_de_midia: string;
    categoria: string;
    autor_id: number;
    topic_ids: number[];
    tags: string;
}

export interface FocusGoal {
    id_meta: number;
    usuario_associado_id: number;
    categoria: 'PRODUTIVIDADE' | 'ENTRETENIMENTO';
    duracao_definida: number;
    status: 'ATIVA' | 'PAUSADA' | 'CONCLUIDA';
}

export interface CreateGoalInput {
    user_id: number;
    tempo_produtividade: number;
    tempo_entretenimento: number;
    modo_absoluto: boolean;
}

export interface Session {
    id_sessao: number;
    usuario_associado_id: number;
    hora_inicio: string;
    hora_fim: string;
    tempo_produtividade_realizado: number;
    tempo_entretenimento_realizado: number;
    feedback_da_sessao: number | null;
    modo_absoluto: boolean;
}

export interface EndSessionInput {
    tempo_produtividade_realizado: number;
    tempo_entretenimento_realizado: number;
    feedback: number | null;
}

export interface SessionReport {
    session: Session;
    goals: FocusGoal[];
    classification: 'progresso' | 'nao_concluido' | 'compromisso_perdido' | 'concluido';
    message: string;
}
