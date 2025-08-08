#!/bin/bash
# Curl Test Commands for Label Printing API

echo "🧪 Zebra Label Printing API - Curl Tests"
echo "========================================"

API_URL="http://localhost:5000"

echo
echo "1. 🔍 Health Check"
echo "Command: curl $API_URL/health"
curl -s "$API_URL/health" | python3 -m json.tool
echo

echo "2. 🖨️  Printer Status"
echo "Command: curl $API_URL/printer/status"
curl -s "$API_URL/printer/status" | python3 -m json.tool
echo

echo "3. 🏷️  Print Single Label"
echo "Command: curl -X POST $API_URL/print -H 'Content-Type: application/json' -d '{...}'"
curl -X POST "$API_URL/print" \
  -H "Content-Type: application/json" \
  -d '{
    "labels": [
      {
        "title": "W-CPN/OUT/CURL",
        "date": "08/08/25",
        "qr_code": "CURL12345"
      }
    ]
  }' | python3 -m json.tool
echo

echo "4. 🏷️🏷️ Print Multiple Labels"
echo "Command: curl -X POST $API_URL/print -H 'Content-Type: application/json' -d '{...}'"
curl -X POST "$API_URL/print" \
  -H "Content-Type: application/json" \
  -d '{
    "labels": [
      {
        "title": "W-CPN/OUT/TEST1",
        "date": "08/08/25",
        "qr_code": "TEST001"
      },
      {
        "title": "W-CPN/OUT/TEST2",
        "date": "08/08/25", 
        "qr_code": "TEST002"
      },
      {
        "title": "W-CPN/OUT/TEST3",
        "date": "08/08/25",
        "qr_code": "TEST003"
      }
    ]
  }' | python3 -m json.tool
echo

echo "5. ❌ Test Error Handling (Missing Fields)"
echo "Command: curl -X POST $API_URL/print -H 'Content-Type: application/json' -d '{...}'"
curl -X POST "$API_URL/print" \
  -H "Content-Type: application/json" \
  -d '{
    "labels": [
      {
        "title": "INCOMPLETE",
        "date": "08/08/25"
      }
    ]
  }' | python3 -m json.tool
echo

echo "6. ❌ Test Error Handling (Invalid JSON)"
echo "Command: curl -X POST $API_URL/print -H 'Content-Type: application/json' -d 'invalid'"
curl -X POST "$API_URL/print" \
  -H "Content-Type: application/json" \
  -d 'invalid json' | python3 -m json.tool
echo

echo "✅ All curl tests completed!"
echo "💡 Use individual commands below for manual testing"