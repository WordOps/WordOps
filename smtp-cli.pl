#!/usr/bin/perl

#
# Command line SMTP client with SSL, STARTTLS, SMTP-AUTH and IPv6 support.
# Michal Ludvig, 2003-2018
# See http://smtp-cli.logix.cz for details
# and https://github.com/mludvig/smtp-cli for code.
# Thanks to all contributors for ideas and fixes!
#

my $version = "3.9";

#
# ChangeLog:
# * Version 3.9    (2018-04-06)
#   - Don't attempt to use IO::Socket::INET6 with --ipv4.
#
# * Version 3.8    (2017-07-05)
#   - New parameter --local-addr
#   - Support body and attachment reading from non-regular files
#   - Various protocol fixes
#
# * Version 3.7    (2014-11-21)
#   - Support STDIN input with --body-plain=- or --body-html=-
#
# * Version 3.6    (2013-07-11)
#   - Improved compatibility with perl < 5.10 and perl >= 5.18
#   - Added support for more chars in user-part of email address.
#
# * Version 3.5    (2013-05-08)
#   - Improved compliance with SMTP RFC 5321
#   - New parameter --text-encoding
#
# * Version 3.4    (2013-02-05)
#   - Ok, ok, support both File::Type and File::LibMagic
#
# * Version 3.3    (2012-07-30)
#   - Moved from File::Type to File::LibMagic
#     (File::Type is no longer maintained and not available
#      in EPEL for RHEL 6)
#
# * Version 3.2    (2012-06-26)
#   - Fixed syntax error
#
# * Version 3.1    (2012-06-25)
#   - New --add-header, --replace-header and --remove-header options.
#   - Improved compatibility with new IO::Socket::SSL releases.
#
# * Version 3.0    (2012-01-24)
#   - Support for server SSL verification agains CA root cert.
#   - Use "Content-Disposition: attachment" for all attachments
#     unless --attach-inline was used.
#   - No longer default to --server=localhost
#   - Support for --charset=<charset> affecting all text/* parts.
#   - Ensure "To: undisclosed-recipients:;" if sending only to Bcc.
#
# * Version 2.9    (2011-09-02)
#   - Fixed problem when using IPv6 addresses with --server.
#     For example with --server 2001:db8::123 it was connecting
#     to server 2001:db8:: port 123. Fixed now.
#
# * Version 2.8    (2011-01-05)
#   - Added --ssl to support for SSMTP (SMTP over SSL). This is
#     turned on by default when --port=465.
#
# * Version 2.7    (2010-09-08)
#   - Added support for Cc header (--cc=...)
#   - Addressess (From, To, Cc) can now contain a "display name",
#     for example --from="Michal Ludvig <michal@logix.cz>"
#   - Support for --mail-from and --rcpt-to addresses independent
#     on --from, --to, --cc and --bcc
#   - Fixed warnings in Perl 5.12
#
# * Version 2.6    (2009-08-05)
#   - Message building fixed for plaintext+attachment case.
#   - Auto-enable AUTH as soon as --user parameter is used.
#     (previously --enable-auth or --auth-plain had to be used
#      together with --user, that was confusing).
#   - New --print-only parameter for displaying the composed
#     MIME message without sending.
#   - All(?) non-standard modules are now optional.
#   - Displays local and remote address on successfull connect.
#
# * Version 2.5    (2009-07-21)
#   - IPv6 support provided the required modules are
#     available.
#
# * Version 2.1    (2008-12-08)
#   - Make the MIME modules optional. Simply disable
#     the required functionality if they're not available.
#
# * Version 2.0    (2008-11-18)
#   - Support for message building through MIME::Lite,
#     including attachments, multipart, etc.
#
# * Version 1.1    (2006-08-26)
#   - STARTTLS and AUTH support
#
# * Version 1.0
#   - First public version
#
# This program is licensed under GNU Public License v3 (GPLv3)
#

## Require Perl 5.8 or higher -> we need open(.., .., \$variable) construct
require 5.008;

use strict;
use IO::Socket::INET;
use MIME::Base64 qw(encode_base64 decode_base64);
use Getopt::Long;
use Socket qw(:DEFAULT :crlf);

my @valid_encodings = ("7bit", "8bit", "binary", "base64", "quoted-printable");

my ($user, $pass, $host, $port, $addr_family, $localaddr,
    $use_login, $use_plain, $use_cram_md5,
    $ehlo_ok, $auth_ok, $starttls_ok, $ssl, $verbose,
    $hello_host, $datasrc,
    $mail_from, @rcpt_to, $from, @to, @cc, @bcc,
    $missing_modules_ok, $missing_modules_count,
    $subject, $body_plain, $body_html, $charset, $text_encoding, $print_only,
    @attachments, @attachments_inline,
    @add_headers, @replace_headers, @remove_headers,
    $ssl_ca_file, $ssl_ca_path,
    $sock, $built_message);

