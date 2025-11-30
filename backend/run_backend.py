import os
import sys

# Ensure the bundle directory and backend subfolder are on sys.path
root = os.path.dirname(__file__)
sys.path.insert(0, root)
sys.path.insert(0, os.path.join(root, 'backend'))

from main import app
import uvicorn

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
