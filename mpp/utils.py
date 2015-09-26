import subprocess


def validate_in_memory(xml):
    cmd = 'StdInParse -v=always -n -s -f'
    s = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # we need stderr from pparse/stdinparse to actually catch the errors
    stdout, stderr = s.communicate(input=xml)
    ret = s.wait()
    return stderr


def transform_xml_in_memory(xml, xslt_path, params):
    param_str = convert_to_xslt_params(params)
    cmd = 'saxonb-xslt -s:- -xsl:%s %s' % (xslt_path, param_str)
    s = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    output = s.communicate(input=xml.encode('utf-8'))[0]
    ret = s.wait()
    return output


def transform_xml_file(xml_file, xslt_path, params):
    param_str = convert_to_xslt_params(params)
    cmd = 'saxonb-xslt -s:%s -xsl:%s %s' % (xml_file, xslt_path, param_str)
    s = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    output = s.communicate()[0]
    ret = s.wait()
    return output


def convert_to_xslt_params(params):
        return ' '.join(
            ['%s=%s' % (p, params[p] if ' ' not in params[p]
                    else '"%s"' % params[p]
                ) for p in params
            ]
        )
