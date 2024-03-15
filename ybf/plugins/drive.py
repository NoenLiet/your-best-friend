import json

from ..configs import settings

import disnake as discord

drive = {}
document = 'http://i.imgur.com/ISkKEZ8.png'
folder = 'http://i.imgur.com/DRoOvgp.png'

# export = False

# TODO: this should be in settings instead!

async def ready(client):
    try:
        with open('./ybf/configs/drive.json', encoding='utf-8') as data:
            globals()['drive'] = json.load(data)

    except FileNotFoundError:
        print(
            'Drive JSON bulunamadı. .drive hata verecek!\n\n'
            'Şöyle yenisini yapabilirsin: '
            '{ "default" : "url", "keys" : { "name" : "url" } }'
        )

async def command(client, message, command):
    if client.stored_roles[message.guild.id]['staff'] not in message.author.roles:
        return await message.channel.send(
            embed=client.embed_builder(
                'error',
                'Google Drive URL\'lerini görüntüleme yetkiniz yok.'
            )
        )

    if message.channel.category_id != settings.guild[message.guild.id]['categories']['staff']:
        return await message.channel.send(
            embed=client.embed_builder(
                'error',
                'Bu komut yalnızca Yetkili kategorisinde çalıştırılabilir.\n'
                'Bunun hata olduğunu düşünüyorsanız, `set` komuduyla bi\' tekrar bakın.'
            )
        )

    try:
        command = command.lower().split(None, 1)[1]
    except IndexError:
        return await message.channel.send(
            embed=discord.Embed(
                title='/r/UndertaleTR',
                url=drive['default'],
                color=client.colors['default']
            ).set_footer(text='Drive değerleri atanamıyor.'
            ).set_thumbnail(url=folder)
        )

    if command == 'car':
        return await message.channel.send(
            embed=client.embed_builder(
                'error',
                'Vınn vınn...'
            )
        )

    if command in drive['keys']:
        return await message.channel.send(
            embed=discord.Embed(
                title=command[0].upper() + command[1:],
                url=drive['keys'][command],
                color=client.colors['default']
            ).set_footer(text='Drive değerleri atanamıyor.'
            ).set_thumbnail(url=document)
        )

    return await message.channel.send(
        embed=client.embed_builder(
            'error',
            'Bilinmeyen drive URL\'si. Geçerli URL\'ler:\n`{}`'.format(
                list(drive['keys'].keys())
            )
        ).set_footer(text='Drive değerleri atanamıyor.')
    )

# async def close(client):
#     if export:
#         with open('./ybf/configs/drive.json', 'w', encoding='utf-8') as data:
#             json.dump(drive, data)

aliases = [
    'drive'
]
