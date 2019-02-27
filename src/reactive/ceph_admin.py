from pathlib import Path

from charms.reactive import (
    when,
    set_flag,
    clear_flag,
    hook,
)

from charms.layer import status

from charmhelpers.core.templating import render


CEPH_CONF = Path('/etc/ceph/ceph.conf')
CEPHX_KEY = Path('/etc/ceph/ceph.client.admin.keyring')


@when('ceph-admin.available')
def render_ceph_configs(ceph_client):
    ceph_conf_ctxt = {
        'mon_hosts': ceph_client.mon_hosts(),
        'fsid': ceph_client.fsid(),
    }

    if CEPH_CONF.exists():
        CEPH_CONF.unlink()

    render('ceph.conf', str(CEPH_CONF), ceph_conf_ctxt)

    cephx_keyring_ctxt = {
        'key': ceph_client.key(),
    }

    if CEPHX_KEY.exists():
        CEPHX_KEY.unlink()

    render('ceph.client.admin.keyring', str(CEPHX_KEY), cephx_keyring_ctxt)

    status.active('ceph-admin connected')
