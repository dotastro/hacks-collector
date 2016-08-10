import yaml
from jinja2 import Environment, FileSystemLoader, Undefined
import glob
import os
from markdown2 import Markdown
import logging
import copy
import shutil


DATA_DIR_PATTERN = 'dotastro*'
README_NAME = 'README.md'
YAML_TEMPLATE = 'template.yml'
EVENTS_FILE = 'site_generator/events.yml'
LOGO_FILE = 'dotlogo_black.png'

OUTPUT_DIR = 'site_generator/html'

TEMPLATE_LOADER = FileSystemLoader('site_generator/templates')

def runner():
    pages = []
    template_data = load_yaml_style()
    events = parse_events_yml()
    for dirname in glob.glob(DATA_DIR_PATTERN):
        if os.path.isdir(dirname):
            header = parse_header(events,dirname)
            hacks_data = collect_data(dirname, template_data)
            render_page_data(header, hacks_data, dirname)
            pages.append(dirname)
    make_index()
    return

def parse_events_yml():
    stream = open(EVENTS_FILE, 'r')
    filedata = yaml.load(stream)
    return filedata

def parse_header(events, dirname):
    dirname = dirname.split("/")[-1]
    events_dict = dict([(key,d[key]) for d in events for key in d])
    header = events_dict.get(dirname,None)
    return header

def make_index():
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    env = Environment(loader=TEMPLATE_LOADER)
    template = env.get_template('index.html')
    events = parse_events_yml()
    output_from_parsed_template = template.render(events=events)
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as fh:
        print('Writing out', fh.name)
        fh.write(output_from_parsed_template)
    # Copy logo to HTML folder_name
    shutil.copy(os.path.join('images',LOGO_FILE), os.path.join(OUTPUT_DIR, LOGO_FILE))

    return

def collect_data(folder_name, template_data):
    files = glob.glob(os.path.join(folder_name, "*.yml"))
    data = []
    for yfile in files:
        stream = open(yfile, 'r')
        filedata = yaml.load(stream)
        cleaned_data = parse_yaml_style(filedata, template_data)
        data.append(cleaned_data)
    return data

def load_yaml_style():
    stream = open(YAML_TEMPLATE, 'r')
    tmpl_data = yaml.load(stream)
    return tmpl_data

def parse_yaml_style(data,template):
    for k, v in template.items():
        if not data.get(k,''):
            data[k] = ''
    # Catch the case where images and creators are not lists
    if type(data['creators']) == str:
        data['creators'] = [data['creators']]
    if type(data['images']) == str:
        data['images'] = [data['images']]
    return data

def render_page_data(header, hacks_data, dirname):
    data = dict()
    env = Environment(loader=TEMPLATE_LOADER)
    template = env.get_template('page.html')
    events = parse_events_yml()
    data['events'] = events
    data['header'] = header
    data['event'] = dirname
    data['hacks'], fromimgs, toimgs = reprocess_image_names(hacks_data, dirname)

    output_from_parsed_template = template.render(**data )
    output_from_parsed_template.replace("–", " ")

    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    with open(os.path.join(OUTPUT_DIR, dirname) + ".html", "w") as fh:
        print('Writing out', fh.name)
        fh.write(output_from_parsed_template)

    for fromimg, toimg in zip(fromimgs, toimgs):
        toimg = os.path.join(OUTPUT_DIR, toimg)
        print('Copying', fromimg, 'to', toimg)
        shutil.copy(fromimg, toimg)
    return

def reprocess_image_names(hacks_data, dirname):
    newdata = []
    fromcpys = []
    tocpys = []
    for hack in hacks_data:
        newhack = copy.copy(hack)
        newimages = []
        for imgname in hack['images']:
            if imgname.startswith('http'):
                newimages.append(imgname)
            elif imgname != '':
                newimages.append('{}_{}'.format(dirname, imgname))
            if imgname != '' and not imgname.startswith('http'):
                fromcpys.append(os.path.join(dirname, imgname))
                tocpys.append(newimages[-1])
        newhack['images'] = newimages
        newdata.append(newhack)
    return newdata, fromcpys, tocpys


if __name__ == '__main__':
    runner()
