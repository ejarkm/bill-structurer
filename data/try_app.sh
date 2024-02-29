curl -X 'POST' \
  'http://localhost:8000/parse-bill' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'INVOICE_API_KEY:111' \
  -d '{"image_url": "https://drive.google.com/uc?id=1EH8eRTR--_goRQGVjmCu3Dazzkh0EZE9", "bill_type": "iberdrola"}'


curl -X 'POST' \
  'http://localhost:8000/parse-bill' \
  -H 'INVOICE_API_KEY:111' \
  -F 'bill_type=iberdrola' \
  -F 'uploaded_file=@/workspaces/bill-structurer/data/output.jpg'