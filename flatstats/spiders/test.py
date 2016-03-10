# -*- coding: utf-8 -*-
import scrapy
from flatstats.items import FlatstatsItem, RunnersItem
import re
import string
from decimal import Decimal
from collections import Counter, defaultdict
from datetime import datetime
from flatstats.systemsdata import getrpid,getisTurf

def getsysteminfo(response):
    system = defaultdict(dict)
    system['system_name'] = response.xpath("//div[@id='system']//div/h4/span/strong/text()").extract()[0]
    system['exposure'] = response.xpath("//table[@id='system']/tbody//tr//td[1]/text()").extract()
    # system['system_desc'] = response.xpath("//h4[contains(text(), 'System Name')]/span/strong/text()/../../../../p/text()").extract()[0]
    system['query'] = list()
    for i,tr in enumerate(response.xpath("//table[@id='system']/tbody//tr")):
        queryclause = dict()
        queryclause['position'] = str(i+1)
        queryclause['_it'] = tr.xpath("td[1]/text()").extract()[0]
        queryclause['_op'] = tr.xpath("td[2]/text()").extract()[0]
        queryclause['_val'] = tr.xpath("td[3]/text()").extract()[0]
        queryclause['_join'] = tr.xpath("td[4]/text()").extract()[0]
        system['query'].append(queryclause)
    #tie query to system
    # z = system
    # z.update()
    # z.update(query)
    # z.update(_d)
    #         racedayinfo[h] = z
    return system

# 13 from 50 (26.0%)
def getwinspcfromlast50(s):
    runs = pc = None
    pcpat = re.compile(r'.*\(([0-9.]+)%\).*')
    try:
        runs = s.split("from")[0].strip()
        pc = re.match(pcpat, s).group(1)
        print(runs, pc)
    except ValueError:
        return
    return(runs, pc)



def getpc(n,d):
    if d != 0:
        return round((n/float(d))*100.0, 2)

def try_int(value):
    try:
        return int(value)
    except:
        return 0

def removeunichars(value):
    return value.encode('ascii', 'ignore')

def removespecialchars(s):
    return ''.join(e for e in s if e.isalnum())

def removepc(s):
    try:
        s.replace(u'%', '')
    except ValueError:
        pass
    return s

def getdigits(s):
    allx=string.maketrans('','')
    nodigs=allx.translate(allx, string.digits)
    return x.translate(allx, nodigs)

def tofloat(s):
    m = re.findall(r"[-+]?\d*\.\d+|\d+", s)
    if len(m)>0:
        return float(m[0])
    else:
        return None

def tomoney(s):
    s.encode('utf8')
    s.replace(unichr(163), "")
    m = tofloat(s)
    if m:
        return Decimal(m)

def toint(s):
    m = re.findall(r"[-+]?\d*\.\d+|\d+", s)
    if len(m)>0:
        return int(m[0])
    else:
        return None


