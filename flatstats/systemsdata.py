
#redo systems make sure they are accesible to flatstats user and scrape into DB
#key is fs name
# racecourseinfo = [
# {'Ascot': [1,8, 'Triangle', 'Right','Galloping', 'Uphill', 'South', '', '']},
#
#
#
# ]
#
#
# }

def getrpid(rc,isTurf):
    if rc == 'Southwell':
        if isTurf:
            return 61,
        else:
            return 394
    if rc == 'Lingfield':
        if isTurf:
            return 31,
        else:
            return 393
    else:
        return {
        'Ascot': 2,
        'Ayr': 3,
        'Bath': 5,
        'Beverley':6,
        'Brighton': 7,
        'Carlisle': 8,
        'Catterick': 10,
        'Chelmsford City': 1083,
        'Chepstow': 12,
        'Chester': 13,
        'Doncaster': 15,
        'Epsom': 17,
        'Ffos Las': 1212,
        'Folkestone':19,
        'Goodwood': 21,
        'Hamilton': 22,
        'Haydock':23,
        'Kempton':1079,
        'Leicester': 30,
        'Musselburgh':16,
        'Newbury': 36,
        'Newcastle': 37,
        'Newmarket': 38, #JUly course is 174!RP no distinction FS
        'Nottingham':40,
        'Pontefract': 46,
        'Redcar': 47,
        'Ripon': 49,
        'Salisbury':52,
        'Sandown':54,
        'Thirsk':80,
        'Warwick': 85,
        'Wetherby': 87,
        'Windsor':93,
        'Wolverhampton': 513,
        'Yarmouth': 104,
        'York': 107
    }.get(str(rc.strip()), 'Not found')

def rc_listtodict(l):
    if not l or type(l)!= type([]):
        return
    #each rc is a dict
    for rc in l:
        _s = dict()
        _s['racecoursename'] = rc
        _s['grade'] = rc[0]
        _s['straight'] = rc[1]
        _s['shape'] = rc[2]
        _s['direction'] = rc[3]
        _s['speed'] = rc[4]
        _s['surface'] = rc[4]
        _s['location'] = rc[4]
        _s['rpid'] = rc[4]
        _s['rpabb'] = rc[4]
    return _s

'''
2016-2- sires
2016-1- sires

'''
ALLSYSTEMS =[
('2016-T-01A', 'Value Maiden Favs Shrewd Yards',244881,True, "Two trainers maiden favorites, Stakes"),
('2016-T-02A', 'Cumani Maiden Machine', ,True, "One trainer maiden favorites not sprints, Stakes"),
('2016-T-03T', 'Carr Lower grade', ,True, "One trainer handicap favorites on Grade 4 courses"),





('2016-4-01A', 'LadiesMan',24447, True, "This jockey is good with the ladies, esp. over galloping tracks"),
('2016-4-02T', 'HiHoSilva',24451, True, "Up and coming jockey at low weights on promising horses"),
('2016-4-03T', 'LouisLouis',24447, True, "Up and coming jockey at heigher weight scale, not fancied"),
('2016-4-04A', 'StraightSprintSpecialists',244454, True, "Exposed horses over straights, where ridership counts"),
('2016-4-05A', 'MasterBaker',244457, True, "A good jockey taking over fit horses from inferior jockeys over all but best grade tracks" , True),
('2016-4-06T', 'SmallFieldMasterTechnicians',244459, True, "3 jockeys in fields of 6 or less"),
('2016-4-07A', 'Sellers&Claimers',244461, True, "2 jockeys who work the poorer-quality races"),
('2016-4-08A', 'C1UnderbetJockeys',244465, True, "2 top consistent jockeys in Class 1 races"),
('2016-4-09A', 'MudlovingJockeys',244470, True, "3 jockeys soft ground over 12.0f distances"),
('2016-4-010T', 'ComebackKid',244472, True, "Former champion apprentice on his way back in C4 and lower races"),
]

#AWT Systems


def getisTurf(snapshot_id):
    snapshot_id = int(snapshot_id)
    #get system from ALLSYSTEMS
    _s = [ x for x in ALLSYSTEMS if x[2] == snapshot_id]
    return _s[3]


def getsystemurlids(l):
    sids = list()
    for i in l:
        sids.append(l[2])
    return sids


def sys_listtodict(l):
    if not l or type(l)!= type([]):
        return
    for s in l:
        _s = dict()
        _s['bookid'] = s[0]
        _s['name'] = s[1]
        _s['fsid'] = s[2]
        _s['isTurf'] = s[3]
        _s['rationale'] = s[4]
    return _s
