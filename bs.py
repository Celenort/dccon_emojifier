from bs4 import BeautifulSoup
from io import BytesIO
import requests
from PIL import Image

DCCON_HOME_URL = 'https://dccon.dcinside.com/'
DCCON_SEARCH_URL = 'https://dccon.dcinside.com/hot/1/title/'
DCCON_SEARCH_TAG_URL = 'https://dccon.dcinside.com/hot/1/tags/'
DCCON_DETAILS_URL = 'https://dccon.dcinside.com/index/package_detail'

package_name = "아로나"

idx = "12"

list_print_mode = False

s = requests.Session()

# Title로 일단 검색해보기.

package_search_req = s.get(DCCON_SEARCH_URL + package_name)
package_search_html = BeautifulSoup(package_search_req.text, 'html.parser')
package_search_none = package_search_html.select(
    '#right_cont_wrap > div > div.dccon_search_none')
package_search_list = package_search_html.select(
    '#right_cont_wrap > div > div.dccon_listbox > ul > li')

if (len(package_search_none) == 1) :
    print("No search result")
    #return (일단은 따로 떼서 실험중이므로 else 안에 넣자.)

else:
    ## 일단 package_search_list 가 15개(1페이지)인 애들만 검색해보자.
    if (len(package_search_list)==15) :
        print("can search next page")
        ## todo : 다음 페이지 검색 인수를 주었을 때 다음 페이지로 넘어가게 하기
    else :
        target_package = package_search_list[0]


target_package_num = target_package.get('package_idx')
target_package_thumb = target_package.select(
    'a > img'
)[0].get('src')
thumb_image_request = s.get(
    target_package_thumb, headers={'Referer': DCCON_HOME_URL})
buffer = BytesIO(thumb_image_request.content)
filename = package_name + '_' + \
    'thumb'
img = Image.open(buffer)
img.save('thumb.gif', format='GIF', save_all=True, loop=0)

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

    #await ctx.channel.send(f'"{package_name}"에서 사용 가능한 디시콘 : ' + ', '.join(available_dccon_list).rstrip(', '))
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

            #await ctx.channel.send(file=File(buffer, filename))
            succeed = True
            break

    if succeed:
        print("Succeed")
        #log(from_text(ctx), 'succeed')
    else:
        print("Fail")
        #log(from_text(ctx), 'not found')

        #await ctx.channel.send(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 찾지 못했습니다.')
        #await ctx.channel.send('인자로 패키지 이름만 넘길 경우 사용 가능한 디시콘 목록이 출력됩니다.')
    print(buffer)
    img = Image.open(buffer)
    img.save('image.gif', format='GIF', save_all=True, loop=0)