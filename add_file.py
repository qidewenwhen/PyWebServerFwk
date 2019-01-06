import os

root_path = os.getcwd()

directory_list = [
        'dbconnector',
        'exceptions',
        'helper',
        'route',
        'session',
        'template_engine',
        'view',
        'wsgi_adapter'
]

children = {'name': '__init__.py', 'children': None, 'type': 'file'}

dir_map = [{
    'name': 'PyFwk',
    'children': [{
        'name': directory,
        'type': 'dir',
        'children': [children]
    } for directory in directory_list] + [children],
    'type': 'dir'
}]

def create(path, kind):
    if kind == 'dir':
        os.mkdir(path)
    else:
        open(path, 'w').close()

def gen_project(parent_path, map_obj):
    for line in map_obj:
        path = os.path.join(parent_path, line['name'])
        create(path, line['type'])
        if line['children']:
            gen_project(path, line['children'])

def main():
    gen_project(root_path, dir_map)

if __name__ == '__main__':
    main()
