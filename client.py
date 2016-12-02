import base64
import argparse
import os
import stat
import time
import sys

WAIT = 1
ENDING_CHAR = b'|'
PERMISSIONS = (
    stat.S_IRUSR,
    stat.S_IWUSR,
    stat.S_IXUSR,

    stat.S_IRGRP,
    stat.S_IWGRP,
    stat.S_IXGRP,

    stat.S_IROTH,
    stat.S_IWOTH,
    stat.S_IXOTH,
)


def write_message(send_message):
    """Send a message through the permissions of a file"""

    print('[*]Waiting for receiver...')
    while os.path.getsize(file_path) == 0:
        time.sleep(WAIT)

    print('[+]Starting transmission')

    b64_message = base64.b64encode(send_message) + ENDING_CHAR
    for char_i, char in enumerate(b64_message):

        bin_char = bin(char)[2:]
        bin_char = '0'*(8-len(bin_char)) + bin_char

        permission_mask = stat.S_IRUSR if char_i % 2 == 1 else 0
        for bit_i, bit in enumerate(bin_char):

            if bit == '1':
                permission_mask |= PERMISSIONS[bit_i + 1]

        os.chmod(file_path, permission_mask)
        time.sleep(WAIT)


def read_message():
    """Read a message through the permissions of a file"""

    print('[*]Writing start sign')
    with open(file_path, 'w') as h_file:
        h_file.write('1')

    print('[*]Reading message')
    message_read = ''

    while message_read == '' or message_read[-1] != '|':
        permissions = os.stat(file_path).st_mode

        if len(message_read) % 2 == int(bool(permissions & stat.S_IRUSR)):
            bin_char = ''
            for permission_mask in PERMISSIONS[2:]:

                if bool(permissions & permission_mask):
                    bin_char += '1'
                else:
                    bin_char += '0'

            message_read += chr(int(bin_char, 2))
            print('[*]Got char: {}'.format(message_read[-1]))

    return base64.b64decode(message_read).decode("utf-8")

argument_parser = argparse.ArgumentParser('File permission covert channel')

argument_parser.add_argument('mode',
                             metavar='read/write',
                             type=str,
                             choices=('r', 'w', 'read', 'write'),
                             help='',
                             )

argument_parser.add_argument('-m', '--message',
                             metavar='string',
                             type=str,
                             help='The message to send. (if mode is "write")',
                             )

argument_parser.add_argument('-f', '--file',
                             metavar='filename',
                             type=str,
                             default='test.lock',
                             help='',
                             )


arguments = argument_parser.parse_args()

file_path = os.path.join('/tmp/', arguments.file)
mode = 'write' if arguments.mode in ('w', 'write') else 'read'

if mode == 'write' and arguments.message is None:
    print('[!]Message is required with mode "write".'.format(file_path))
    sys.exit()

if mode == 'write' and os.path.exists(file_path):
    print('[!]{} exists.'.format(file_path))
    sys.exit()

if mode == 'read' and not os.path.exists(file_path):
    print('[!]{} does not exist.'.format(file_path))
    sys.exit()

if mode == 'write':

    message = arguments.message.encode('utf-8')

    print('[*]Creating file')
    open(file_path, 'w').close()
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IWOTH)

    write_message(message)

    print('[+]Message sent')
    print('[*]Removing file')
    os.remove(file_path)

else:
    message = read_message()
    print('[+]Read: {}'.format(message))
