---------- Server-wide settings ----------
-- Settings in this section apply to the whole server and are the default settings for any virtual hosts

-- admins for the server
admins = { "admin@localhost" }

-- Enable use of libevent for better performance under high load : https://prosody.im/doc/libevent 
--use_libevent = true

-- pecify additional locations where Prosody will look for modules first.
plugin_paths = { "/usr/lib/prosody/modules-custom", "/usr/lib/prosody/modules-community" }

-- list of modules Prosody will load on startup.
-- It looks for mod_modulename.lua in the plugins folder, so make sure that exists too.
modules_enabled = {

	-- Generally required
		"roster"; -- Allow users to have un carnet de contact
		"saslauth"; -- Authentication for clients and servers. Recommended if you want to log in.
		"tls"; -- Add support for secure TLS on c2s/s2s connections
		"dialback"; -- s2s dialback support
		"disco"; -- Service discovery

	-- Not essential, but recommended
		"carbons"; -- Keep multiple clients in sync
		"pep"; -- Enables users to publish their avatar, mood, activity, playing music and more
		"private"; -- Private XML storage (for room bookmarks, etc.)
		"blocklist"; -- Allow users to block communications with other users
		"vcard4"; -- User profiles (stored in PEP)
		"vcard_legacy"; -- Conversion between legacy vCard and PEP Avatar, vcard

	-- Nice to have
		"version"; -- Replies to server version requests
		"uptime"; -- Report how long server has been running
		"time"; -- Let others know the time here on this server
		"ping"; -- Replies to XMPP pings with pongs
		"register"; -- Allow users to register on this server using a client and change passwords
		"mam"; -- Store messages in an archive and allow users to access it
		"csi_simple"; -- Simple Mobile optimizations

	-- Admin interfaces
		"admin_adhoc"; -- Allows administration via an XMPP client that supports ad-hoc commands

	-- HTTP modules
		"bosh"; -- Enable BOSH clients, aka "Jabber over HTTP"
		"websocket"; -- XMPP over WebSockets

	-- Other specific functionality
		"posix"; -- POSIX functionality, sends server to background, enables syslog, etc.
		"welcome"; -- Welcome users who register accounts
		"watchregistrations"; -- Alert admins of registrations
		"legacyauth"; -- Legacy authentication. Only used by some old clients and bots.
}

-- Bosh Server
bosh_max_inactivity = 60 --Maximum amount of time in seconds a client may remain silent for, with no requests
consider_bosh_secure = true -- Use if proxying HTTPS->HTTP on the server side, If true then BOSH connections will be allowed when requiring encryption, even if unencrypted
cross_domain_bosh = true -- Allow access from scripts on any site with no proxy (requires a modern browser), Set to true to enable cross-domain requests from websites, or a list like { "http://jabber.org", "http://prosody.im" }
consider_bosh_secure = true -- handle the fact if your web server does https and you proxy to Prosodys http port, it will think that connections are insecure and may not offer some features.

-- modules disabled
modules_disabled = {
	-- "offline";
	-- "c2s"; -- Handle client connections
	-- "s2s"; -- Handle server-to-server connections
}

-- Disable account creation by default, for security
allow_registration = true

-- Force clients to use encrypted connections? This option will
-- prevent clients from authenticating unless they are using encryption.
c2s_require_encryption = false
--c2s_ports = { 5222 } -- Listen on 5322 as well as 5222
--c2s_interfaces = { "127.0.0.1", "::1" } -- Listen only on these interfaces

-- Force servers to use encrypted connections? prevent servers from authenticating unless they are using encryption (different from authentication)
s2s_require_encryption = true

-- Force certificate authentication for server-to-server connections?
s2s_secure_auth = false

-- Debian: Do not send the server to background, either systemd or start-stop-daemon take care of that.
daemonize = false;

-- Required for init scripts and prosodyctl
pidfile = "/var/run/prosody/prosody.pid"

--authentication backend to use
authentication = "internal_hashed"

-- Select the storage backend to use
storage = "sql"
sql = { driver = "MySQL", database = "proso", username = "rootrm", password = "test", host = "mysqldb" }

-- Archiving configuration : This setting controls how long Prosody will keep messages in the archive before removing them.
archive_expires_after = "1w" -- Remove archived messages after 1 week

-- Logging configuration : Logs all to console
log = {
    {levels = {min = "all"}, to = "console"};
}

-- Location of directory to find certificates in (relative to main config file):
certificates = "certs"

-- HTTPS currently only supports a single certificate, specify it here:
https_certificate = "/etc/prosody/certs/localhost.crt"

----------- Virtual hosts -----------
-- You need to add a VirtualHost entry for each domain you wish Prosody to serve.
VirtualHost "localhost"

-- TEST
-- déclaration des rooms(salon)
Component "accident.localhost" "muc"
   --modules_enabled { "mam_muc"; } -- on définit le composant mod_muc pour la création de room(salon)
   name = "Salon des accidents"
   storage = { "sql"; } -- on définit le stockage dans la BDD SQL
   restrict_room_creation = true

Component "bouchon.localhost" "muc"
   --modules_enabled { "mam_muc"; }
   name = "Salon des bouchons"
   storage = { "sql"; }
   restrict_room_creation = true

-- on définit le composant pubsub
Component "pubsub.localhost" "pubsub"
	component_secret = "test"
	--modules_enabled = {"delegation"}
	autocreate_on_subscribe = true
	autocreate_on_publish = true
	name = "Service de publication / souscription";
