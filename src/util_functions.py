""" Utility functions for gr_modtool.py """

import re
import sys

### Utility functions ########################################################
def get_command_from_argv(possible_cmds):
    """ Read the requested command from argv. This can't be done with optparse,
    since the option parser isn't defined before the command is known, and
    optparse throws an error."""
    command = None
    for arg in sys.argv:
        if arg[0] == "-":
            continue
        else:
            command = arg
        if command in possible_cmds:
            return arg
    return None

def append_re_line_sequence(filename, linepattern, newline):
    """Detects the re 'linepattern' in the file. After its last occurrence,
    paste 'newline'. If the pattern does not exist, append the new line
    to the file. Then, write. """
    oldfile = open(filename, 'r').read()
    lines = re.findall(linepattern, oldfile, flags=re.MULTILINE)
    if len(lines) == 0:
        open(filename, 'a').write(newline)
        return
    last_line = lines[-1]
    newfile = oldfile.replace(last_line, last_line + newline + '\n')
    open(filename, 'w').write(newfile)

def remove_pattern_from_file(filename, pattern):
    """ Remove all occurrences of a given pattern from a file. """
    oldfile = open(filename, 'r').read()
    pattern = re.compile(pattern, re.MULTILINE)
    open(filename, 'w').write(pattern.sub('', oldfile))

def str_to_fancyc_comment(text):
    """ Return a string as a C formatted comment. """
    l_lines = text.splitlines()
    outstr = "/* " + l_lines[0] + "\n"
    for line in l_lines[1:]:
        outstr += " * " + line + "\n"
    outstr += " */\n"
    return outstr

def str_to_python_comment(text):
    """ Return a string as a Python formatted comment. """
    return re.compile('^', re.MULTILINE).sub('# ', text)

def strip_default_values(string):
    """ Strip default values from a C++ argument list. """
    return re.sub(' *=[^,)]*', '', string)

def strip_arg_types(string):
    """" Strip the argument types from a list of arguments
    Example: "int arg1, double arg2" -> "arg1, arg2" """
    string = strip_default_values(string)
    return ", ".join([part.strip().split(' ')[-1] for part in string.split(',')])

def get_modname():
    """ Grep the current module's name from gnuradio.project or CMakeLists.txt """
    modname_trans = {'howto-write-a-block': 'howto'}
    try:
        prfile = open('gnuradio.project', 'r').read()
        regexp = r'projectname\s*=\s*([a-zA-Z0-9-_]+)$'
        return re.search(regexp, prfile, flags=re.MULTILINE).group(1).strip()
    except IOError:
        pass
    # OK, there's no gnuradio.project. So, we need to guess.
    cmfile = open('CMakeLists.txt', 'r').read()
    regexp = r'(project\s*\(\s*|GR_REGISTER_COMPONENT\(")gr-(?P<modname>[a-zA-Z0-9-_]+)(\s*(CXX)?|" ENABLE)'
    try:
        modname = re.search(regexp, cmfile, flags=re.MULTILINE).group('modname').strip()
        if modname in modname_trans.keys():
            modname = modname_trans[modname]
        return modname
    except AttributeError:
        return None

def get_class_dict():
    " Return a dictionary of the available commands in the form command->class "
    classdict = {}
    for g in globals().values():
        try:
            if issubclass(g, ModTool):
                classdict[g.name] = g
                for a in g.aliases:
                    classdict[a] = g
        except (TypeError, AttributeError):
            pass
    return classdict

def is_number(s):
    " Return True if the string s contains a number. "
    try:
        float(s)
        return True
    except ValueError:
        return False

def xml_indent(elem, level=0):
    """ Adds indents to XML for pretty printing """
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            xml_indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def ask_yes_no(question, default):
    """ Asks a binary question. Returns True for yes, False for no.
    default is given as a boolean. """
    question += {True: ' [Y/n] ', False: ' [y/N] '}[default]
    if raw_input(question).lower() != {True: 'n', False: 'y'}[default]:
        return default
    else:
        return not default
