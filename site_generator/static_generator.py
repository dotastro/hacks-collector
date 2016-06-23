import yaml
from jinja2 import Environment, FileSystemLoader, Undefined
import glob
import os
from markdown2 import Markdown
import logging


DATA_DIR_PATTERN = 'dotastro*'
README_NAME = 'README.md'

OUTPUT_DIR = 'site_generator/html'

TEMPLATE_LOADER = FileSystemLoader('site_generator/templates')

class SilentUndefined(Undefined):
    '''
    Dont break pageloads because vars arent there!
    '''
    def _fail_with_undefined_error(self, *args, **kwargs):
        logging.exception('JINJA2: something was undefined!')
        return None

def runner():
    pages = []
    for dirname in glob.glob(DATA_DIR_PATTERN):
        if os.path.isdir(dirname):
            header = render_markdown(os.path.join(dirname, README_NAME))
            data = collect_data(dirname)
            render_page_data(header, data, dirname)
            pages.append(dirname)
    make_index(pages)
    return

def make_index(pages):
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    env = Environment(loader=TEMPLATE_LOADER)
    template = env.get_template('index.html')
    output_from_parsed_template = template.render(pages=pages)
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as fh:
        print('Writing out', fh.name)
        fh.write(output_from_parsed_template)
    return

def render_markdown(readme):
    readme_file = open(readme, 'r')
    md = Markdown()
    header = md.convert(readme_file.read())
    return header

def collect_data(folder_name):
    files = glob.glob(os.path.join(folder_name, "*.yml"))
    data = []
    for yfile in files:
        stream = open(yfile, 'r')
        filedata = yaml.load(stream)
        data.append(filedata)
    return data

def render_page_data(header, data, dirname):
    env = Environment(loader=TEMPLATE_LOADER)
    template = env.get_template('page.html')
    output_from_parsed_template = template.render(header=header, pages=data, event=dirname )
    output_from_parsed_template.replace("–", " ")

    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    with open(os.path.join(OUTPUT_DIR, dirname) + ".html", "w") as fh:
        print('Writing out', fh.name)
        fh.write(output_from_parsed_template)

if __name__ == '__main__':
    runner()
