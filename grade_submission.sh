#!/bin/bash

echo "🏆 SUBMITTING FINAL GRADE TO MERCOR"
echo "=" * 50

curl \
  -H 'Authorization: bhaumik.tandan@gmail.com' \
  -H 'Content-Type: application/json' \
  -d @grade_endpoint_payload.json \
  'https://mercor-dev--search-eng-interview.modal.run/grade'

echo ""
echo "✅ Submission complete!" 