$host = undef;
$port = 'smtp(25)';
$addr_family = AF_UNSPEC;
$localaddr = undef;
$hello_host = 'localhost';
$verbose = 0;
$use_login = 0;
$use_plain = 0;
$use_cram_md5 = 0;
$starttls_ok = 1;
$ssl = undef;
$auth_ok = 0;
$ehlo_ok = 1;
$missing_modules_ok = 0;
$missing_modules_count = 0;
$charset = undef;
$text_encoding = "quoted-printable";
$print_only = 0;

# Get command line options.
GetOptions (
	'host|server=s' => \$host,
	'port=i' => \$port,
	'4|ipv4' => sub { $addr_family = AF_INET; },
	'6|ipv6' => sub { $addr_family = AF_INET6; },
	'local-addr=s' => \$localaddr,
	'user=s' => \$user, 'password=s' => \$pass,
	'auth-login' => \$use_login,
	'auth-plain' => \$use_plain,
	'auth-cram-md5' => \$use_cram_md5,
	'disable-ehlo' => sub { $ehlo_ok = 0; },
	'force-ehlo' => sub { $ehlo_ok = 2; },
	'hello-host|ehlo-host|helo-host=s' => \$hello_host,
	'auth|enable-auth' => \$auth_ok,
	'disable-starttls|disable-tls|disable-ssl' =>
		sub { $starttls_ok = 0; },
	'ssl' => sub { $ssl = 1 },
	'disable-ssl' => sub { $ssl = 0 },
	'mail-from=s' => \$mail_from,
	'rcpt-to=s' => \@rcpt_to,
	'from=s' => \$from,
	'to=s' => \@to,
	'cc=s' => \@cc,
	'bcc=s' => \@bcc,
	'data=s' => \$datasrc,
	'subject=s' => \$subject,
	'body|body-plain=s' => \$body_plain,
	'body-html=s' => \$body_html,
	'charset=s' => \$charset,
	'text-encoding=s' => \$text_encoding,
	'attachment|attach=s' => \@attachments,
	'attachment-inline|attach-inline=s' => \@attachments_inline,
	'add-header=s' => \@add_headers,
	'replace-header=s' => \@replace_headers,
	'remove-header=s' => \@remove_headers,
	'print-only' => \$print_only,
	'missing-modules-ok' => \$missing_modules_ok,
	'ssl-ca-file=s' => \$ssl_ca_file,
	'ssl-ca-path=s' => \$ssl_ca_path,
	'v|verbose+' => \$verbose,
	'version' => sub { &version() },
	'help' => sub { &usage() } );

#### Try to load optional modules

## IO::Socket::SSL and Net::SSLeay are optional
my $have_ssl = eval { require IO::Socket::SSL; require Net::SSLeay; 1; };
if (not $have_ssl and not $missing_modules_ok) {
	warn("!!! IO::Socket::SSL and/or Net::SSLeay modules are not found\n");
	warn("!!! These modules are required for SSL and STARTTLS support\n");
	$missing_modules_count += 2;
}

## IO::Socket::INET6 and Socket6 are optional
my $socket6 = eval { require IO::Socket::INET6; require Socket6; 1; };
if (not $socket6 and not ($addr_family == AF_INET)) {
	if ($addr_family == AF_INET6) {
		die("!!! IO::Socket::INET6 and Socket6 modules are not found\nIPv6 support is not available\n");
	}
	if (not $missing_modules_ok) {
		warn("!!! IO::Socket::INET6 -- optional module not found\n");
		warn("!!! Socket6 -- optional module not found\n");
		warn("!!! These modules are required for IPv6 support\n\n");
		$missing_modules_count += 2;
	}
}

## MIME::Lite dependency is optional
my $mime_lite = eval { require MIME::Lite; 1; };
if (not $mime_lite and not $missing_modules_ok) {
	warn("!!! MIME::Lite -- optional module not found\n");
	warn("!!! Used for composing messages from --subject, --body, --attachment, etc.\n\n");
	$missing_modules_count++;
}

## File::LibMagic dependency is optional
my $file_libmagic = eval { require File::LibMagic; File::LibMagic->new(); };

## File::Type dependency is optional
## Not needed if File::LibMagic is available
my $file_type = eval { require File::Type; File::Type->new(); };

if (not $file_libmagic and not $file_type and not $missing_modules_ok) {
	warn("!!! Neither File::LibMagic nor File::Type module found.\n");
	warn("!!! Used for guessing MIME types of attachments. Optional.\n\n");
	$missing_modules_count++;
}

