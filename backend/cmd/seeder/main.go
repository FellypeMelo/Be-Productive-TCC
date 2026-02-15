package main

import (
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"fmt"
	"log"
	"math/rand"
	"os"
	"strings"

	_ "github.com/go-sql-driver/mysql"
)

// Config - XAMPP Defaults
const (
	DBDriver      = "mysql"
	DBUser        = "root"
	DBPass        = ""
	DBName        = "be_productive"
	DBHost        = "localhost:3306"
	MigrationFile = "migrations/001_create_tables.up.sql"
)

func main() {
	log.SetFlags(0) // KISS: Clean output
	log.Println("Starting Database Seeder...")

	// 1. Connect to Database
	dsn := fmt.Sprintf("%s:%s@tcp(%s)/%s?parseTime=true", DBUser, DBPass, DBHost, DBName)
	db, err := sql.Open(DBDriver, dsn)
	if err != nil {
		log.Fatalf("Error opening database: %v", err)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		log.Fatalf("Error connecting to database (is MySQL running?): %v", err)
	}
	log.Println("Connected to MySQL")

	// 1.5. Run Migrations (KISS: Simple runner for all .up.sql files)
	log.Println("... Checking/Running Migrations")
	files, err := os.ReadDir("migrations")
	if err != nil {
		log.Printf("Warning: Could not read migrations directory: %v", err)
	} else {
		for _, f := range files {
			if strings.HasSuffix(f.Name(), ".up.sql") {
				log.Printf("... Running %s", f.Name())
				migrationSQL, err := os.ReadFile("migrations/" + f.Name())
				if err != nil {
					log.Printf("Error reading %s: %v", f.Name(), err)
					continue
				}
				statements := strings.Split(string(migrationSQL), ";")
				for _, stmt := range statements {
					stmt = strings.TrimSpace(stmt)
					if stmt == "" {
						continue
					}
					_, err := db.Exec(stmt)
					if err != nil {
						log.Printf("Warning: Migration %s stmt warning: %v", f.Name(), err)
					}
				}
			}
		}
		log.Println("Migrations executed")
	}

	// 2. Data Pools
	names := []string{"Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy"}
	topics := []string{
		"Technology", "Productivity", "Mental Health", "Music", "Movies", "Gaming",
		"Reading", "Fitness", "Meditation", "Cooking", "Science", "History",
	}

	// 3. Transactions for Safety
	tx, err := db.Begin()
	if err != nil {
		log.Fatal(err)
	}
	defer tx.Rollback()

	// 3.5. Clean Slate (KISS: Truncate existing data to avoid duplicates/old mock data)
	log.Println("... Cleaning existing data")
	tables := []string{"feedback_conteudo", "denuncia", "conteudo_topico", "usuario_topico", "conteudo", "topico", "usuario"}
	tx.Exec("SET FOREIGN_KEY_CHECKS = 0")
	for _, table := range tables {
		tx.Exec("TRUNCATE TABLE " + table)
	}
	tx.Exec("SET FOREIGN_KEY_CHECKS = 1")

	// 4. Seed Users
	log.Println("... Seeding Users")
	var userIDs []int64
	stmtUser, err := tx.Prepare("INSERT INTO usuario (nome, email, senha_criptografada, estado_emocional_inferido) VALUES (?, ?, ?, ?)")
	if err != nil {
		log.Fatalf("Error preparing user statement: %v", err)
	}
	defaultPass := hashPassword("password123")

	for i, name := range names {
		email := fmt.Sprintf("%s%d@example.com", name, i)
		res, err := stmtUser.Exec(name, email, defaultPass, "NEUTRO")
		if err != nil {
			log.Printf("Warning: Skipping user %s (maybe exists): %v", email, err)
			continue
		}
		id, _ := res.LastInsertId()
		userIDs = append(userIDs, id)
	}
	stmtUser.Close()

	// 5. Seed Topics
	log.Println("... Seeding Topics")
	var topicIDs []int64
	stmtTopic, err := tx.Prepare("INSERT INTO topico (nome_topico, descricao) VALUES (?, ?)")
	if err != nil {
		log.Fatalf("Error preparing topic statement: %v", err)
	}
	for _, t := range topics {
		res, err := stmtTopic.Exec(t, "Description for "+t)
		if err != nil {
			continue // Likely exists
		}
		id, _ := res.LastInsertId()
		topicIDs = append(topicIDs, id)
	}
	stmtTopic.Close()

	// Get all topic IDs if we skipped some (KISS: just fetch them back)
	rows, err := tx.Query("SELECT id_topico FROM topico")
	if err != nil {
		log.Fatalf("Error querying topics: %v", err)
	}
	topicIDs = nil // reset
	for rows.Next() {
		var id int64
		rows.Scan(&id)
		topicIDs = append(topicIDs, id)
	}
	rows.Close()

	// 6. Seed Content & Interactions
	log.Println("... Seeding Content and Interactions")
	stmtContent, err := tx.Prepare("INSERT INTO conteudo (titulo, corpo, midia_url, tipo_de_midia, categoria, autor_id, score_de_qualidade, tags_relevantes, data_publicacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NOW())")
	if err != nil {
		log.Fatalf("Error preparing content statement: %v", err)
	}
	stmtFeedback, err := tx.Prepare("INSERT INTO feedback_conteudo (id_conteudo, id_usuario, tipo) VALUES (?, ?, ?)")
	if err != nil {
		log.Fatalf("Error preparing feedback statement: %v", err)
	}

	mediaTypes := []string{"TEXTO", "VIDEO", "AUDIO"}
	categories := []string{"PRODUTIVIDADE", "ENTRETENIMENTO"}

	for i := 0; i < 50; i++ {
		if len(userIDs) == 0 {
			break
		}
		author := userIDs[rand.Intn(len(userIDs))]
		title := fmt.Sprintf("Content Title %d", i)
		tags := fmt.Sprintf("tag%d,mock,be-productive", i%5)
		mediaType := mediaTypes[rand.Intn(len(mediaTypes))]

		var midiaURL string
		switch mediaType {
		case "VIDEO":
			midiaURL = "https://www.youtube.com/embed/dQw4w9WgXcQ" // Rickroll for testing KISS
		case "AUDIO":
			midiaURL = "https://w.soundcloud.com/player/?url=https%%3A//api.soundcloud.com/tracks/293" // Random SC track
		default:
			midiaURL = ""
		}

		res, err := stmtContent.Exec(
			title,
			"This is some mock content body.",
			midiaURL,
			mediaType,
			categories[rand.Intn(len(categories))],
			author,
			0.5+rand.Float64()*0.5,
			tags,
		)
		if err != nil {
			continue
		}

		contentID, _ := res.LastInsertId()

		// Add random feedback
		for j := 0; j < rand.Intn(5); j++ {
			reactor := userIDs[rand.Intn(len(userIDs))]
			stmtFeedback.Exec(contentID, reactor, "util")
		}
	}
	stmtContent.Close()
	stmtFeedback.Close()

	// 7. Commit
	if err := tx.Commit(); err != nil {
		log.Fatalf("Error committing transaction: %v", err)
	}

	log.Println("Database seeded successfully! (KISS: Simple, Safe, Fast)")
}

func hashPassword(password string) string {
	hash := sha256.Sum256([]byte(password))
	return hex.EncodeToString(hash[:])
}
