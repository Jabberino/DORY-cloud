#!/bin/bash
# Comprehensive API endpoint test script

BASE_URL="http://localhost:8000"

echo "=== Testing DORY Cloud API ==="
echo ""

# Health check
echo "1. Health Check"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

# Create a coach
echo "2. Create Coach"
COACH=$(curl -s -X POST "$BASE_URL/coaches" \
  -H "Content-Type: application/json" \
  -d '{"name": "Coach Mike", "email": "mike@test.com"}')
echo $COACH | python3 -m json.tool
COACH_ID=$(echo $COACH | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Coach ID: $COACH_ID"
echo ""

# Create a team
echo "3. Create Team"
TEAM=$(curl -s -X POST "$BASE_URL/teams" \
  -H "Content-Type: application/json" \
  -d '{"name": "Dolphins Swim Club"}')
echo $TEAM | python3 -m json.tool
TEAM_ID=$(echo $TEAM | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
JOIN_CODE=$(echo $TEAM | python3 -c "import sys, json; print(json.load(sys.stdin)['join_code'])")
echo "Team ID: $TEAM_ID"
echo "Join Code: $JOIN_CODE"
echo ""

# Add coach to team
echo "4. Add Coach to Team"
curl -s -X POST "$BASE_URL/teams/$TEAM_ID/coaches" \
  -H "Content-Type: application/json" \
  -d "{\"coach_id\": \"$COACH_ID\", \"is_owner\": true}" | python3 -m json.tool
echo ""

# Create a swimmer
echo "5. Create Swimmer"
SWIMMER=$(curl -s -X POST "$BASE_URL/swimmers" \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane@test.com", "birthday": "2005-03-15", "sex": "F", "height_cm": 165.5, "weight_kg": 58.0, "wingspan_cm": 170.0}')
echo $SWIMMER | python3 -m json.tool
SWIMMER_ID=$(echo $SWIMMER | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Swimmer ID: $SWIMMER_ID"
echo ""

# Add swimmer to team
echo "6. Add Swimmer to Team"
curl -s -X POST "$BASE_URL/teams/$TEAM_ID/swimmers" \
  -H "Content-Type: application/json" \
  -d "{\"swimmer_id\": \"$SWIMMER_ID\"}" | python3 -m json.tool
echo ""

# Get team with members
echo "7. Get Team with Members"
curl -s "$BASE_URL/teams/$TEAM_ID" | python3 -m json.tool
echo ""

# Get team by join code
echo "8. Get Team by Join Code ($JOIN_CODE)"
curl -s "$BASE_URL/teams/code/$JOIN_CODE" | python3 -m json.tool
echo ""

# Create an exercise
echo "9. Create Exercise"
EXERCISE=$(curl -s -X POST "$BASE_URL/teams/$TEAM_ID/exercises" \
  -H "Content-Type: application/json" \
  -d '{"name": "100m Freestyle Sprint", "category": "sprint", "distance_m": 100, "description": "Fast-paced freestyle practice"}')
echo $EXERCISE | python3 -m json.tool
EXERCISE_ID=$(echo $EXERCISE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Exercise ID: $EXERCISE_ID"
echo ""

# List team exercises
echo "10. List Team Exercises"
curl -s "$BASE_URL/teams/$TEAM_ID/exercises" | python3 -m json.tool
echo ""

# Create a goal for swimmer
echo "11. Create Goal for Swimmer"
GOAL=$(curl -s -X POST "$BASE_URL/swimmers/$SWIMMER_ID/goals" \
  -H "Content-Type: application/json" \
  -d '{"event_name": "100m Freestyle", "target_time_s": 55.0, "goal_type": "sprint", "start_date": "2026-01-01", "end_date": "2026-06-30"}')
echo $GOAL | python3 -m json.tool
GOAL_ID=$(echo $GOAL | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Goal ID: $GOAL_ID"
echo ""

# List swimmer goals
echo "12. List Swimmer Goals"
curl -s "$BASE_URL/swimmers/$SWIMMER_ID/goals" | python3 -m json.tool
echo ""

# Add progress to goal
echo "13. Add Goal Progress"
curl -s -X POST "$BASE_URL/goals/$GOAL_ID/progress" \
  -H "Content-Type: application/json" \
  -d '{"projected_time_s": 58.5}' | python3 -m json.tool
echo ""

# Get goal with progress
echo "14. Get Goal with Progress"
curl -s "$BASE_URL/goals/$GOAL_ID" | python3 -m json.tool
echo ""

# Check Swagger docs
echo "15. Check API Docs"
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs")
echo "Swagger UI (/docs): HTTP $DOCS_STATUS"
OPENAPI_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/openapi.json")
echo "OpenAPI JSON: HTTP $OPENAPI_STATUS"
echo ""

echo "=== ALL TESTS COMPLETE ==="
