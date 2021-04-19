import requests


def get_page(url, file_name):

    r = requests.get(url)

    print(r.headers['content-type'])
    print(r.encoding)

    import pdb; pdb.set_trace()

    with open(file_name, 'wb') as fo:
        fo.write(r.content)

if __name__ == '__main__':
    url = 'https://asuntojen.hintatiedot.fi/haku/?c=Helsinki&cr=1&ps=&nc=0&amin=&amax=&renderType=renderTypeTable&search=1'

    get_page(url, 'test_helsinki.html')
