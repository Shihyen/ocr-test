
import os
import re
import smtplib
from collections import OrderedDict
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText
from urllib import request

import requests
# from hoppdataapi.app.api_log import logged

from dateutil.relativedelta import relativedelta

from qrcodeocr.util import cache_util

conns = {}


def getconn(database):
    if database not in conns:
        dsn = "dbname=%s user=jim password=12zy host=127.0.0.1 port=5432" % database
        conns[database] = psycopg2.connect(dsn=dsn)
    return conns[database]


def query(database, sqlstring):
    conn = getconn(database)
    cur = conn.cursor()
    cur.execute(sqlstring)
    r = cur.fetchall()
    cur.close()
    return r


def fetchall(database, sqlstring):
    conn = getconn(database)
    cur = conn.cursor()
    cur.execute(sqlstring)
    r = cur.fetchall()
    cur.close()
    return r


def fetchone(database, sqlstring):
    conn = getconn(database)
    cur = conn.cursor()
    cur.execute(sqlstring)
    r = cur.fetchone()
    cur.close()
    return r


def execute(database, sqlstring):
    conn = getconn(database)
    cur = conn.cursor()
    cur.execute(sqlstring)
    conn.commit()


def insert_u(database, table, adict):
    sqlstring = insert(table, adict).replace('`', '"')
    execute(database, sqlstring)


def truncate(f, n):
    '''
    Truncates/pads a float f to n decimal places without rounding
    From: http://stackoverflow.com/questions/783897/truncating-floats-in-python
    :param f: floating number
    :param n: number of decimals
    :return:
    '''

    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')

    return '.'.join([i, (d + '0' * n)[:n]])


def split_list_into_n_parts(lst, size):
    lol = lambda lst, size: [lst[i:i + size] for i in range(0, len(lst), size)]

    return lol(lst, size)


def show_efficient_frontier(risks, returns, name):
    '''
    Show efficient frontier
    :param risks: risk list
    :param returns: return list
    :param name: portfolio name list
    :return:
    '''
    # plt.figure(name)
    # plt.title(' Efficient Frontier')
    # plt.ylabel('Mean')
    # plt.xlabel('Std')
    # plt.plot(risks, returns, 'b-o')
    # plt.show()

    return


def get_sys_date():
    '''
    Get system date of today
    :return:
    '''
    sys_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return sys_date


def get_months_diff(date1, date2):
    '''
    return date difference in months
    :param date1: target date
    :param date2: referencing date
    :return:
    '''
    rd = relativedelta(date1, date2)
    return (12 * rd.years + rd.months) + 1


def format_float(s, precision=6):
    if (isinstance(s, float)):

        if np.isnan(s) or np.isinf(s):
            return ""

        format_str = "{:.%sf}" % precision

        return format_str.format(s)
    return s


def format_pct_float(f, precision=6):
    if (isinstance(f, float)):
        f = f / 100
        format_str = "{:.%sf}" % precision

        return format_str.format(f)
    return f


def round_float(s, precision=6):
    format_str = "{:.%sf}" % precision
    if isinstance(s, float):
        return float(format_str.format(s))
    elif isinstance(s, str):
        try:
            return float(format_str.format(float(s)))
        except:
            return float('nan')

def round_float_for_df(s, precision=4):
    format_str = "{:.%sf}" % precision

    # if nan return 'nan' as string
    if s != s:
        return 'nan'

    elif isinstance(s, float):
        return float(format_str.format(s))

    return s

def get_today(to_format='%Y%m%d'):
    today = datetime.today()
    return today.strftime(to_format)

def format_currency(d):
    if str(d) == 'nan':
        return None

    return float(d.replace(',', ''))

def format_date(d, format_str='%Y%m%d'):
    try:
        d = datetime.strptime(d, format_str)
        return d.date().isoformat()
    except:
        return d


def format_date_api(d, from_format='%Y-%m-%d', to_format='%Y%m%d'):
    d = datetime.strptime(d, from_format)

    return d.strftime(to_format)


def format_24time(t, format_str='%I:%M%p'):
    try:
        t = datetime.strptime(t, format_str)
        return t.strftime("%H:%M")
    except:
        return t


