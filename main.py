import time
import requests
from telegram import Bot

# CONFIGURAÇÕES FIXAS
TELEGRAM_TOKEN = '8313642991:AAGMdtS-Fe4_QV_ucVsZ2zlrGTlhCQZad98'
CHAT_ID = '1688799390'
API_KEY = '92c32ce729de4e3e19c3e8cf7029059e'  # API Key do último bot

# CONFIGURAÇÃO DO BOT
CASAS = ['Novibet', 'Betano', 'Pinnacle', 'Bet365', 'Bwin', '1xbet', 'Betnacional', 'Superbet']
LUCRO_MINIMO = 10  # %
INTERVALO_CHECAGEM = 60  # segundos
REGIAO = "eu"  # Europa

# Inicia bot Telegram
bot = Bot(token=TELEGRAM_TOKEN)

def enviar_telegram(msg):
    """Envia mensagem para o Telegram"""
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print("Mensagem enviada:", msg)
    except Exception as e:
        print("Erro ao enviar:", e)

def buscar_odds():
    """Busca odds usando API"""
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}&regions={REGIAO}&markets=h2h"
    try:
        r = requests.get(url)
        if r.status_code != 200:
            print("Erro ao buscar odds:", r.text)
            return []
        return r.json()
    except Exception as e:
        print("Erro na requisição:", e)
        return []

def verificar_odds():
    """Verifica odds e envia alerta se houver lucro mínimo"""
    eventos = buscar_odds()
    for evento in eventos:
        jogo = evento.get("home_team", "Time A") + " x " + evento.get("away_team", "Time B")
        odds_coletadas = []

        for site in evento.get("bookmakers", []):
            casa = site.get("title")
            if any(c.lower() in casa.lower() for c in CASAS):
                try:
                    odd = site["markets"][0]["outcomes"][0]["price"]
                    odds_coletadas.append((casa, odd))
                except:
                    pass

        if len(odds_coletadas) > 1:
            odds_valores = [odd for _, odd in odds_coletadas]
            maior = max(odds_valores)
            media = sum(odds_valores) / len(odds_valores)
            diff = (maior - media) / media * 100

            if diff >= LUCRO_MINIMO:
                mensagem = f"⚠️ Odd desajustada!\nJogo: {jogo}\nDiferença: {diff:.2f}%\n"
                for casa, odd in odds_coletadas:
                    mensagem += f"{casa}: {odd}\n"
                enviar_telegram(mensagem)

if __name__ == "__main__":
    enviar_telegram("✅ Bot iniciado com sucesso!")
    while True:
        verificar_odds()
        time.sleep(INTERVALO_CHECAGEM)
