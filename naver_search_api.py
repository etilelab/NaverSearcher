import json
import datetime
import urllib.request
import urllib.parse


# search api function
def search_api(keyword, client_id, client_secret):
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


if __name__ == '__main__':
    keyword_list = txt_file_open('keywords.txt')
    api_list = txt_file_open('api.txt')

    option = 1

    for api in api_list:

        now = datetime.datetime.now()
        nowDatetime = now.strftime('%Y_%m_%d_%H_%M_%S')

        api_client_key = api.split(' ')[0].replace('\n', '')
        api_secret_key = api.split(' ')[1].replace('\n', '')
        for k in keyword_list:
            try:

                if option == 1:
                    k = 'site:' + k

                flag, keyword, content = search_api(k, api_client_key, api_secret_key)
                if flag:
                    total_count = json.loads(content)['total']
                    write_result(nowDatetime + '.txt', keyword.replace('\n', ''), total_count)
            except:
                print("error 발생")
                break