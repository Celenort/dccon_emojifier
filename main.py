import requests
from datetime import datetime
import discord
from io import BytesIO
from bs4 import BeautifulSoup
from discord import Game, Embed, File
from discord.ext import commands
from PIL import Image
import asyncio

def quary_thumb(session, package_name, page, tag_mode) :
    tag_src="title/"
    if (tag_mode):
        tag_src = "tags/"
    package_search_req = session.get(DCCON_SEARCH_URL+'/'+page+'/'+tag_src + package_name)
    package_search_html = BeautifulSoup(package_search_req.text, 'html.parser')
    package_search_list = package_search_html.select(
        '#right_cont_wrap > div > div.dccon_listbox > ul > li')
    return package_search_list


def txt(ctx):
    # msg_fr = msg.server.name + ' > ' + msg.channel.name + ' > ' + msg.author.name
    return f'{ctx.guild.name} > {ctx.channel.name} > {ctx.author.name}'


def log(fr, text):
    print(f'{fr} | {str(datetime.now())} | {text}')  # TODO: 시간대 조정



BOT_TOKEN=""
COMMAND_PREFIX = "!"

DCCON_HOME_URL = 'https://dccon.dcinside.com/'
DCCON_SEARCH_URL = 'https://dccon.dcinside.com/hot/'

DCCON_DETAILS_URL = 'https://dccon.dcinside.com/index/package_detail'
EMBED_COLOR = 0x4559e9
INVITE_URL = 'https://discord.com/api/oauth2/authorize?client_id=1062225362764955668&permissions=363520&scope=bot'

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=discord.Intents.all())

@bot.event ## 커스텀 이모지를 큰 이모지로 바꾸어 줍니다.
async def on_message(message):
    if message.content[0:2]=="<:" and message.content[-1]==">":
        splitted_emoj = message.content.split(":")[1]
        emoji = discord.utils.get(bot.emojis, name=splitted_emoj)
        if(emoji == None) :
            return
        else :
            await message.channel.purge(limit=1)
        file = await emoji.to_file(filename="Emoji.gif")
        embed = discord.Embed()
        embed.set_author(name=message.author, icon_url=message.author.avatar.url)
        embed.set_image(url="attachment://Emoji.gif")
        await message.channel.send(file=file, embed=embed)


@bot.event
async def on_ready():
    await bot.change_presence(activity=Game(name=f'{COMMAND_PREFIX}도움'))
    log('SYSTEM', 'Bot ready')


@bot.command(name='도움')
async def help(ctx):
    log(txt(ctx), 'help command')
    embed = Embed(title='안녕하세요! 디시콘 핫산이에요!',
                  description='명령어들은 아래에서 전부 보실 수 있어요.',
                  color=EMBED_COLOR)
    embed.add_field(
        name='사용 방법', value=f'{COMMAND_PREFIX}콘 "디시콘 패키지 제목" "콘 이름"', inline=False)
    embed.add_field(
        name='사용 예시 1', value=f'{COMMAND_PREFIX}콘 멘헤라콘 15, {COMMAND_PREFIX}콘 "마히로콘 리메이크" 꿀잠, {COMMAND_PREFIX}콘 "좋은말콘 스페셜 에디션" 응원, ...', inline=False)
    embed.add_field(
        name='사용 예시 2', value=f'{COMMAND_PREFIX}콘 "나나히라 라인", {COMMAND_PREFIX}콘 카구야는인사받고싶어, ... (디시콘 패키지 이름만 입력 시 디시콘 목록 출력)', inline=False)
    embed.add_field(
        name='명령어', value=f'{COMMAND_PREFIX}콘, {COMMAND_PREFIX}도움, {COMMAND_PREFIX}대하여, {COMMAND_PREFIX}초대링크', inline=False)
    embed.set_footer(text='디시콘봇_현재 수정중')
    await ctx.channel.send(embed=embed)


@bot.command(name='초대링크')
async def invite_link(ctx):
    log(txt(ctx), 'invite_link command')
    await ctx.channel.send(f'봇 초대 링크 : {INVITE_URL}')


@bot.command(name='대하여')
async def about(ctx):
    log(txt(ctx), 'about command')
    embed = Embed(title='디시콘 핫산',
                  description='디시콘을 디스코드에서 쓸 수 있게 해주는 디스코드 봇입니다.',
                  color=EMBED_COLOR)
    embed.add_field(name='Repository',
                    value='https://github.com/Dogdriip/dccon_hassan', inline=False)
    await ctx.channel.send(embed=embed)

