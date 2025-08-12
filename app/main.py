from fastapi import FastAPI
from app.controllers import github_controller
from mangum import Mangum

app = FastAPI(title="GitHub Colab API")
app.include_router(github_controller.router)

handler = Mangum(app)
