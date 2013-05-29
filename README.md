# Staging Control #
This is a script to help start and stop EC2 instances.

It parses and validates a list of instance IDs,
then acts upon the viable candidates from the list, if any.

Any invalid IDs get moved in the list automatically, to a non-actioned section.


## Assumptions ##
The instance IDs listed in the instancelist file are all
staging/UAT/development machines, expected to be powered
off and on automatically.


## Format of instancelist ##
The file with the instance IDs must be a normal config file,
in the .ini style. The script expects (by default) the section
"[Staging]" (no quotes) to be present, with a list of instance IDs
underneath this. An example:
### instancelist example ###
[Staging]  
i-1b3456  
i-234c34  


## AWS Access keys ##
Access keys need to be supplied in a credentials file.
The file may simply contain, for example:
### aws_id file example ###
AWSAccessKeyId=ATEST2AWS4EXAMPLE12K  
AWSSecretKey=THISISYOURB1GSECrectKey4AWSacc35sExample  


