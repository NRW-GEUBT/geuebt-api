import os

from dotenv import load_dotenv
import uvicorn


if __name__ == "__main__":
    load_dotenv(".env", override=True)
    uvicorn.run(
        "server.app:app",
        host=os.environ.get('API_HOST'),
        port=int(os.environ.get('API_PORT')),
        reload=True
    )
