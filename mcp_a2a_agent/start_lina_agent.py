import uvicorn
from lina.agent import app


uvicorn.run(app=app,port=8001,host="localhost")
