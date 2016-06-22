import yaml
from jinja2 import Environment, FileSystemLoader, Undefined
import glob
import os
from markdown2 import Markdown
import logging


DATA_DIRS = ['dotastro1','dotastro2','dotastro3','dotastro4','dotastro5','dotastro6','dotastro7','dotastro8']

OUTPUT_DIR = 'public'

README_NAME = 'README.md'

class SilentUndefined(Undefined):
    '''
    Dont break pageloads because vars arent there!
    '''
    def _fail_with_undefined_error(self, *args, **kwargs):
        logging.exception('JINJA2: something was undefined!')
        return None

def runner():
    for dirname in DATA_DIRS:
        header = render_markdown(os.path.join(dirname,README_NAME))
        data = collect_data(dirname)
        render_page_data(header, data, dirname)
    return

def make_index():
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
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('page.html')
    output_from_parsed_template = template.render(header=header, pages=data, event=dirname )
    output_from_parsed_template.replace("–", " ")

    with open(os.path.join(OUTPUT_DIR, dirname) + ".html", "w") as fh:
        fh.write(output_from_parsed_template)

    return

if __name__ == '__main__':
    runner()
