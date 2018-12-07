#!/usr/bin/env python
import time

import PW_Config as Cfg
import PW_Helper as Hlp

Hlp.setup_logging(Cfg.log_file)
logger = Hlp.logging.getLogger(__name__)
logger.info('Start PVOutput datalogger')

while True:
    try:
        pw = Hlp.getPowerwallData(Cfg.PowerwallIP)
        soc = Hlp.getPowerwallSOCData(Cfg.PowerwallIP)
        if pw is not False and soc is not False:
            lpvPower = float(pw['solar']['instant_power'])
            lpvVoltage = float(pw['solar']['instant_average_voltage'])
            lpvBatteryFlow = float(pw['battery']['instant_power'])
            lpvLoadPower = float(pw['load']['instant_power'])
            lpvSitePower = float(pw['site']['instant_power'])
            lpvLoadVoltage = float(pw['load']['instant_average_voltage'])
            lpvSOC = float(soc['percentage'])
            values = (
                lpvPower,
                lpvLoadPower,
                0,
                lpvVoltage,
                lpvBatteryFlow,
                lpvLoadPower,
                lpvSOC,
                lpvSitePower,
                lpvLoadVoltage
            )
            Hlp.insertdb(Cfg.sqlite_file, values)
        else:
            logger.info('No data received, retrying')
        time.sleep(5)

    except StandardError as e:
        logger.info('Main: Sleeping 5 minutes ' + str(e))
        time.sleep(60 * 5)
