#!/usr/bin/env python3
# Copyright 2021 Hernan Garcia
# See LICENSE file for licensing details.

import logging
import cprocess

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main, subprocess
from ops.model import ActiveStatus

from charms.nginx_ingress_integrator.v0.ingress import IngressRequires

logger = logging.getLogger(__name__)


class CockroachdbCharm(CharmBase):
    """Charm the service."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.cockroachdb_pebble_ready,
            self._on_cockroachdb_pebble_ready)
        self.framework.observe(self.on.init_action,
            self._on_init_action)
        self._stored.set_default(things=[])

        self.ingress = IngressRequires(self, {
            "service-hostname": "cockroachdb.juju",
            "service-name": self.app.name,
            "service-port": 8080
        })

    def _on_cockroachdb_pebble_ready(self, event):
        """Define and start a workload using the Pebble API.

        Learn more about Pebble layers at https://github.com/canonical/pebble
        """
        container = event.workload
        
        self_endpoint = f"{self.unit.name}.{self.app.name}-endpoints.{self.model.name}.svc.cluster.local"
        self_endpoint = self_endpoint.replace('/','-')

        command = (
            "/cockroach/cockroach "
            "start "
            "--logtostderr "
            "--insecure "
            "--advertise-host "
            f"{self_endpoint} "
            "--http-addr 0.0.0.0 "
            "--join "
            "cockroachdb-operator-0.cockroachdb-operator-endpoints.development.svc.cluster.local,"
            "cockroachdb-operator-1.cockroachdb-operator-endpoints.development.svc.cluster.local,"
            "cockroachdb-operator-2.cockroachdb-operator-endpoints.development.svc.cluster.local"
        )

        pebble_layer = {
            "summary": "cockroachdb layer",
            "description": "pebble config layer for cockroachdb",
            "services": {
                "cockroachdb": {
                    "override": "replace",
                    "summary": "cockroachdb",
                    "command": command,
                    "startup": "enabled"
                }
            },
        }
        
        container.add_layer("cockroachdb", pebble_layer, combine=True)
        container.autostart()
        
        self.unit.status = ActiveStatus()

    def _on_init_action(self, event):
        """Just an example to show how to receive actions.
        """
        cmd = "/cockroach/cockroach init --insecure"
        output = self._container_execute(cmd.split())

        # Set the results of the action
        event.set_results({"result": output})

    def _container_execute(self, args: list) -> str:
        """Execute a command in the workload container
        """
        # block execution for 1 second to fix
        # "(cannot start service: exited quickly with code 0)" error
        # in the cprocess.run() call
        args.extend(["&&", "/bin/sleep", "1"])
        logger.debug(f"CMD: {args}")

        container = self.unit.get_container('cockroachdb')
        try:
            return cprocess.check_output(container, args)
        except cprocess.TimeoutExpired as e:
            logger.error(e.output)


if __name__ == "__main__":
    main(CockroachdbCharm)
