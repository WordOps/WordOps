"""WordOps domain validation module."""
from urllib.parse import urlparse
import os


def ValidateDomain(url):
    """
        This function returns domain name removing http:// and https://
        returns domain name only with or without www as user provided.
    """

    # Check if http:// or https://  present remove it if present
    domain_name = url.split('/')
    if 'http:' in domain_name or 'https:' in domain_name:
        domain_name = domain_name[2]
    else:
        domain_name = domain_name[0]
    www_domain_name = domain_name.split('.')
    final_domain = ''
    if www_domain_name[0] == 'www':
        final_domain = '.'.join(www_domain_name[1:])
    else:
        final_domain = domain_name

    return (final_domain, domain_name)


def GetDomainlevel(domain):
    """
        This function returns the domain type : domain, subdomain,
    """
    domain_name = domain.split('.').lower()
    if domain_name[0] == 'www':
        domain_name = domain_name[1:]
    domain_type = ''
    if os.path.isfile("/var/lib/wo/public_suffix_list.dat"):
        # Read mode opens a file for reading only.
        Suffix_file = open(
            "/var/lib/wo/public_suffix_list.dat", encoding='utf-8', )
        # Read all the lines into a list.
        for domain_suffix in Suffix_file:
            if (str(domain_suffix).strip()) == ('.'.join(domain_name[1:])):
                domain_type = 'domain'
                root_domain = ('.'.join(domain_name[0:]))
                break
            elif (str(domain_suffix).strip()) == ('.'.join(domain_name[2:])):
                domain_type = 'subdomain'
                root_domain = ('.'.join(domain_name[1:]))
                break
            else:
                domain_type = 'other'
        Suffix_file.close()

    return (domain_type, root_domain)
