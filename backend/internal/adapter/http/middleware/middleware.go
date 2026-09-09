package middleware

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// CORS adds Cross-Origin Resource Sharing headers
func CORS(allowedOrigins []string, next http.Handler) http.Handler {
	allowed := make(map[string]struct{}, len(allowedOrigins))
	for _, origin := range allowedOrigins {
		allowed[origin] = struct{}{}
	}
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		origin := r.Header.Get("Origin")
		if origin != "" {
			if _, ok := allowed[origin]; !ok {
				http.Error(w, "origin not allowed", http.StatusForbidden)
				return
			}
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Vary", "Origin")
		}
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Request-ID")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func SecurityHeaders(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("X-Frame-Options", "DENY")
		w.Header().Set("Referrer-Policy", "no-referrer")
		w.Header().Set("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
		w.Header().Set("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
		next.ServeHTTP(w, r)
	})
}

func BodyLimit(maxBytes int64, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Body != nil {
			r.Body = http.MaxBytesReader(w, r.Body, maxBytes)
		}
		next.ServeHTTP(w, r)
	})
}

var requestSequence uint64

func RequestID(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		id := strings.TrimSpace(r.Header.Get("X-Request-ID"))
		if id == "" || len(id) > 128 {
			id = fmt.Sprintf("%x-%x", time.Now().UnixMilli(), atomic.AddUint64(&requestSequence, 1))
		}
		w.Header().Set("X-Request-ID", id)
		r.Header.Set("X-Request-ID", id)
		next.ServeHTTP(w, r)
	})
}

type rateWindow struct {
	count int
	reset time.Time
}

type RateLimiter struct {
	mu      sync.Mutex
	clients map[string]rateWindow
	limit   int
	window  time.Duration
}

func NewRateLimiter(limit int, window time.Duration) *RateLimiter {
	return &RateLimiter{clients: make(map[string]rateWindow), limit: limit, window: window}
}

func (l *RateLimiter) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		host := r.RemoteAddr
		if i := strings.LastIndex(host, ":"); i > 0 {
			host = host[:i]
		}
		now := time.Now()
		l.mu.Lock()
		entry := l.clients[host]
		if entry.reset.IsZero() || now.After(entry.reset) {
			entry = rateWindow{reset: now.Add(l.window)}
		}
		entry.count++
		l.clients[host] = entry
		if len(l.clients) > 10000 {
			for client, candidate := range l.clients {
				if now.After(candidate.reset) {
					delete(l.clients, client)
				}
			}
		}
		remaining := l.limit - entry.count
		l.mu.Unlock()
		w.Header().Set("X-RateLimit-Limit", strconv.Itoa(l.limit))
		w.Header().Set("X-RateLimit-Remaining", strconv.Itoa(max(0, remaining)))
		if entry.count > l.limit {
			w.Header().Set("Retry-After", strconv.Itoa(max(1, int(time.Until(entry.reset).Seconds()))))
			http.Error(w, "rate limit exceeded", http.StatusTooManyRequests)
			return
		}
		next.ServeHTTP(w, r)
	})
}

type Metrics struct {
	mu       sync.Mutex
	requests map[string]uint64
	duration map[string]time.Duration
}

func NewMetrics() *Metrics {
	return &Metrics{requests: make(map[string]uint64), duration: make(map[string]time.Duration)}
}

func (m *Metrics) Middleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		rw := &responseWriter{ResponseWriter: w, status: http.StatusOK}
		next.ServeHTTP(rw, r)
		pattern := r.Pattern
		if pattern == "" {
			pattern = "unmatched"
		}
		key := r.Method + "|" + pattern + "|" + strconv.Itoa(rw.status)
		m.mu.Lock()
		m.requests[key]++
		m.duration[key] += time.Since(start)
		m.mu.Unlock()
	})
}

func (m *Metrics) ServeHTTP(w http.ResponseWriter, _ *http.Request) {
	m.mu.Lock()
	defer m.mu.Unlock()
	w.Header().Set("Content-Type", "text/plain; version=0.0.4")
	for key, count := range m.requests {
		parts := strings.Split(key, "|")
		fmt.Fprintf(w, "be_productive_http_requests_total{method=%q,route=%q,status=%q} %d\n", parts[0], parts[1], parts[2], count)
		fmt.Fprintf(w, "be_productive_http_request_duration_seconds_sum{method=%q,route=%q,status=%q} %.6f\n", parts[0], parts[1], parts[2], m.duration[key].Seconds())
	}
}

// responseWriter is a wrapper to capture status codes
type responseWriter struct {
	http.ResponseWriter
	status      int
	wroteHeader bool
}

func (rw *responseWriter) WriteHeader(code int) {
	if rw.wroteHeader {
		return
	}
	rw.status = code
	rw.wroteHeader = true
	rw.ResponseWriter.WriteHeader(code)
}

func (rw *responseWriter) Write(b []byte) (int, error) {
	if !rw.wroteHeader {
		rw.WriteHeader(http.StatusOK)
	}
	return rw.ResponseWriter.Write(b)
}

// Logger logs each request with status code and duration
func Logger(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		rw := &responseWriter{ResponseWriter: w, status: http.StatusOK}

		next.ServeHTTP(rw, r)

		entry, _ := json.Marshal(map[string]any{
			"duration_ms": time.Since(start).Milliseconds(), "method": r.Method,
			"path": r.URL.Path, "request_id": r.Header.Get("X-Request-ID"), "status": rw.status,
		})
		log.Print(string(entry))
	})
}

// Recover handles panics gracefully
func Recover(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				log.Printf("[CRITICAL] panic recovered: %v", err)
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusInternalServerError)
				_, _ = w.Write([]byte(`{"success":false,"error":{"message":"internal server error"}}`))
			}
		}()
		next.ServeHTTP(w, r)
	})
}
