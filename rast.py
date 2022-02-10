"""
RaST - Rapid Subdomains Take Over
Taking control over AWS subdomains with "NoSuchBucket" error.
Author: Higor Melgaço
Date: 07/02/2022
"""

from tqdm import tqdm
from time import sleep
from colorama import Fore
from boto3 import client as boto3_client
from traceback import format_exc as print_traceback
from argparse import ArgumentParser, SUPPRESS, HelpFormatter


messages = {
    "logs": {
        "start": "{}[{}>{}] ~ RaST started!",
        "done": "{}[{}>{}] ~ RaST finished!",
        "key_interrupt": "{}[{}!{}] ~ Well, it looks like someone interrupted the execution...",
        "error": "{}[{}!{}] ~ An error occurred: {}{}"
    },
    "argparser": {
        'desc_general': 'RaST - Rapid Subdomains Take Over: Taking control over AWS subdomains with "NoSuchBucket" error.',
        'address': 'A single subdomain url to take control',
        'file': 'A file with subdomains urls to take control',
        'take_over': 'Creates the buckets with the name contained in the "NoSuchBucket" error and uploads a file to evidence the PoC',
        'clear_s3': 'Clears all the buckets in the AWS account used',
        'help': 'Show this help message and exit.'
    },
    "logo": r'''
    {}
                   (
                   )
                   (                 
            /\  .-"""-.  /\          *--------------------------------------* 
           //\\/  ,,,  \//\\         |   {}RaST - Rapid Subdomains Take Over{}  |
           |/\| ,;;;;;, |/\|         |  {}Taking control over AWS subdomains{}  |
           //\\\;-"""-;///\\         *--------------------------------------*
          //  \/       \/  \\        |        {}eremit4@protonmail.com{}        | 
         (| ,-_|       |_-, |)       |              {}SP/Brazil{}               |
           //`__\.-.-./__`\\         *--------------------------------------*
          // /.-({}O{}\ /{}O{})-.\ \\
         (\ |)   '---'   (| /)
          ` (|           |) `
            \)           (/

    '''
}


class CustomHelpFormatter(HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=50, width=100)

    def format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super().format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ', '.join(action.option_strings) + ' ' + args_string


def main(arguments: ArgumentParser.parse_args) -> None:
    """
    Execute the main function.
    :param arguments: The arguments typed on the CLI.
    :return: None.
    """
    print(messages["logs"]["start"].format(Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX))
    s3_client = boto3_client("s3")
    print(messages["logs"]["mission_done"].format(Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX))


if __name__ == "__main__":
    arg_style = lambda prog: CustomHelpFormatter(prog)
    args = ArgumentParser(description=messages["argparser"]["desc_general"], add_help=False, formatter_class=arg_style)
    group_required = args.add_argument_group(title="required arguments")
    group_required.add_argument("-a", "--address", metavar="address", type=str, help=messages["argparser"]["address"])
    group_required.add_argument("-f", "--file", metavar="file", type=str, help=messages["argparser"]["file"])
    group_required.add_argument("-t", "--take-over", metavar="takeover", help=messages["argparser"]["take_over"])
    group_required.add_argument("-c", "--clear-buckets", metavar="clear", help=messages["argparser"]["clear_s3"])
    group_optional = args.add_argument_group(title="optional arguments")
    group_optional.add_argument("-h", "--help", help=messages["argparser"]["help"], action="help", default=SUPPRESS)

    try:
        print(messages['logo'].format(Fore.LIGHTWHITE_EX,
                                      Fore.RED,
                                      Fore.LIGHTWHITE_EX,
                                      Fore.RED,
                                      Fore.LIGHTWHITE_EX,
                                      Fore.RED,
                                      Fore.LIGHTWHITE_EX,
                                      Fore.RED,
                                      Fore.LIGHTWHITE_EX,
                                      Fore.LIGHTRED_EX,
                                      Fore.LIGHTWHITE_EX,
                                      Fore.LIGHTRED_EX,
                                      Fore.LIGHTWHITE_EX))
        main(args.parse_args())
    except KeyboardInterrupt:
        print(messages["logs"]["key_interrupt"].format(Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX))
    except Exception:
        print(messages["logs"]["error"].format(Fore.LIGHTWHITE_EX,
                                               Fore.LIGHTRED_EX,
                                               Fore.LIGHTWHITE_EX,
                                               Fore.LIGHTRED_EX,
                                               print_traceback()))
    print(messages["logs"]["done"].format(Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX))
