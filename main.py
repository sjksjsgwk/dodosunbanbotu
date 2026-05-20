import os 
import logging as l
import asyncio as a
from telethon import TelegramClient as TC, events as e, errors as err
from telethon.tl.functions.channels import EditBannedRequest as EBR
from telethon.tl.types import ChatBannedRights as CBR

l.basicConfig(level=50)
l.getLogger("telethon").setLevel(50)

I = int(os.getenv("API_ID"))
H = os.getenv("API_HASH")
T = os.getenv("BOT_TOKEN")

# Yetkili kullanıcı ID'leri
S = [8627915546, 7410828118]

# Ban yetkileri
R = CBR(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
    send_polls=True,
    change_info=True,
    invite_users=True,
    pin_messages=True
)

# Client
c = TC("x_session", I, H)

# Sayaç
_c = 0

# Aynı anda işlem limiti
_l = a.Semaphore(85)


async def _b(chat, user_id):
    global _c

    async with _l:
        try:
            await c(EBR(chat, user_id, R))
            _c += 1

        except err.FloodWaitError as f:
            await a.sleep(f.seconds)
            await _b(chat, user_id)

        except Exception:
            pass


@c.on(e.NewMessage(pattern="/ban"))
async def _x(m):
    global _c

    # Yetki kontrolü
    if m.sender_id not in S:
        return

    p = m.text.split()

    if len(p) < 3:
        await m.reply(
            "Kullanım:\n/ban <grup_id> <sayı>"
        )
        return

    try:
        t_id = int(p[1])
        n = int(p[2])

        g = await c.get_entity(t_id)

        u = [
            i for i in await c.get_participants(g)
            if not i.bot and not i.is_self
        ]

    except Exception as ex:
        await m.reply(f"Hata:\n{ex}")
        return

    total = len(u)

    if total == 0:
        await m.reply("Üye bulunamadı.")
        return

    n = min(n, total)
    _c = 0

    await m.reply(
        f"🚀 {g.title}\n\n"
        f"Toplam üye: {total}\n"
        f"Ban hedefi: {n}\n\n"
        f"İşlem başlatıldı."
    )

    await a.gather(
        *[_b(g, k.id) for k in u[:n]]
    )

    await m.reply(
        f"✅ İşlem tamamlandı.\n"
        f"Toplam banlanan: {_c}"
    )


if __name__ == "__main__":
    c.start(bot_token=T)
    print("Bot aktif.")
    c.run_until_disconnected()
