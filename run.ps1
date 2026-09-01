# Install Python dependencies
pip install -r requirements.txt

# Install node dependencies
npm install

# Run Python app in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python api.py"

# Run frontend (Node)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"