class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["flatstats.co.uk"]
    badsids = [244678,244750,244457,244461]
    goodsids = [244881]
    #do one at a time!
    # sids = [244678,244677,244675,244673,244447,244451,244452,244454,244457,244459,244461,244465,244470,244472]
    THE_URLS = ["https://www.flatstats.co.uk/racing-system-builder.php?snapshot_id={}".format(sid) for sid in goodsids]
    start_urls = THE_URLS
    # start_urls = (
    #     'https://www.flatstats.co.uk/racing-system-builder.php?snapshot_id=201980',
    # )

    def parse(self, response):
        from scrapy.shell import inspect_response
        # inspect_response(response, self)
        item = FlatstatsItem()
        snapshot_id = response.url.split('=')[1]
        item['snapshotid']= snapshot_id

        # isTurf = getisTurf(snapshot_id)
        isTurf = True
        item['isTurf'] = isTurf
        #system
        system = dict()
        system = getsysteminfo(response)
        item['systemname']= system['system_name']
        item['exposure'] = {'exposure': system['exposure']}
        item['query'] = system['query']

        #//div[@id='full-report']/table/tbody//td[contains(text(),'Expected Wins')]/following-sibling::td/text()
        #BetfairSPruns
        red_rows = response.xpath("//tr[td[contains(@class,'red')]]")
        blue_rows = response.xpath("//tr[td[contains(@class,'blue')]]")
        green_rows = response.xpath("//tr[td[contains(@class,'red')]]")
        total_rows = response.xpath("//tr[td[contains(@class,'green') or contains(@class, 'red') or contains(@class, 'blue')]]")
        print(len(red_rows), len(blue_rows), len(total_rows))
        # assert(len(red_rows)==2)
        item['red_rows_ct'] = len(red_rows)
        item['blue_rows_ct']= len(blue_rows)
        item['green_rows_ct'] = len(green_rows)
        item['total_rows_ct'] = len(total_rows)
        item['red_rows_pc'] = getpc(len(red_rows), len(total_rows))
        item['green_rows_pc'] = getpc(len(green_rows), len(total_rows))
        item['blue_rows_pc'] = getpc(len(blue_rows), len(total_rows))
        #get attr for red rows
        redrowsd = dict()
        bluerowsd = dict()
        greenrowsd = dict()
        for r in red_rows:
            _errantval = r.xpath("td[1]/text()").extract()[0]
            _attr = "".join(r.xpath("../../thead/tr/th[1]/text()").extract())
            redrowsd[_attr] = _errantval
        for r in blue_rows:
            _errantval = r.xpath("td[1]/text()").extract()[0]
            _attr = "".join(r.xpath("../../thead/tr/th[1]/text()").extract())
            bluerowsd[_attr] = _errantval
        for r in green_rows:
            _errantval = r.xpath("td[1]/text()").extract()[0]
            _attr = "".join(r.xpath("../../thead/tr/th[1]/text()").extract())
            greenrowsd[_attr] = _errantval
        item['redrows'] = redrowsd
        item['greenrows'] = greenrowsd
        item['bluerows'] = bluerowsd
        ####BF down to Year Stats
        bfsection = response.xpath("//div[@id='full-report']/table/tbody//th[contains(text(),'Betfair')]")

        _bf1=  bfsection.xpath("../following-sibling::tr/td//text()").extract()

        bfruns = toint(_bf1[1])
        print(bfruns)
        item['bfruns']= bfruns
        levelbspprofit = tomoney(_bf1[5])
        item['levelbspprofit'] = levelbspprofit
        levelbsprofitpc = tofloat(_bf1[6])
        item['levelbsprofitpc'] = round(levelbsprofitpc,3)
        item['bfwins'] = toint(_bf1[8])
        print(levelbspprofit,levelbsprofitpc, bfruns)
        # assert(levelbsprofitpc== getpc(levelbspprofit, bfruns) )

        item['bfwinpc'] = tofloat(_bf1[9])
        item['expectedwins'] = tofloat(_bf1[22])
        item['a_e'] = tofloat(_bf1[23])
        item['archie_allruns'] = tofloat(_bf1[81])
        item['expected_last50'] = tofloat(_bf1[84])
        item['archie_last50'] = tofloat(_bf1[87])
        last50wins, last50pc = getwinspcfromlast50(_bf1[90])
        item['last50wins'] = toint(last50wins)
        item['last50pc'] = tofloat(last50pc)
        item['a_e_last50'] = tofloat(_bf1[91])
        item['profit_last50'] = tomoney(_bf1[92])
        item['last50str'] = _bf1[94]
        print(_bf1[94].count('1'))
        print(toint(last50wins))
        # assert(_bf1[94].count('1')== last50wins)
        last28daysruns_ = _bf1[96]
        if "No Runners" in last28daysruns_:
            item['last28daysruns'] = 0.0
        else:
            item['last28daysruns']= last28daysruns_
        item['individualrunners'] = toint(_bf1[98])
        item['uniquewinners'] = toint(_bf1[101])
        item['uniquewinnerstorunnerspc'] = tofloat(_bf1[102])
        #uniquewinnerstorunnerspc should equal
        # assert(uniquewinnerstorunnerspc == uniquewinners/float(individualrunners))
        item['longestwinningstreak'] = toint(_bf1[108])
        item['longestlosingstreak'] = toint(_bf1[112])
        item['averagelosingstreak'] = tofloat(_bf1[118])


        #next year stats
        yearstats= defaultdict(dict)
        colorclasses = defaultdict(list)
        for y in response.xpath("//div[@id='full-report']/table[2]/tbody/tr"):
            #year, wins, runs, winpc, plcpc, impactvalue, a_e, levelprofit, levelroipc
            colorclass = y.xpath("td[1]/@class").extract()[0].replace('l ', '')
            year = y.xpath("td[1]/text()").extract()[0]
            colorclasses[colorclass].append(year)
            yearstats[year]['wins'] = tofloat(y.xpath("td[2]/text()").extract()[0])
            yearstats[year]['runs'] = tofloat(y.xpath("td[3]/text()").extract()[0])
            yearstats[year]['winpc'] = tofloat(y.xpath("td[4]/text()").extract()[0])
            yearstats[year]['plcpc'] = tofloat(y.xpath("td[5]/text()").extract()[0])
            yearstats[year]['impactvalue'] = tofloat(y.xpath("td[6]/text()").extract()[0])
            yearstats[year]['a_e'] = tofloat(y.xpath("td[7]/text()").extract()[0])
            yearstats[year]['levelprofit'] = tomoney(y.xpath("td[8]/text()").extract()[0])
            yearstats[year]['levelroipc'] = tofloat(y.xpath("td[9]/text()").extract()[0])

        print(yearstats)
        item['yearstats'] = yearstats
        item['yearcolorcounts'] = dict(colorclasses)
        item['totalbackyears'] = len(yearstats.items())

        ## runners record to derive correlations
        runner_items = list()
        colpat = re.compile(r'.*color: ((?:blue|red|green));.*')
        for tr in response.xpath("//div[@id='runners']//table[@class='ui-jqgrid-btable']/tbody/tr[position()>1]"):
            ritem = RunnersItem()
            racedate_ = tr.xpath("/td[2]/text()").extract()[0] # 2009-10-16
            racedate = datetime.strptime(d, "%Y-%m-%d").date()
            racecoursename = tr.xpath("/td[3]/text()").extract()[0]
            rprcid = getrpid(racecoursename,isTurf)
            racename = tr.xpath("/td[4]/text()").extract()[0]
            typehorse = tr.xpath("/td[5]/text()").extract()[0]
            typerace = tr.xpath("/td[6]/text()").extract()[0]
            handicapstakes = tr.xpath("/td[7]/text()").extract()[0]
            agerestriction = tr.xpath("/td[8]/text()").extract()[0]
            raceclass = tr.xpath("/td[9]/text()").extract()[0]
            distance = tr.xpath("/td[10]/text()").extract()[0]
            going= tr.xpath("/td[11]/text()").extract()[0]
            runners= tr.xpath("/td[12]/text()").extract()[0]
            horsename= tr.xpath("/td[13]/text()").extract()[0]
            trainername= tr.xpath("/td[14]/text()").extract()[0]
            jockeyname= tr.xpath("/td[15]/text()").extract()[0]
            FINALPOS= tr.xpath("/td[16]/text()").extract()[0]
            _color = tr.xpath("/td[16]/@style")
            poscolor = None
            if re.match(colpat, _color):
                poscolor = re.match(colpat, _color).group(1)
            winsp= tr.xpath("/td[18]/text()").extract()[0]
            bfsp= tr.xpath("/td[19]/text()").extract()[0]
            ratingrank= tr.xpath("/td[21]/text()").extract()[0]
            rating = tr.xpath("/td[22]/text()").extract()[0]
            placed = tr.xpath("/td[23]/text()").extract()[0]
            raceno = tr.xpath("/td[24]/text()").extract()[0] #important used as key
            if reportraceno:
                RunnersItem['racedate'] = racedate
                RunnersItem['racecoursename']=racecoursename
                RunnersItem['racename']=racename
                RunnersItem['racecourseid']=rprcid
                RunnersItem['racetypehorse'] =typehorse
                RunnersItem['racetypeconditions'] = typerace
                RunnersItem['racetypehs'] =handicapstakes
                RunnersItem['ages'] =agerestriction
                RunnersItem['raceclass'] =raceclass
                RunnersItem['distance'] =distance
                RunnersItem['going'] =going
                RunnersItem['runners'] =runners
                RunnersItem['horsename'] =horsename
                # RunnersItem['sirename'] =sirename?
                RunnersItem['trainername'] =trainername
                RunnersItem['jockeyname'] =jockeyname
                # RunnersItem['allowance'] =allowance
                RunnersItem['FINALPOS'] =FINALPOS
                # RunnersItem['lbw'] =lbw
                RunnersItem['poscolor'] =poscolor
                RunnersItem['winsp'] =winsp
                # RunnersItem['winsppos'] =winsppos
                RunnersItem['bfsp'] =bfsp
                # RunnersItem['bfspsp'] =bfpsp
                RunnersItem['ratingrank'] =ratingrank
                RunnersItem['rating'] =rating
                # RunnersItem['damname'] =damname
                # RunnersItem['draw'] =draw
                # RunnersItem['damsirename'] =damsirename
                # RunnersItem['racetime'] =racetime
                RunnersItem['placed'] =placed
                # RunnersItem['totalruns'] =totalruns
                # RunnersItem['bfplaced'] =bfplaced
                RunnersItem['raceno'] =raceno
                runner_items.append(ritem.item_loader())
        #MONGO PIPELINE
        item['runners'] = runner_items
        return item
        # except ValueError:
        #     pass
        # #remove " "
        # print(response.xpath("//div[@id='full-report']").extract()[0])
        # inspect_response(response, self)
