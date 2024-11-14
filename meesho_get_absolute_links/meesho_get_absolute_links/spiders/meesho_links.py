from typing import Iterable
import scrapy
import parsel
import pymysql
import json
import sys
from scrapy import Request
from scrapy.cmdline import execute

class MeeshoLinksSpider(scrapy.Spider):
    name = "meesho_links"
    start_urls = ["https://www.meesho.com/"]

    connect = pymysql.connect(
        host='localhost',
        user='root',
        password='actowiz',
        database='meesho_page_save'
    )
    cursor = connect.cursor()


    cursor.execute('''CREATE TABLE IF NOT EXISTS pages_link_with_input(id int AUTO_INCREMENT PRIMARY KEY,
                            url varchar(1000),
                            status varchar(100),
                            status_560001 varchar(100))''')
    connect.commit()


    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,tr;q=0.8',
        'cache-control': 'no-cache',
        # 'cookie': 'ANONYMOUS_USER_CONFIG=j%3A%7B%22clientId%22%3A%2237c506e0-07eb-464a-8259-4f8b754e%22%2C%22instanceId%22%3A%2237c506e0-07eb-464a-8259-4f8b754e%22%2C%22xo%22%3A%22eyJ0eXBlIjoiY29tcG9zaXRlIn0%3D.eyJqd3QiOiJleUpvZEhSd2N6b3ZMMjFsWlhOb2J5NWpiMjB2ZG1WeWMybHZiaUk2SWpFaUxDSm9kSFJ3Y3pvdkwyMWxaWE5vYnk1amIyMHZhWE52WDJOdmRXNTBjbmxmWTI5a1pTSTZJa2xPSWl3aVlXeG5Jam9pU0ZNeU5UWWlmUS5leUpwWVhRaU9qRTNNalkzTWpZek5URXNJbVY0Y0NJNk1UZzRORFF3TmpNMU1Td2lhSFIwY0hNNkx5OXRaV1Z6YUc4dVkyOXRMMmx1YzNSaGJtTmxYMmxrSWpvaU16ZGpOVEEyWlRBdE1EZGxZaTAwTmpSaExUZ3lOVGt0TkdZNFlqYzFOR1VpTENKb2RIUndjem92TDIxbFpYTm9ieTVqYjIwdllXNXZibmx0YjNWelgzVnpaWEpmYVdRaU9pSTVNVGhtTnpaaU9TMHpNMkZtTFRSaFlUTXRPRFEyWmkwek5qTXhZbVF4T1RrNFptUWlmUS5VR0VldEpQd3l0akVwSkpzY0dabW1YS3lFRGQ4UzlQc3ZDWUQwMDBxVVBvIiwieG8iOm51bGx9%22%2C%22createdAt%22%3A%222024-09-19T06%3A12%3A31.422Z%22%7D; __connect.sid__=s%3Alu38QZhOufyeX9fggpxsXqVDXUrHm9yx.dJVj0slY2xXGjtCzSNRom2mQnbUmWS9nn3TelM8NOSc; location-details=%7B%22city%22%3A%22Bengaluru%22%2C%22lat%22%3A%2213.2257%22%2C%22long%22%3A%2277.575%22%2C%22pincode%22%3A%22560001%22%7D; CAT_NAV_V2_COOKIE=0.1911256911868111; _is_logged_in_=1; isWG=false; INP_POW=0.8552047911900043; _abck=AEFF86642C743E828DEFF1C2C6526F0C~0~YAAQN0ISAhJrSCaTAQAAEBKJKQx6UJ1Rm+LOabpDrgf7NyngFQa3mSFmyMtFWNRcART/4QdU6P7njuJuFf0t0NDpA9cdnp9UXT21l0j0X+R2EY9a/Cq6HFmR48r1iXXRVUEhCsVAABku4LabGdmgIjrB3KOvOctaiuI/TDk8KKt51wHwc+UgavRtSewPYvU7aeZ/Qn3/NCamq+WPrtZ7R5pwk07uiSvETHd2U8yKnZA8PPBJZeRo0lk+HIsafCywXUJMOha1nrd3I8ZReTV5euwjG40fkbrGQtVpQkh0Z90lI/T1o4I/f5pwOkQEfKYvjXH2O/0X6cZi9dASVYrWmPG2MfYmVXf4pBxKdszGBey8FDokDlEfCLlQjjPjrai4u2tqbmhqcAM0vF+sMoaxW04ys/Pg53CgaERS5S+T1h4Xhcn4BZPhSJP+MEoYZS8tf2hgfhxOFpTD7rxYgTTzRUAetO1ZNRIPgrD2Bu+t6+J7V0RD0c7v/HeNe/AKzxVinMgQV/35hS8PnFjHNVMh1bbpr8OMqR6N/Q/IiYVYYc8ExQf9U5YO3omZZnzNGTyNVEUTw18CH/HrpHTQtMorK73l8g5qkheTH9h6QfU7WHcu+jfaUDOZoR5QoCtDoB/GhVSLma+KxdYHTxsjZyATMCuNV66/uADeItC9wtSWoPSeoxrl3lb/u9QBBRBKBQzQmPn+wDxzjn7Z37NtJ1/59oQp3mQ0mms6~-1~-1~1731572269; bm_mi=04BEF246828FEF94E6E2FD72F80B97A2~YAAQN0ISAgt1SCaTAQAA8tSJKRnNl3uodFhj4MmCgzVdGS5nLLAYDeTp8gJVp7Jrbn6UDDwgGeXehbXwJGS3r7YHfFpqNcmTadOPkd+BDsjFFpJ8N/TnNEYv5cX4bVh/l80SgasRRrr1PaKea5t98kv5ZFsHE7wQLoMBblWPe//aXm6W24aEJXDwpmZkaUU2QrBPcEzzH2VXKxOH05Cv0558myIQ5W4xv9HysLy8Y8nutNaQYd+xZIdt8XHF1nR4REudy0r6vzJTQOWsBEgTgD7urgorrhjZEVz+o3l8IcOFjuzWVy3g4PRu4QUFE3fjnEpOYPIXtC4cDtIn5051yzUNCHDZX6rVAwPQlsukejxnIyUrwN0NciCxJVF9uh5foiiiPyjTKVr9BuGhEi0sZePavGYQK08/VlxHq9sFIWXhUd7lJJeUu4mP2lYfXn//KLyTqBIqhPc9ZRDGjdlXPiko~1; bm_sz=AA939C2E0B9422CE5944C4171198AA1F~YAAQN0ISAg11SCaTAQAA8tSJKRnz7kYVVR7PA1KbJVmnl8tKeBAWaWIPX4YHkj3qIF3cDFBWClD7ZbLhV2LM7nCaQhSZQOhTRUNW0nEbbLX7MpZU1RZxJv0xVJuxXFB18OywSNV/NGyTbxfK/BbGoC6tBSqJbcrOPrxSpulaKEC0Vn7UGL8Kn+25uGTcL2C0stGfB7GCUdAKGftJlMOLRmyKXfvNsXwVqNbXmxi5OKU//HbH3nc+TFoIJ2eFlsyXy8NNkpnmLWa6i++5HyqpL+YF9ut5dpfBy43JF54AUXn1yDgny7nPqAy7AnFURpGuEJ2BYoakpcq/QrVt++uDOBw2raQDNz7+ovO23H6vROcO7NSrl9mcJSR9zWR1Za8ZGE338DGgGtwWE1ubA+d9zMg3Dcf0z4zBqf1eOR59eXcIzBrniASpkstbNw75+Q==~3294775~4404278; bm_sv=327A51C6FDEB6023FF622B6065518836~YAAQN0ISAmZ1SCaTAQAAyN6JKRnTWnmM5Pm5mpW+d7aH50OwN3qCi/WYoWd0aK6YRdYZSCOFYOh+0KDvl8sE1azP5JLmRiOxi40xdTxCMkBFmcVofPfocva/R/zYU6YlLPLt5OrG1DXPYDr7X+fFUEm2iUkD3AKSJoKSxL97SK+J2wZNhk9OlFGq4GAcEFhTLmhfpOz7JRbm+tWGMIxSOtwoFLDy/hRPAuLlf4Djs10N8EBwarh4efABxjGWxYpU~1; ak_bmsc=C2CCD60FA0A9D09F9F797DD01C29A489~000000000000000000000000000000~YAAQN0ISAm11SCaTAQAAgN+JKRlHXZh9sOh/6SPaMHxezOdN8d4DHBF3gAauDCHEesUkcL+8gm6bpo75tF6BRz6sqkYxzaojVjfu1BZdWWxHgyqq0S8cmLZAEXe1V+JZwovJeVseO4uaCHzmEbu79zozltUKuoyZPtIqhtnvUsvAi0KFsn5xvGE1x328gqJJD1Bw38x9w/uINLQspIrHk6XmZUJJZiQ3WNRouyasiCNTvF8BC4aAOGifmN5FtQL7l/BgDP/A8WrStalYXlrlvZe5c4v1xQrx+3EwxeTYh9uyUzyzTIpj061EQuqJc9rJxTGLczjW+aVMox21dSSdDFce/wDQ9T0HdPpjKmKuyiGjU0b7p7KaFRnKid2zDFu3wwNFXW2vgwV+z0zHT2VZVApiNdrH7IwYotPZxOKMfTJ4I69t1vfsRgN78YXMTxSbOLaLjq4XDIb6mdShEOBAiERt7JwhtaibW6Cyyj7XS4NTo6Z3EaFH+ft8p4mevXpIPwIcPLS0qj2+XaXXew6ueMefQ+4Azv18dn+G6yDLmWNzLaJ2kVsfjQcP6uEs3kPP945RyvqBDV18Ls3Kwt1kBuBCeZk4/Fx8H4YOX1wiwBl3umzupAmMOj4hFXfHoddprjylog==; mp_60483c180bee99d71ee5c084d7bb9d20_mixpanel=%7B%22distinct_id%22%3A%20%221931ea7d5e46f8-0144d51ae835d3-26011951-e1000-1931ea7d5e51378%22%2C%22%24device_id%22%3A%20%221931ea7d5e46f8-0144d51ae835d3-26011951-e1000-1931ea7d5e51378%22%2C%22Session%20ID%22%3A%20%222e39a51b-0ab3-4648-8be6-7dea0259%22%2C%22last%20event%20time%22%3A%201731568723687%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22%24user_id%22%3A%20%221931ea7d5e46f8-0144d51ae835d3-26011951-e1000-1931ea7d5e51378%22%2C%22Is%20Anonymous%22%3A%20%22False%22%2C%22Instance_Id%22%3A%20%2237c506e0-07eb-464a-8259-4f8b754e%22%2C%22V2%20Cat-Nav%20Exp%20Enabled%22%3A%20true%2C%22__alias%22%3A%20408393094%7D',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }

    cookiess = {
        'ANONYMOUS_USER_CONFIG': 'j%3A%7B%22clientId%22%3A%2237c506e0-07eb-464a-8259-4f8b754e%22%2C%22instanceId%22%3A%2237c506e0-07eb-464a-8259-4f8b754e%22%2C%22xo%22%3A%22eyJ0eXBlIjoiY29tcG9zaXRlIn0%3D.eyJqd3QiOiJleUpvZEhSd2N6b3ZMMjFsWlhOb2J5NWpiMjB2ZG1WeWMybHZiaUk2SWpFaUxDSm9kSFJ3Y3pvdkwyMWxaWE5vYnk1amIyMHZhWE52WDJOdmRXNTBjbmxmWTI5a1pTSTZJa2xPSWl3aVlXeG5Jam9pU0ZNeU5UWWlmUS5leUpwWVhRaU9qRTNNalkzTWpZek5URXNJbVY0Y0NJNk1UZzRORFF3TmpNMU1Td2lhSFIwY0hNNkx5OXRaV1Z6YUc4dVkyOXRMMmx1YzNSaGJtTmxYMmxrSWpvaU16ZGpOVEEyWlRBdE1EZGxZaTAwTmpSaExUZ3lOVGt0TkdZNFlqYzFOR1VpTENKb2RIUndjem92TDIxbFpYTm9ieTVqYjIwdllXNXZibmx0YjNWelgzVnpaWEpmYVdRaU9pSTVNVGhtTnpaaU9TMHpNMkZtTFRSaFlUTXRPRFEyWmkwek5qTXhZbVF4T1RrNFptUWlmUS5VR0VldEpQd3l0akVwSkpzY0dabW1YS3lFRGQ4UzlQc3ZDWUQwMDBxVVBvIiwieG8iOm51bGx9%22%2C%22createdAt%22%3A%222024-09-19T06%3A12%3A31.422Z%22%7D',
        '__connect.sid__': 's%3Alu38QZhOufyeX9fggpxsXqVDXUrHm9yx.dJVj0slY2xXGjtCzSNRom2mQnbUmWS9nn3TelM8NOSc',
        'location-details': '%7B%22city%22%3A%22Bengaluru%22%2C%22lat%22%3A%2213.2257%22%2C%22long%22%3A%2277.575%22%2C%22pincode%22%3A%22560001%22%7D',
        'CAT_NAV_V2_COOKIE': '0.1911256911868111',
        '_is_logged_in_': '1',
        'isWG': 'false',
        'INP_POW': '0.8552047911900043',
        'bm_mi': '04BEF246828FEF94E6E2FD72F80B97A2~YAAQN0ISAgt1SCaTAQAA8tSJKRnNl3uodFhj4MmCgzVdGS5nLLAYDeTp8gJVp7Jrbn6UDDwgGeXehbXwJGS3r7YHfFpqNcmTadOPkd+BDsjFFpJ8N/TnNEYv5cX4bVh/l80SgasRRrr1PaKea5t98kv5ZFsHE7wQLoMBblWPe//aXm6W24aEJXDwpmZkaUU2QrBPcEzzH2VXKxOH05Cv0558myIQ5W4xv9HysLy8Y8nutNaQYd+xZIdt8XHF1nR4REudy0r6vzJTQOWsBEgTgD7urgorrhjZEVz+o3l8IcOFjuzWVy3g4PRu4QUFE3fjnEpOYPIXtC4cDtIn5051yzUNCHDZX6rVAwPQlsukejxnIyUrwN0NciCxJVF9uh5foiiiPyjTKVr9BuGhEi0sZePavGYQK08/VlxHq9sFIWXhUd7lJJeUu4mP2lYfXn//KLyTqBIqhPc9ZRDGjdlXPiko~1',
        'ak_bmsc': 'C2CCD60FA0A9D09F9F797DD01C29A489~000000000000000000000000000000~YAAQN0ISAm11SCaTAQAAgN+JKRlHXZh9sOh/6SPaMHxezOdN8d4DHBF3gAauDCHEesUkcL+8gm6bpo75tF6BRz6sqkYxzaojVjfu1BZdWWxHgyqq0S8cmLZAEXe1V+JZwovJeVseO4uaCHzmEbu79zozltUKuoyZPtIqhtnvUsvAi0KFsn5xvGE1x328gqJJD1Bw38x9w/uINLQspIrHk6XmZUJJZiQ3WNRouyasiCNTvF8BC4aAOGifmN5FtQL7l/BgDP/A8WrStalYXlrlvZe5c4v1xQrx+3EwxeTYh9uyUzyzTIpj061EQuqJc9rJxTGLczjW+aVMox21dSSdDFce/wDQ9T0HdPpjKmKuyiGjU0b7p7KaFRnKid2zDFu3wwNFXW2vgwV+z0zHT2VZVApiNdrH7IwYotPZxOKMfTJ4I69t1vfsRgN78YXMTxSbOLaLjq4XDIb6mdShEOBAiERt7JwhtaibW6Cyyj7XS4NTo6Z3EaFH+ft8p4mevXpIPwIcPLS0qj2+XaXXew6ueMefQ+4Azv18dn+G6yDLmWNzLaJ2kVsfjQcP6uEs3kPP945RyvqBDV18Ls3Kwt1kBuBCeZk4/Fx8H4YOX1wiwBl3umzupAmMOj4hFXfHoddprjylog==',
        'bm_sz': 'BA1551ADAD9F26AEE15E75B83719F844~YAAQN0ISArLUSSaTAQAABTKuKRm5MywAnzcsN6BDCrLqdIoU2NzIB0caRreGAJNmt/+49MA38EoF1NrWZIhDIlFrghXXMjvkuf/q2Ep/HD1Q/OEQIsXDNOkeUcTwPd464b1FWFbse8OSImAaCaZO9Y3CqETWNncOuB/FCdOL+ZWWxBM4e3ltBpZbF14HXviL7um96jUWwxHGmMsnT3JNP8be0deQ5X40H2bc6HrZfMNi9xqF8xo2/caDc1CZnhU0sR3sIl81AQfYiWAHHaPItgfcx34CXPwOCIJMGZieNTL0x1/mAt1a1y/ksMZpM81glgg1CKyqeP1Z6VTStmEG2wYT+XXKdgs07ki0+J9oiSRoaWSJIqviaiLK/rsQX3lhtFjnr+C/UODIpmKxG8X9PvwZesTLSBi2V+KTKIRf10463ZqxC/kf+ytGmmxruz74FQQmpsyln0UCLA8San/c59SotFhZo36Etz7G/I9evTG2nlVs~3224641~4539204',
        'bm_sv': '327A51C6FDEB6023FF622B6065518836~YAAQN0ISAt7USSaTAQAAGz6uKRnFILiIhJoeMfYCTV5YjmY/1bnSBJp/MH5vOE0lyyYDr4Lz4v0fWkfdqn0ZQzAcGXrgsqLrD/ozxjyfUbwtG570FG/J6iucVkssiCsKYuRdrUQQ9u+SU+cjnwpVAZ+nVP7gl2fwbY4p6erMmlRvV4Uh+aQxAkpYDO/PFXKkEvEGj5+QpnBkO73GC5JhA+oDuP/27EIB0z+oQBOs++kuk+8oSpB/xDwgjzIXXyVdoA==~1',
        'mp_60483c180bee99d71ee5c084d7bb9d20_mixpanel': '%7B%22distinct_id%22%3A%20%221931ea7d5e46f8-0144d51ae835d3-26011951-e1000-1931ea7d5e51378%22%2C%22%24device_id%22%3A%20%221931ea7d5e46f8-0144d51ae835d3-26011951-e1000-1931ea7d5e51378%22%2C%22Session%20ID%22%3A%20%221dd30b00-98cc-429b-964b-e22361a9%22%2C%22last%20event%20time%22%3A%201731571111358%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22%24user_id%22%3A%20%221931ea7d5e46f8-0144d51ae835d3-26011951-e1000-1931ea7d5e51378%22%2C%22Is%20Anonymous%22%3A%20%22False%22%2C%22Instance_Id%22%3A%20%2237c506e0-07eb-464a-8259-4f8b754e%22%2C%22V2%20Cat-Nav%20Exp%20Enabled%22%3A%20true%2C%22__alias%22%3A%20408393094%7D',
        '_abck': 'AEFF86642C743E828DEFF1C2C6526F0C~0~YAAQbm5WaGVGMyaTAQAA0QjAKQwuVoXTwx5EZAI4C+6la4GDEjeoX8JcdRVOEeSXKKQ/e4MDxmvaiV1QNjxe7H3jlONmESFLTaIIemwqGklpHM65ZK2RkY134soKLnBfweeLl5tJrI6lnJ94gZeZowk/UulpWbUKO+RpVi3EJD8g590Tp5+PWCZyVEr+TLczgRDjm9YNm/1zfYC7vqmMZYCbs7ExG/iC4aBd8+3EfshYpYI+iAAODOCgry1uPdJ02G01sCD+TCQov+Q7e7eIh70Nqy3MhCSOSuufJZWkqbdbV1PtpH6L9Yh8QA5o8ClCqi9FOj2O09b8OUW4KNElxrhYeRu7IjmhQNwLxpKYoZi4ssWnvzT2lrolOoJhy7KgqwdywgJrdTHn9qfSTGTEuVQNtWb1HTk/UtiiVQ2UxDeMsY98xcv0dGiVjLiukJLDaonXfaqM8hnpwfDRot41eaIB7dWA/cWK7i1wJwT4M4mvl5HyaWRqkcvzUKkygi8uVNce3aJ5j2C2jxB94TgXm3LAyX385p1W7aN61QaxyjA0eAwCYkhNX0l0xCzsMGslqlpDpnXvpK6n0rPX9CJI510l7OElnM630URX6a/gXu8/z4lgDSvxMyb/22WXxdahWPD4MNr2ElqRDHRD1C48T1DQDLPTn7gCkvkG14zsdQPyYcqv/uicJzA6Ey0NOOTPIBIcE8noC+K4~-1~-1~1731575871',
    }

    def __init__(self, pincode, start_id, end_id, **kwargs):
        super().__init__(**kwargs)
        self.pincode = pincode
        self.start_id = start_id
        self.end_id = end_id


    def start_requests(self):
        yield scrapy.Request(
            self.start_urls[0],
            headers=self.headers,
            cookies=self.cookiess,
            callback=self.parse
        )

    def parse(self, response, **kwargs):
        query = f"SELECT Product_Url_MEESHO FROM template_20241017_distinct WHERE `status` != 'Done' AND status_{self.pincode} != 'Done' AND id BETWEEN {self.start_id} AND {self.end_id}"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        cookies_dic = {}

        with open('9737090010_20241112.json', 'r') as f:
            cookies = json.loads(f.read())

        for cookie in cookies['cookies']:
            cookies_dic[cookie['name']] = cookie['value']

        for pos, link_ in enumerate(rows):
            link = link_[0]
            self.cursor.execute("SELECT * FROM pages_link_with_input WHERE url = %s AND status = %s", (link, 'done'))
            self.connect.commit()
            print(link)
            if self.cursor.fetchone():
                print('url already scraped...', '\n')
            else:
                yield scrapy.Request(link,
                                 headers=self.headers,
                                 cookies=cookies_dic,
                                 callback=self.link_save)

    def link_save(self, response):

        selector = parsel.Selector(response.text)
        print('\n')
        print(response.url)
        input_text = selector.xpath('//*[@id="pin"]').get()
        # print(input_text)
        if input_text is None:
            print('input not available')
            insert_query = f"""INSERT INTO pages_link_with_input(url, status, status_560001) VALUES (%s, %s, %s)"""
            self.cursor.execute(insert_query, (response.url, 'pending', 'pending'))
            self.connect.commit()
        else:
            print('input available')
            insert_query = f"""INSERT INTO pages_link_with_input(url, status, status_560001) VALUES (%s, %s, %s)"""
            self.cursor.execute(insert_query, (response.url, 'done', 'done'))
            self.connect.commit()

# if __name__ == '__main__':
#     pincode = sys.argv[1]
#     start_id = sys.argv[2]
#     end_id = sys.argv[3]
#
#     execute(f"scrapy crawl meesho_links -a pincode={pincode} -a start_id={start_id} -a end_id={end_id} -s CONCURRENT_REQUESTS=16".split())