def format_taipeiTime_from_localopenclose(tradeDate, local, taipeiTime, openTime, closeTime, local_tz, isFuture):
    taipeiTime = format_taipeitime(taipeiTime)

    if ":" in str(local) and len(str(local)) == 5 and len(str(openTime)) > 0 and len(str(closeTime)) > 0 and isFuture == False:

        current_local = datetime.now().astimezone(pytz.timezone(local_tz)).strftime("%H:%M")

        open_diff = local_time_diff(openTime, current_local)
        close_diff = local_time_diff(current_local, closeTime)

        if open_diff >= 60 or close_diff >= 60:
            taipeiTime = format_taipeitime(tradeDate)

    return taipeiTime


def local_time_diff(local1, local2):
    h1, m1 = [int(i) for i in local1.split(":")]
    h2, m2 = [int(i) for i in local2.split(":")]

    diff = 60 * (h1 - h2) + (m1 - m2)
    return diff


def get_ordered_dict(d, reverse=True):
    res = OrderedDict(sorted(d.items(), key=lambda t: t[1], reverse=reverse))
    return res


def get_month_to_date(today):
    mtd = today + relativedelta(days=(-1 * today.day + 1))

    return mtd


def get_year_to_date(today):
    ytd = today + relativedelta(days=(-1 * today.day + 1), months=(-1 * today.month + 1))

    return ytd


def get_year_to_date_bystr(today_str, today_format='%Y-%m-%d'):
    today = datetime.strptime(today_str, today_format)
    ytd = today + relativedelta(days=(-1 * today.day + 1), months=(-1 * today.month + 1))

    return ytd


def get_ytd(today, offset_year = 0, to_format='%Y%m%d'):
    ytd = today + relativedelta(years=offset_year, days=(-1 * today.day + 1), months=(-1 * today.month + 1))
    ytd_str = ytd.strftime(to_format)
    return ytd_str


def get_ytd__bystr(today_str, from_format='%Y%m%d', to_format='%Y%m%d'):
    # print ("start")
    # print(today_str)
    today = datetime.strptime(today_str, from_format)
    # print(today)

    ytd = today + relativedelta(days=(-1 * today.day + 1), months=(-1 * today.month + 1))

    ytd_str = ytd.strftime(to_format)
    # print(ytd)
    return ytd_str


def get_delta_date(date, days=0, weeks=0, months=0, years=0):
    dt = date + relativedelta(days=days, weeks=weeks, months=months, years=years)
    return dt.strftime("%Y%m%d")


def get_formatterd_delta_date_bystr(today_str, days=0, weeks=0, months=0, years=0, from_format='%Y%m%d',
                                    to_format='%Y%m%d'):
    try:
        today = datetime.strptime(today_str, from_format)
        dt = today + relativedelta(days=days, weeks=weeks, months=months, years=years)
        return dt.strftime(to_format)
    except:
        return str(today_str)

def get_delta_date_str(today, to_format='%Y%m%d', days=0, weeks=0, months=0, years=0):
    start_date = today + relativedelta(days=days, weeks=weeks, months=months, years=years)
    return start_date.strftime(to_format)


def get_delta_date_bystr(today_str, days=0, weeks=0, months=0, years=0, format='%Y-%m-%d'):
    today = datetime.strptime(today_str, format)
    start_date = today + relativedelta(days=days, weeks=weeks, months=months, years=years)
    return start_date


def get_ytd_for_google():
    today = datetime.today()
    offset = 5
    startdate = today + relativedelta(days=(-1 * today.day - offset), months=(-1 * today.month + 1))
    enddate = today + relativedelta(days=(-1 * today.day), months=(-1 * today.month + 1))

    return startdate.date().isoformat(), enddate.date().isoformat()


def get_period_deltas():
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../conf/period_delta.csv'))

    deltas = pd.read_csv(file_path, index_col='period')

    return deltas


def get_fund_categories(only_enabled=False):
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../conf/fund_categories.csv'))
    categories = pd.read_csv(file_path, index_col='category')
    if (only_enabled):
        categories = categories[categories.enabled == 1]
    return categories


def get_howidxtype_names():
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../conf/howIdxType_names.csv'))

    df = pd.read_csv(file_path, index_col='howIdxType', encoding='utf-8')

    return df


def get_popular_stocks():
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../conf/popular_stocks.csv'))

    df = pd.read_csv(file_path, encoding='utf-8')
    df['symbol'] = df['ticker'] + ":" + df['exch']
    df.set_index(['ticker'], inplace=True)
    return df


def list_cache_timeouts(prex='api', version='v1'):
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../conf/api_cache_timeout.csv'))

    df = pd.read_csv(file_path, index_col='name', encoding='utf-8')
    df.index = ['/%s/%s/%s' % (prex, version, name) for name in df.index]
    res = df.to_dict(orient='index')
    return res


