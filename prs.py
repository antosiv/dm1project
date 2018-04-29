import requests
import csv
from lxml import html


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.00'
}


def write_reviews(html_text, file=None):
    tree = html.fromstring(html_text)
    with open(file, 'a') as csv_out:
        writer = csv.writer(csv_out, delimiter='^')
        for i in range(1, 76):
            first, second = None, None
            order = list()
            try:
                first = tree.xpath('/html/body/div[5]/div[2]/div/div/div[2]/'+
                                   'div/ul/li[%i]/div[4]/div/div[2]/p[1]/span' % i)\
                   [0].text
                first = first.replace('"', '')
                first = first.replace('\n', '')
                if str(tree.xpath('/html/body/div[5]/div[2]/div/div/div[2]/'+
                              'div/ul/li[%i]/div[4]/div/div[2]/p[1]/@class' % i)[0]) == 'review_pos ':
                    order.append('plus')
                else:
                    order.append('minus')
            except IndexError:
                pass
            try:
                second = tree.xpath('/html/body/div[5]/div[2]/div/div/div[2]'+
                                    '/div/ul/li[%i]/div[4]/div/div[2]/p[2]/span' % i)[0].text
                second = second.replace('"', '')
                second = second.replace('\n', '')
                if str(tree.xpath('/html/body/div[5]/div[2]/div/div/div[2]/'+
                              'div/ul/li[%i]/div[4]/div/div[2]/p[2]/@class' % i)[0]) == 'review_pos ':
                    order.append('plus')
                else:
                    order.append('minus')
            except IndexError:
                pass
            if first is not None:
                if second is not None:
                    buf = list()
                    buf.append('plus')
                    buf.append(second)
                    writer.writerow(buf)
                buf = list()
                buf.append('minus')
                buf.append(first)
                writer.writerow(buf)
            if first is None and second is not None:
                with open('data_.html', 'w') as dt:
                    dt.write(html_text)
                    print('something wrong')

    try:
        link = tree.xpath('//*[@id="review_next_page_link"]/@href')[0]
        return link
    except IndexError:
        return None


r = requests.get('https://www.booking.com/reviews/us/hotel/'+
                 'mgm-grande.en-gb.html?aid=356980;'+
                 'label=gog235jc-reviewshotel-XX-us-mgmNgrande-unspec-ru-com-L%3Aen-O%3Ax11-B%3A'+
                 'firefox-N%3AXX-S%3Abo-U%3AXX-H%3As;sid=59ccb5a772e26cc9bb92641ae30ed589;'+
                 'customer_type=total&hp_nav=0&order=featuredreviews&page=1&r_lang=en&rows=75&')
tmp = write_reviews(r.text, 'reviews.csv')
while tmp is not None:
    r = requests.get('https://www.booking.com' + tmp)
    tmp = write_reviews(r.text, 'reviews.csv')
