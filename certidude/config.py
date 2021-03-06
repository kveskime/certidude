
import click
import codecs
import configparser
import ipaddress
import os
import string
import const
from random import choice

# Options that are parsed from config file are fetched here

cp = configparser.RawConfigParser()
cp.readfp(codecs.open(const.CONFIG_PATH, "r", "utf8"))

AUTHENTICATION_BACKENDS = set([j for j in
    cp.get("authentication", "backends").split(" ") if j])   # kerberos, pam, ldap
AUTHORIZATION_BACKEND = cp.get("authorization", "backend")  # whitelist, ldap, posix
ACCOUNTS_BACKEND = cp.get("accounts", "backend")             # posix, ldap

if ACCOUNTS_BACKEND == "ldap":
    LDAP_GSSAPI_CRED_CACHE = cp.get("accounts", "ldap gssapi credential cache")

USER_SUBNETS = set([ipaddress.ip_network(j) for j in
    cp.get("authorization", "user subnets").split(" ") if j])
ADMIN_SUBNETS = set([ipaddress.ip_network(j) for j in
    cp.get("authorization", "admin subnets").split(" ") if j]).union(USER_SUBNETS)
AUTOSIGN_SUBNETS = set([ipaddress.ip_network(j) for j in
    cp.get("authorization", "autosign subnets").split(" ") if j])
REQUEST_SUBNETS = set([ipaddress.ip_network(j) for j in
    cp.get("authorization", "request subnets").split(" ") if j]).union(AUTOSIGN_SUBNETS)

AUTHORITY_DIR = "/var/lib/certidude"
AUTHORITY_PRIVATE_KEY_PATH = cp.get("authority", "private key path")
AUTHORITY_CERTIFICATE_PATH = cp.get("authority", "certificate path")
REQUESTS_DIR = cp.get("authority", "requests dir")
SIGNED_DIR = cp.get("authority", "signed dir")
REVOKED_DIR = cp.get("authority", "revoked dir")
OUTBOX = cp.get("authority", "outbox")

USER_CERTIFICATE_ENROLLMENT = {
    "forbidden": False, "single allowed": True, "multiple allowed": True }[
    cp.get("authority", "user certificate enrollment")]
USER_MULTIPLE_CERTIFICATES = {
    "forbidden": False, "single allowed": False, "multiple allowed": True }[
    cp.get("authority", "user certificate enrollment")]

CERTIFICATE_BASIC_CONSTRAINTS = "CA:FALSE"
CERTIFICATE_KEY_USAGE_FLAGS = "digitalSignature,keyEncipherment"
CERTIFICATE_EXTENDED_KEY_USAGE_FLAGS = "clientAuth"
CERTIFICATE_LIFETIME = cp.getint("signature", "certificate lifetime")
CERTIFICATE_AUTHORITY_URL = cp.get("signature", "certificate url")
CERTIFICATE_CRL_URL = cp.get("signature", "revoked url")

REVOCATION_LIST_LIFETIME = cp.getint("signature", "revocation list lifetime")

PUSH_TOKEN = cp.get("push", "token")
PUSH_EVENT_SOURCE = cp.get("push", "event source")
PUSH_LONG_POLL = cp.get("push", "long poll")
PUSH_PUBLISH = cp.get("push", "publish")

TAGGING_BACKEND = cp.get("tagging", "backend")
LOGGING_BACKEND = cp.get("logging", "backend")
LEASES_BACKEND = cp.get("leases", "backend")


if "whitelist" == AUTHORIZATION_BACKEND:
    USERS_WHITELIST = set([j for j in  cp.get("authorization", "users whitelist").split(" ") if j])
    ADMINS_WHITELIST = set([j for j in  cp.get("authorization", "admins whitelist").split(" ") if j])
elif "posix" == AUTHORIZATION_BACKEND:
    USERS_GROUP = cp.get("authorization", "posix user group")
    ADMIN_GROUP = cp.get("authorization", "posix admin group")
elif "ldap" == AUTHORIZATION_BACKEND:
    LDAP_USER_FILTER = cp.get("authorization", "ldap user filter")
    LDAP_ADMIN_FILTER = cp.get("authorization", "ldap admin filter")
    if "%s" not in LDAP_USER_FILTER: raise ValueError("No placeholder %s for username in 'ldap user filter'")
    if "%s" not in LDAP_ADMIN_FILTER: raise ValueError("No placeholder %s for username in 'ldap admin filter'")
else:
    raise NotImplementedError("Unknown authorization backend '%s'" % AUTHORIZATION_BACKEND)

for line in open("/etc/ldap/ldap.conf"):
    line = line.strip().lower()
    if "#" in line:
        line, _ = line.split("#", 1)
    if not " " in line:
        continue
    key, value = line.split(" ", 1)
    if key == "uri":
        LDAP_SERVERS = set([j for j in value.split(" ") if j])
        click.echo("LDAP servers: %s" % " ".join(LDAP_SERVERS))
    elif key == "base":
        LDAP_BASE = value

# TODO: Check if we don't have base or servers
