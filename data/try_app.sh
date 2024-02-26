curl -X 'POST' \
  'http://localhost:8000/parse-bill' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"image_url": "https://drive.google.com/uc?id=1EH8eRTR--_goRQGVjmCu3Dazzkh0EZE9", "bill_type": "iberdrola"}'