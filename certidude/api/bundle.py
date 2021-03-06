

import logging
import hashlib
from certidude import config, authority
from certidude.auth import login_required

logger = logging.getLogger("api")

KEYWORDS = (
    (u"Android", u"android"),
    (u"iPhone", u"iphone"),
    (u"iPad", u"ipad"),
    (u"Ubuntu", u"ubuntu"),
)

class BundleResource(object):
    @login_required
    def on_get(self, req, resp):
        common_name = req.context["user"].name
        if config.USER_MULTIPLE_CERTIFICATES:
            for key, value in KEYWORDS:
                if key in req.user_agent:
                    device_identifier = value
                    break
            else:
                device_identifier = u"unknown-device"
            common_name = u"%s@%s-%s" % (common_name, device_identifier, \
                hashlib.sha256(req.user_agent).hexdigest()[:8])

        logger.info(u"Signing bundle %s for %s", common_name, req.context.get("user"))
        resp.set_header("Content-Type", "application/x-pkcs12")
        resp.set_header("Content-Disposition", "attachment; filename=%s.p12" % common_name.encode("ascii"))
        resp.body, cert = authority.generate_pkcs12_bundle(common_name,
                                owner=req.context.get("user"))

