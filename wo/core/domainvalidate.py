"""WordOps domain validation module."""
import os


class WODomain:
    """WordOps domain validation utilities"""

    def validate(self, url):
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
            return final_domain
        return domain_name

    def getlevel(self, domain):
        """
            Returns the domain type : domain, subdomain and the root domain
        """
        domain_name = domain.lower().strip().split('.')
        if domain_name[0] == 'www':
            domain_name = domain_name[1:]
        domain_type = ''
        if os.path.isfile("/var/lib/wo/public_suffix_list.dat"):
            # Read mode opens a file for reading only.
            suffix_file = open(
                "/var/lib/wo/public_suffix_list.dat", encoding='utf-8')
            # Read all the lines into a list.
            for domain_suffix in suffix_file:
                if (str(domain_suffix).strip()) == ('.'.join(domain_name[1:])):
                    domain_type = 'domain'
                    break
                else:
                    domain_type = 'subdomain'
            suffix_file.close()
        if domain_type == 'domain':
            root_domain = ('.'.join(domain_name[0:]))
        else:
            root_domain = ('.'.join(domain_name[1:]))
        return (domain_type, root_domain)
