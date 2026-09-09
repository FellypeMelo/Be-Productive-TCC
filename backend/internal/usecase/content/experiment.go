package content

import (
	"crypto/sha256"
	"fmt"
)

const (
	ExperimentID      = "sustainable-attention-v1"
	AssignmentVersion = "sha256-v1"
	AlgorithmVersion  = "2.3.0-sustainable-attention"
)

func stableVariant(userID int64) string {
	digest := sha256.Sum256([]byte(fmt.Sprintf("%s:%s:%d", ExperimentID, AssignmentVersion, userID)))
	if digest[0] < 128 {
		return "treatment"
	}
	return "control"
}
