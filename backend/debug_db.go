package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/go-sql-driver/mysql"
)

func main() {
	db, err := sql.Open("mysql", "root:@tcp(127.0.0.1:3306)/be_productive?parseTime=true")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	rows, err := db.Query("SELECT id_conteudo, titulo, tipo_de_midia, COALESCE(midia_url, '') FROM conteudo WHERE tipo_de_midia IN ('VIDEO', 'AUDIO') LIMIT 5")
	if err != nil {
		log.Fatalf("Error querying: %v", err)
	}
	defer rows.Close()

	for rows.Next() {
		var id int64
		var titulo, tipoMidia, midiaURL string
		if err := rows.Scan(&id, &titulo, &tipoMidia, &midiaURL); err != nil {
			log.Fatal(err)
		}
		fmt.Printf("ID: %d | Type: %s | URL: %s\n", id, tipoMidia, midiaURL)
	}
}
