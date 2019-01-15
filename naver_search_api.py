import json
import datetime
import urllib.request
import urllib.parse


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


def txt_file_open(fp):
    f = open(fp, "r", encoding='utf-8')
    str_list = f.readlines()
    f.close()
    return str_list


def write_result(file_name, keyword_id, keyword_count):
    with open(file_name, 'a', encoding='utf-8') as f:
        f.write("{keyword_id} {keyword_count}\n".format(keyword_id=str(keyword_id),
                                                        keyword_count=str(keyword_count)))
        f.close()

def blog_search_process(option):

    if option == 0: # not use naver search api
        blog_keyword_list = txt_file_open('blog_keywords.txt')
        key_idx = 0



    else:
        api_idx = 0
        key_idx = 0

        blog_keyword_list = txt_file_open('set/web_keywords.txt')
        api_list = txt_file_open('set/api.txt')

        api_client_key = api_list[api_idx].split(' ')[0].replace('\n', '')
        api_secret_key = api_list[api_idx].split(' ')[1].replace('\n', '')

        now = datetime.datetime.now()
        now_date_time = now.strftime('%Y_%m_%d_%H_%M_%S')

        while key_idx < len(blog_keyword_list):
            try:
                k = blog_keyword_list[key_idx]
                flag, keyword, content = search_blog_api(k, api_client_key, api_secret_key)
                if flag:  # search success
                    total_count = json.loads(content)['total']
                    if total_count > 0:
                        write_result(now_date_time + '.txt', keyword.replace('\n', ''), total_count)
                    key_idx = key_idx + 1
                else:  # search error
                    api_idx = api_idx + 1
            except:
                api_idx = api_idx + 1


def web_search_process(option):
    api_idx = 0
    key_idx = 0

    web_keyword_list = txt_file_open('set/web_keywords.txt')
    api_list = txt_file_open('set/api.txt')

    api_client_key = api_list[api_idx].split(' ')[0].replace('\n', '')
    api_secret_key = api_list[api_idx].split(' ')[1].replace('\n', '')

    now = datetime.datetime.now()
    now_date_time = now.strftime('%Y_%m_%d_%H_%M_%S')

    while key_idx < len(web_keyword_list):
        try:
            k = web_keyword_list[key_idx]
            if option == 1:  # site
                k = 'site:' + k
            flag, keyword, content = search_web_api(k, api_client_key, api_secret_key)
            if flag:  # search success
                total_count = json.loads(content)['total']
                if total_count > 0:
                    write_result(now_date_time + '.txt', keyword.replace('\n', ''), total_count)
                key_idx = key_idx + 1
            else:  # search error
                api_idx = api_idx + 1
        except:
            api_idx = api_idx + 1


if __name__ == '__main__':
    web_search_process(0)
