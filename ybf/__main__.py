import disnake
import ybf # import base necessities

print('Başlatılıyor...')

YBF = ybf.Client()

KEY = None
with open('./ybf/configs/token.key', encoding='utf-8') as keyfile:
    KEY = keyfile.read().strip()

YBF.run(KEY)
