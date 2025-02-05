from datetime import datetime
from asyncio import sleep

from ..configs import settings

reactions = {}

warned = []

active = False

async def command(client, message, command):
    global active
    global reactions
    global warned

    if client.stored_roles[message.guild.id]['staff'] not in message.author.roles:
        # print('Ignoring non-staff')
        return
    
    c = command.split(None, 1)
    if len(c) > 1:
        c = c[1].strip()

    # print(c)
    
    if c == 'on' or c == 'true':
        await message.channel.send('Anti-react\'ı açtım.')
        active = True
    elif c == 'off' or c == 'false':
        await message.channel.send('Anti-react\'ı kapattım.')
        active = False
    
    if c == 'off' or c == 'false' or c == 'clear':
        reactions = {}
        warned = []
        await message.channel.send('Uyarılmış kullanıcılar temizlendi.')

async def react(client, payload):
    if not active: return

    token = f'{payload.message_id}|{payload.user_id}'

    now = datetime.now()

    reactions[token] = now

    # print(token)

    await sleep(5)

    if token in reactions:
        del reactions[token]
        # print('Token removed.')

async def reactRemove(client, payload):
    if not active: return

    token = f'{payload.message_id}|{payload.user_id}'

    if (
        payload.guild_id not in settings.guild or # guild not found (DM?)
        token not in reactions
    ):
        # print('No effect on removed reaction.')
        return

    # print('Taking action.')
    now = datetime.now()

    delta = now - reactions[token] # just to make sure we don't bug out

    channel = client.get_channel(payload.channel_id)
    staff_id = client.stored_roles[channel.guild.id]['staff'].id

    # print(delta)

    if delta.total_seconds() < 3:
        if payload.user_id not in warned:
            # print('Warning.')
            warned.append(payload.user_id)
            await channel.send(
                content=f'***UYARI:*** <@{payload.user_id}> hızlıca tepki '
                         'silmeyi tetikledi.\n'
                         'Lütfen tepkiler arasında 3 saniye boşluk bırakın.\n'
                         '*İkinci ihlâlde otomatik olarak  '
                         'susturulacaksınız.*\n'
                        f'<@&{staff_id}>'
                )
        else:
            # print('Roleban.')
            member = await channel.guild.get_member(payload.user_id)
            await member.edit(
                roles=[
                    client.stored_roles[channel.guild.id]['rolebanned']
                ]
            )
            await channel.send(f'<@{payload.user_id} birden fazla hızlıca tepki '
                                'silme eyleminden dolayı rolebanlandı.'
                               f'<@&{staff_id}>')

aliases = [
    'react',
    'tepki'
]