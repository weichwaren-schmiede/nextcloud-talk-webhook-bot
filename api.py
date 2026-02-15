from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class MessageRequest(BaseModel):
    message: str


class AlertmanagerAlert(BaseModel):
    status: str
    labels: Dict[str, Any]
    annotations: Dict[str, Any]
    startsAt: Optional[str] = None
    endsAt: Optional[str] = None


class AlertmanagerWebhook(BaseModel):
    status: str
    alerts: List[AlertmanagerAlert]
    groupLabels: Optional[Dict[str, Any]] = None


app = FastAPI()


def format_alertmanager_message(webhook: AlertmanagerWebhook) -> str:
    """Format Alertmanager webhook into a readable message."""
    status_emoji = "🔴" if webhook.status == "firing" else "✅"
    message_parts = [f"{status_emoji} **Alert {webhook.status.upper()}**"]
    
    for alert in webhook.alerts:
        alert_name = alert.labels.get("alertname", "Unknown")
        severity = alert.labels.get("severity", "unknown")
        summary = alert.annotations.get("summary", "")
        description = alert.annotations.get("description", "")
        instance = alert.labels.get("instance", "")
        
        message_parts.append(f"\n**{alert_name}** ({severity})")
        if summary:
            message_parts.append(f"📋 {summary}")
        if description:
            message_parts.append(f"📝 {description}")
        if instance:
            message_parts.append(f"🖥️ Instance: {instance}")
    
    return "\n".join(message_parts)


@app.post("/send_message")
async def send_message(request: Request):
    """Accept simple message or Alertmanager webhook."""
    try:
        body = await request.json()
        
        # Check if it's an Alertmanager webhook
        if "alerts" in body:
            webhook = AlertmanagerWebhook(**body)
            message = format_alertmanager_message(webhook)
        else:
            msg_req = MessageRequest(**body)
            message = msg_req.message
        
        from bot import NextcloudBot
        bot = NextcloudBot()
        return bot.send_message(message)
        
    except Exception as e:
        return {"status": "error", "message": str(e)}