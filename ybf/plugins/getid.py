from re import match

async def command(client, message, command):
    search_string = None

    try:
        search_string = command.split(None, 1)[1]
    except IndexError:
        return await message.channel.send(
            embed=client.embed_builder(
                'error',
                'Yeterli parametre yok. Kullanıcının ID\'sini istiyorsan '
                'isim veya etiket sunman gerek.'
            )
        )

    member = None

    mention = match(r'\<\@\!?([0-9]+?)\>', message.content.split(None, 1)[1])

    if mention:
        member = message.guild.get_member(mention.group(1))

    else:
        member = message.guild.get_member_named(search_string)

    if member is None:
        return await message.channel.send(
            embed=client.embed_builder(
                'error',
                'Verilen etiket veya isim ile bir '
                'kullanıcı bulunamadı.'
            )
        )

    return await message.channel.send(
        member.id,
        embed=client.embed_builder(
            'default',
            f'{member.name} kullanıcısının ID\'sine bakılıyor',
            title='ID bulundu'
        ).set_footer(
            text='Bu kullanıcı aradığınız kişi değilse, doğru ismi veya etiketi '
                 'sunduğunuzdan emin olun.',
            icon_url=member.avatar
        )
    )

aliases = [
    'getid',
    'id',
    'who',
    'whois'
]
