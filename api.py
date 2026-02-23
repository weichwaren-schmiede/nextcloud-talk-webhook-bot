from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
from urllib.parse import parse_qs


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
        raw_body = await request.body()
        content_type = request.headers.get("content-type", "").lower()

        body: Any
        if "application/json" in content_type:
            decoded = raw_body.decode("utf-8", errors="replace")
            try:
                body = json.loads(decoded or "{}")
            except json.JSONDecodeError:
                body = decoded
        else:
            decoded = raw_body.decode("utf-8", errors="replace")
            if decoded.strip().startswith("{") or decoded.strip().startswith("["):
                try:
                    body = json.loads(decoded)
                except json.JSONDecodeError:
                    body = decoded
            elif "application/x-www-form-urlencoded" in content_type:
                form = parse_qs(decoded, keep_blank_values=True)
                body = {k: v[0] if len(v) == 1 else v for k, v in form.items()}
            else:
                body = decoded

        # Check if it's an Alertmanager webhook
        if isinstance(body, dict) and "alerts" in body:
            webhook = AlertmanagerWebhook(**body)
            message = format_alertmanager_message(webhook)
        else:
            if isinstance(body, dict):
                if "message" in body and isinstance(body["message"], str):
                    message = body["message"]
                elif "title" in body and "message" in body:
                    title = str(body.get("title", "")).strip()
                    text = str(body.get("message", "")).strip()
                    message = f"{title}\n{text}".strip()
                elif "entries" in body and isinstance(body["entries"], list):
                    entries = [str(entry) for entry in body["entries"]]
                    message = "\n".join(entries)
                else:
                    message = json.dumps(body, ensure_ascii=False)
            else:
                message = str(body)

        from bot import NextcloudBot
        bot = NextcloudBot()
        result = bot.send_message(message)
        if isinstance(result, dict) and result.get("status") == "error":
            raise HTTPException(status_code=502, detail=result.get("message", "Unknown bot error"))
        return result

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))