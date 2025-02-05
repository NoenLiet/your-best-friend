from ..configs import settings

import disnake as discord
import asyncio
import json

reports = {}

export = False

valid_mojis = {
    '\U0001F4DD', # :memo: / :pencil:
    '\u21A9',     # :leftwards_arrow_with_hook:
    '\u270D',     # :writing_hand:
    '\U0001F4E7', # :e_mail:
    '\U0001F4AC', # :speech_balloon:
    '\U0001F5E8\ufe0f', # :speech_left:
    '\U0001F441\u200D\U0001F5E8' # :eye_in_speech_bubble: / :eye_am_a_witness:
}

close_moji = {
    '\u274c' # :x:
}

async def ready(client):
    try:
        with open('./ybf/configs/reports.json', encoding='utf-8') as data:
            globals()['reports'] = json.load(data)

    except FileNotFoundError:
        print('JSON görmezden geliniyor: dosyayı bulamadım')
        # export = True

    except json.decoder.JSONDecodeError:
        print('JSON görmezden geliniyor: dosya boş veya bozuk.')

async def command(client, message, command):
    message_deleted = False

    if not isinstance(message.channel, discord.abc.PrivateChannel):
        msg = None

        try:
            settings.purge['ignored_channels'].append(message.channel.id)
            await message.delete()
            message_deleted = True
        except discord.Forbidden:
            msg = 'Mesajınız silinemedi. Anonimliğinizi garanti edemiyorum.'
        except discord.NotFound:
            msg = 'Mesajınızı bulamadım. Anonimliğinizi garanti edemiyorum.'

        if msg:
            await message.channel.send(
                embed=client.embed_builder(
                    'warning',
                    msg,
                    title='Uyarı'
                )
            )

    if message_deleted:
        settings.purge['ignored_channels'].remove(message.channel.id)

    context = command.split(None, 1)
    if len(context) < 2:
        try:
            await message.author.send(
                embed=client.embed_builder(
                    'error',
                    'Rapor edecek bir şey sunman lazım.'
                )
            )
        except discord.Forbidden:
            # We are blocked or the user has DMs closed.
            await message.channel.send(
                embed=client.embed_builder(
                    'error',
                    'Rapor namına hiçbir şey gönderilmedi.'
                )
            )
        return

    current_guild = None
    for guild in settings.guild.keys():
        # check if report channel exists
        if settings.guild[guild]['channels']['report'] != 0:
            this_guild = client.get_guild(guild)
            # make sure I'm in the guild and so are they
            this_member = await this_guild.fetch_member(message.author.id)
            if this_guild and this_member:
                # assume first guild I share with this user is the correct one
                current_guild = this_guild
                # pretty sure keys() goes in order so rundertale should be first
                break

    if not current_guild:
        raise Exception('Sunucu Bulunamadı')
        # This shouldn't happen.

    report_id = None

    if message_deleted and len(message.attachments) > 0:
        # message was sent in a public channel and was instantly deleted, so
        # the images are now gone
        await message.author.send(
            embed=discord.Embed(
                color=client.colors['warning'],
                title='Lütfen Dosyalarınızı Tekrar Yollayın',
                description='**Raporunuz henüz gönderilmedi.**\n'
                            'Mesajınız, mesajınızla beraber silinen dosyalar '
                            'içeriyordu. Lütfen hepsini bu kanala '
                            'tekrardan yükleyin.'
            )
        )
        def check(m):
            return (
                isinstance(m.channel, discord.abc.PrivateChannel) and
                m.author.id == message.author.id and
                len(m.attachments) > 0
            )

        newmsg = await client.wait_for('message', check=check)

        report_id = await current_guild.get_channel(
            settings.guild[current_guild.id]['channels']['report']
        ).send(
            '\n'.join([attachment.url for attachment in newmsg.attachments]),
            embed=discord.Embed(
                color=client.colors['error'],
                title='Bir rapor aldım.',
                description=message.content.split(None, 1)[1]
            ).set_footer(text='Bütün dosyalar URL olarak dâhil edildi.')
        )

    else:
        # send this if we're just good to go
        report_id = await current_guild.get_channel(
            settings.guild[current_guild.id]['channels']['report']
        ).send(
            '\n'.join([attachment.url for attachment in message.attachments]),
            embed=discord.Embed(
                color=client.colors['error'],
                title='Bir rapor aldım.',
                description=message.content.split(None, 1)[1]
            ).set_footer(text='Bütün dosyalar URL olarak dâhil edildi.')
        )

    globals()['reports'][str(report_id.id)] = message.author.id

    globals()['export'] = True

    try:
        return await message.author.send(
            embed=discord.Embed(
                color=client.colors['default'],
                title='Başarılı',
                description=f'Raporunuz iletildi. Rapor ID\'si: {report_id.id}\n'
                              'Size en kısa zamanda yanıt vermeye çalışacağız. '
                              'Eğer raporunuz kapatılırsa bilgilendirileceksiniz.'
            )
        )
    except discord.Forbidden:
        # we are blocked
        return

    '''
    # old report dupe code
    await msg.add_reaction('\u2705') # :white_check_mark:

    def check(reaction, user):
        return (
            isinstance(reaction.message.channel, discord.abc.PrivateChannel) and
            user == message.author and
            # reaction.message.id == msg.id and # why isnt this working
            str(reaction.emoji) == '\u2705'
        )

    try:
        await client.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await msg.remove_reaction('\u2705', client.user)
        return

    await message.author.send(
        report_id.content,
        embed=discord.Embed(
            color=client.colors['error'],
            title='A report has been recieved.',
            description=message.content.split(None, 1)[1]
        ).set_footer(text='Any attachments have been included as URLs.')
    )
    '''

