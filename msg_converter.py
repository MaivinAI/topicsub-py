from pathlib import Path
import sys
import os

def main(file):
    builtin_types = ['float32', 'float64', 
                     'int8', 'int16', 'int32', 'int64',
                     'uint8', 'uint16', 'uint32', 'uint64',
                     'string', 'bool']
    type_defaults = {'float32': '0', 'float64': '0',
                     'int8': '0', 'int16': '0', 'int32': '0', 'int64': '0',
                     'uint8': '0', 'uint16': '0', 'uint32': '0', 'uint64': '0',
                    'string': "''",
                    'str': "''",
                    'bool': 'False'}
    
    available_msgs = []
    additional_deps = []
    parent_directory = Path(file).parent
    for msg_file in os.listdir(parent_directory):
        if msg_file.endswith('.py'):
            python_class = msg_file[:msg_file.find('.py')]
            available_msgs.append(python_class)
            type_defaults[python_class] = '%s()' % python_class

    messages = {}
    reliance = {}
    used_builtin_types = []
    created_types = []
    lists_used = False
    sequences_used = False
    main_msg = Path(file).name
    main_msg = main_msg[:main_msg.rfind('.')]
    messages[main_msg] = []
    reliance[main_msg] = []
    lines = []

    with open(file, 'r') as f:
        for line in f.readlines():
            if line[0] =='\n' or line.lstrip()[0] in ['#', '=']:
                continue
            lines.append(line)

    current_msg = main_msg
    for line in lines:
        if line.startswith('MSG: '):
            current_msg = line[5:]
            current_msg = current_msg.replace('\n', '')
            if '/' in current_msg:
                current_msg = current_msg[current_msg.rfind('/')+1:]
            messages[current_msg] = []
            reliance[current_msg] = []
            continue

        comment = None
        line = line.strip().replace('\n', '')
        if '#' in line:
            comment = line[line.find('#'):]
            line = line[:line.find('#')]
        components = line.strip().split(' ')
        while '' in components:
            components.remove('')
        if len(components) == 1:
            raise ValueError(".msg file not formatted correctly")
        
        default_value = None
        array_length = None
        datatype = components[0].replace('\n', '')
        if '/' in datatype:
            datatype = datatype[datatype.rfind('/')+1:]
        if '[' in datatype:
            if datatype.find('[') + 1 == datatype.find(']'):
                sequences_used = True
                array_length = -1
            else:
                lists_used = True
                array_length = int(datatype[datatype.find('[')+1:datatype.find(']')])
            datatype = datatype[:datatype.find('[')]

        name = components[1].replace('\n', '')
        if len(components) == 3:
            default_value = components[2].replace('\n', '')
        messages[current_msg].append([datatype, name, default_value, array_length, comment])

        if datatype not in builtin_types:
            if datatype in available_msgs and datatype not in additional_deps:
                additional_deps.append(datatype)
            elif datatype not in reliance[current_msg]:
                reliance[current_msg].append(datatype)
        else:
            if datatype not in used_builtin_types:
                used_builtin_types.append(datatype)

    new_python_file = file.replace('.msg', '.py')
    f = open(new_python_file, 'w')
    f.write('from dataclasses import dataclass, field\n')
    f.write('import copy\n')
    f.write('from pycdr2 import IdlStruct\n')
    if lists_used:
        used_builtin_types.append('array')
    if sequences_used:
        used_builtin_types.append('sequence')
    if len(used_builtin_types) != 0:
        f.write('from pycdr2.types import ')
        for i in range(len(used_builtin_types)):
            if i == len(used_builtin_types) - 1:
                if used_builtin_types[i] in ['bool', 'string']:
                    f.write('\n')
                else:
                    f.write(used_builtin_types[i] + '\n')
            else:
                if used_builtin_types[i] not in ['bool', 'string']:
                    f.write(used_builtin_types[i] + ', ')

    if additional_deps:
        for dep in additional_deps:
            f.write("from %s import %s\n" % (dep, dep))
    
    f.write('\n')
    f.write('def default_field(obj):\n')
    f.write('    return field(default_factory=lambda: copy.copy(obj))\n')
    f.write('\n')

    while True:
        if len(messages) == 0:
            break

        created_msgs = []
        found_msg = False
        for key, val in messages.items():
            if len(reliance[key]) != 0:
                continue
            found_msg = True
            message_name = key.replace('\\', '_').replace('/', '_')
            f.write('@dataclass\n')
            f.write("class %s(IdlStruct, typename='%s'):\n" % (message_name, key))
            # [datatype, name, default_value, array_length, comment]
            for i in range(len(val)):
                if val[i][0] == 'string':
                    val[i][0] = 'str'
                f.write("    %s: " % val[i][1])
                if val[i][3] is None:
                    if val[i][2] is None:
                        f.write("%s = %s" % (val[i][0], type_defaults[val[i][0]]))
                    else:
                        f.write("%s = %s" % (val[i][0], val[i][2]))
                else:
                    # Sequences Support
                    if val[i][3] == -1:
                        f.write('sequence[%s] = default_field([])' % val[i][0])
                    # Lists support
                    else: 
                        f.write('array[%s, %d] = ' % (val[i][0], val[i][3]))
                        if val[i][2] is None:
                            val[i][2] = '[%s] * %d' % (type_defaults[val[i][0]], val[i][3])
                        f.write("default_field(%s)" % val[i][2])
                
                # Add comment
                if val[i][4] is None:
                    f.write('\n')
                else:
                    f.write(' %s\n' % val[i][4])
            f.write('\n')
            for rel_key, rel_val in reliance.items():
                if key in rel_val:
                    rel_val.remove(key)
            created_msgs.append(key)
            created_types.append(message_name)
            type_defaults[message_name] = message_name + '()'

            for _, update_val in messages.items():
                for i in range(len(update_val)):
                    if update_val[i][0] == key:
                        update_val[i][0] = message_name

        if not found_msg:
            print(reliance)
            raise ValueError("Unable to determine all types")
        for c_msg in created_msgs:
            del messages[c_msg]
            del reliance[c_msg]

    f.close()
    

if __name__ == '__main__':
    file = sys.argv[1:][0]
    main(file)