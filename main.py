
from fastapi import FastAPI, Query, Path, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get('/health_status')
def health_status():
    return JSONResponse(status_code=200, content={"message": "Server is live..."})