def get_start_end_date_periods(today_str):
    deltas = get_period_deltas()

    periods_dict = {}

    change_periods = ["1W", "1M", "3M", "6M", "1Y", "2Y", "3Y", "5Y"]

    today = datetime.strptime(today_str, '%Y-%m-%d')

    # get calendar periods
    for period in change_periods:
        # print(period)

        start_date = today + relativedelta(days=int(deltas.days[period]), weeks=int(deltas.weeks[period]),
                                           months=int(deltas.months[period]), years=int(deltas.years[period]))

        periods_dict[period] = [start_date, today]

    # add MTD and YTD
    periods_dict["MTD"] = [get_month_to_date(today), today]
    periods_dict["YTD"] = [get_year_to_date(today), today]

    return periods_dict


def get_standard_return_periods():
    """

    :return:
    """
    deltas = get_period_deltas()

    periods_dict = {}

    change_periods = ["1W", "1M", "3M", "6M", "1Y", "3Y", "5Y"]

    today = datetime.today()

    # get calendar periods
    for period in change_periods:
        # print(period)

        start_date = today + relativedelta(days=int(deltas.days[period]), weeks=int(deltas.weeks[period]),
                                           months=int(deltas.months[period]), years=int(deltas.years[period]))

        periods_dict[period] = [start_date, today]

    return periods_dict


def convert_datetime_timezone(dt, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)

    dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")

    return dt


def convert_timzeone(dt, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)

    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    return dt


def convert_percent_to_float(s):
    try:
        if isinstance(type(eval(s.replace("%", ""))), tuple):
            return ""
        if float(s) > float(100):
            return s

        f = eval(s.replace("%", "")) / 100.0
        return format_float(f)
    except Exception as e:
        print(str(e))

def convert_float_to_percent(s):
    try:
        if not isinstance(s, float):
            return s
        else:
            return s * 100

    except Exception as e:
        print(str(e))

def format_taipeitime(s):
    s=str(s)
    if len(s) != 5:
        # convert 20170331 to 03/31
        if (s.isdigit() and len(s) == 8):
            d = datetime.strptime(s, '%Y%m%d')
            return d.strftime("%m/%d")

        # convert 6/8 to 06/08
        if ("/" in s and len(s) < 5):
            d = datetime.strptime(s, '%m/%d')
            return d.strftime("%m/%d")

        # convert 6:8 to 06/08
        if (":" in s and len(s) < 5):
            d = datetime.strptime(s, '%H:%M')
            return d.strftime("%H:%M")

    return s


def format_yearmonth(s):
    # convert 20170331 to 2017/03
    if (s.isdigit() and len(s) == 8):
        d = datetime.strptime(s, '%Y%m%d')
        return d.strftime("%Y/%m")

    return s


def get_marketdata_count(openTime, closeTime, freq):
    # default use whole day
    diff = 1440
    if openTime != '' and closeTime != '':
        # cause OS error on Windows enviorment
        # open = datetime.strptime(openTime, '%H:%M').timestamp() / 60
        # close = datetime.strptime(closeTime, '%H:%M').timestamp() / 60
        open = datetime.strptime(openTime, '%H:%M')
        close = datetime.strptime(closeTime, '%H:%M')
        delta = close - open
        diff = int(delta.seconds / 60)

        # for future open/close, ex. 5:30 ~ 4:30(next day), use default
        if diff < 0:
            diff = 1440

    return 1 + int(diff / int(freq))

def get_marketdata_count_1(openTime, closeTime, timeNow, count):
    # default use whole day
    diff = 1440

    if openTime != '' and closeTime != '':
        # cause OS error on Windows enviorment
        # open = datetime.strptime(openTime, '%H:%M').timestamp() / 60
        # close = datetime.strptime(closeTime, '%H:%M').timestamp() / 60
        # time_now = datetime.strptime(timeNow, '%H:%M').timestamp() / 60
        open = datetime.strptime(openTime, '%H:%M')
        close = datetime.strptime(closeTime, '%H:%M')
        time_now = datetime.strptime(timeNow, '%H:%M')

        delta = close - open
        delta1 = time_now - open

        diff = int(delta.seconds / 60)
        diff1 = int(delta1.seconds / 60)

        # for future open/close, ex. 5:30 ~ 4:30(next day), use default
        if diff < 0:
            diff = 1440
        if diff1 < 0:
            return 0
    return 1 + count * int(diff / diff1)