@bot.command(name='검색')
async def search_dccon(ctx, *args):
    log(txt(ctx), 'search_dccon command')
    if not args :
        log(txt(ctx), 'empty args')
        await ctx.channel.send('검색할 디시콘의 이름을 인수로 남겨주어야 합니다.')
        return
    package_name = args[0]        
    s = requests.Session()
    tag_mode = False
    package_search_req = s.get(DCCON_SEARCH_URL+'/1/title/' + package_name)
    package_search_html = BeautifulSoup(package_search_req.text, 'html.parser')
    package_search_none = package_search_html.select(
        '#right_cont_wrap > div > div.dccon_search_none')
    package_search_list = package_search_html.select(
        '#right_cont_wrap > div > div.dccon_listbox > ul > li')
    if (len(package_search_none) == 1) :
        tag_mode = True
        log(txt(ctx), 'no result w/ title. Try again with tags')
        package_search_req = s.get(DCCON_SEARCH_URL+'/1/tag/'+ package_name)
        package_search_html = BeautifulSoup(package_search_req.text, 'html.parser')
        package_search_none_t = package_search_html.select(
            '#right_cont_wrap > div > div.dccon_search_none')
        if (len(package_search_none_t)==1) :
            log(txt(ctx), 'also no result w/ tag. Terminates the request')
            ctx.channel.send('검색결과가 없습니다.')
            return
        package_search_list = package_search_html.select(
        '#right_cont_wrap > div > div.dccon_listbox > ul > li')


    if (len(args)==1) :
        ## 일단 package_search_list 가 15개(1페이지)인 애들만 검색해보자.
        num_packages = len(package_search_list)
        if (num_packages<9) :
            idx = num_packages
        else :
            idx = 9
        print(idx)
        image_list = []
        for i in range(idx):
            target_package = package_search_list[i]
            target_package_num = target_package.get('package_idx')
            target_package_thumb = target_package.select(
                'a > img'
            )[0].get('src')
            thumb_image_request = s.get(
                target_package_thumb, headers={'Referer': DCCON_HOME_URL})

            buffer = BytesIO(thumb_image_request.content)
            filename = package_name + '_' + \
                'thumb.gif'
            imagefile = File(buffer, filename)
            image_list.append(imagefile)
        await ctx.channel.send(files=image_list)
        return
    else :
        await ctx.channel.send('기능 미구현')
        return
    # try:
    #     package_idx = int(args[1])
    # except ValueError:
    #     log(from_text(ctx), '2번째 인수는 자연수여야 합니다.')
    #     return
    # if (package_idx<1) :
    #     log(from_text(ctx), '2번째 인수는 자연수여야 합니다.')
    #     return
    # q = package_idx//5
    # r = package_idx%5
    # first_page = 3*q + int((r+1)/2) ## r=2, 4일 때는 second_page가 활성화 되어야 함.
    # second_page = -1
    # if (r==2 or r == 4):
    #     second_page = first_page + 1
    # package_search_list = quary_thumb(s, package_name, first_page, tag_mode)
    # num_packages = len(package_search_list)
    # start = (first_page-1)*9

    # image_list = []
    # for i in range(idx):
    #     target_package = package_search_list[i]
    #     target_package_num = target_package.get('package_idx')
    #     target_package_thumb = target_package.select(
    #         'a > img'
    #     )[0].get('src')
    #     thumb_image_request = s.get(
    #         target_package_thumb, headers={'Referer': DCCON_HOME_URL})

    #     buffer = BytesIO(thumb_image_request.content)
    #     filename = package_name + '_' + \
    #         'thumb.gif'
    #     imagefile = File(buffer, filename)
    #     image_list.append(imagefile)
    # await ctx.channel.send(files=image_list)
    # return


