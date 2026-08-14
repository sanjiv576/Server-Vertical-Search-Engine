
from fastapi import FastAPI, Query, Path, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get('/')
def root_home():
    return JSONResponse(status_code=200, content={"message": "Server is live..."})
