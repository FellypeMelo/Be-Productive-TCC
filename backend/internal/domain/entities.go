package domain

import "time"

// User represents a platform user
type User struct {
	ID                      int64     `json:"id_usuario"`
	Nome                    string    `json:"nome"`
	Email                   string    `json:"email"`
	SenhaCriptografada      string    `json:"-"`
	EstadoEmocionalInferido string    `json:"estado_emocional_inferido"`
	CreatedAt               time.Time `json:"created_at"`
	UpdatedAt               time.Time `json:"updated_at"`
}

// Topic represents an interest topic
type Topic struct {
	ID         int64  `json:"id_topico"`
	NomeTopico string `json:"nome_topico"`
	Descricao  string `json:"descricao"`
}

// Community represents a topic-based community
type Community struct {
	ID                int64  `json:"id_comunidade"`
	NomeComunidade    string `json:"nome_comunidade"`
	TopicoPrincipalID int64  `json:"topico_principal_id"`
	RegrasDeModeração string `json:"regras_de_moderacao"`
}

// ContentCategory enum
type ContentCategory string

const (
	CategoryProdutividade  ContentCategory = "PRODUTIVIDADE"
	CategoryEntretenimento ContentCategory = "ENTRETENIMENTO"
)

// ContentType enum
type ContentType string

const (
	ContentTypeTexto ContentType = "TEXTO"
	ContentTypeVideo ContentType = "VIDEO"
	ContentTypeAudio ContentType = "AUDIO"
)

// Content represents user-published content
type Content struct {
	ID               int64           `json:"id_conteudo"`
	Titulo           string          `json:"titulo"`
	Corpo            string          `json:"corpo"`
	MidiaURL         string          `json:"midia_url,omitempty"`
	TipoDeMidia      ContentType     `json:"tipo_de_midia"`
	Categoria        ContentCategory `json:"categoria"`
	AutorID          int64           `json:"autor_id"`
	DataPublicacao   time.Time       `json:"data_publicacao"`
	TagsRelevantes   string          `json:"tags_relevantes"`
	ScoreDeQualidade float64         `json:"score_de_qualidade"`
	Topics           []Topic         `json:"topics,omitempty"`
}

// ContentInteraction is a ranking signal from an authenticated user.
type ContentInteraction struct {
	EventID       string    `json:"event_id"`
	ContentID     int64     `json:"content_id"`
	UserID        int64     `json:"user_id"`
	Type          string    `json:"type"`
	DwellSeconds  int       `json:"dwell_seconds"`
	Position      int       `json:"position"`
	Algorithm     string    `json:"algorithm"`
	Experiment    string    `json:"experiment"`
	FrictionLevel string    `json:"friction_level"`
	CreatedAt     time.Time `json:"created_at"`
}

// ExperimentExposure records the minimum server-side exposure contract for an
// eligible real-user experiment. It intentionally contains no raw telemetry.
type ExperimentExposure struct {
	EventID           string    `json:"event_id"`
	ExperimentID      string    `json:"experiment_id"`
	Variant           string    `json:"variant"`
	AssignmentVersion string    `json:"assignment_version"`
	AlgorithmVersion  string    `json:"algorithm_version"`
	RequestID         string    `json:"request_id"`
	UserID            int64     `json:"user_id"`
	Eligible          bool      `json:"eligible"`
	Served            bool      `json:"served"`
	Fallback          bool      `json:"fallback"`
	PositionCount     int       `json:"position_count"`
	CreatedAt         time.Time `json:"created_at"`
}

// FocusGoalStatus enum
type FocusGoalStatus string

const (
	FocusGoalStatusAtiva     FocusGoalStatus = "ATIVA"
	FocusGoalStatusPausada   FocusGoalStatus = "PAUSADA"
	FocusGoalStatusConcluida FocusGoalStatus = "CONCLUIDA"
)

// FocusGoal represents a user's focus goal
type FocusGoal struct {
	ID                 int64           `json:"id_meta"`
	UsuarioAssociadoID int64           `json:"usuario_associado_id"`
	Categoria          ContentCategory `json:"categoria"`
	DuracaoDefinida    int             `json:"duracao_definida"` // in minutes
	Status             FocusGoalStatus `json:"status"`
}

// UserSettings represents user preferences (UC17)
type UserSettings struct {
	UsuarioID             int64 `json:"id_usuario"`
	SugestaoSaudavelAtiva bool  `json:"sugestao_saudavel_ativa"`
	PersonalizacaoAtiva   bool  `json:"personalizacao_ativa"`
	NotificacaoFocoAtiva  bool  `json:"notificacao_foco_ativa"`
	PesquisaConsentimento bool  `json:"consentimento_pesquisa"`
	PesquisaConsentimentoVersao string `json:"consentimento_pesquisa_versao,omitempty"`
}

// Session represents a focus session
type Session struct {
	ID                           int64     `json:"id_sessao"`
	UsuarioAssociadoID           int64     `json:"usuario_associado_id"`
	HoraInicio                   time.Time `json:"hora_inicio"`
	HoraFim                      time.Time `json:"hora_fim"`
	TempoProdutividadeRealizado  int       `json:"tempo_produtividade_realizado"`
	TempoEntretenimentoRealizado int       `json:"tempo_entretenimento_realizado"`
	FeedbackDaSessao             *int      `json:"feedback_da_sessao"` // 1-5, nullable
	ModoAbsoluto                 bool      `json:"modo_absoluto"`
}
