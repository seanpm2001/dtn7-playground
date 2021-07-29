#! /usr/bin/env python3

import os
import time
import shutil
import glob
import logging
import re

from core.emulator.coreemu import CoreEmu
from core.emulator.enumerations import EventTypes
from core.services import ServiceManager


def collect_logs(session_dir, dest_dir="/tmp/results"):
    exclude = [r"store_.*", r"var.run", r"var.log"]

    for node_dir in glob.glob(f"{session_dir}/*.conf"):
        _, node_name = os.path.split(node_dir)

        for filepath in glob.glob(f"{node_dir}/*"):
            path, name = os.path.split(filepath)

            if any(re.match(regex, name) for regex in exclude):
                logging.info(f"removing {filepath}")
                shutil.rmtree(filepath)
            else:
                logging.info(f"keeping {filepath}")

    shutil.move(session_dir, dest_dir)


if __name__ in ["__main__", "__builtin__"]:
    logging.basicConfig(level=logging.DEBUG, force=True)

    logging.info("Gathering experiment settings.")
    runtime = int(60)

    logging.info("Setting up CORE.")
    coreemu = CoreEmu()
    session = coreemu.create_session()
    session.set_state(EventTypes.CONFIGURATION_STATE)
    print(ServiceManager.add_services("/root/.core/myservices"))

    logging.info("Starting virtual nodes.")
    session.open_xml(file_name="/root/.core/configs/scenario.xml", start=True)
    time.sleep(10)

    logging.info(f"Experiment is running for {runtime} seconds.")
    time.sleep(runtime)

    logging.info("Collecting logs.")
    session.set_state(EventTypes.DATACOLLECT_STATE)
    collect_logs(session.session_dir)

    logging.info("Shutting down CORE.")
    coreemu.shutdown()
    os.system("core-cleanup")

    logging.info("Experiment finished.")