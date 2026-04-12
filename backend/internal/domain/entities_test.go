package domain_test

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/be-productive/backend/internal/domain"
	"github.com/stretchr/testify/assert"
)

func TestUserJSONOmitsPassword(t *testing.T) {
	u := domain.User{
		ID:                 1,
		Nome:               "Test User",
		Email:              "test@example.com",
		SenhaCriptografada: "secret_should_not_appear_in_json",
	}
	data, err := json.Marshal(u)
	assert.NoError(t, err)
	assert.NotContains(t, string(data), "secret_should_not_appear_in_json")
}

func TestUserJSONMarshalDoesNotIncludePassword(t *testing.T) {
	u := domain.User{
		ID:                 1,
		Nome:               "Test User",
		Email:              "test@example.com",
		SenhaCriptografada: "secret",
	}
	data, err := json.Marshal(u)
	assert.NoError(t, err)
	assert.NotContains(t, string(data), "secret")
	assert.Contains(t, string(data), "email")
}

func TestContentCategoryEnums(t *testing.T) {
	assert.Equal(t, domain.ContentCategory("PRODUTIVIDADE"), domain.CategoryProdutividade)
	assert.Equal(t, domain.ContentCategory("ENTRETENIMENTO"), domain.CategoryEntretenimento)
}

func TestContentTypeEnums(t *testing.T) {
	assert.Equal(t, domain.ContentType("TEXTO"), domain.ContentTypeTexto)
	assert.Equal(t, domain.ContentType("VIDEO"), domain.ContentTypeVideo)
	assert.Equal(t, domain.ContentType("AUDIO"), domain.ContentTypeAudio)
}

func TestFocusGoalStatusEnums(t *testing.T) {
	assert.Equal(t, domain.FocusGoalStatus("ATIVA"), domain.FocusGoalStatusAtiva)
	assert.Equal(t, domain.FocusGoalStatus("PAUSADA"), domain.FocusGoalStatusPausada)
	assert.Equal(t, domain.FocusGoalStatus("CONCLUIDA"), domain.FocusGoalStatusConcluida)
}

func TestFocusGoalCreation(t *testing.T) {
	goal := domain.FocusGoal{
		UsuarioAssociadoID: 1,
		Categoria:          domain.CategoryProdutividade,
		DuracaoDefinida:    30,
		Status:             domain.FocusGoalStatusAtiva,
	}
	assert.Equal(t, int(30), goal.DuracaoDefinida)
	assert.Equal(t, domain.CategoryProdutividade, goal.Categoria)
	assert.Equal(t, domain.FocusGoalStatusAtiva, goal.Status)
}

func TestSessionCreation(t *testing.T) {
	fb := 5
	session := domain.Session{
		UsuarioAssociadoID:           1,
		HoraInicio:                   time.Now(),
		TempoProdutividadeRealizado:  25,
		TempoEntretenimentoRealizado: 10,
		FeedbackDaSessao:             &fb,
		ModoAbsoluto:                 true,
	}
	assert.True(t, session.ModoAbsoluto)
	assert.NotNil(t, session.FeedbackDaSessao)
	assert.Equal(t, 5, *session.FeedbackDaSessao)
}

func TestSessionNilFeedback(t *testing.T) {
	session := domain.Session{
		UsuarioAssociadoID:           1,
		HoraInicio:                   time.Now(),
		TempoProdutividadeRealizado:  0,
		TempoEntretenimentoRealizado: 0,
		FeedbackDaSessao:             nil,
		ModoAbsoluto:                 false,
	}
	assert.Nil(t, session.FeedbackDaSessao)
	assert.False(t, session.ModoAbsoluto)
}

func TestUserSettingsCreation(t *testing.T) {
	settings := domain.UserSettings{
		UsuarioID:             1,
		SugestaoSaudavelAtiva: true,
		PersonalizacaoAtiva:   true,
		NotificacaoFocoAtiva:  false,
	}
	assert.True(t, settings.SugestaoSaudavelAtiva)
	assert.True(t, settings.PersonalizacaoAtiva)
	assert.False(t, settings.NotificacaoFocoAtiva)
}

func TestDomainErrorsAreDistinct(t *testing.T) {
	errs := []error{
		domain.ErrNotFound,
		domain.ErrUnauthorized,
		domain.ErrForbidden,
		domain.ErrInvalidInput,
		domain.ErrAlreadyExists,
		domain.ErrInternalServer,
		domain.ErrInvalidCredentials,
	}
	for i, e1 := range errs {
		for j, e2 := range errs {
			if i != j {
				assert.NotEqual(t, e1.Error(), e2.Error(), "error %d and %d should be distinct", i, j)
			}
		}
	}
}

func TestTopicCreation(t *testing.T) {
	topic := domain.Topic{
		ID:         1,
		NomeTopico: "Focus",
		Descricao:  "Focus and productivity",
	}
	assert.Equal(t, "Focus", topic.NomeTopico)
	assert.Equal(t, "Focus and productivity", topic.Descricao)
}

func TestCommunityCreation(t *testing.T) {
	comm := domain.Community{
		ID:                1,
		NomeComunidade:    "Deep Work",
		TopicoPrincipalID: 1,
		RegrasDeModeração: "No spam",
	}
	assert.Equal(t, "Deep Work", comm.NomeComunidade)
	assert.Equal(t, int64(1), comm.TopicoPrincipalID)
}
