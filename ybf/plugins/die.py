from random import choice
import disnake as discord

from ybf.configs import settings

async def command(client, message, command):
    go = True

    # don't allow reboot if not owner
    if message.author.id != settings.self['owner_id']:
        go = False
    
    # but DO allow reboot if mod in runder
    if not isinstance(message.channel, discord.abc.PrivateChannel) and \
        message.guild.id == 120330239996854274 and \
        client.stored_roles[message.guild.id]['staff'] in message.author.roles:
            go = True
    
    if not go: return

    await message.channel.send(
        embed=client.embed_builder(
            'error',
            choice([
                'O kadar kolay ölmem!',
                'Yardım edebilirim... Yardım edebilirim... Lütfen beni öldürme...',
                'Gerçekten öleceğimi mi sandınız?...',
                '* Toza dönüşür *'
                ]),
            title=None))
    return await client.close()
    # return await message.channel.send(
    #     embed=client.embed_builder(
    #         'error',
    #         'You do not have permission to shut down this bot.'))

aliases = [
    'shutdown',
    'exit',
    'die',
    'kapa',
    'kapat',
    'çık',
    'geber',
    'öl'
]