## Term::ReadKey dependency is optional
my $have_term_readkey = eval { require Term::ReadKey; 1; };
if (not $have_term_readkey and not $missing_modules_ok) {
	warn("!!! Term::ReadKey -- optional module not found\n");
	warn("!!! Used for hidden reading SMTP password from the terminal\n\n");
	$missing_modules_count++;
}

my $have_hmac_md5 = eval { require Digest::HMAC_MD5; 1; };
if (not $have_hmac_md5 and not $missing_modules_ok) {
	if ($use_cram_md5) {
		die("!!! CRAM-MD5 authentication is not available because Digest::HMAC_MD5 module is missing\n");
	}
	warn("!!! Digest::HMAC_MD5 -- optional module missing\n");
	warn("!!! Used for CRAM-MD5 authentication method\n");
	$missing_modules_count++;
}

## Advise about --missing-modules-ok parameter
if ($missing_modules_count) {
	warn("!!! Use --missing-modules-ok if you don't need the above listed modules\n");
	warn("!!! and don't want to see this message again.\n\n");
}

## Make sure we've got a server name to connect to
if (not defined($host)) {
	if (not $print_only) {
		die("Error: Specify the SMTP server with --server=hostname[:port]\n");
	} else {
		# We're printing to stdout only, let's assign just about any
		# hostname to satisfy the next few tests.
		$host = "localhost";
	}
}

## Make sure the --text-encoding value is valid
if (not grep(/^$text_encoding$/, @valid_encodings))
{
	die ("The --text-encoding value is invalid: $text_encoding\nMust be one of: " . join(', ', @valid_encodings) . "\n");
}

## Accept hostname with port number as host:port
## Either it's a hostname:port or 1.2.3.4:port or [2001:db8::1]:port.
## Don't parse 2001:db8::1 as $host=2001:db8:: and $port=1!
if (($host =~ /^([^:]+):([:alnum:]+)$/) or
    ($host =~ /^\[([[:xdigit:]:]+)\]:([:alnum:]+)$/))
{
	$host = $1;
	$port = $2;
}

## Automatically start in SSL mode if port == 465 (SSMTP)
if (not defined($ssl)) {
	$ssl = ($port == 465);
}

# Extract $mail_from address from $from
if (not defined($mail_from) and defined($from)) {
	$mail_from = &find_email_addr($from) or
		die ("The --from string does not contain a valid email address: $from\n");
}

# Extract @rcpt_to list from @to, @cc and @bcc
if (not @rcpt_to) {
	foreach my $rcpt (@to, @cc, @bcc) {
		my $rcpt_addr = &find_email_addr($rcpt);
		if (not defined($rcpt_addr)) {
			warn("No valid email address found in: $rcpt\n");
			next;
		}
		push(@rcpt_to, $rcpt_addr);
	}
}

# Ensure "To: undisclosed-recipients:;" when sending only to Bcc's
if (not @to and not @cc) {
	push(@to, "undisclosed-recipients:;");
}

# Build the MIME message if required
if (defined($subject) or defined($body_plain) or defined($body_html) or
		@attachments or @attachments_inline) {
	if (not $mime_lite) {
		die("Module MIME::Lite is not available. Unable to build the message, sorry.\n".
		    "Use --data and provide a complete email payload including headers instead.\n");
	}
	if (defined($datasrc)) {
		die("Requested building a message and at the same time used --data parameter.\n".
		    "That's not possible, sorry.\n");
	}
	if (defined($body_plain)) {
		if (-e $body_plain) {
			local $/=undef;
			open(FILE, $body_plain);
			$body_plain = <FILE>;
			close(FILE);
		} elsif ($body_plain eq "-") {
			local $/=undef;
			$body_plain = <STDIN>;
		}
	}
	if (defined($body_html)) {
		if (-e $body_html) {
			local $/=undef;
			open(FILE, $body_html);
			$body_html = <FILE>;
			close(FILE);
		} elsif ($body_html eq "-") {
			local $/=undef;
			$body_html = <STDIN>;
		}
	}
	my $message = &build_message();

	open(BUILT_MESSAGE, "+>", \$built_message);
	$datasrc = "///built_message";
	if ($print_only) {
		$message->print();
		exit(0);
	} else {
		$message->print(\*BUILT_MESSAGE);
	}
	seek(BUILT_MESSAGE, 0, 0);
}

# Username was given -> enable AUTH
if ($user)
	{ $auth_ok = 1; }

# If at least one --auth-* option was given, enable AUTH.
if ($use_login + $use_plain + $use_cram_md5 > 0)
	{ $auth_ok = 1; }

# If --enable-auth was given, enable all AUTH methods.
elsif ($auth_ok && ($use_login + $use_plain + $use_cram_md5 == 0))
{
	$use_login = 1;
	$use_plain = 1;
	$use_cram_md5 = 1 if ($have_hmac_md5);
}

