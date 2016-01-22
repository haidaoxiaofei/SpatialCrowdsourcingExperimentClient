from gmission import *
import requests


USERNAME = 'zchenah'
PASSWORD = '123456'


class Campaign:
    def __init__(self, client, id):
        self.id = id
        self.client = client

    def create_selection_hit(self, title, desp, fname, choices):
        att_id = self.client.new_attchment_with_image(fname)["id"]
        hit_id = self.client.create_hit('selection', title, desp, att_id, self.id, 1, 100, 12).get('id')
        for choice in choices:
            self.client.create_selection(hit_id, choice)
    # def create_hit(self, type, title, description, attachment_id, campaign_id, credit, required_answer_count,
        # location_id, min_selection_count=1, max_selection_count=1):


class Client(GmissionClient):
    def get_or_create_location(self, name, lon, lat):
        try:
            loc_id = self.create_location(name, lon, lat).get('id')
        except requests.HTTPError as e:
            print e
            locs = self.get_locations()
            loc_id = [c["id"] for c in locs if c["name"]==name].pop()
        return loc_id

    def get_or_create_campaign(self, title, desp=""):
        try:
            campaign_id = self.create_campaign(title, desp).get('id', 0)
        except requests.HTTPError as e:
            print e
            campaigns = self.get_campaigns()
            campaign_id = [c["id"] for c in campaigns if c["title"]==title].pop()
        return Campaign(self, campaign_id)


import os
import shutil
import random
import os.path


def download_image(url, fname):
    response = requests.get(url, stream=True)
    with open(fname, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)


def download_faces():
    faces = []
    folder = "temp-images"
    if not os.path.exists(folder):
        os.makedirs(folder)
    for origin_url in (line.strip() for line in file('imagelist.txt')):
        if '0001' in origin_url:
            fname = os.path.join(folder, origin_url.split('/')[-1])
            print origin_url
            download_image(origin_url, fname)
            faces.append(fname)
    return faces


from PIL import Image
def join_images(fnames):
    size = 250
    width = size
    height = size*len(fnames)
    res = Image.new('RGB', (width, height))
    for idx, startY in enumerate(range(0, height, size)):
        img = Image.open(fnames[idx])
        res.paste(img, (0, startY))
    res.save("temp_joined_faces.jpg")
    return "temp_joined_faces.jpg"


def main():
    client = Client('http://lccpu3.cse.ust.hk/gmission-dev/')
    client.user_auth(USERNAME, PASSWORD)

    campaign = client.get_or_create_campaign('Who is better-looking?', "Just choose the one you believe who has a better-looing face!")
    client.assign_user_to_campaign(campaign.id, CAMPAIGN_USER_ROLE_OWNER)

    faces = download_faces()
    for face_filename in faces[:20]:  # for each face find at least 1 group of other faces to compare with
        filenames = [face_filename.strip()]
        group_size = 2
        while len(filenames) < group_size:
            c = random.choice(faces)
            if c not in filenames:
                filenames.append(c)

        people_names = [' '.join(fname.split('/')[-1].split('_')[:-1]) for fname in filenames]
        title = ' VS '.join(people_names)
        desp = 'Choose the better-looking one from the below face. They are: %s from top to bottom.'%(', '.join(people_names))
        joined_fname = join_images(filenames)
        campaign.create_selection_hit(title, desp, joined_fname, people_names)


if __name__ == '__main__':
    main()

