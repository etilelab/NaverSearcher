import json
import datetime
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import time


# search web api function
def search_web_api(keyword, client_id, client_secret):
    enc_text = urllib.parse.quote(keyword)  # korean encoding
    url = "https://openapi.naver.com/v1/search/webkr?query=" + enc_text
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
        return True, keyword, response_body.decode('utf-8')
    else:
        return False, keyword, rescode


# search blog api function
# search success = True, search Fail = False
def search_blog_api(keyword, client_id, client_secret):
    enc_text = urllib.parse.quote(keyword)  # korean encoding
    url = "https://openapi.naver.com/v1/search/blog?query=" + enc_text
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
        return True, keyword, response_body.decode('utf-8')
    else:
        return False, keyword, rescode


# search blog not use api function
# serach success = True, search Fail = False
def search_blog_not_api(keyword, domain, proxy):
    enc_text = urllib.parse.quote(keyword)  # korean encoding
    domain = urllib.parse.quote(domain)  # korean encoding

    url = "https://search.naver.com/search.naver?where=post&query=" + enc_text + "&st=sim&sm=tab_opt&date_from=&date_to=&date_option=0&srchby=all&dup_remove=1&post_blogurl=" + domain  + "&post_blogurl_without=&nso=so%3Ar%2Ca%3Aall%2Cp%3Aall&mson=0"

    request = urllib.request.Request(url)

    if proxy is not None:
        request.set_proxy(proxy[0],'http')
        request.set_proxy(proxy[1], 'https')

    request.add_header("referer", 'https://search.naver.com/search.naver?sm=tab_hty.top&where=post&query=%ED%95%98%ED%95%98&oquery=%ED%95%98%ED%95%98&tqi=Uv0HllpVuFRssvJSfyKssssssy0-519159')
    request.add_header("user-agent", 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36')

    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
        html = BeautifulSoup(response_body.decode('utf-8'), 'html.parser')
        return True, keyword, html
    else:
        return False, keyword, rescode


def txt_file_open(fp):
    f = open(fp, "r", encoding='utf-8')
    str_list = f.readlines()
    f.close()
    return str_list


def proxy_txt_file_open(fp):
    f = open(fp, "r", encoding='utf-8')
    str_list = f.readlines()
    p_list = []
    for item in str_list:
        tmp = item.split(' ')
        tmp2 = [ tmp[0].replace('\n',''), tmp[1].replace('\n','')]
        p_list.append(tmp2)
    f.close()
    return p_list


def write_result(file_name, domain, keyword_id, keyword_count):
    with open(file_name, 'a', encoding='utf-8') as f:
        f.write("{domain} {keyword_count} {keyword_id}\n".format(domain=domain, keyword_id=str(keyword_id),
                                                        keyword_count=str(keyword_count)))
        f.close()


def blog_search_process(domain_use_option, proxy_use_option):

    if domain_use_option is True: # using domain, but we do not use naver search api
        blog_keyword_list = txt_file_open('test_set/blog_keywords.txt')

        domain_list = txt_file_open('test_set/domain.txt')
        proxy_list = proxy_txt_file_open('test_set/proxy.txt')

        key_idx = 0
        proxy_idx = 0

        now = datetime.datetime.now()
        now_date_time = now.strftime('%Y_%m_%d_%H_%M_%S')

        while key_idx < len(blog_keyword_list) :
            try:
                k = blog_keyword_list[key_idx]
                for domain in domain_list:
                    if proxy_use_option:
                        proxy = proxy_list[proxy_idx]
                    else:
                        proxy = None

                    flag, keyword, content = search_blog_not_api(k, domain, proxy)

                    if flag:  # search success
                        total_tag = content.find('span',{'class':'title_num'})
                        if total_tag is not None:
                            total_count = str(total_tag.text).split('/')[1].split('건')[0].strip()
                            print(domain.replace('\n','') + ' / ' + keyword.replace('\n','') + ' / ' + str(total_count))
                            write_result(now_date_time + '.txt',domain.replace('\n',''),  keyword.replace('\n', '') + ' ', total_count)

                    else:  # search error, need proxy server
                        print(domain.replace('\n','') + ' ' + keyword.replace('\n','') + ' error 발생')
                        proxy_idx = proxy_idx + 1

                key_idx = key_idx + 1
                time.sleep(2)
            except Exception as e:
                print(k.replace('\n','') + ' 에러 발생')
                proxy_idx = proxy_idx + 1

            if proxy_idx >= len(proxy_list):
                break

    else:
        api_idx = 0
        key_idx = 0

        blog_keyword_list = txt_file_open('test_set/blog_keywords.txt')
        api_list = txt_file_open('test_set/api.txt')

        api_client_key = api_list[api_idx].split(' ')[0].replace('\n', '')
        api_secret_key = api_list[api_idx].split(' ')[1].replace('\n', '')

        now = datetime.datetime.now()
        now_date_time = now.strftime('%Y_%m_%d_%H_%M_%S')

        while key_idx < len(blog_keyword_list) and api_idx < len(api_list):
            try:
                k = blog_keyword_list[key_idx]
                flag, keyword, content = search_blog_api(k, api_client_key, api_secret_key)

                if flag:  # search success
                    total_count = json.loads(content)['total']
                    print('블로그 ' + keyword.replace('\n', '') + ' ' + str(total_count) + ' 검색결과')
                    if total_count > 0:
                        write_result(now_date_time + '.txt','', keyword.replace('\n', ''), total_count)
                    key_idx = key_idx + 1
                    time.sleep(2)
                else:  # search error
                    api_idx = api_idx + 1
                    print('검색 error')
            except Exception as e:
                api_idx = api_idx + 1
                print('error')


def web_search_process(option):
    api_idx = 0
    key_idx = 0

    web_keyword_list = txt_file_open('test_set/web_keywords.txt')
    api_list = txt_file_open('test_set/api.txt')

    api_client_key = api_list[api_idx].split(' ')[0].replace('\n', '')
    api_secret_key = api_list[api_idx].split(' ')[1].replace('\n', '')

    now = datetime.datetime.now()
    now_date_time = now.strftime('%Y_%m_%d_%H_%M_%S')

    while key_idx < len(web_keyword_list) and api_idx < len(api_list):
        try:
            k = web_keyword_list[key_idx]
            if option == 1:  # site
                k = 'site:' + k
            flag, keyword, content = search_web_api(k, api_client_key, api_secret_key)
            if flag:  # search success
                total_count = json.loads(content)['total']
                print('웹문서 ' + keyword.replace('\n', '') + ' ' + str(total_count) + ' 검색결과')
                if total_count > 0:
                    write_result(now_date_time + '.txt', '', keyword.replace('\n', ''), total_count)
                key_idx = key_idx + 1
                time.sleep(2)
            else:  # search error
                api_idx = api_idx + 1
                print('api 에러 error')
        except Exception as e:
            api_idx = api_idx + 1
            print(e)

# 검색옵션
# 0 : 블로그 검색(출처 사용 안함, naver api 이용)
# 1 : 블로그 검색(출처 사용)
# 2 : 웹 문서 검색(naver api 이용)
# 아래에 해당하는 번호를 적어주세요, 0 이면 블로그 검색(출처 사용안함, naver api 이용) 을 진행하게 됩니다.
# 아래 숫자만 변경하시고, 절대 다른 텍스트나 줄을 변경하시면 안됩니다.
0
if __name__ == '__main__':
    search_option = int(txt_file_open('set.txt')[8])
    if search_option == 0:
        print('블로그 검색(출처 사용 안함, naver api 이용)으로 검색 시작')
        blog_search_process(False, False)
    elif search_option == 1:
        print('블로그 검색(출처 사용, naver api 이용 안함, 프록시 사용안함))')
        blog_search_process(True, False)
    elif search_option == 2:
        print('블로그 검색(출처 사용, naver api 이용안함, 프록시 사용)')
        blog_search_process(True, True)
    elif search_option == 3:
        print('웹 문서 검색(naver api 이용, site 사용 안함)')
        web_search_process(0)
    elif search_option == 4:
        print('웹 문서 검색(naver api 이용, site 사용)')
        web_search_process(1)
    else:
        print('search option error')