async def react(client, payload):
    if (
        payload.guild_id not in settings.guild or # guild not found (DM?)
        payload.channel_id != settings.guild[payload.guild_id]['channels']['report'] or # didn't react in our report channel: ignore
        str(payload.message_id) not in reports or # not a report: ignore
        payload.emoji.is_custom_emoji() # unicode emojis only
    ):
        return
    
    if (
        payload.emoji.name not in valid_mojis and # not a reply emoji
        payload.emoji.name not in close_moji # not a close emoji
    ):
        return

    bot_spam_channel = client.get_guild(payload.guild_id).get_channel(
        settings.guild[payload.guild_id]['channels']['bot_spam']
    )
    reporter = await client.get_guild(payload.guild_id).fetch_member(reports[str(payload.message_id)])

    if not reporter:
        reports.pop(str(payload.message_id) )
        return await bot_spam_channel.send(
            embed=client.embed_builder(
                'error',
                'Rapor düzenlenemiyor: Kullanıcı sunucudan ayrıldı.'
            ).set_footer(text='Bu rapor silinmiştir.')
        )
    try:
        # close report
        if payload.emoji.name in close_moji:

            await reporter.send(
                embed=client.embed_builder(
                        payload.member.colour,
                        'Bunun bir hata olduğunu düşünüyorsanız, lütfen bize daha detaylı bir tane daha rapor yollayın.',
                        title=f'{payload.message_id} no\'lu rapor kapatıldı.'
                    ).set_footer(icon_url=payload.member.display_avatar.url, text=f'{payload.member.display_name} tarafından kapatılmıştır.')
                )

            await client.get_guild(payload.guild_id).get_channel(
                    settings.guild[payload.guild_id]['channels']['report']
                ).send(f'{payload.message_id} no\'lu rapor **kapatılmıştır**.')

            return reports.pop(str(payload.message_id))

        # send report

        editmsg = await bot_spam_channel.send(
            f'**<@{payload.user_id}>, {payload.message_id} no\'lu rapora '
            f'yanıt vermeyi seçtiniz.**\n\nLütfen cevabınızı bu kanala '
            'gönderin.\n3 dakikanın ardından zaman aşımına uğrar. `cancel` veya `iptal` yazarak '
            'iptal edebilirsiniz.'
        )

        def check(m):
            if (
                m.channel == bot_spam_channel and
                m.author.id == payload.user_id
            ):
                if m.content.lower() == 'cancel' or m.content.lower() == 'iptal':
                    raise NameError

                return True

        try:
            msg = await client.wait_for('message', timeout=180.0, check=check)
        except (asyncio.TimeoutError, NameError):
            return await editmsg.edit(content=f'~~{editmsg.content}~~\n\İptal edildi.')

        await reporter.send(
            embed=client.embed_builder(
                msg.author.colour,
                msg.content,
                title=f'{payload.message_id} no\'lu rapora cevap:'
            ).set_footer(icon_url=msg.author.display_avatar.url, text=f'--{msg.author.display_name}')
        )

        await bot_spam_channel.send('Cevap başarıyla yollandı.')

        # reports.pop(str(payload.message_id) )
    
    except discord.errors.Forbidden:
        return await bot_spam_channel.send(
            embed=client.embed_builder(
                'error',
                'Kullanıcıya mesaj gönderilemiyor: DM\'lerini kapatmış.'
            ).set_footer(text='Bu rapor silinemedi.')
        )

async def close(client):
    if export:
        with open('./ybf/configs/reports.json', 'w', encoding='utf-8') as data:
            json.dump(reports, data)

aliases = [
    'report',
    'rapor'
    'r'
]
