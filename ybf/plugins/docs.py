import shlex
import json

from .. import commands
from ..configs import settings

import disnake as discord

docs = {}

export = False

def addNewCommand(command):
    docs[command.aliases[0]] = {
        'aliases' : command.aliases,
        'description_small' : 'N/A',
        'description' : 'Açıklama temin edilmedi.',
        'usage' : 'Kullanım örneği temin edilmedi.',
        'hidden' : False
    }

async def ready(client):
    try:
        with open('./ybf/configs/docs.json', encoding='utf-8') as data:
            globals()['docs'] = json.load(data)

        # Add new commands
        for command in commands.iterable:
            if command.aliases[0] not in docs:
                # print(command)
                addNewCommand(command)
                globals()["export"] = True

    except FileNotFoundError:
        print('Yeni doküman dosyası oluşturuluyor: dizinde dosya bulunamadı')
        for command in commands.iterable:
            addNewCommand(command)
        globals()["export"] = True

async def command(client, message, command):
    context = command.split(None, 1)
    # help
    if len(context) == 1:
        helpmsg = discord.Embed(
            title='Kullanılabilir Komutlar:',
            color=client.colors['default']
        )

        for command in docs:
            if (
              not docs[command]['hidden'] or
              message.channel.category_id == settings.guild[message.guild.id]['categories']['staff'] # staff channel
            ):
                helpmsg.add_field(
                    name=command,
                    value=docs[command]['description_small'],
                    inline=False)

        return await message.channel.send(embed=helpmsg)

    # help set
    if context[1].startswith('set '): # I'm making fucking lazy code and nobody can stop
        # if message.author.id != self.get_user(settings.self['owner_id']):
        if client.stored_roles[message.guild.id]['staff'] not in message.author.roles:
            return await message.channel.send(
                embed=client.embed_builder(
                    'error',
                    'Yardım komudu açıklamalarını düzenleme ' \
                    'yetkisine sahip değilsiniz.'
                )
            )

        setting = shlex.split(context[1])
        if len(setting) < 4:
            return await message.channel.send(
                embed=client.embed_builder(
                    'error',
                    '`set`\'in çalışması için 3 ek parametre lazım. '\
                    '(`help set command "property" "value"`)\n'\
                    'Geçerli property\'ler: `description`, `description_small`, '\
                    '`usage`, ve `hidden`.')
                )

        identified = None
        for command in docs:
            if setting[1] in docs[command]['aliases']:
                identified = command

        if not identified:
            return await message.channel.send(
                embed=client.embed_builder(
                    'error',
                    f'{setting[1]} komudu bulunamadı.')
                )

        if setting[2].lower() == 'hidden':
            if setting[3].lower() not in ('true', 'false'):
                return await message.channel.send(
                    embed=client.embed_builder(
                        'error',
                        '`hidden` boolean türünde, yalnızca `True` veya '\
                        '`False` değerlerini alabilir.')
                    )

            if setting[3].lower() == 'true':
                setting[3] = True
            else:
                setting[3] = False

        docs[identified][setting[2]] = setting[3]
        globals()["export"] = True

        return await message.channel.send(
            embed=client.embed_builder(
                'default',
                'Değerler sorunsuzca güncellendi.',
                title='Başarı')
            )

    # help command
    for command in docs:
        if context[1] in docs[command]['aliases']:
            helpmsg = discord.Embed(
                title=command,
                description=docs[command]['description'],
                color=client.colors['default']
            )
            helpmsg.add_field(
                name='Kullanım',
                value=docs[command]['usage'],
                inline=False)
            helpmsg.add_field(
                name='Alias\'lar',
                value=docs[command]['aliases'],
                inline=False)

            return await message.channel.send(embed=helpmsg)

    return await message.channel.send(
        embed=client.embed_builder(
            'error',
            'Komut bulunamadı. `help` ile tüm komutlarımı görmeyi deneyebilirsin.',
            title='Bulunamadı'
        )
    )

async def close(client):
    print(export)
    if export:
        with open('./ybf/configs/docs.json', 'w', encoding='utf-8') as data:
            json.dump(docs, data)

aliases = [
    'help',
    'docs',
    'whatis',
    'whats',
    'yardım',
]
