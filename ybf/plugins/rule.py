import json
import shlex
import disnake as discord

rules = {}

export = False

async def ready(client):
    try:
        with open('./ybf/configs/rules.json', encoding='utf-8') as data:
            globals()['rules'] = json.load(data)

    except FileNotFoundError:
        print('Kural dosyası bulamadım o yüzden yenisini oluşturuyorum.')
        globals()['rules'] = {
            'start_at' : 1,
            'simple' : [
                'Be excellent to each other!',
                'Party on, dudes!'
            ],
            'extended' : {
                '1' : '__***Rule 1: Be excellent to each other!***__',
                '2' : '__***Rule 2: Party on, dudes!***__'
            }
        }
        globals()["export"] = True

async def command(client, message, command):
    context = command.split(None, 1)

    if len(context) == 1:
        helpmsg = discord.Embed(
            title='Kurallar Listesi:',
            description = '',
            color=client.colors['default']
        )

        for i,rule in enumerate(rules['simple']):
            index = i + rules['start_at']
            helpmsg.description += f'{index}: {rule}\n'

        helpmsg.set_footer(text='Bu kurallarla ilgili daha fazla bilgi "kural #" komuduyla edinilebilir.')

        return await message.channel.send(embed=helpmsg)

    if context[1].startswith('set '):
        if client.stored_roles[message.guild.id]['staff'] not in message.author.roles:
            return await message.channel.send(
                embed=client.embed_builder(
                    'error',
                    'Kuralları düzenlemeye yetkiniz yok.'
                )
            )

        setting = shlex.split(context[1])
        if len(setting) < 2 or (
            len(setting) < 3 and setting[1] != 'list'
        ):
            return await message.channel.send(
                embed=client.embed_builder(
                    'error',
                    '`set` 2 ek parametre gerektirir. '
                    '(`rule set "isim" "değer"`)'
                )
            )

        if setting[1] == 'list':
            return await message.channel.send(
                embed=client.embed_builder(
                    'default',
                    [rule_name for rule_name in rules['extended']],
                    title='Kurallar Listesi'
                )
            )

        if setting[1] == 'simple':
            command = None

            if len(setting) < 4:
                return await message.channel.send(
                    embed=client.embed_builder(
                        'error',
                        '`set simple` 1 ek parametre gerektirir. '
                        '(`rule set simple "isim" "değer"`)'
                    )
                )

            try:
                command = int(setting[2]) - rules['start_at']
            except ValueError:
                return await message.channel.send(
                    embed=client.embed_builder(
                        'error',
                        'Yalnızca başında sayı olan kuralların basit açıklamaları olabilir.'
                    )
                )

            rules['simple'][command] = setting[3]
            globals()["export"] = True
            return await message.channel.send(
                embed=client.embed_builder(
                    'default',
                    f'{setting[1]} kuralının basit açıklaması başarıyla ayarlandı.',
                    title='Yaptım be!'
                )
            )

        if setting[1] == 'start_at':
            try:
                rules['start_at'] = int(setting[2])
            except ValueError:
                return await message.channel.send(
                    embed=client.embed_builder(
                        'error',
                        'Kuralları sıralamak için yalnızca sayıları kullanabilirsiniz.'
                    )
                )

        try:
            command = int(setting[1]) - rules['start_at']
            interval = command - len(rules['simple'])
            if interval == 1:
                g.append(setting[2])
                await message.channel.send(
                    embed=client.embed_builder(
                        'warning',
                        'Adding a new simple rule description to accomodate the '
                        'new rule. '
                        '(ç.n. bu hata ne için çıkıyor bakmak istemiyorum saat 02.16 aw) '
                        '(denk gelirsen anlarsın zaten ne olduğunu, sonra git çevir)',
                        title='Uyarı'
                    )
                )
            elif command - len(rules['simple']) > 1:
                return await message.channel.send(
                    embed=client.embed_builder(
                        'error',
                        'Numaralandırılmış kurallarda sayı atlayamazsınız.'
                    )
                )
        except ValueError:
            # named rule
            pass

        rules['extended'][setting[1]] = setting[2]
        globals()["export"] = True
        return await message.channel.send(
            embed=client.embed_builder(
                'default',
                f'{setting[1]} başarıyla ayarlandı.',
                title='Yaptım be!'
            ).set_footer(text='Basit açıklamayı da değiştirmek isteyebilirsin.')
        )

    if context[1] not in rules['extended']:
        return await message.channel.send(
            embed=client.embed_builder(
                'error',
                'Bu kurala dair açıklama bulunamadı.',
                title='Bulunamadı'
            )
        )

    return await message.channel.send(
        embed=discord.Embed(
            description=rules['extended'][context[1]],
            color=client.colors['default']
        )
    )


async def close(client):
    if export:
        with open('./ybf/configs/rules.json', 'w', encoding='utf-8') as data:
            json.dump(rules, data)

aliases = [
    'rules',
    'rule',
    'kural',
]