# Exit if user haven't specified username for AUTH.
if ($auth_ok && !defined ($user))
	{ die ("SMTP AUTH support requested without --user\n"); }

# Ask for password if it wasn't supplied on the command line.
if ($auth_ok && defined ($user) && !defined ($pass))
{
	if ($have_term_readkey) {
		# Set echo off.
		Term::ReadKey::ReadMode (2);
	} else {
		warn ("Module Term::ReadKey not available - password WILL NOT be hidden!!!\n");
	}
	printf ("Enter password for %s@%s : ", $user, $host);
	$pass = <>;
	if ($have_term_readkey) {
		# Restore echo.
		Term::ReadKey::ReadMode (0);
		printf ("\n");
	}
	exit if (! defined ($pass));
	chop ($pass);
}

# Connect to the SMTP server.
my %connect_args = (
	PeerAddr => $host,
	PeerPort => $port,
	Proto => 'tcp',
	Timeout => 5);

if (defined($localaddr)) {
  $connect_args{'LocalAddr'} = $localaddr;
}

if ($addr_family == AF_INET) {
	# If the user requested --ipv4 don't even bother with INET6 module
	# (although it should work some users reported problems)
	$sock = IO::Socket::INET->new(%connect_args) or die ("Connect failed: $@\n");
} else {
	# Either --ipv6 or no preference - do the best we can
	$connect_args{'Domain'} = $addr_family;
	$sock = IO::Socket::INET6->new(%connect_args) or die ("Connect failed: $@\n");
}

if ($verbose >= 1) {
	my $addr_fmt = "%s";
	$addr_fmt = "[%s]" if ($sock->sockhost() =~ /:/); ## IPv6 connection

	printf ("Connection from $addr_fmt:%s to $addr_fmt:%s\n",
		$sock->sockhost(), $sock->sockport(),
		$sock->peerhost(), $sock->peerport());
}

if ($ssl) {
	printf ("Starting SMTP/SSL...\n") if ($verbose >= 1);
	&socket_to_ssl($sock);
}

my ($code, $text);
my (%features);

# Wait for the welcome message of the server.
($code, $text) = &get_line ($sock);
die ("Unknown welcome string: '$code $text'\n") if ($code != 220);
$ehlo_ok-- if ($text !~ /ESMTP/);

# Send EHLO
&say_hello ($sock, $ehlo_ok, $hello_host, \%features) or exit (1);

# Run the SMTP session
my $exitcode = &run_smtp ();

# Good bye...
&send_line ($sock, "QUIT\n");
($code, $text) = &get_line ($sock);
die ("Unknown QUIT response '$code'.\n") if ($code != 221);

exit $exitcode;

