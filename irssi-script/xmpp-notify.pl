##
## Put me in ~/.irssi/scripts, and then execute the following in irssi:
##
##       /load perl
##       /script load xmpp-notify
##
## Inspired from script http://irssi-libnotify.googlecode.com/svn/trunk/notify.pl

use strict;
use Irssi;
use vars qw($VERSION %IRSSI);

$VERSION = "0.01";
%IRSSI = (
    authors     => 'Chmouel Boudjnah',
    contact     => 'chmouel@chmouel.com',
    name        => 'xnmpp-notify',
    description => 'Use XMPP to alert user to hilighted messages',
    license     => 'GNU General Public License'
);

Irssi::settings_add_str('xmpp-notify', 'xmpp-notify.py', '/usr/local/bin/xmpp-notify.py');

sub notify {
    my ($server, $summary, $message) = @_;

    # Make the message entity-safe
    $message =~ s/&/&amp;/g; # That could have been done better.
    $message =~ s/</&lt;/g;
    $message =~ s/>/&gt;/g;
    $message =~ s/'/&apos;/g;

    my $cmd = "EXEC - " .
    Irssi::settings_get_str('xmpp-notify.py') .
	" '" . $summary . "'" .
	" '" . $message . "'";

    $server->command($cmd);
}

sub print_text_notify {
    my ($dest, $text, $stripped) = @_;
    my $server = $dest->{server};

    return if (!$server || !($dest->{level} & MSGLEVEL_HILIGHT));
    my $sender = $stripped;
    $sender =~ s/^\<.([^\>]+)\>.+/\1/ ;
    $stripped =~ s/^\<.[^\>]+\>.// ;
    my $summary = $dest->{target} . ": " . $sender;
    notify($server, $summary, $stripped);
}

sub message_private_notify {
    my ($server, $msg, $nick, $address) = @_;

    return if (!$server);
    notify($server, "Private message from ".$nick, $msg);
}

sub dcc_request_notify {
    my ($dcc, $sendaddr) = @_;
    my $server = $dcc->{server};

    return if (!$dcc);
    notify($server, "DCC ".$dcc->{type}." request", $dcc->{nick});
}

Irssi::signal_add('print text', 'print_text_notify');
Irssi::signal_add('message private', 'message_private_notify');
Irssi::signal_add('dcc request', 'dcc_request_notify');
