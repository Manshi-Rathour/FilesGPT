cd "C:\Users\udipt\OneDrive\Desktop\MinorProject\Pdf-Assistant-App\backend"

.\venv\Scripts\Activate.ps1
uvicorn backend_app.main:app --reload --port 5000
