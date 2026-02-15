package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"strings"

	_ "github.com/go-sql-driver/mysql"
)

// Config - XAMPP Defaults
const (
	DBDriver = "mysql"
	DBUser   = "root"
	DBPass   = ""
	DBName   = "be_productive"
	DBHost   = "localhost:3306"
)

func main() {
	log.SetFlags(0)
	log.Println("Starting Database Seeder (Migration + Mock Data)...")

	// 1. Connect to Database
	dsn := fmt.Sprintf("%s:%s@tcp(%s)/%s?parseTime=true&multiStatements=true", DBUser, DBPass, DBHost, DBName)
	db, err := sql.Open(DBDriver, dsn)
	if err != nil {
		log.Fatalf("Error opening database: %v", err)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		log.Fatalf("Error connecting to database (is MySQL running?): %v", err)
	}
	log.Println("Connected to MySQL")

	// 2. Run Migrations first
	log.Println("... Running Migrations")
	files, err := os.ReadDir("migrations")
	if err != nil {
		log.Printf("Warning: Could not read migrations directory: %v", err)
	} else {
		for _, f := range files {
			if strings.HasSuffix(f.Name(), ".up.sql") {
				log.Printf("... Applying %s", f.Name())
				mContent, err := os.ReadFile("migrations/" + f.Name())
				if err != nil {
					log.Printf("Error reading migration %s: %v", f.Name(), err)
					continue
				}
				_, err = db.Exec(string(mContent))
				if err != nil {
					log.Printf("Warning: Migration %s maybe partially failed or already applied: %v", f.Name(), err)
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
