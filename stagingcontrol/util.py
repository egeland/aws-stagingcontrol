from boto.exception import EC2ResponseError
import sys, os

def is_running(instance):
    """(EC2 instance) -> bool
    
    Check if the instance supplied is running, returning True iif it is, or False otherwise"""
    return u'running' == instance.state

def prompt_for_confirmation(args):
    """Interactive confirmation prompt"""
    
    if args.stop:
        detail = "STOPPING"
    else:
        detail = "starting up"
    print "Are you sure you want to proceed with the {0} of every instance in the list? (yes|[no]) ".format(detail),
    answer = sys.stdin.readline()
    answer = answer.strip().lower()
    if 0 == len(answer):
        answer = 'n'
    answer = answer[0]
    print ""
    if 'y' != answer:
        print "Aborting on user request"
        sys.exit(1)
    return True

def set_aws_credentials(aws_id_file):
    """
    Parse credentials file and set environment variables

    Access keys need to be supplied in a credentials file.
    The file may simply contain, for example:

    aws_id file example
    -------------------
    AWSAccessKeyId=ATEST2AWS4EXAMPLE12K
    AWSSecretKey=THISISYOURB1GSECrectKey4AWSacc35sExample
    """

    try:
        with open(aws_id_file) as fh:
            for line in fh.readlines():
                line = line.strip()
                if '' == line:
                    continue
                line = line.split('=')
                if 'access' in line[0].lower():
                    os.environ['AWS_ACCESS_KEY_ID'] = line[1]
                elif 'secret' in line[0].lower():
                    os.environ['AWS_SECRET_ACCESS_KEY'] = line[1]
        os.environ['AWS_CREDENTIAL_FILE'] = aws_id_file
    except Exception:
        if None != os.getenv('AWS_ACCESS_KEY_ID'):
            print "No AWS identity file found - relying on environment variables"
        else:
            print "No AWS identity found - no file or environment variable.\nAborting."
            sys.exit(1)

