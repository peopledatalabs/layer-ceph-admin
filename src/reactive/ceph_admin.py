from pathlib import Path

from charms.reactive import (
    when,
    when_not,
    set_flag,
    clear_flag,
    hook,
)

from charms.layer import status

from charmhelpers.core.templating import render
from charmhelpers.core.hookenv import log


CEPH_CONF = Path('/etc/ceph/ceph.conf')
CEPHX_KEY = Path('/etc/ceph/ceph.client.admin.keyring')


@when('ceph-admin.connected')
@when_not('ceph.admin.connected')
def set_ceph_admin_connected_flag():
    set_flag('ceph.admin.connected')


@when('ceph-admin.available',
      'ceph.admin.connected')
@when_not('ceph.conf.rendered')
def render_ceph_configs(ceph_client):

    all_vars = {
        'mon_hosts': ceph_client.mon_hosts(),
        'fsid': ceph_client.fsid(),
        'key': ceph_client.key(),
    }

    log(all_vars)

    if not all(all_vars.values()):
        status.blocked("Need all vars")
        return

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
    set_flag('ceph.conf.rendered')
