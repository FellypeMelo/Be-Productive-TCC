package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"

	mysqldriver "github.com/go-sql-driver/mysql"
)

func main() {
	log.SetFlags(0)
	log.Println("Starting Database Seeder (Migration + Mock Data)...")

	// 1. Connect to Database
	dbHost := env("DB_HOST", "localhost") + ":" + env("DB_PORT", "3306")
	dsn := fmt.Sprintf("%s:%s@tcp(%s)/%s?parseTime=true&multiStatements=true",
		env("DB_USER", "root"), env("DB_PASSWORD", ""), dbHost, env("DB_NAME", "be_productive"))
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		log.Fatalf("Error opening database: %v", err)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		log.Fatalf("Error connecting to database (is MySQL running?): %v", err)
	}
	log.Println("Connected to MySQL")

	if _, err := db.Exec(`CREATE TABLE IF NOT EXISTS schema_migration (
		version VARCHAR(255) PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)`); err != nil {
		log.Fatalf("Error creating migration ledger: %v", err)
	}

	// 2. Run unapplied migrations in filename order.
	log.Println("... Running Migrations")
	files, err := os.ReadDir("migrations")
	if err != nil {
		log.Printf("Warning: Could not read migrations directory: %v", err)
	} else {
		for _, f := range files {
			if strings.HasSuffix(f.Name(), ".up.sql") {
				var applied int
				if err := db.QueryRow("SELECT COUNT(*) FROM schema_migration WHERE version = ?", f.Name()).Scan(&applied); err != nil {
					log.Fatalf("Error checking migration %s: %v", f.Name(), err)
				}
				if applied > 0 {
					continue
				}
				log.Printf("... Applying %s", f.Name())
				mContent, err := os.ReadFile(filepath.Join("migrations", f.Name()))
				if err != nil {
					log.Fatalf("Error reading migration %s: %v", f.Name(), err)
				}
				_, err = db.Exec(string(mContent))
				if err != nil {
					if !isExistingSchemaError(err) {
						log.Fatalf("Migration %s failed: %v", f.Name(), err)
					}
					log.Printf("... Existing schema detected for %s; recording baseline", f.Name())
				}
				if _, err := db.Exec("INSERT INTO schema_migration (version) VALUES (?)", f.Name()); err != nil {
					log.Fatalf("Error recording migration %s: %v", f.Name(), err)
				}
			}
		}
	}

	// 3. Read and Execute Mock Data SQL file
	sqlFile := "scripts/mock_data.sql"
	log.Printf("... Reading and applying %s", sqlFile)
	content, err := os.ReadFile(sqlFile)
	if err != nil {
		log.Fatalf("Error reading SQL file: %v", err)
	}

	_, err = db.Exec(string(content))
	if err != nil {
		log.Fatalf("Error executing Mock Data SQL: %v", err)
	}

	log.Println("Database schema and mock data updated successfully!")
}

func isExistingSchemaError(err error) bool {
	mysqlErr, ok := err.(*mysqldriver.MySQLError)
	if !ok {
		return false
	}
	return mysqlErr.Number == 1050 || mysqlErr.Number == 1060 || mysqlErr.Number == 1061
}

func env(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}