# This is the main SMTP "engine".
sub run_smtp
{
	# See if we could start encryption
	if ((defined ($features{'STARTTLS'}) || defined ($features{'TLS'})) && $starttls_ok && !$have_ssl)
	{
		warn ("Module IO::Socket::SSL is missing - STARTTLS support disabled.\n");
		warn ("Use --disable-starttls or install the modules to avoid this warning.\n");
		undef ($features{'STARTTLS'});
		undef ($features{'TLS'});
	}

	if ((defined ($features{'STARTTLS'}) || defined ($features{'TLS'})) && $starttls_ok)
	{
		printf ("Starting TLS...\n") if ($verbose >= 1);

		&send_line ($sock, "STARTTLS\n");
		($code, $text) = &get_line ($sock);
		die ("Unknown STARTTLS response '$code'.\n") if ($code != 220);

		&socket_to_ssl($sock);

		# Send EHLO again (required by the SMTP standard).
		&say_hello ($sock, $ehlo_ok, $hello_host, \%features) or return 0;
	}

	# See if we should authenticate ourself
	if (defined ($features{'AUTH'}) && $auth_ok)
	{
		printf ("AUTH method (%s): ", $features{'AUTH'}) if ($verbose >= 1);

		## Try DIGEST-MD5 first
		# Actually we won't. It never worked reliably here.
		# After all DIGEST-MD5 is on a way to deprecation
		# see this thread: http://www.imc.org/ietf-sasl/mail-archive/msg02996.html

		# Instead use CRAM-MD5 if supported by the server
		if ($features{'AUTH'} =~ /CRAM-MD5/i && $use_cram_md5)
		{
			printf ("using CRAM-MD5\n") if ($verbose >= 1);
			&send_line ($sock, "AUTH CRAM-MD5\n");
			($code, $text) = &get_line ($sock);
			if ($code != 334)
				{ die ("AUTH CRAM-MD5 failed: $code $text\n"); }

			my $response = &encode_cram_md5 ($text, $user, $pass);
			&send_line ($sock, "%s\n", $response);
			($code, $text) = &get_line ($sock);
			if ($code != 235)
				{ die ("AUTH CRAM-MD5 failed: $code $text\n"); }
		}
		# Eventually try LOGIN method
		elsif ($features{'AUTH'} =~ /LOGIN/i && $use_login)
		{
			printf ("using LOGIN\n") if ($verbose >= 1);
			&send_line ($sock, "AUTH LOGIN\n");
			($code, $text) = &get_line ($sock);
			if ($code != 334)
				{ die ("AUTH LOGIN failed: $code $text\n"); }

			&send_line ($sock, "%s\n", encode_base64 ($user, ""));

			($code, $text) = &get_line ($sock);
			if ($code != 334)
				{ die ("AUTH LOGIN failed: $code $text\n"); }

			&send_line ($sock, "%s\n", encode_base64 ($pass, ""));

			($code, $text) = &get_line ($sock);
			if ($code != 235)
				{ die ("AUTH LOGIN failed: $code $text\n"); }
		}
		# Or finally PLAIN if nothing else was supported.
		elsif ($features{'AUTH'} =~ /PLAIN/i && $use_plain)
		{
			printf ("using PLAIN\n") if ($verbose >= 1);
			&send_line ($sock, "AUTH PLAIN %s\n",
				encode_base64 ("$user\0$user\0$pass", ""));
			($code, $text) = &get_line ($sock);
			if ($code != 235)
				{ die ("AUTH PLAIN failed: $code $text\n"); }
		}
		# Complain otherwise.
		else
		{
			warn ("No supported authentication method\n".
			      "advertised by the server.\n");
			return 1;
		}

		printf ("Authentication of $user\@$host succeeded\n") if ($verbose >= 1);
	}

	# We can do a relay-test now if a recipient was set.
	if ($#rcpt_to >= 0)
	{
		if (!defined ($mail_from))
		{
			warn ("From: address not set. Using empty one.\n");
			$mail_from = "";
		}
		&send_line ($sock, "MAIL FROM:<%s>\n", $mail_from);
		($code, $text) = &get_line ($sock);
		if ($code != 250)
		{
			warn ("MAIL FROM <$mail_from> failed: '$code $text'\n");
			return 1;
		}

		my $i;
		for ($i=0; $i <= $#rcpt_to; $i++)
		{
			&send_line ($sock, "RCPT TO:<%s>\n", $rcpt_to[$i]);
			($code, $text) = &get_line ($sock);
			if ($code != 250)
			{
				warn ("RCPT TO <".$rcpt_to[$i]."> ".
				      "failed: '$code $text'\n");
				return 0;
			}
		}
	}

	# Wow, we should even send something!
	if (defined ($datasrc))
	{
		if ($datasrc eq "///built_message")
		{
			*MAIL = *BUILT_MESSAGE;
		}
		elsif ($datasrc eq "-")
		{
			*MAIL = *STDIN;
		}
		elsif (!open (MAIL, $datasrc))
		{
			warn ("Can't open file '$datasrc'\n");
			return 0;
		}

		&send_line ($sock, "DATA\n");
		($code, $text) = &get_line ($sock);
		if ($code != 354)
		{
			warn ("DATA failed: '$code $text'\n");
			return 0;
		}

		while (<MAIL>)
		{
			my $line = $_;
			# RFC 5321 section 4.5.2 - leading dot must be doubled
			$line =~ s/^\./\.\./;
			# RFC 5321 section 2.3.8 - ensure CR-LF line ending
			$line =~ s/[\r\n]+$/$CRLF/;
			$sock->print ($line);
		}

		close (MAIL);

		$sock->printf ("$CRLF.$CRLF");

		($code, $text) = &get_line ($sock);
		if ($code != 250)
		{
			warn ("DATA not send: '$code $text'\n");
			return 0;
		}
	}

	# Perfect. Everything succeeded!
	return 1;
}

# Get one line of response from the server.
sub get_one_line ($)
{
	my $sock = shift;
	my ($code, $sep, $text) = ($sock->getline() =~ /(\d+)(.)([^\r]*)/);
	my $more;
	$more = ($sep eq "-");
	if ($verbose)
		{ printf ("[%d] '%s'\n", $code, $text); }
	return ($code, $text, $more);
}

# Get concatenated lines of response from the server.
sub get_line ($)
{
	my $sock = shift;
	my ($code, $text, $more) = &get_one_line ($sock);
	while ($more) {
		my ($code2, $line);
		($code2, $line, $more) = &get_one_line ($sock);
		$text .= " $line";
		die ("Error code changed from $code to $code2. That's illegal.\n") if ($code ne $code2);
	}
	return ($code, $text);
}

# Send one line back to the server
sub send_line ($@)
{
	my $socket = shift;
	my @args = @_;

	if ($verbose)
		{ printf ("> "); printf (@args); }
	$args[0] =~ s/\n/$CRLF/g;
	$socket->printf (@args);
}

sub socket_to_ssl($)
{
	if (!$have_ssl) {
		die ("SSL/TLS support is not available due to missing modules. Sorry.\n");
	}

	# Do Net::SSLeay initialization
	Net::SSLeay::load_error_strings();
	Net::SSLeay::SSLeay_add_ssl_algorithms();
	Net::SSLeay::randomize();

	if (! IO::Socket::SSL->start_SSL($sock, {
		SSL_ca_file => $ssl_ca_file,
		SSL_ca_path => $ssl_ca_path,
		SSL_verify_mode => (defined($ssl_ca_file) or defined($ssl_ca_path)) ? 0x01 : 0x00,
	}))
	{
		die ("SSL/TLS: ".IO::Socket::SSL::errstr()."\n");
	}

	if ($verbose >= 1)
	{
		printf ("Using cipher: %s\n", $sock->get_cipher ());
		printf ("%s", $sock->dump_peer_certificate());
	}
}

# Helper function to encode CRAM-MD5 challenge
sub encode_cram_md5 ($$$)
{
	my ($ticket64, $username, $password) = @_;
	my $ticket = decode_base64($ticket64) or
		die ("Unable to decode Base64 encoded string '$ticket64'\n");

	print "Decoded CRAM-MD5 challenge: $ticket\n" if ($verbose > 1);
	my $password_md5 = Digest::HMAC_MD5::hmac_md5_hex($ticket, $password);
	return encode_base64 ("$username $password_md5", "");
}

# Store all server's ESMTP features to a hash.
sub say_hello ($$$$)
{
	my ($sock, $ehlo_ok, $hello_host, $featref) = @_;
	my ($feat, $param);
	my $hello_cmd = $ehlo_ok > 0 ? "EHLO" : "HELO";

	&send_line ($sock, "$hello_cmd $hello_host\n");
	my ($code, $text, $more) = &get_one_line ($sock);

	if ($code != 250)
	{
		warn ("$hello_cmd failed: '$code $text'\n");
		return 0;
	}

	# Empty the hash
	%{$featref} = ();

	($feat, $param) = ($text =~ /^(\w+)[= ]*(.*)$/);
	$featref->{$feat} = $param;

	# Load all features presented by the server into the hash
	while ($more == 1)
	{
		($code, $text, $more) = &get_one_line ($sock);
		($feat, $param) = ($text =~ /^(\w+)[= ]*(.*)$/);
		$featref->{$feat} = $param;
	}

	return 1;
}

sub find_email_addr($)
{
	my $addr = shift;
	if ($addr =~ /([A-Z0-9._%=#+-]+@(?:[A-Z0-9-]+\.)+[A-Z]+)\b/i) {
		return $1;
	}
	return undef;
}

sub guess_mime_type($)
{
	my $filename = shift;
	if (defined($file_libmagic)) {
		## Use File::LibMagic if possible
		return $file_libmagic->checktype_filename($filename);
	} elsif (defined($file_type)) {
		## Use File::Type if possible
		return $file_type->mime_type($filename);
	} else {
		## Module File::LibMagic is not available
		## Still recognise some common extensions
		return "image/jpeg" if ($filename =~ /\.jpe?g/i);
		return "image/gif" if ($filename =~ /\.gif/i);
		return "image/png" if ($filename =~ /\.png/i);
		return "text/plain" if ($filename =~ /\.txt/i);
		return "application/zip" if ($filename =~ /\.zip/i);
		return "application/x-gzip" if ($filename =~ /\.t?gz/i);
		return "application/x-bzip" if ($filename =~ /\.t?bz2?/i);
	}
	return "application/octet-stream";
}

sub basename($)
{
	my $path = shift;
	my @parts = split(/\//, $path);
	return $parts[$#parts];
}

sub prepare_attachment($)
{
	my $attachment = shift;
	my ($path, $mime_type);

	if (-e $attachment) {
		$path = $attachment;
		$mime_type = guess_mime_type($attachment);
	} elsif ($attachment =~ /(.*)@([^@]*)$/ and -e $1) {
		$path = $1;
		$mime_type = $2;
	}
	return ($path, $mime_type);
}

sub attach_attachments($$@)
{
	my $message = shift;
	my $disposition = shift;
	my @attachments = @_;

	foreach my $attachment (@attachments) {
		my ($path, $mime_type) = prepare_attachment($attachment);
		if (not defined($path)) {
			warn("$attachment: File not found. Ignoring.\n");
			next;
		}
		$message->attach(
			Type => $mime_type,
			Path => $path,
			Id   => basename($path),
			Disposition => $disposition,
		);
	}
}

sub safe_attach($$)
{
	my ($message, $part) = @_;
	## Remove some headers when $part is becoming a subpart of $message
	$part->delete("Date");
	$part->delete("X-Mailer");
	$part->attr("MIME-Version" => undef);
	$message->attach($part);
	return $message;
}

sub mime_message($$)
{
	my ($type, $data) = @_;

	## Set QP encoding for text/* types, let MIME::Lite decide for all other types.
	my $encoding = $type =~ /^text\// ? $text_encoding : undef;
	my $message = MIME::Lite->new(
		Type	=> $type,
		Encoding=> $encoding,
		Data	=> $data);
	$message->attr('content-type.charset' => $charset) if (($type =~ /^text\//i) and defined($charset));
	return $message;
}

sub build_message
{
	my ($part_plain, $part_html, $part_body, $message);

	if (@attachments_inline) {
		if (not defined($body_html)) {
			die("Inline attachments (--attach-inline) must be used with --body-html\n");
		}
		$part_html = MIME::Lite->new(Type => 'multipart/related');
		$part_html->attach(Type => 'text/html', Data => $body_html);
		attach_attachments($part_html, "inline", @attachments_inline);
		$message = $part_html;
		# undefine $body_html to prevent confusion in the next if()
		undef($body_html);
	}

	if (defined($body_html)) {
		$part_html = mime_message('text/html', $body_html);
		$message = $part_html;
	}

	if (defined($body_plain)) {
		$part_plain = mime_message('text/plain', $body_plain);
		$message = $part_plain;
	}

	if (defined($part_plain) and defined($part_html)) {
		$part_body = mime_message("multipart/alternative", undef);
		safe_attach($part_body, $part_plain);
		safe_attach($part_body, $part_html);
		$message = $part_body;
	}

	if (@attachments) {
		if (defined($message)) {
			# We already have some plaintext and/or html content built
			# => make it the first part of multipart/mixed
			my $message_body = $message;
			$message = mime_message("multipart/mixed", undef);
			safe_attach($message, $message_body);
			attach_attachments($message, "attachment", @attachments);
		} elsif ($#attachments == 0) {
			# Only one single attachment - let it be the body
			my ($path, $mime_type) = prepare_attachment($attachments[0]);
			if (not defined($path)) {
				die($attachments[0].": File not found. No other message parts defined. Aborting.\n");
			}
			$message = MIME::Lite->new(
				Type => $mime_type,
				Path => $path);
		} else {
			# Message consisting only of attachments
			$message = mime_message("multipart/mixed", undef);
			attach_attachments($message, "attachment", @attachments);
		}
	}

	# Last resort - empty plaintext message
	if (!defined($message)) {
		$message = mime_message("TEXT", "");
	}

	$message->replace("From" => $from);
	$message->replace("To" => join(", ", @to));
	$message->replace("Cc" => join(", ", @cc));
	$message->replace("Subject" => $subject);
	$message->replace("X-Mailer" => "smtp-cli $version, see http://smtp-cli.logix.cz");
	$message->replace("Message-ID" => "<".time()."-".int(rand(999999))."\@smtp-cli>");

	for my $header (@add_headers) {
		my ($hdr, $val) = ($header =~ /^([^:]+):\s*(.*)$/);
		die("Not a valid header format: ${header}\n") if (not $hdr or not $val);
		$message->add($hdr => $val);
	}
	for my $header (@replace_headers) {
		my ($hdr, $val) = ($header =~ /^([^:]+):\s*(.*)$/);
		die("Not a valid header format: ${header}\n") if (not $hdr or not $val);
		$message->replace($hdr => $val);
	}
	for my $header (@remove_headers) {
		my ($hdr) = ($header =~ /^([^:\s]+)/);
		$message->replace($header => "");
	}

	return $message;
}

sub version ()
{
	print "smtp-cli version $version\n";
	exit (0);
}

sub usage ()
{
	printf (
"Simple SMTP client written in Perl that supports advanced
features like STARTTLS and SMTP-AUTH and IPv6. It can also
create messages from components (files, text snippets) and
attach files.

Version: smtp-cli v$version

Author: Michal Ludvig <mludvig\@logix.net.nz> (c) 2003-2017
        http://smtp-cli.logix.cz

Usage: smtp-cli [--options]

        --server=<hostname>[:<port>]
                                Host name or IP address of the SMTP server.
                                May include the port after colon, alternatively
                                use --port.
        --port=<number>         Port where the SMTP server is listening.
                                (default: 25)
        -4 or --ipv4            Use standard IP (IPv4) protocol.
        -6 or --ipv6            Use IPv6 protocol. For hosts that have
                                both IPv6 and IPv4 addresses the IPv6
                                connection is tried first.
        --local-addr=<address>  Specify local address (by default the OS chooses)

        --hello-host=<string>   String to use in the EHLO/HELO command.
        --disable-ehlo          Don't use ESMTP EHLO command, only HELO.
        --force-ehlo            Use EHLO even if server doesn't say ESMTP.

        Transport encryption (TLS)
        --disable-starttls      Don't use encryption even if the remote
                                host offers it.
        --ssl                   Start in SMTP/SSL mode (aka SSMTP).
                                Default when --port=465
        --disable-ssl           Don't start SSMTP even if --port=465
        --ssl-ca-file=<filename>
                                Verify the server's SSL certificate against
                                a trusted CA root certificate file.
        --ssl-ca-path=<dirname> Similar to --ssl-ca-file but will look for
                                the appropriate root certificate file in
                                the given directory. The certificates must
                                must be stored one per file with hash-links
                                generated by, for example, c_rehash script
                                from OpenSSL.

        Authentication options (AUTH)
        --user=<username>       Username for SMTP authentication.
        --pass=<password>       Corresponding password.
        --auth-login            Enable only AUTH LOGIN method.
        --auth-plain            Enable only AUTH PLAIN method.
        --auth-cram-md5         Enable only AUTH CRAM-MD5 method.
        --auth                  Enable all supported methods. This is
                                normally not needed, --user enables
                                everything as well.

        Sender / recipient
        --from=\"Display Name <add\@re.ss>\"
                                Sender's name address (or address only).
        --to=\"Display Name <add\@re.ss>\"
        --cc=\"Display Name <add\@re.ss>\"
        --bcc=\"Display Name <add\@re.ss>\"
                                Message recipients. Each parameter can be
                                used multiple times.
                                The --bcc addresses won't apprear in
                                the composed message.

        SMTP Envelope sender / recipient
        (rarely needed, use --from, --to, --cc and --bcc instead)
        --mail-from=<address>   Address to use in MAIL FROM command.
                                Use --from instead, unless you want
                                a different address in the envelope and
                                in the headers.
        --rcpt-to=<address>     Address to use in RCPT TO command. Can be
                                used multiple times. Normally not needed,
                                use --to, --cc and --bcc instead.
                                If set the --to, --cc and --bcc will only
                                be used for composing the message body and
                                not for delivering the messages.

        Send a complete RFC822-compliant email message:
        --data=<filename>       Name of file to send after DATA command.
                                With \"--data=-\" the script will read
                                standard input (useful e.g. for pipes).

        Alternatively build email a message from provided components:
        --subject=<subject>     Subject of the message
        --body-plain=<text|filename>
        --body-html=<text|filename>
                                Plaintext and/or HTML body of the message
                                If both are provided the message is sent
                                as multipart.
        --charset=<charset>     Character set used for Subject and Body,
                                for example UTF-8, ISO-8859-2, KOI8-R, etc.
        --text-encoding=<encoding>
                                Enforce Content-Transfer-Encoding for text
                                parts of the email, including body and
                                attachments. Must be one of:
                                ".join(", ", @valid_encodings)."
                                The default is: quoted-printable
        --attach=<filename>[\@<MIME/Type>]
                                Attach a given filename.
                                MIME-Type of the attachment is guessed
                                by default guessed but can optionally
                                be specified after '\@' delimiter.
                                For instance: --attach mail.log\@text/plain
                                Parameter can be used multiple times.
        --attach-inline=<filename>[\@<MIME/Type>]
                                Attach a given filename (typically a picture)
                                as a 'related' part to the above 'body-html'.
                                Refer to these pictures as <img src='cid:filename'>
                                in the 'body-html' contents.
                                See --attach for details about MIME-Type.
                                Can be used multiple times.
        --add-header=\"Header: value\"
        --replace-header=\"Header: value\"
        --remove-header=\"Header\"
                                Add, Replace or Remove pretty much any header
                                in the email. For example to set a different
                                Mailer use --replace-header=\"X-Mailer: Blah\",
                                to remove it altogether --remove-header=X-Mailer
                                or to add a completely custom header use
                                --add-header=\"X-Something: foo bar\".
        --print-only            Dump the composed MIME message to standard
                                output. This is useful mainly for debugging
                                or in the case you need to run the message
                                through some filter before sending.

        Other options
        --verbose[=<number>]    Be more verbose, print the SMTP session.
        --missing-modules-ok    Don't complain about missing optional modules.
        --version               Print: smtp-cli version $version
        --help                  Guess what is this option for ;-)

PayPal donations: http://smtp-cli.logix.cz/donate
                  Thanks in advance for your support!

");
	exit (0);
}
