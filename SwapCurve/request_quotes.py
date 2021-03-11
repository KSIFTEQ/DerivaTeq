from bs4            import BeautifulSoup
from datetime       import datetime
from urllib.request import urlopen, Request
from collections    import defaultdict, OrderedDict
import re
import yaml
    
def USD_LIBOR():
    dict_rates = defaultdict(dict)

    libor_link = 'https://www.global-rates.com/en/interest-rates/libor/american-dollar/american-dollar.aspx'
    req   = Request(libor_link, headers={'User-Agent': 'Mozilla/5.0'})
    html  = urlopen(req)
    bsObj = BeautifulSoup(html, 'html.parser')
    
    table = bsObj.find('table', 
        {'style' : 'width:100%;margin:16px 0px 0px 0px;border:1px solid #CCCCCC;'}
    )

    # Get columns(dates) as datetime format
    table_dates = str(table.find('tr', {'class' : 'tableheader'})).split('</td>')
    for i, item in enumerate(table_dates[1:-1]):
        str_left, str_right = f'hdr{i+2}">', '</span>'
        i_left, i_right     = len(str_left), len(str_right)

        date = datetime.strptime(
            re.search(r'%s(.*?)%s' %(str_left, str_right), item)[0][i_left:-i_right],
            '%m-%d-%Y'
        ).date()

        # Insert date into dict as key; insert keys only (without values)
        dict_rates[date]

    for i in [1, 2]:
        table_data = str(table.findAll('tr', {'class' : 'tabledata%s'%(i)})).split('</tr>')
        for row_term in table_data:
            for i, item in enumerate(row_term.split('</td>')[:-1]):
                if i == 0:
                    str_left, str_right = 'USD LIBOR - ', '</a>'
                    i_left, i_right     = len(str_left), len(str_right)
                    term = re.search(r'%s(.*?)%s' %(str_left, str_right), item)[0][i_left:-i_right]
                else:
                    str_left = '<td align="center">'
                    try:
                        rate = float(item.replace(str_left, '')[:-2])
                    except ValueError:
                        continue

                    list_keys = list(dict_rates)
                    dict_rates[list_keys[i-1]].update({term : rate})
            
    return dict_rates


def Eurodollar_Futures():
    dict_quotes = OrderedDict()

    libor_link = 'https://www.cmegroup.com/CmeWS/mvc/Quotes/Future/1/G?quoteCodes=null'
    req   = Request(libor_link, headers={'User-Agent': 'Mozilla/5.0'})
    html  = urlopen(req)
    bsObj = str(BeautifulSoup(html, 'html.parser'))

    get_quotes = yaml.load(bsObj)['quotes']
    for dict_month in get_quotes:
        month, quote = dict_month['expirationMonth'], dict_month['last']
        if quote == '-':
            continue
        dict_quotes[month] = quote
    
    return dict_quotes