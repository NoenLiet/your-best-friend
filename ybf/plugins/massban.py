import disnake
from shlex import split

async def command(client, message, command):
    if message.author.id != 88401933936640000 and \
      client.stored_roles[message.guild.id]['staff'] not in message.author.roles:
        return

    ban_reason = "Toplu Ban: Sebep sunulmadı."
    bans = split(command)
    bans.pop(0)
    
    try:
        int(bans[0])
    except ValueError:
        ban_reason = bans.pop(0)
    
    ban_reason = f'[Ban {message.author.name}#{message.author.discriminator} tarafından atıldı] {ban_reason}'

    banamt = len(bans)

    msg = await message.reply(
        content=f'{banamt} sayıda kullanıcıyı banlıyorum...',
        mention_author=False
    )

    for i,dumb in enumerate(bans):
        try:
            await message.guild.ban(
                disnake.Object(id=int(dumb)),
                reason=ban_reason
            )
            await msg.edit(
                content=f'<@{dumb}> sunucudan banlandı.\n\n{banamt - i+1} tane ban kaldı...'
            )
        except disnake.HTTPException:
            await msg.edit(
                content=f'<@{dumb}> denen malı banlayamadım. (Hâlihazırda banlanmış olabilirler mi?)\n\n{banamt - i+1} tane ban kaldı...'
            )
    
    await msg.edit(
        content='Bütün kullanıcılar banlandı.'
    )

aliases = [
    'ban',
    'massban'
]
