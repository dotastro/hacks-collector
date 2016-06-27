import yaml
from jinja2 import Environment, FileSystemLoader, Undefined
import glob
import os
from markdown2 import Markdown
import logging


DATA_DIR_PATTERN = 'dotastro*'
README_NAME = 'README.md'
YAML_TEMPLATE = 'template.yml'
EVENTS_FILE = 'site_generator/events.yml'

OUTPUT_DIR = 'site_generator/html'

TEMPLATE_LOADER = FileSystemLoader('site_generator/templates')

def runner():
    pages = []
    template_data = load_yaml_style()
    for dirname in glob.glob(DATA_DIR_PATTERN):
        if os.path.isdir(dirname):
            header = render_markdown(os.path.join(dirname, README_NAME))
            cleaned_data = collect_data(dirname, template_data)
            render_page_data(header, cleaned_data, dirname)
            pages.append(dirname)
    make_index()
    return

def parse_events_yml():
    stream = open(EVENTS_FILE, 'r')
    filedata = yaml.load(stream)
    return filedata

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
    return

def render_markdown(readme):
    readme_file = open(readme, 'r')
    md = Markdown()
    header = md.convert(readme_file.read())
    return header

def collect_data(folder_name, template_data):
    files = glob.glob(os.path.join(folder_name, "*.yml"))
    data = []
    for yfile in files:
        stream = open(yfile, 'r')
        filedata = yaml.load(stream)
        cleaned_data = parse_yaml_style(filedata,template_data)
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

def render_page_data(header, data, dirname):
    data = dict()
    env = Environment(loader=TEMPLATE_LOADER)
    template = env.get_template('page.html')
    data['header'] = header
    data['event'] = dirname
    data['hacks'] = data
    output_from_parsed_template = template.render(**data )
    output_from_parsed_template.replace("–", " ")

    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    with open(os.path.join(OUTPUT_DIR, dirname) + ".html", "w") as fh:
        print('Writing out', fh.name)
        fh.write(output_from_parsed_template)
    return


if __name__ == '__main__':
    runner()
