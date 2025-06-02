import fastapi
from fastapi.middleware.cors import CORSMiddleware


app = fastapi.FastAPI()

origins = [ 
    "http://localhost", 
    "http://localhost:8080", 
    "http://localhost:7071", 
    "http://localhost:3000" 
] 
 
app.add_middleware( 
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"], 
)