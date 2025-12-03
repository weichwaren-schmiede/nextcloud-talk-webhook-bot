from fastapi import FastAPI
from pydantic import BaseModel


class MessageRequest(BaseModel):
    message: str

app = FastAPI()


@app.post("/send_message")
async def send_message(request: MessageRequest):
    try:
        from bot import NextcloudBot
        bot = NextcloudBot()
        return bot.send_message(request.message)
    except Exception as e:
        return {"status": "error", "message": str(e)}