def get_dataframe_from_post(post):
    df = DataFrame(list(post))
    # print(len(df))
    return df


def list_all_business_day(start, end, freq='BM', to_format='%Y%m%d'):
    """

    :param start:
    :param end:
    :param freq:
    :param to_format:
    :return:
    """
    days = []
    for d in pd.date_range(start, end, freq=freq):
        days.append(d)
    return days


def get_response_soup(url, features='lxml', retry=3):

    while (retry > 0):
        response = request.urlopen(url)
        soup = BeautifulSoup(response.read(), features)

        if len(re.findall(u'[\u4e00-\u9fff]+', soup.text)) == 0:
            retry -= 1
        else:
            return soup
    return None


def get_post_response_soup(url, payload, headers=None, features='lxml', retry=3):

    while (retry > 0):
        response = requests.post(url, data=payload, headers=headers)
        soup = BeautifulSoup(response.text, features)
        return soup
    return None


def get_today_str():
    return datetime.now().strftime("%Y%m%d")


def get_tradeDate():
    threshold = datetime.today().replace(hour=5, minute=46)
    now_date = datetime.today()
    if now_date > threshold:
        return date.today().strftime('%Y%m%d')
    elif now_date <= threshold:
        return (date.today() - timedelta(1)).strftime('%Y%m%d')


# convert local/taipei time format to 5 letters
def format_local_taipei(s):
    if len(s) != 5:
        # convert 20170331 to 03/31
        if (s.isdigit() and len(s) == 8):
            d = datetime.strptime(s, '%Y%m%d')
            return d.strftime("%m/%d")

        # convert 6/8 to 06/08
        if ("/" in s and len(s) < 5):
            d = datetime.strptime(s, '%m/%d')
            return d.strftime("%m/%d")

        # convert 6:8 to 06/08
        if (":" in s and len(s) < 5):
            d = datetime.strptime(s, '%H:%M')
            return d.strftime("%H:%M")

    return s


def get_tradeDate_taipeiTime_from_local(local, timezone, hours_buffer=3):
    tradeDate = ''
    taipeiTime = ''
    local = format_local_taipei(local)

    # local in 12/31 format:
    if "/" in local:

        tradeDate = format_md_to_ymd(local)
        taipeiTime = local

    # local in 24:00 format
    elif ":" in local:

        if timezone != '':

            dt, tradeDate, date_md, current_local = get_timezone_now(timezone)

            local_diff = local_time_diff(current_local, local)

            # check if the local time is a valid time (not future)
            if local_diff > 60 * hours_buffer:

                return None, None
            elif 0 > local_diff and local_diff > (60 * hours_buffer - 1440):
                return None, None
            elif 0 > local_diff and local_diff < (60 * hours_buffer - 1440):
                tradeDate = get_prev_weekday(tradeDate)

            taipeiTime = convert_betwen_timezone(tradeDate, local, tz1=timezone, tz2="Asia/Taipei")

    return tradeDate, taipeiTime


def get_tradeDate_local_from_taipeiTime(taipeiTime, timezone, hours_buffer=3):
    tradeDate = ''
    local = ''
    taipeiTime = format_local_taipei(taipeiTime)

    # taipeiTime in 12/31 format:
    if "/" in taipeiTime:

        tradeDate = format_md_to_ymd(taipeiTime)
        local = taipeiTime

    # local in 24:00 format
    elif ":" in taipeiTime:

        if timezone != '':

            # dt, date_ymd, date_md, current = get_timezone_now(timezone)
            current_taipeiTime = get_current_taipeiTime()

            local_diff = local_time_diff(current_taipeiTime, taipeiTime)

            # check if the taipei time is a valid time (not future)
            if local_diff > 60 * hours_buffer:

                return None, None
            elif 0 > local_diff and local_diff > (60 * hours_buffer - 1440):

                return None, None

            dt, tradeDate, date_md, time_hm = convert_taipei_to_local(taipeiTime, timezone)

            local = convert_betwen_timezone(tradeDate, taipeiTime, tz1="Asia/Taipei", tz2=timezone)

    return tradeDate, local


def get_local_taipeiTime_from_tradeDate(tradeDate):
    local = format_local_taipei(tradeDate)
    taipeiTime = format_local_taipei(tradeDate)
    tradeDate = format_md_to_ymd(tradeDate)

    return tradeDate, local, taipeiTime


