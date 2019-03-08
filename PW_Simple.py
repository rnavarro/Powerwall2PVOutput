#!/usr/bin/env python
import datetime
import time

import PW_Config as Cfg
import PW_Helper as Hlp

Hlp.setup_logging(Cfg.log_file)
logger = Hlp.logging.getLogger(__name__)
logger.info('Start PVOutput simple')

while True:
    try:
        lpvPower = []
        lpvAdjustedPower = []
        lpvVoltage = []
        lpvBatteryFlow = []
        lpvLoadPower = []
        lpvSitePower = []
        lpvLoadVoltage = []
        lpvSOC = []
        i = 0

        while i < 60:
            pw = Hlp.getPowerwallData(Cfg.PowerwallIP)
            soc = Hlp.getPowerwallSOCData(Cfg.PowerwallIP)
            if pw is not False and soc is not False:
                lpvPower.append(float(pw['solar']['instant_power']))
                lpvVoltage.append(float(pw['solar']['instant_average_voltage']))
                lpvBatteryFlow.append(float(pw['battery']['instant_power']))
                lpvLoadPower.append(float(pw['load']['instant_power']))
                lpvSitePower.append(float(pw['site']['instant_power']))
                lpvLoadVoltage.append(float(pw['load']['instant_average_voltage']))
                lpvSOC.append(float(soc['percentage']))
                # lpvAdjustedPower.append(float(pw['solar']['instant_power']) - float(pw['load']['instant_power']) + float(pw['battery']['instant_power']))

                lpvAdjustedPower.append(float(pw['solar']['instant_power']) + float(pw['battery']['instant_power']))
            else:
                logger.info('No data received, retrying')
            i = i + 1
            # time.sleep(5) # 6 * 50 = 300s = 5m

        if len(lpvPower) != 0:
            pvPower = Hlp.avg(lpvPower)
            pvAdjustedPower = Hlp.avg(lpvAdjustedPower)
            pvVoltage = Hlp.avg(lpvVoltage)
            pvBatteryFlow = Hlp.avg(lpvBatteryFlow)
            pvLoadPower = Hlp.avg(lpvLoadPower)
            pvSitePower = Hlp.avg(lpvSitePower)
            pvLoadVoltage = Hlp.avg(lpvLoadVoltage)
            pvSOC = Hlp.avg(lpvSOC)
            if pvPower <= 30:
                pvPower = 0
            pvTemp = 0

            pvConsumption = pvLoadPower
            pvGeneration = pvAdjustedPower

            if pvConsumption < 0:
                pvConsumption = 0

            if pvGeneration < 0:
                pvGeneration = 0

            pwdate = datetime.datetime.now()
            pvDate = pwdate.strftime("%Y%m%d")
            pvTime = pwdate.strftime("%H:%M")
            pvoutz = Hlp.Connection(Cfg.pvo_key, Cfg.pvo_systemid, Cfg.pvo_host)
            if Cfg.extData is True:
                pvoutz.add_status(pvDate, pvTime, power_exp=pvGeneration, power_imp=pvConsumption, temp=pvTemp, vdc=pvVoltage, battery_flow=pvBatteryFlow, load_power=pvLoadPower, soc=pvSOC, site_power=pvSitePower, load_voltage=pvLoadVoltage, ext_power_exp=pvPower)
                std_out = "Date: " + str(pvDate) + " Time: " + str(pvTime) + " Generation Power: " + str(
                    pvPower) + " Load Power: " + str(pvLoadPower) + " SOC: " + str(pvSOC) + " Site Power: " + str(
                    pvSitePower) + " Load Voltage: " + str(pvLoadVoltage) + " Battery Flow: " + str(
                    pvBatteryFlow) + " Temp: " + str(pvTemp) + " Solar Voltage: " + str(pvVoltage)
                logger.info(std_out)
            else:
                pvoutz.add_status(pvDate, pvTime, power_exp=pvGeneration, power_imp=pvConsumption, temp=pvTemp, vdc=pvVoltage)
                std_out = "Date: " + str(pvDate) + " Time: " + str(pvTime) + " Generation Power: " + str(
                    pvPower) + " Solar Voltage: " + str(pvVoltage)
                logger.info(std_out)
        else:
            logger.info('No data sent')

    except StandardError as e:
        logger.info('Main: Sleeping 5 minutes ' + str(e))
        time.sleep(60 * 5)