@bot.command(name='콘')
async def send_dccon(ctx, *args):
    log(txt(ctx), 'send_dccon command')

    if not args or len(args) > 2:
        log(txt(ctx), 'empty args')
        await ctx.channel.send(f'사용법을 참고해주세요. ({COMMAND_PREFIX}도움)')
        await ctx.channel.send('디시콘 패키지명이나 디시콘명에 공백이 있을 경우 큰따옴표로 묶어야 합니다.')
        return

    list_print_mode = False
    package_name = args[0]
    idx = 'list_print_mode'
    if len(args) == 2:
        idx = args[1]
    else:
        list_print_mode = True

    log(txt(ctx),
        f'interpreted: {package_name}, {idx}. list_print_mode: {list_print_mode}')

    ############################################################################################################
    # respect https://github.com/gw1021/dccon-downloader/blob/master/python/app.py#L7:L18

    # TODO: 변수명 간단히

    s = requests.Session()

    package_search_req = s.get(DCCON_SEARCH_URL+'/1/title/' + package_name)
    package_search_html = BeautifulSoup(package_search_req.text, 'html.parser')
    package_search_list = package_search_html.select(
        '#right_cont_wrap > div > div.dccon_listbox > ul > li')

    try:
        # pick first dccon package (bs4 obj) from search list
        target_package = package_search_list[0]
    except IndexError as e:  # maybe no search result w/ IndexError?
        log(txt(ctx), 'error! (maybe no search result) : ' + str(e))
        await ctx.channel.send(f'"{package_name}" 디시콘 패키지 정보를 찾을 수 없습니다.')
    else:
        # get dccon number of target dccon package
        target_package_num = target_package.get('package_idx')
        log(txt(ctx), 'processing with: ' + target_package_num)

        # for i in package_search_req.cookies:
        #     print(i.name, i.value)

        package_detail_req = s.post(DCCON_DETAILS_URL,
                                    # content-type: application/x-www-form-urlencoded; charset=UTF-8
                                    cookies={'ci_c': package_search_req.cookies['ci_c'],
                                             'PHPSESSID': package_search_req.cookies['PHPSESSID']},
                                    headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                             'Referer': DCCON_SEARCH_URL+'/1/title/' + str(package_name.encode('utf-8')),
                                             'Origin': DCCON_HOME_URL,
                                             'X-Requested-With': 'XMLHttpRequest'},
                                    data={'ci_t': package_search_req.cookies['ci_c'],
                                          'package_idx': target_package_num,
                                          'code': ''})

        # 에러 핸들링 여기서 해야함

        package_detail_json = package_detail_req.json()

        '''
            info /  'package_idx'
                    'seller_no'
                    'seller_id'
                    'title'
                    'category'
                    'path'
                    'description'
                    'price'
                    'period'
                    'icon_cnt'
                    'state'
                    'open'
                    'sale_count'
                    'reg_date'
                    'seller_name'
                    'code'
                    'seller_type'
                    'mandoo'
                    'main_img_path'
                    'list_img_path'
                    'reg_date_short'
                    
            detail /  () /  'idx'
                            'package_idx'
                            'title'
                            'sort'
                            'ext'
                            'path'
        '''

        # 검색 결과로 바꿔치기
        package_name = package_detail_json['info']['title']

        if list_print_mode:
            available_dccon_list = []
            for dccon in package_detail_json['detail']:
                available_dccon_list.append(dccon['title'])

            await ctx.channel.send(f'"{package_name}"에서 사용 가능한 디시콘 : ' + ', '.join(available_dccon_list).rstrip(', '))
        else:
            succeed = False
            for dccon in package_detail_json['detail']:
                if dccon['title'] == idx:
                    dccon_img = "http://dcimg5.dcinside.com/dccon.php?no=" + \
                        dccon['path']
                    dccon_img_request = s.get(
                        dccon_img, headers={'Referer': DCCON_HOME_URL})

                    buffer = BytesIO(dccon_img_request.content)
                    filename = package_name + '_' + \
                        dccon['title'] + '.' + dccon['ext']
                    imagefile = File(buffer, "image.png")
                    embed = Embed()
                    embed.set_thumbnail(url="attachment://image.png")
                    embed.set_image(url="attachment://image.png")
                    embed.set_footer(text="footer", icon_url="attachment://image.png")
                    await ctx.channel.send(file=imagefile, embed=embed)
                    succeed = True
                    break

            if succeed:
                log(txt(ctx), 'succeed')
            else:
                log(txt(ctx), 'not found')

                await ctx.channel.send(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 찾지 못했습니다.')
                await ctx.channel.send('인자로 패키지 이름만 넘길 경우 사용 가능한 디시콘 목록이 출력됩니다.')
    #
    ############################################################################################################


@bot.command(name='등록')
async def send_dccon(ctx, *args):
    log(txt(ctx), 'registering emoji to server')

    if not args or len(args) > 2:
        log(txt(ctx), 'empty args')
        await ctx.channel.send(f'사용법을 참고해주세요. ({COMMAND_PREFIX}도움)')
        await ctx.channel.send('디시콘 패키지명이나 디시콘명에 공백이 있을 경우 큰따옴표로 묶어야 합니다.')
        return

    list_print_mode = False
    package_name = args[0]
    idx = 'list_print_mode'
    if len(args) == 2:
        idx = args[1]
    else:
        list_print_mode = True

    log(txt(ctx),
        f'interpreted: {package_name}, {idx}. list_print_mode: {list_print_mode}')

    ############################################################################################################
    # respect https://github.com/gw1021/dccon-downloader/blob/master/python/app.py#L7:L18

    # TODO: 변수명 간단히

    s = requests.Session()

    package_search_req = s.get(DCCON_SEARCH_URL + package_name)
    package_search_html = BeautifulSoup(package_search_req.text, 'html.parser')
    package_search_list = package_search_html.select(
        '#right_cont_wrap > div > div.dccon_listbox > ul > li')

    try:
        # pick first dccon package (bs4 obj) from search list
        target_package = package_search_list[0]
    except IndexError as e:  # maybe no search result w/ IndexError?
        log(txt(ctx), 'error! (maybe no search result) : ' + str(e))
        await ctx.channel.send(f'"{package_name}" 디시콘 패키지 정보를 찾을 수 없습니다.')
    else:
        # get dccon number of target dccon package
        target_package_num = target_package.get('package_idx')
        log(txt(ctx), 'processing with: ' + target_package_num)

        # for i in package_search_req.cookies:
        #     print(i.name, i.value)

        package_detail_req = s.post(DCCON_DETAILS_URL,
                                    # content-type: application/x-www-form-urlencoded; charset=UTF-8
                                    cookies={'ci_c': package_search_req.cookies['ci_c'],
                                             'PHPSESSID': package_search_req.cookies['PHPSESSID']},
                                    headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                             'Referer': DCCON_SEARCH_URL + str(package_name.encode('utf-8')),
                                             'Origin': DCCON_HOME_URL,
                                             'X-Requested-With': 'XMLHttpRequest'},
                                    data={'ci_t': package_search_req.cookies['ci_c'],
                                          'package_idx': target_package_num,
                                          'code': ''})

        # 에러 핸들링 여기서 해야함

        package_detail_json = package_detail_req.json()

        '''
            info /  'package_idx'
                    'seller_no'
                    'seller_id'
                    'title'
                    'category'
                    'path'
                    'description'
                    'price'
                    'period'
                    'icon_cnt'
                    'state'
                    'open'
                    'sale_count'
                    'reg_date'
                    'seller_name'
                    'code'
                    'seller_type'
                    'mandoo'
                    'main_img_path'
                    'list_img_path'
                    'reg_date_short'
                    
            detail /  () /  'idx'
                            'package_idx'
                            'title'
                            'sort'
                            'ext'
                            'path'
        '''

        # 검색 결과로 바꿔치기
        package_name = package_detail_json['info']['title']

        if list_print_mode:
            available_dccon_list = []
            for dccon in package_detail_json['detail']:
                available_dccon_list.append(dccon['title'])

            await ctx.channel.send(f'"{package_name}"에서 사용 가능한 디시콘 : ' + ', '.join(available_dccon_list).rstrip(', '))
        else:
            succeed = False
            for dccon in package_detail_json['detail']:
                if dccon['title'] == idx:
                    dccon_img = "http://dcimg5.dcinside.com/dccon.php?no=" + \
                        dccon['path']
                    dccon_img_request = s.get(
                        dccon_img, headers={'Referer': DCCON_HOME_URL})

                    buffer = BytesIO(dccon_img_request.content)
                    filename = package_name + '_' + \
                        dccon['title'] + '.' + dccon['ext']

                    await ctx.channel.send(file=File(buffer, filename))
                    succeed = True
                    #image = Image.open(dccon_img_request.content)
                    ##await ctx.channel.send('1')
                    #resize = image.resize((400,400))
                    #image_bytes=bytes()
                    #resize.save(image_bytes, format='png')
                    #await ctx.channel.send('2')
                    numemojis = len(ctx.guild.emojis)
                    try:
                        await ctx.guild.create_custom_emoji(name="bot_emoji"+str(numemojis), image=dccon_img_request.content)
                        await ctx.channel.send('등록 완료!')
                    except:
                        await ctx.channel.send('GIF파일은 이모지로 등록 불가.')



            if succeed:
                log(txt(ctx), 'succeed')
            else:
                log(txt(ctx), 'not found')

                await ctx.channel.send(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 찾지 못했습니다.')
                await ctx.channel.send('인자로 패키지 이름만 넘길 경우 사용 가능한 디시콘 목록이 출력됩니다.')
    #
    ############################################################################################################




@bot.event
async def on_command_error(ctx, error):
    log(txt(ctx), error)
    await ctx.channel.send(error)


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
