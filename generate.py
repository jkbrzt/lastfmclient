#!/usr/bin/env python
import sys
import json
import textwrap
from io import StringIO
from collections import defaultdict
from datetime import datetime

import requests
from lxml import etree


def now():
    return datetime.utcnow().isoformat() + 'Z'


def generate_spec(root='http://www.last.fm'):
    """
    Generate structured JSON with description of all the endpoints
    listed on http://www.last.fm/api/intro.

    It crawlers the documentation pages and extracts resource names,
    parameter types, etc.

    """

    def get_doc(path):
        return etree.fromstring(
            requests.get(root + path).text.replace('<=', '&lt;='),
            parser=etree.HTMLParser()
        )

    paths = get_doc('/api/intro').xpath(
        '//a[starts-with(@href, "/api/show")]/@href')

    spec = defaultdict(dict)
    spec['__generated__'] = now()

    requires_auth = None

    for path in paths:

        sys.stderr.write(path + '\n')

        params = {}
        doc = get_doc(path)
        package, method = path.split('/')[-1].split('.')

        for param, desc in zip(
            doc.xpath('//div[@id="wsdescriptor"]/span[@class="param"]'),
            doc.xpath('//div[@id="wsdescriptor"]'
                      '/span[@class="param"]/following-sibling::text()[1]')
        ):
            if not param.text:
                # <span class="param"></span>  <br />
                continue

            name = param.text.strip()

            requires_auth = not doc.xpath('contains(normalize-space(/), '
                                          '"does not require authentication")')

            if name in {'api_key', 'api_sig', 'sk'}:
                if name == 'sk':
                    assert requires_auth
                continue

            boolean = False
            multiple = False
            brackets = ''

            if '[' in name:
                i = name.index('[')
                brackets = name[i:]
                name = name[:i]
                if brackets == '[0|1]':
                    boolean = True
                elif brackets in ['[i]', '[1|2]']:
                    multiple = True
                else:
                    pass
                brackets += ' '

            params[name] = {
                'description': brackets + ' '.join(desc.split()),
                'required': 'Required' in desc,
                'boolean': boolean,
                'multiple': multiple,
            }

        desc = ' '.join(
            doc.xpath('string(//div[@class="wsdescription"])').strip().split())

        spec[package][method] = {
            'documentation': root + path,
            'description': desc,
            'auth': requires_auth,
            'http': (
                'POST' if doc.xpath('contains(normalize-space(/),'
                                    ' "HTTP POST request")')
                else 'GET'
            ),
            'params': params
        }

    print json.dumps(spec, indent=4, sort_keys=True)


def generate_code(specfile='api.json'):
    """Take a path to a spec file and generate the actual Python code."""

    spec = json.load(open(specfile))
    del spec['__generated__']

    out = StringIO()
    out.write(u'# Generated code. Do not edit.\n')
    out.write(u'# %s\n' % now())
    out.write(u'from .package import Package\n\n\n')

    packages = sorted(spec.keys())

    out.write(u'class BaseClient(object):\n\n')
    out.write(u'    def __init__(self):\n')
    for package in packages:
        out.write(u'        self.%s = %s(self)\n' % (
            package, package.capitalize())
        )
    out.write(u'\n\n')

    for package in packages:

        out.write(u'class %s(Package):\n\n' % package.capitalize())

        for method in sorted(spec[package].keys()):
            method_spec = spec[package][method]
            args, doc, call = args_doc_call(method, method_spec)
            out.write(u'    def %s(%s):\n%s\n%s' % (
                uncamel(method),
                args,
                doc,
                call
            ))
            out.write(u'\n')
    print out.getvalue()


def prefix(text, p='    '):
    return '\n'.join((p + line) for line in text.splitlines())


def uncamel(name):
    """helloWorld => hello_world"""
    n = ''
    for c in name:
        if c.isupper():
            n += '_' + c.lower()
        else:
            n += c
    return n


def args_doc_call(method_name, spec):
    """Return args code, docstring, and call code."""

    def make_safe(name):
        if name in {'from', }:
            return name + '_'
        return name

    def q(s):
        return "'%s'" % s

    params = spec['params']
    safe = {name: make_safe(name) for name in params}
    required = [safe[name] for name in params if params[name]['required']]
    optional = [safe[name] for name in params if not params[name]['required']]

    params = sorted(required)
    for name in optional:
        params.append(name + '=None')
    args = ', '.join(['self'] + params)

    doc = [
        '"""',
    ] + textwrap.wrap(spec['description']) + [
        '',
        ('Authorization required.'
         if spec['auth']
         else 'Authorization not required.'),
        '',
        spec['documentation'],
        '',
    ]

    for name in sorted(required) + sorted(optional):
        param = spec['params'][name.rstrip('_')]

        type_spec = ['required' if param['required'] else 'optional']
        if param['multiple']:
            type_spec.append('multiple')
        if param['boolean']:
            type_spec.append('boolean')

        doc.append(':param %s: %s' % (
            name,
            ', '.join(type_spec))
        )
        doc.extend('    ' + line for line
                   in textwrap.wrap(param['description']))

    doc.append('\n"""\n')

    doc = prefix('\n'.join(doc), ' ' * 8)

    call = '%sreturn self._call(%s)\n' %(
        ' ' * 8,
        ', '.join([q(spec['http']), q(method_name), 'auth=%s' % spec['auth']] +
                  [name + '=' + name
                   for name in
                   sorted(required) + sorted(optional)])
    )
    return args, doc, call


if __name__ == '__main__':
    {
        'spec': generate_spec,
        'code': generate_code
    }[sys.argv[1]]()
