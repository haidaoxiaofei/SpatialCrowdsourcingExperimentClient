from gmission import *
from requests import HTTPError


USERNAME = 'zchenah'
PASSWORD = '123456'


class Campaign:
    def __init__(self, client, id):
        self.id = id
        self.client = client

    def create_selection_hit(self, title, desp, choices):
        hit_id = self.client.create_hit('selection', title, desp, None, self.id, 1, 100, 12).get('id')
        for choice in choices:
            self.client.create_selection(hit_id, choice)
    # def create_hit(self, type, title, description, attachment_id, campaign_id, credit, required_answer_count,
        # location_id, min_selection_count=1, max_selection_count=1):


class Client(GmissionClient):
    def get_or_create_location(self, name, lon, lat):
        try:
            loc_id = self.create_location(name, lon, lat).get('id')
        except HTTPError as e:
            print e
            locs = self.get_locations()
            loc_id = [c["id"] for c in locs if c["name"]==name].pop()
        return loc_id

    def get_or_create_campaign(self, title, desp=""):
        try:
            campaign_id = self.create_campaign(title, desp).get('id', 0)
        except HTTPError as e:
            print e
            campaigns = self.get_campaigns()
            campaign_id = [c["id"] for c in campaigns if c["title"]==title].pop()
        return Campaign(self, campaign_id)

def PremierMatchesIter():
    f = file('premierleague.txt', 'r')
    status = 'new'
    matches = []
    for line in f:
        if status=='new':
            match_day = int(line.split()[-1])
            status='date'
        elif status=='date':
            date = line[1:-2]
            status='match'
        elif status=='match':
            if line.strip()=='':
                yield (match_day, date, matches)
                status='new'
                matches = []
            else:
                matches.append(line.strip())

def LigaMatchesIter():
    f = file('liga.txt', 'r')
    status = 'new'
    matches = []
    for line in f:
        if status=='new':
            match_day = int(line.split()[-1])
            status='date'
        elif status=='date':
            date = '/'.join(line[1:-2].split('.')[-3:-1])
            status='match'
        elif status=='match':
            if line.strip()=='':
                yield (match_day, date, matches)
                status='new'
                matches = []
            else:
                match = ' VS '.join(line.strip().split('  '))
                matches.append(match)

def main():
    client = Client('http://lccpu3.cse.ust.hk/gmission-dev/')
    client.user_auth(USERNAME, PASSWORD)
    campaign = client.get_or_create_campaign('Premier League Prediction', "Try to predict the result of future Premier League matches. See if you are a real football fan!")
    client.assign_user_to_campaign(campaign.id, CAMPAIGN_USER_ROLE_OWNER)
    for (match_day, date, matches) in PremierMatchesIter():
        for match in matches:
            title = 'Day %d: %s'%(match_day, match)
            desp = 'Try to predict the result of the Premier League match: [%s] on %s, match day %d.'%(match, date, match_day)
            campaign.create_selection_hit(title, desp, ["Home Win","Away Win"," Draw"] )

    campaign = client.get_or_create_campaign('La Liga Prediction', "Try to predict the result of future La Liga matches. See if you are a real football fan!")
    client.assign_user_to_campaign(campaign.id, CAMPAIGN_USER_ROLE_OWNER)
    for (match_day, date, matches) in LigaMatchesIter():
        for match in matches:
            title = 'Day %d: %s'%(match_day, match)
            desp = 'Try to predict the result of the La Liga match: [%s] on %s, match day %d.'%(match, date, match_day)
            campaign.create_selection_hit(title, desp, ["Home Win","Away Win"," Draw"] )



if __name__ == '__main__':
    main()
    # for (match_day, date, matches) in LigaMatchesIter():
    #     print match_day, date, matches