def get_timezone_now(local_tz):
    dt = datetime.now().astimezone(pytz.timezone(local_tz))
    date_ymd = dt.strftime("%Y%m%d")
    date_md = dt.strftime("%m/%d")
    time_hm = dt.strftime("%H:%M")
    return dt, date_ymd, date_md, time_hm


def get_current_taipeiTime():
    time_hm = datetime.now().strftime("%H:%M")
    return time_hm


def convert_taipei_to_local(taipeiTime, local_tz):
    taipeidate = datetime.now().strftime("%Y%m%d")
    dt = datetime.strptime(taipeidate + taipeiTime, "%Y%m%d%H:%M").astimezone(pytz.timezone(local_tz))

    # if dt is greater than now => future day => change dt to the day before
    if (dt.timestamp() > datetime.now().timestamp()):
        dt = dt + relativedelta(days=-1)

    date_ymd = dt.strftime("%Y%m%d")
    date_md = dt.strftime("%m/%d")
    time_hm = dt.strftime("%H:%M")
    return dt, date_ymd, date_md, time_hm


def convert_betwen_timezone(tradeDate, local, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)

    dt = datetime.strptime(tradeDate + local, "%Y%m%d%H:%M")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%H:%M")

    return dt


def date_for_idx():
    threshold = datetime.today().replace(hour=5, minute=46)
    now_date = datetime.today()
    if now_date > threshold:
        return date.today().strftime('%Y%m%d')
    elif now_date <= threshold:
        return (date.today() - timedelta(1)).strftime('%Y%m%d')


def format_md_to_ymd(md_str, from_dt=datetime.now(), from_format='%m/%d', to_format='%Y%m%d'):
    try:
        to_dt = datetime.strptime(str(from_dt.year) + md_str, '%Y' + from_format)

        # check the day difference and adjust the year
        day_diff = (to_dt.timestamp() - from_dt.timestamp()) / 86400
        if (day_diff > 180):
            to_dt = datetime.strptime(str(from_dt.year - 1) + md_str, '%Y' + from_format)
        elif (day_diff < -180):
            to_dt = datetime.strptime(str(from_dt.year + 1) + md_str, '%Y' + from_format)

        return to_dt.strftime(to_format)

    except Exception as e:

        return md_str


def local_time_diff(local1, local2):
    h1, m1 = [int(i) for i in local1.split(":")]
    h2, m2 = [int(i) for i in local2.split(":")]

    diff = 60 * (h1 - h2) + (m1 - m2)
    return diff


def is_wekend(tradeDate, format='%Y%m%d'):
    weekday = datetime.strptime(tradeDate, format).weekday()

    if weekday >= 5:
        return True
    else:
        return False


def list_all_days(sd_str, ed_str, from_format='%Y%m%d', to_format='%Y%m%d', weekday_only=True):
    sd = datetime.strptime(sd_str, from_format)
    ed = datetime.strptime(ed_str, from_format)
    delta = ed - sd
    days = []
    for i in range(delta.days + 1):
        d = sd + timedelta(days=i)

        if weekday_only and d.weekday() >= 5:
            continue

        days.append(d.strftime(to_format))

    return days


def list_all_business_day(start, end, freq='BM', to_format='%Y%m%d'):
    days = []
    for d in pd.date_range(start, end, freq=freq):
        days.append(d.strftime(to_format))
    return days

def list_monthly_business_day_by_freq(start, end, freq=1, to_format='%Y%m%d'):
    """
    list all business month end by different frequency
    :param start:
    :param end:
    :param freq:
    :param to_format:
    :return:
    """
    # first day will be the start date
    days = []

    if freq <= 0:
        # for no rebalance
        days.append([start, end])

    else:
        # get the monthly day list
        dates = list(pd.date_range(start, end, freq="BM"))
        sd = parse_date(start)
        end = parse_date(end)

        # iternate all dates
        for i, d in enumerate(dates):
            if (i + 1) % freq == 0:
                # ed = d.strftime(to_format)
                ed = d
                if sd != ed:
                    days.append([sd, ed])

                sd = ed

        # check the last period
        if sd != end:
            days.append([sd, end])

    return days

def list_monthly_business_day_for_pr(start, end, freq=1, to_format='%Y%m%d'):
    """
    list all business month end by different frequency
    :param start:
    :param end:
    :param freq:
    :param to_format:
    :return:
    """
    days = [start]

    dates = list(pd.date_range(start, end, freq="BM"))

    # # if there is no rebalance, return the first date
    # if freq == 0:
    #     return [dates[0].strftime(to_format)]
    if freq > 0:
        for i, d in enumerate(dates):
            if i % freq == 0:
                days.append(d.strftime(to_format))

    return days


