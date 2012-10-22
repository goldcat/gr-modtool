''' A parser for blocks written in C++ '''
import re
import sys

### Parser for CC blocks ####################################################
def dummy_translator(the_type, default_v=None):
    """ Doesn't really translate. """
    return the_type

class ParserCCBlock(object):
    """ Class to read blocks written in C++ """
    def __init__(self, filename_cc, filename_h, blockname, type_trans=dummy_translator):
        self.code_cc = open(filename_cc).read()
        self.code_h  = open(filename_h).read()
        self.blockname = blockname
        self.type_trans = type_trans

    def read_io_signature(self):
        """ Scans a .cc file for an IO signature. """
        def _figure_out_vlen(typestr):
            """ From a type identifier, returns the vector length of the block's
            input/out. E.g., for 'sizeof(int) * 10', it returns 10. For
            'sizeof(int)', it returns 1. For 'sizeof(int) * vlen', it returns
            the string vlen. """
            if typestr.find('*') == -1:
                return '1'
            vlen_parts = typestr.split('*')
            for fac in vlen_parts:
                if fac.find('sizeof') != -1:
                    vlen_parts.remove(fac)
            if len(vlen_parts) == 1:
                return vlen_parts[0].strip()
            elif len(vlen_parts) > 1:
                return '*'.join(vlen_parts).strip()
        iosig = {}
        iosig_regex = 'gr_make_io_signature\s*\(\s*([^,]+),\s*([^,]+),\s*([^,]+)\),\s*' + \
                      'gr_make_io_signature\s*\(\s*([^,]+),\s*([^,]+),\s*([^,{]+)\)\)\s*[{,]'
        iosig_match = re.compile(iosig_regex, re.MULTILINE).search(self.code_cc)
        try:
            io_type_re = re.compile('sizeof\s*\(([^)]*)\)')
            iosig['in']  = {'min_ports': iosig_match.groups()[0],
                            'max_ports': iosig_match.groups()[1],
                            'type': self.type_trans(io_type_re.search(iosig_match.groups()[2]).groups()[0]),
                            'vlen': _figure_out_vlen(iosig_match.groups()[2])
                           }
            iosig['out'] = {'min_ports': iosig_match.groups()[3],
                            'max_ports': iosig_match.groups()[4],
                            'type': self.type_trans(io_type_re.search(iosig_match.groups()[5]).groups()[0]),
                            'vlen': _figure_out_vlen(iosig_match.groups()[5])
                           }
        except ValueError:
            print "Error: Can't parse io signatures."
            sys.exit(1)
        return iosig

    def read_params(self):
        """ Read the parameters required to initialize the block """
        make_regex = '(?<=_API)\s+\w+_sptr\s+\w+_make_\w+\s*\(([^)]*)\)'
        make_match = re.compile(make_regex, re.MULTILINE).search(self.code_h)
        # Go through params
        try:
            params = []
            for param in make_match.groups()[0].split(','):
                p_split = param.strip().split('=')
                if len(p_split) == 2:
                    default_v = p_split[1].strip()
                else:
                    default_v = ''
                (p_type, p_name) = [x for x in p_split[0].strip().split() if x != '']
                params.append({'key': p_name,
                               'type': self.type_trans(p_type, default_v),
                               'default': default_v,
                               'in_constructor': True})
        except ValueError:
            print "Error: Can't parse this: ", make_match.groups()[0]
            sys.exit(1)
        return params

if __name__ == "__main__":
    parser = ParserCCBlock('digital_descrambler_bb.cc', 'digital_descrambler_bb.h', 'descrambler_bb')
    print parser.read_io_signature()
    print parser.read_params()

