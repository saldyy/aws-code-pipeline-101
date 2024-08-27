package main

import "testing"

func TestAdd(t *testing.T) {
	result := Add(1, 2)
	expectedResult := Add(2, 1)

	if result != expectedResult {
		t.Errorf("Add(1, 2) = %d; want %d", result, expectedResult)
	}
}