def unify_symbol(s):
    # apply to number only
    if (not s.isupper()) and (not s.islower()):
        s = s.replace(',', '')

    if '--' in s:
        return s.strip('--')

    if '▼' in s:
        return '-{}'.format(s.strip('▼▲%-'))
    else:
        return s.strip('▼▲%')


def format_float(s, precision=4):
    if (isinstance(s, float)):
        format_str = "{:.%sf}" % precision

        return format_str.format(s)
    return s


def round_pct_float(s, precision=4):
    format_str = "{:.%sf}" % precision

    if isinstance(s, float):
        s = s / 100
        return float(format_str.format(s))
    elif isinstance(s, str):
        try:
            return float(format_str.format(float(s) / 100))
        except:
            return float('nan')


# def format_pct_float(f, precision=4):
#     if (isinstance(f, float)):
#         f = f / 100
#         format_str = "{:.%sf}" % precision
#
#         return format_str.format(f)
#     return f


def get_period_deltas():
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../conf/period_delta.csv'))

    deltas = pd.read_csv(file_path, index_col='period')

    return deltas


def get_period_startdate(today_str, today_format='%Y%m%d'):
    deltas = get_period_deltas()

    periods_dict = {}

    change_periods = ["1W", "1M", "3M", "6M", "1Y"]

    today = datetime.strptime(today_str, today_format)

    # get calendar periods
    for period in change_periods:
        start_date = today + relativedelta(days=int(deltas.days[period]), weeks=int(deltas.weeks[period]),
                                           months=int(deltas.months[period]), years=int(deltas.years[period]))

        periods_dict[period] = [start_date, today]

    # add MTD and YTD
    periods_dict["MTD"] = [get_month_to_date(today), today]
    periods_dict["YTD"] = [get_year_to_date(today), today]

    return periods_dict


def get_month_to_date(today):
    mtd = today + relativedelta(days=(-1 * today.day + 1))

    return mtd


def get_year_to_date(today):
    ytd = today + relativedelta(days=(-1 * today.day + 1), months=(-1 * today.month + 1))

    return ytd


def get_prev_weekday(today_str, today_format='%Y%m%d', to_format='%Y%m%d'):
    today = datetime.strptime(today_str, today_format)
    adate = today - timedelta(days=1)
    while adate.weekday() > 4:  # Mon-Fri are 0-4
        adate -= timedelta(days=1)
    return adate.strftime(to_format)



def parse_date(date_str, format='%Y%m%d', to_format=None):
    """

    :param date_str:
    :param format:
    :return:
    """
    if to_format is not None:
        return datetime.strptime(date_str, format).strftime(to_format)
    else:
        return datetime.strptime(date_str, format)



def send_email(name, portfolio_id, receiver):
    """

    :param name:
    :param portfolio_id:
    :param receiver:
    :return:
    """

    sender = 'ada.ai@howfintech.com'

    content = "Hi!\n\nThe back testing portfolio you created, %s, is ready to review.\n\n" \
              "Click the link below to see the result:\n" \
              "http://192.168.10.201:83/portfolio/parameter/result/%s" % (name, portfolio_id)

    subject = "Email notification for portfolio back testing"

    try:
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver

        conn = smtplib.SMTP_SSL('smtp.worksmobile.com', 465)
        conn.login('ada.ai@howfintech.com', 'Howbot9900')
        conn.sendmail(sender, receiver, msg.as_string())
    finally:
        conn.quit()

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def json_return(code, message = '', data ={}):
    if code != 200:
        status = 'fail'
    else:
        status = 'success'
    return {'data': data, 'msg':message, 'code': code}

@cache_util.cached(timeout=86400)
def get_fund_categories():

    mysqlutil = MySQLUtil()
    category_df = mysqlutil.get_fund_categories(index_col='algorithmCategory')
    category = category_df.to_dict(orient='index')

    res = {}
    for item in category:
        if category[item]['category'].find('ALTER') >= 0:
            fund_type = "貨幣型"
        elif category[item]['category'].find('BOND') >= 0:
            fund_type = "債券型"
        elif category[item]['category'].find('STOCK') >= 0:
            fund_type = "股票型"

        res[category[item]['category']] = {'category': item, 'fund_type': fund_type}
        res[item] = category[item]

    return  res

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')