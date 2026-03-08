import os
import json
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("VK_TOKEN")

vk = VkApi(token=TOKEN)
longpoll = VkBotLongPoll(vk, None)
vk_api = vk.get_api()

forms = {}  # {form_id: {type, target_nick, reason, author_id, peer_id}}

def send_form(author_id, peer_id, target_nick, action, reason):
    form_id = len(forms) + 1
    forms[form_id] = {
        "type": action,
        "target_nick": target_nick,
        "reason": reason,
        "author_id": author_id,
        "peer_id": peer_id
    }
    keyboard = {
        "one_time": True,
        "buttons": [
            [{"action": {"type": "text", "label": f"Принять {form_id}"}, "color": "positive"}],
            [{"action": {"type": "text", "label": f"Отклонить {form_id}"}, "color": "negative"}]
        ]
    }
    vk_api.messages.send(
        peer_id=peer_id,
        random_id=0,
        message=f"Форма на {action} игрока {target_nick} с причиной: {reason}\nПримите или отклоните.",
        keyboard=json.dumps(keyboard)
    )

def apply_action(form):
    target = form["target_nick"]
    action = form["type"]
    return f"{action} применен к игроку {target}"

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        msg = event.object.message['text']
        from_id = event.object.message['from_id']
        peer_id = event.object.message['peer_id']

        # Команды
        if msg.startswith("/ban"):
            parts = msg.split()
            if len(parts) < 2: continue
            target_nick = parts[1]
            reason = " ".join(parts[2:])
            send_form(from_id, peer_id, target_nick, "бан", reason)
        elif msg.startswith("/unban"):
            parts = msg.split()
            if len(parts) < 2: continue
            target_nick = parts[1]
            reason = " ".join(parts[2:])
            send_form(from_id, peer_id, target_nick, "разбан", reason)
        elif msg.startswith("/mute"):
            parts = msg.split()
            if len(parts) < 2: continue
            target_nick = parts[1]
            reason = " ".join(parts[2:])
            send_form(from_id, peer_id, target_nick, "мут", reason)
        elif msg.startswith("/unmute"):
            parts = msg.split()
            if len(parts) < 2: continue
            target_nick = parts[1]
            reason = " ".join(parts[2:])
            send_form(from_id, peer_id, target_nick, "размут", reason)

        # Подтверждение форм
        elif msg.startswith("Принять"):
            form_id = int(msg.split()[1])
            if form_id in forms and forms[form_id]["peer_id"] == peer_id:
                result = apply_action(forms[form_id])
                vk_api.messages.send(peer_id=peer_id, random_id=0, message=f"Форма {form_id} принята. {result}")
                del forms[form_id]
        elif msg.startswith("Отклонить"):
            form_id = int(msg.split()[1])
            if form_id in forms and forms[form_id]["peer_id"] == peer_id:
                vk_api.messages.send(peer_id=peer_id, random_id=0, message=f"Форма {form_id} отклонена.")
                del forms[form_id]
