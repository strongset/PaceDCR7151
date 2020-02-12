# -*- coding: utf-8 -*-
# Software Upgrade_Atualiza Desatualizadas
# Test name = Software Upgrade
# Test description = Set environment, perform software upgrade and check STB state after sw upgrade

from datetime import datetime
from time import gmtime, strftime
import time
import os.path
import sys
import device
import TEST_CREATION_API
import shutil
##import shutil
##shutil.copyfile('\\\\bbtfs\\RT-Executor\\API\\NOS_API.py', 'NOS_API.py')
try:    
    if ((os.path.exists(os.path.join(os.path.dirname(sys.executable), "Lib\NOS_API.py")) == False) or (str(os.path.getmtime('\\\\rt-rk01\\RT-Executor\\API\\NOS_API.py')) != str(os.path.getmtime(os.path.join(os.path.dirname(sys.executable), "Lib\NOS_API.py"))))):
        shutil.copy2('\\\\rt-rk01\\RT-Executor\\API\\NOS_API.py', os.path.join(os.path.dirname(sys.executable), "Lib\NOS_API.py"))
except:
    TEST_CREATION_API.display_message(str(error))

import NOS_API

try:
    # Get model
    model_type = NOS_API.get_model()

    # Check if folder with thresholds exists, if not create it
    if(os.path.exists(os.path.join(os.path.dirname(sys.executable), "Thresholds")) == False):
        os.makedirs(os.path.join(os.path.dirname(sys.executable), "Thresholds"))

    # Copy file with threshold if does not exists or if it is updated
    if ((os.path.exists(os.path.join(os.path.dirname(sys.executable), "Thresholds\\" + model_type + ".txt")) == False) or (str(os.path.getmtime(NOS_API.THRESHOLDS_PATH + model_type + ".txt")) != str(os.path.getmtime(os.path.join(os.path.dirname(sys.executable), "Thresholds\\" + model_type + ".txt"))))):
        shutil.copy2(NOS_API.THRESHOLDS_PATH + model_type + ".txt", os.path.join(os.path.dirname(sys.executable), "Thresholds\\" + model_type + ".txt"))
except Exception as error:
    pass
    
## Number of alphanumeric characters in SN
SN_LENGTH = 14

## Number of alphanumeric characters in Cas_Id
CASID_LENGTH = 12

## Number of alphanumeric characters in MAC
MAC_LENGTH = 12

def runTest():
    
    System_Failure = 0

    while (System_Failure < 2):    
        try:
            NOS_API.read_thresholds()
        
            error_codes = ""
            error_messages = ""
            ## Set test result default to FAIL
            test_result = "FAIL"
            SN_LABEL = False
            CASID_LABEL = False
            MAC_LABEL = False
            
            Software_Upgrade_TestCase = False
        
            Input_Signal_TestCase = False
        
            Serial_Number_TestCase = False
        
            ## Reset all global variables 
            NOS_API.reset_test_cases_results_info()          
            
            try:
                ## Perform scanning with barcode scanner   
                all_scanned_barcodes = NOS_API.get_all_scanned_barcodes()     
                NOS_API.test_cases_results_info.s_n_using_barcode = all_scanned_barcodes[1]
                NOS_API.test_cases_results_info.cas_id_using_barcode = all_scanned_barcodes[2]
                NOS_API.test_cases_results_info.mac_using_barcode = all_scanned_barcodes[3]
                NOS_API.test_cases_results_info.nos_sap_number = all_scanned_barcodes[0]
            except Exception as error:   
                TEST_CREATION_API.write_log_to_file(error)
                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.scan_error_code \
                                            + "; Error message: " + NOS_API.test_cases_results_info.scan_error_message)
                NOS_API.set_error_message("Leitura de Etiquetas")
                error_codes = NOS_API.test_cases_results_info.scan_error_code
                error_messages = NOS_API.test_cases_results_info.scan_error_message
                
                NOS_API.add_test_case_result_to_file_report(
                        test_result,
                        "- - - - - - - - - - - - - - - - - - - -",
                        "- - - - - - - - - - - - - - - - - - - -",
                        error_codes,
                        error_messages)
        
                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                report_file = NOS_API.create_test_case_log_file(
                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                    NOS_API.test_cases_results_info.nos_sap_number,
                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                    end_time)
                NOS_API.upload_file_report(report_file)      
                NOS_API.test_cases_results_info.isTestOK = False
                
                NOS_API.send_report_over_mqtt_test_plan(
                        test_result,
                        end_time,
                        error_codes,
                        report_file)
                        
                ## Update test result
                TEST_CREATION_API.update_test_result(test_result)
        
                return
            
            test_number = NOS_API.get_test_number(NOS_API.test_cases_results_info.s_n_using_barcode)
            device.updateUITestSlotInfo("Teste N\xb0: " + str(int(test_number)+1))
            
            if ((len(NOS_API.test_cases_results_info.s_n_using_barcode) == SN_LENGTH) and (NOS_API.test_cases_results_info.s_n_using_barcode.isalnum() or NOS_API.test_cases_results_info.s_n_using_barcode.isdigit()) and (NOS_API.test_cases_results_info.cas_id_using_barcode != NOS_API.test_cases_results_info.mac_using_barcode)):
                SN_LABEL = True
            
            if ((len(NOS_API.test_cases_results_info.cas_id_using_barcode) == CASID_LENGTH) and (NOS_API.test_cases_results_info.cas_id_using_barcode.isalnum() or NOS_API.test_cases_results_info.cas_id_using_barcode.isdigit())):
                CASID_LABEL = True
                
            if ((len(NOS_API.test_cases_results_info.mac_using_barcode) == MAC_LENGTH) and (NOS_API.test_cases_results_info.mac_using_barcode.isalnum() or NOS_API.test_cases_results_info.mac_using_barcode.isdigit())):
                MAC_LABEL = True
            
            if not(SN_LABEL and CASID_LABEL and MAC_LABEL):
                TEST_CREATION_API.write_log_to_file("Labels Scaning")
                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.scan_error_code \
                                            + "; Error message: " + NOS_API.test_cases_results_info.scan_error_message)
                NOS_API.set_error_message("Leitura de Etiquetas")
                error_codes = NOS_API.test_cases_results_info.scan_error_code
                error_messages = NOS_API.test_cases_results_info.scan_error_message
                
                NOS_API.add_test_case_result_to_file_report(
                            test_result,
                            "- - - - - - - - - - - - - - - - - - - -",
                            "- - - - - - - - - - - - - - - - - - - -",
                            error_codes,
                            error_messages)
        
                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                report_file = NOS_API.create_test_case_log_file(
                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                NOS_API.test_cases_results_info.nos_sap_number,
                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                NOS_API.test_cases_results_info.mac_using_barcode,
                                end_time)
            
                NOS_API.upload_file_report(report_file)
                NOS_API.test_cases_results_info.isTestOK = False
                                        
                NOS_API.send_report_over_mqtt_test_plan(
                        test_result,
                        end_time,
                        error_codes,
                        report_file)
                        
                ## Update test result
                TEST_CREATION_API.update_test_result(test_result)
                
                ## Return DUT to initial state and de-initialize grabber device
                #NOS_API.deinitialize()
                
                return    
                
##############################################################################################################################################################################################################################    
###########################################################################################Software Upgrade###################################################################################################################    
##############################################################################################################################################################################################################################
    
            if(System_Failure > 0):
                if (NOS_API.configure_power_switch_by_inspection()):
                    if not(NOS_API.power_off()):
                        TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                        
                        NOS_API.set_error_message("POWER SWITCH")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_switch_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.power_switch_error_message)
                        error_codes = NOS_API.test_cases_results_info.power_switch_error_code
                        error_messages = NOS_API.test_cases_results_info.power_switch_error_message
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        NOS_API.add_test_case_result_to_file_report(
                                test_result,
                                "- - - - - - - - - - - - - - - - - - - -",
                                "- - - - - - - - - - - - - - - - - - - -",
                                error_codes,
                                error_messages)
                    
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        report_file = NOS_API.create_test_case_log_file(
                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                    NOS_API.test_cases_results_info.nos_sap_number,
                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                    end_time)
                        NOS_API.upload_file_report(report_file)
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)
                        
                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        
                        return
                  
            ## Set test result default to FAIL
            test_result = "FAIL"
            SW_UPGRADE_TIMEOUT = 500
            ## Time needed to STB power on (in seconds)
            WAIT_TO_POWER_STB = 15
            ## Max time to perform sw upgrade (in seconds)
            WAIT_FOR_SEARCHING_SW = 600 
            ## Time out after stb power on 
            TIMEOUT_CAUSE_SW_UPGRADE = 20 
            
            upgrade = 0
            counter_black = 0        
            Tentativas_Act = 0       
            Num_Tentativas_Atualizcao = 6       
            HDMI_No_Repeat = 0        
            NOS_API.Upgrade_State = 0
            
            error_codes = ""
            error_messages = ""
            
            ######Input Signal################
            
            ## Threshold for ber value
            BER_VALUE_THRESHOLD = "1.0E-6"

            ## Threshold for snr value
            SNR_VALUE_THRESHOLD_LOW = 20
            SNR_VALUE_THRESHOLD_HIGH = 80
            
            snr_value = "-"
            ber_value = "-"
            frequencia = "-"
            modulation = "-"
            
            ######Serial Number################
            
            RX_THRESHOLD_LOW = -20
            RX_THRESHOLD_HIGH = 20
            TX_THRESHOLD = 60
            DOWNLOADSTREAM_SNR_THRESHOLD = 20
                
            tx_value = "-"
            rx_value = "-"
            downloadstream_snr_value = "-"
            ip_adress = "-"
            sc_number = "-"
            cas_id_number = "-"
            sw_version = "-"
            
            TEST_CREATION_API.write_log_to_file("####Software Upgrade####")

            if (NOS_API.configure_power_switch_by_inspection()):
                if not(NOS_API.power_on()):
                    TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                    
                    NOS_API.set_error_message("POWER SWITCH")
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_switch_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.power_switch_error_message)
                    error_codes = NOS_API.test_cases_results_info.power_switch_error_code
                    error_messages = NOS_API.test_cases_results_info.power_switch_error_message
                    ## Return DUT to initial state and de-initialize grabber device
                    NOS_API.deinitialize()
                    NOS_API.add_test_case_result_to_file_report(
                            test_result,
                            "- - - - - - - - - - - - - - - - - - - -",
                            "- - - - - - - - - - - - - - - - - - - -",
                            error_codes,
                            error_messages)
                
                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    report_file = NOS_API.create_test_case_log_file(
                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                NOS_API.test_cases_results_info.nos_sap_number,
                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                NOS_API.test_cases_results_info.mac_using_barcode,
                                end_time)
                    NOS_API.upload_file_report(report_file)
                    
                    NOS_API.send_report_over_mqtt_test_plan(
                        test_result,
                        end_time,
                        error_codes,
                        report_file)
                    
                    ## Update test result
                    TEST_CREATION_API.update_test_result(test_result)
                    
                    return
                  
                time.sleep(2)
            else:
                TEST_CREATION_API.write_log_to_file("Incorrect test place name")
                
                NOS_API.set_error_message("POWER SWITCH")
                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_switch_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.power_switch_error_message)
                error_codes = NOS_API.test_cases_results_info.power_switch_error_code
                error_messages = NOS_API.test_cases_results_info.power_switch_error_message
                ## Return DUT to initial state and de-initialize grabber device
                NOS_API.deinitialize()
                NOS_API.add_test_case_result_to_file_report(
                        test_result,
                        "- - - - - - - - - - - - - - - - - - - -",
                        "- - - - - - - - - - - - - - - - - - - -",
                        error_codes,
                        error_messages)
            
                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                report_file = NOS_API.create_test_case_log_file(
                            NOS_API.test_cases_results_info.s_n_using_barcode,
                            NOS_API.test_cases_results_info.nos_sap_number,
                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                            NOS_API.test_cases_results_info.mac_using_barcode,
                            end_time)
                NOS_API.upload_file_report(report_file)
                
                NOS_API.send_report_over_mqtt_test_plan(
                    test_result,
                    end_time,
                    error_codes,
                    report_file)
                    
                ## Update test result
                TEST_CREATION_API.update_test_result(test_result)
               
                return 
             
            if(System_Failure == 0):
                if not(NOS_API.display_new_dialog("Conectores?", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"): 
                    TEST_CREATION_API.write_log_to_file("Conectores NOK")
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.conector_nok_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.conector_nok_error_message)
                    NOS_API.set_error_message("Danos Externos")
                    error_codes = NOS_API.test_cases_results_info.conector_nok_error_code
                    error_messages = NOS_API.test_cases_results_info.conector_nok_error_message
                    
                    NOS_API.add_test_case_result_to_file_report(
                                test_result,
                                "- - - - - - - - - - - - - - - - - - - -",
                                "- - - - - - - - - - - - - - - - - - - -",
                                error_codes,
                                error_messages)
            
                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                    report_file = NOS_API.create_test_case_log_file(
                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                    NOS_API.test_cases_results_info.nos_sap_number,
                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                    end_time)
                
                    NOS_API.upload_file_report(report_file)
                    NOS_API.test_cases_results_info.isTestOK = False
                                            
                    NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)
                            
                    ## Update test result
                    TEST_CREATION_API.update_test_result(test_result)
                    
                    ## Return DUT to initial state and de-initialize grabber device
                    NOS_API.deinitialize()
                    
                    return    
                if not(NOS_API.display_new_dialog("Painel Traseiro?", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                    TEST_CREATION_API.write_log_to_file("Back Panel NOK")
                    NOS_API.set_error_message("Danos Externos")
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.back_panel_nok_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.back_panel_nok_error_message) 
                    error_codes = NOS_API.test_cases_results_info.back_panel_nok_error_code
                    error_messages = NOS_API.test_cases_results_info.back_panel_nok_error_message
                    
                    NOS_API.add_test_case_result_to_file_report(
                                test_result,
                                "- - - - - - - - - - - - - - - - - - - -",
                                "- - - - - - - - - - - - - - - - - - - -",
                                error_codes,
                                error_messages)
            
                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                    report_file = NOS_API.create_test_case_log_file(
                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                    NOS_API.test_cases_results_info.nos_sap_number,
                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                    end_time)
                
                    NOS_API.upload_file_report(report_file)
                    NOS_API.test_cases_results_info.isTestOK = False
                                            
                    NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)
                            
                    ## Update test result
                    TEST_CREATION_API.update_test_result(test_result)
                    
                    ## Return DUT to initial state and de-initialize grabber device
                    NOS_API.deinitialize()
                    
                    return     
                if not(NOS_API.display_custom_dialog("Inserir SmartCard! A STB est\xe1 ligada?", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):  
                    TEST_CREATION_API.write_log_to_file("No Power")
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.no_power_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.no_power_error_message) 
                    NOS_API.set_error_message("Não Liga") 
                    error_codes =  NOS_API.test_cases_results_info.no_power_error_code
                    error_messages = NOS_API.test_cases_results_info.no_power_error_message
                    NOS_API.deinitialize()
                    
                    NOS_API.add_test_case_result_to_file_report(
                            test_result,
                            "- - - - - - - - - - - - - - - - - - - -",
                            "- - - - - - - - - - - - - - - - - - - -",
                            error_codes,
                            error_messages)
                
                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    report_file = NOS_API.create_test_case_log_file(
                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                NOS_API.test_cases_results_info.nos_sap_number,
                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                NOS_API.test_cases_results_info.mac_using_barcode,
                                end_time)
                    NOS_API.upload_file_report(report_file)
                    
                    NOS_API.send_report_over_mqtt_test_plan(
                        test_result,
                        end_time,
                        error_codes,
                        report_file)
                        
                    ## Update test result
                    TEST_CREATION_API.update_test_result(test_result)

                    return
            
            NOS_API.grabber_hour_reboot()
            
            ## Initialize grabber device
            NOS_API.initialize_grabber()

            ## Start grabber device with video on default video source
            NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
            
            while(upgrade < 2):            
                if (upgrade == 1):
                    while(Tentativas_Act < Num_Tentativas_Atualizcao):
                        if (Tentativas_Act == 0):
                            #if not(NOS_API.change_usb_port("USBHUB-06##")):
                            NOS_API.Send_Serial_Key("a", "feito")
                            time.sleep(1) 
                        NOS_API.configure_power_switch_by_inspection()                          
                        if not(NOS_API.power_off()):
                            TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                            
                            NOS_API.set_error_message("POWER SWITCH")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_switch_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.power_switch_error_message)
                            error_codes = NOS_API.test_cases_results_info.power_switch_error_code
                            error_messages = NOS_API.test_cases_results_info.power_switch_error_message
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            NOS_API.add_test_case_result_to_file_report(
                                    test_result,
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    error_codes,
                                    error_messages)
                        
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            report_file = NOS_API.create_test_case_log_file(
                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                        NOS_API.test_cases_results_info.nos_sap_number,
                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                        end_time)
                            NOS_API.upload_file_report(report_file)
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
                                
                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            return
                        
                        time.sleep(2)
                        
                        if not(NOS_API.power_on()):
                            TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                            
                            NOS_API.set_error_message("POWER SWITCH")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_switch_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.power_switch_error_message)
                            error_codes = NOS_API.test_cases_results_info.power_switch_error_code
                            error_messages = NOS_API.test_cases_results_info.power_switch_error_message
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            NOS_API.add_test_case_result_to_file_report(
                                    test_result,
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    error_codes,
                                    error_messages)
                        
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            report_file = NOS_API.create_test_case_log_file(
                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                        NOS_API.test_cases_results_info.nos_sap_number,
                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                        end_time)
                            NOS_API.upload_file_report(report_file)
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
                                
                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            return
                            
                        time.sleep(TIMEOUT_CAUSE_SW_UPGRADE)
                        
                        if not(NOS_API.display_custom_dialog("A STB est\xe1 a atualizar?", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                            Tentativas_Act = Tentativas_Act + 1
                            if (Tentativas_Act == 5):
                                TEST_CREATION_API.write_log_to_file("Doesn't upgrade")    
                                
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)
                                NOS_API.set_error_message("Não Actualiza") 
                                error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                                NOS_API.deinitialize()
                                NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                            
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                                NOS_API.upload_file_report(report_file)
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                    
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                return
                        else:
                            NOS_API.Upgrade_State = 1
                            NOS_API.test_cases_results_info.DidUpgrade = 1
                            Tentativas_Act = 6
                            
                    WAIT_FOR_SEARCHING_SW = 700
                    
                #time.sleep(3)

                # Get start time
                start_time = time.localtime()
                delta_time = 0
                signal_detected_on_hdmi = False
                signal_detected_on_cvbs = False
                counter_ended = False
                while(counter_ended == False):
                    TEST_CREATION_API.write_log_to_file(delta_time)
                    if(delta_time > WAIT_FOR_SEARCHING_SW):
                        counter_ended = True
                        break

                    # Reset flags
                    signal_detected_on_hdmi = False
                    signal_detected_on_cvbs = False

                    # Get current time and check is testing finished
                    delta_time = (time.mktime(time.localtime()) - time.mktime(start_time))
                    
                    #time.sleep(2)
                                        
                    if not(NOS_API.is_signal_present_on_video_source()):
                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                        time.sleep(10)
                    
                    if (NOS_API.is_signal_present_on_video_source()):
                        time.sleep(5)
                        if (NOS_API.is_signal_present_on_video_source()):
                            result = NOS_API.wait_for_multiple_pictures(
                                            ["check_cables_HDMI", "Check_Por_Favor_HDMI", "Black_HDMI", "Black_HDMI_1080_ref"],
                                            4,
                                            ["[FULL_SCREEN_720]", "[FULL_SCREEN_576]", "[FULL_SCREEN_720]", "[FULL_SCREEN]"],
                                            [80, 70, 80, 80])
                            if(result == -1):
                                signal_detected_on_hdmi = True
                                signal_detected_on_cvbs = True
                                if not (NOS_API.grab_picture("HDMI_Image")):
                                    TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                    NOS_API.set_error_message("Video HDMI")
                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                    
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                                                            
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                            
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    return
                                break
                            elif(result == 2):
                                TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                time.sleep(4)
                                TEST_CREATION_API.send_ir_rc_command("[CH-]")
                                time.sleep(10)
                                TEST_CREATION_API.send_ir_rc_command("[CH+]")
                                time.sleep(2)
                    ## Start grabber device with video on CVBS2
                    NOS_API.grabber_stop_video_source()
                    NOS_API.reset_dut()
                    #time.sleep(2)
                    NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.CVBS2)
                    
                    if not(NOS_API.is_signal_present_on_video_source()):
                        TEST_CREATION_API.send_ir_rc_command("[POWER]")
                        time.sleep(10)
                    if (NOS_API.is_signal_present_on_video_source()):
                        time.sleep(5)
                        if (NOS_API.is_signal_present_on_video_source()):
                            result = NOS_API.wait_for_multiple_pictures_fast_picture_transition(
                                            ["black_screen_cvbs", "check_cables_CVBS", "Check_Por_Favor_CVBS", "Check_Por_Favor_CVBS_old", "Scart_Image_foggy_ref"],
                                            4,
                                            ["[FULL_SCREEN_576]", "[FULL_SCREEN_576]", "[FULL_SCREEN_576]", "[FULL_SCREEN_576]", "[FULL_SCREEN_576]"],
                                            [80, 40, 40, 40, 50])
                            if(result == -1):
                                signal_detected_on_cvbs = True
                                if not (NOS_API.grab_picture("Scart_Image")):
                                    ## if black screen or check power cable screen
                                    NOS_API.grabber_stop_video_source()
                                    NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                                    continue 
                                    #TEST_CREATION_API.write_log_to_file("No video SCART.")
                                    #NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.scart_image_absence_error_code \
                                    #                                        + "; Error message: " + NOS_API.test_cases_results_info.scart_image_absence_error_message)
                                    #error_codes = NOS_API.test_cases_results_info.scart_image_absence_error_code
                                    #error_messages = NOS_API.test_cases_results_info.scart_image_absence_error_message
                                    #NOS_API.set_error_message("Video Scart")
                                    #
                                    #NOS_API.add_test_case_result_to_file_report(
                                    #            test_result,
                                    #            "- - - - - - - - - - - - - - - - - - - -",
                                    #            "- - - - - - - - - - - - - - - - - - - -",
                                    #            error_codes,
                                    #            error_messages)
                                    #
                                    #end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    #report_file = NOS_API.create_test_case_log_file(
                                    #                NOS_API.test_cases_results_info.s_n_using_barcode,
                                    #                NOS_API.test_cases_results_info.nos_sap_number,
                                    #                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                    #                NOS_API.test_cases_results_info.mac_using_barcode,
                                    #                end_time)
                                    #
                                    #NOS_API.upload_file_report(report_file)
                                    #NOS_API.test_cases_results_info.isTestOK = False
                                    #                        
                                    #NOS_API.send_report_over_mqtt_test_plan(
                                    #        test_result,
                                    #        end_time,
                                    #        error_codes,
                                    #        report_file)
                                    #        
                                    ### Update test result
                                    #TEST_CREATION_API.update_test_result(test_result)
                                    #
                                    ### Return DUT to initial state and de-initialize grabber device
                                    #NOS_API.deinitialize()
                                    #
                                    #return
                            else:
                                ## if black screen or check power cable screen
                                NOS_API.grabber_stop_video_source()
                                NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                                continue 
                        else:
                            NOS_API.grabber_stop_video_source()
                            NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)                       
                            continue
                    else:
                        NOS_API.grabber_stop_video_source()
                        NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)                       
                        continue                    

                    ## Start grabber device with video on HDMI1
                    NOS_API.grabber_stop_video_source()
                    NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                    
                    time.sleep(1)
                    
                    if not(NOS_API.is_signal_present_on_video_source()):
                        NOS_API.display_dialog("Confirme o cabo HDMI e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                        time.sleep(2)
                        HDMI_No_Repeat = 1
                        #if not(NOS_API.is_signal_present_on_video_source()):
                        #    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                        #time.sleep(10)
                    if (NOS_API.is_signal_present_on_video_source()):
                        time.sleep(5)
                        if (NOS_API.is_signal_present_on_video_source()):
                            result = NOS_API.wait_for_multiple_pictures(
                                            ["check_cables_HDMI", "Check_Por_Favor_HDMI", "Black_HDMI", "Black_HDMI_1080_ref"],
                                            4,
                                            ["[FULL_SCREEN_720]", "[FULL_SCREEN_576]", "[FULL_SCREEN_720]", "[FULL_SCREEN]"],
                                            [80, 70, 80, 80])
                            if(result == -1):
                                signal_detected_on_hdmi = True
                                if not (NOS_API.grab_picture("HDMI_Image")):
                                    TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                    NOS_API.set_error_message("Video HDMI")
                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                    
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                                                            
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                            
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    return
                            elif((result == 2 or result == 3) and signal_detected_on_cvbs == True):
                                counter_black = counter_black + 1  
                                time.sleep(10)
                                if (counter_black < 2):
                                    continue
                            elif(result == 0 or result == 1 or result == -2):
                                continue
                    else:
                        ## Start grabber device with video on CVBS2
                        NOS_API.grabber_stop_video_source()
                        NOS_API.reset_dut()

                        NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.CVBS2)
                        time.sleep(2)
                        if not(NOS_API.is_signal_present_on_video_source()):
                            NOS_API.grabber_stop_video_source()
                            NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                            continue 
                        
                    if((signal_detected_on_hdmi == False) and (signal_detected_on_cvbs == True)):
                        if (HDMI_No_Repeat == 1):
                            TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                            NOS_API.set_error_message("Video HDMI (Não Retestar)")
                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                            
                            NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
            
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                        
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False
                                                    
                            NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                    
                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            return
                        else:
                            TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                            NOS_API.set_error_message("Video HDMI")
                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                            
                            NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
            
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                        
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False
                                                    
                            NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                    
                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            return                

                    if((signal_detected_on_hdmi == True) and (signal_detected_on_cvbs == True)):
                        break

                if(counter_ended == True):
                    TEST_CREATION_API.write_log_to_file("No boot")
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.no_boot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.no_boot_error_message)
                    NOS_API.set_error_message("Não arranca")
                    error_codes =  NOS_API.test_cases_results_info.no_boot_error_code
                    error_messages = NOS_API.test_cases_results_info.no_boot_error_message
                    NOS_API.add_test_case_result_to_file_report(
                                test_result,
                                "- - - - - - - - - - - - - - - - - - - -",
                                "- - - - - - - - - - - - - - - - - - - -",
                                error_codes,
                                error_messages)

                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                    report_file = NOS_API.create_test_case_log_file(
                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                    NOS_API.test_cases_results_info.nos_sap_number,
                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                    end_time)
                
                    NOS_API.upload_file_report(report_file)
                    NOS_API.test_cases_results_info.isTestOK = False
                                            
                    NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)
                            
                    ## Update test result
                    TEST_CREATION_API.update_test_result(test_result)
                    
                    ## Return DUT to initial state and de-initialize grabber device
                    NOS_API.deinitialize()
                    
                    return   
                   
                if((signal_detected_on_hdmi == True) and (signal_detected_on_cvbs == True)):
                    
                    #time.sleep(5)
                                    
                    start_time_standby_mode = time.localtime()
                    delta_time_standby = 0
                    delta_check = 60
                    while (delta_time_standby < SW_UPGRADE_TIMEOUT):
                        delta_time_standby = (time.mktime(time.localtime()) - time.mktime(start_time_standby_mode))     
                        if (NOS_API.is_signal_present_on_video_source()):                        
                        
                            compare_result = NOS_API.wait_for_multiple_pictures(
                                                                ["Block_Image_ref", "sw_upgrade_loop_3_ref", "sw_upgrade_loop_3_eng_ref", "sw_update_loop_1_720p", "sw_update_loop_1_1080p", "sw_update_loop_2_720p", "sw_update_loop_2_720p_SD", "UMA_Inst_ref", "SW_UMA_error_ref", "UMA_No_Ch_ref", "Color_Channel_ref", "Old_Sw_Message_ref", "Inst_Nagra_ref", "Inst_Nagra_Eng_ref", "Old_Sw_Channel_ref", "Old_Shiftted_Inst_Error_ref", "No_Signal_Nagra_ref", "Old_Shiffted_Channel_ref", "Old_Shiftted_Installation_ref", "Old_SW_Shiftted_ref", "Old_SW_Shiftted_signal_ref", "Old_SW_Shiftted_Eng_ref", "sw_update_error_720p", "sw_update_error1_720p", "sw_update_error2_720p", "Message_Error_No_Channel_ref", "sd_service_720p_ref1", "sd_service_720p_ref2", "sd_service_ref1", "sd_service_ref2", "hd_channel_ref", "hd_channel_ref1", "no_signal_channel_mode_ref", "no_signal_channel_mode_2_ref", "no_signal_channel_mode_720_ref", "no_signal_channel_mode_2_720_ref", "error_message_1080_ref", "menu_576_ref", "menu_720_ref", "menu_1080_ref", "No_Channel_1", "installation_boot_up_ref", "language_installation_mode_ref", "installation_text_installation_mode_ref", "english_installation", "english_termos", "english_language_installation_ref", "installation_boot_up_ref_old", "installation_boot_up_ref_old_1", "Inst_Success_ref", "installation_boot_up_ref_old_2"],
                                                                delta_check,
                                                                ["[FULL_SCREEN]", "[SW_UPDATE_LOOP_3]", "[SW_UPDATE_LOOP_3]", "[SW_UPDATE_LOOP_1_720p]", "[SW_UPDATE_LOOP_1_1080p]", "[SW_UPDATE_LOOP_720p]", "[SW_UPDATE_LOOP_720p]", "[UMA_Inst_1080]", "[SW_UMA_ERROR]", "[UMA_No_Ch_1080]", "[Uma_Sw_Channel]", "[Old_Sw_Message]", "[Inst_Nagra_720]", "[Inst_Nagra_720]", "[HALF_SCREEN_SD_CH_1080p]", "[Old_Shiftted_Inst_Error]", "[No_Signal_Nagra]", "[Old_Shiftted_Channel]", "[Old_Shiftted_Installation]", "[Old_SW_Shiftted_ref]", "[Old_SW_Shiftted_Signal_ref]", "[Old_SW_Shiftted_ref]", "[SW_UPDATE_ERROR_720p]", "[SW_UPDATE_ERROR_720p]", "[SW_UPDATE_ERROR_720p]", "[Message_Error_No_Channel]", "[HALF_SCREEN]", "[HALF_SCREEN]", "[HALF_SCREEN_SD_CH_1080p]", "[HALF_SCREEN_SD_CH_1080p]", "[HALF_SCREEN_HD]", "[HALF_SCREEN_HD]", "[NO_SIGNAL_CHANNEL_MODE]", "[NO_SIGNAL_CHANNEL_MODE]", "[NO_SIGNAL_CHANNEL_MODE_720p]", "[NO_SIGNAL_CHANNEL_MODE_720p]", "[NO_SIGNAL_CHANNEL_MODE]", "[MENU_576]", "[MENU_720]", "[MENU_1080]", "[No_Channel_1]", "[FTI_AFTER_SW_UPGRADE]", "[LANGUAGE_INSTALLATION_MODE]", "[INSTALLATION_TEXT_FTI]", "[INSTALLATION_ENGLISH]", "[ENGLISH_TERMOS]", "[ENGLISH_INSTALLATION_LANGUAGE]", "[FTI_AFTER_SW_UPGRADE_OLD]", "[FTI_AFTER_SW_UPGRADE_OLD_1]", "[Inst_Success]", "[FTI_AFTER_SW_UPGRADE]"],
                                                                [80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 30, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80])                       

                            if(compare_result == 1 or compare_result == 2 or compare_result == 3 or compare_result == 4 or compare_result >= 41):
                                NOS_API.test_cases_results_info.channel_boot_up_state = False
                                time.sleep(2)
                                Software_Upgrade_TestCase = True
                                #test_result = "PASS"
                                upgrade = 2
                            elif(compare_result == 7 or compare_result == 8 or compare_result == 9):
                                TEST_CREATION_API.write_log_to_file("Incorrect SW - UMA")
        
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.Incorret_SW_UMA_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.Incorret_SW_UMA_error_message)                                        
                                NOS_API.set_error_message("Sw Incorreto - UMA") 
                                error_codes =  NOS_API.test_cases_results_info.Incorret_SW_UMA_error_code
                                error_messages = NOS_API.test_cases_results_info.Incorret_SW_UMA_error_message                               
                                test_result = "FAIL"
                                upgrade = 2
                            elif(compare_result >= 10 and compare_result < 22):
                                if (upgrade == 0):
                                    upgrade = upgrade + 1
                                else:
                                    TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
            
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                    NOS_API.set_error_message("Não Actualiza") 
                                    error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message                               
                                    test_result = "FAIL"
                                    upgrade = 2
                            elif(compare_result == 22 or compare_result == 23 or compare_result == 24):
                                if (upgrade == 0):
                                    upgrade = upgrade + 1
                                else:
                                    TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
            
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                    NOS_API.set_error_message("Não Actualiza") 
                                    error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                                    upgrade = 2
                                    test_result = "FAIL"
                            elif(compare_result == 5 or compare_result == 6 or compare_result >= 25 and compare_result < 41):
                                NOS_API.test_cases_results_info.channel_boot_up_state = True
                                
                                result = NOS_API.wait_for_multiple_pictures(
                                                                    ["error_channel_mode_ref"],
                                                                    45,
                                                                    ["[ERROR_CHANNEL_MODE]"],
                                                                    [80])
                                if(result == -2):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return    
                                if(result != -1):
                                    if (upgrade == 0):
                                        upgrade = upgrade + 1
                                    else:
                                        TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
            
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                        NOS_API.set_error_message("Não Actualiza") 
                                        error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message      
                                        upgrade = 2
                                else:
                                    Software_Upgrade_TestCase = True
                                    #test_result = "PASS"
                                    upgrade = 2
                                                                
                            else:
                                delta_time_standby = (time.mktime(time.localtime()) - time.mktime(start_time_standby_mode))
                                
                                if(delta_time_standby < SW_UPGRADE_TIMEOUT):
                                    
                                    TEST_CREATION_API.send_ir_rc_command("[BACK]")
                                    TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                    TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                    time.sleep(4)
                                    continue
                                if(compare_result == 0):
                                    TEST_CREATION_API.write_log_to_file("STB Blocks on Installation")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.block_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.block_error_message )
                                    NOS_API.set_error_message("STB bloqueou")
                                    error_codes = NOS_API.test_cases_results_info.block_error_code
                                    error_messages = NOS_API.test_cases_results_info.block_error_message 
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return
                                
                                result = NOS_API.wait_for_multiple_pictures(
                                        ["searching_for_sw_576_ref", "Check_Por_Favor_CVBS", "Check_Por_Favor_CVBS_old", "searching_for_sw_720_ref", "searching_for_sw_1080_ref", "Por_Favor_Shifted"],
                                        3,
                                        ["[SEARCH_SW_HDMI_576]", "[FULL_SCREEN_576]", "[FULL_SCREEN_576]", "[SEARCH_SW_HDMI_720]", "[SEARCH_SW_HDMI_1080]", "[Por_Favor_Shifted]"],
                                        [30,30,30,80,80,80])
                                if(result == -2):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return        
                                if(result != -1):
                                    TEST_CREATION_API.write_log_to_file("No boot")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.no_boot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.no_boot_error_message)
                                    NOS_API.set_error_message("Não arranca")
                                    error_codes =  NOS_API.test_cases_results_info.no_boot_error_code
                                    error_messages = NOS_API.test_cases_results_info.no_boot_error_message
                                    upgrade = 2
                                else: 
                                    TEST_CREATION_API.write_log_to_file("Image is not reproduced correctly on HDMI.")
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_message)
                                    error_codes = NOS_API.test_cases_results_info.hdmi_720p_noise_error_code
                                    error_messages = NOS_API.test_cases_results_info.hdmi_720p_noise_error_message
                                    NOS_API.set_error_message("Video HDMI")
                                    upgrade = 2
                            
                            delta_time_standby = (time.mktime(time.localtime()) - time.mktime(start_time_standby_mode))  
                            break
                        else:
                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                            time.sleep(5)
                            if (NOS_API.is_signal_present_on_video_source()):
                                continue
                            time.sleep(10)
                    
                    # If STB didn't power on
                    if(delta_time_standby > SW_UPGRADE_TIMEOUT):
                        if not(NOS_API.is_signal_present_on_video_source()):
                            TEST_CREATION_API.write_log_to_file("No boot")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.no_boot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.no_boot_error_message)
                            NOS_API.set_error_message("Não arranca")
                            error_codes =  NOS_API.test_cases_results_info.no_boot_error_code
                            error_messages = NOS_API.test_cases_results_info.no_boot_error_message
                            Software_Upgrade_TestCase = False
                            upgrade = 2
                 

            if (NOS_API.test_cases_results_info.DidUpgrade == 1):
                #if not(NOS_API.change_usb_port("USBHUB-10##")):
                NOS_API.Send_Serial_Key("d", "feito")
                    
        ##############################################################################################################################################################################################################################    
        #############################################################################################Input Signal#####################################################################################################################    
        ##############################################################################################################################################################################################################################
                
            if(Software_Upgrade_TestCase):    
                TEST_CREATION_API.write_log_to_file("####Input Signal####")
                
                ## Threshold for ber value
                BER_VALUE_THRESHOLD = "1.0E-6"

                ## Threshold for snr value
                SNR_VALUE_THRESHOLD_LOW = 20
                SNR_VALUE_THRESHOLD_HIGH = 80
                
                snr_value = "-"
                ber_value = "-"
                frequencia = "-"
                modulation = "-"
                    
                ## Set test result default to FAIL
                test_result = "FAIL"
                test_result_boot = True
                sw_version_prod = NOS_API.Firmware_Version_DCR_7151
                iris_version_prod = NOS_API.IRIS_Version_DCR_7151
                
                SW_UPGRADE_TIMEOUT = 500

                ## Time needed to STB power on (in seconds)
                WAIT_TO_POWER_STB = 15
                
                ## Max time to perform sw upgrade (in seconds)
                WAIT_FOR_SEARCHING_SW = 700
                
                ## Time out after stb power on 
                TIMEOUT_CAUSE_SW_UPGRADE = 20
                
                upgrade = 0
                
                counter_black = 0
                
                Tentativas_Act = 0
                
                Num_Tentativas_Atualizacao = 6
                
                error_codes = ""
                error_messages = ""

                while (upgrade < 2):
                    if (upgrade == 1 and NOS_API.Upgrade_State == 0):
                        test_result = "FAIL"
                        test_result_boot = False
                            
                        while(Tentativas_Act < Num_Tentativas_Atualizacao):
                            if (Tentativas_Act == 0):
                                #if not(NOS_API.change_usb_port("USBHUB-06##")):
                                NOS_API.Send_Serial_Key("a", "feito")
                            NOS_API.configure_power_switch_by_inspection()
                            if not(NOS_API.power_off()):
                                TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                                
                                NOS_API.set_error_message("POWER SWITCH")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_switch_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.power_switch_error_message)
                                error_codes = NOS_API.test_cases_results_info.power_switch_error_code
                                error_messages = NOS_API.test_cases_results_info.power_switch_error_message
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                            
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                                NOS_API.upload_file_report(report_file)
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                    
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                return
                            
                            time.sleep(2)
                            
                            if not(NOS_API.power_on()):
                                TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                                
                                NOS_API.set_error_message("POWER SWITCH")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_switch_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.power_switch_error_message)
                                error_codes = NOS_API.test_cases_results_info.power_switch_error_code
                                error_messages = NOS_API.test_cases_results_info.power_switch_error_message
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                            
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                                NOS_API.upload_file_report(report_file)
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                return
                                
                            time.sleep(TIMEOUT_CAUSE_SW_UPGRADE)
                            
                            if not(NOS_API.display_custom_dialog("A STB est\xe1 a atualizar?", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                                Tentativas_Act = Tentativas_Act + 1
                                if (Tentativas_Act == 5):
                                    TEST_CREATION_API.write_log_to_file("Doesn't upgrade")

                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)
                                    NOS_API.set_error_message("Não Actualiza") 
                                    error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                                    NOS_API.deinitialize()
                                    NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                                
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                    NOS_API.upload_file_report(report_file)
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                        
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    return
                            else:
                                NOS_API.test_cases_results_info.DidUpgrade = 1
                                Tentativas_Act = 6
                            
                        time.sleep(3)
            
                        # Get start time
                        start_time = time.localtime()
                        delta_time = 0
                        signal_detected_on_hdmi = False
                        signal_detected_on_cvbs = False
                        counter_ended = False
                        while(counter_ended == False):
                            if(delta_time > WAIT_FOR_SEARCHING_SW):
                                counter_ended = True
                                break
            
                            # Reset flags
                            signal_detected_on_hdmi = False
                            signal_detected_on_cvbs = False
            
                            # Get current time and check is testing finished
                            delta_time = (time.mktime(time.localtime()) - time.mktime(start_time))
                            
                            time.sleep(2)
                                                
                            if not(NOS_API.is_signal_present_on_video_source()):
                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                time.sleep(10)
                            
                            if (NOS_API.is_signal_present_on_video_source()):
                                time.sleep(5)
                                if (NOS_API.is_signal_present_on_video_source()):
                                    result = NOS_API.wait_for_multiple_pictures(
                                                    ["check_cables_HDMI", "Check_Por_Favor_HDMI", "Black_HDMI"],
                                                    3,
                                                    ["[FULL_SCREEN_720]", "[FULL_SCREEN_576]", "[FULL_SCREEN_720]"],
                                                    [80, 70, 80])
                                    if(result == -1):
                                        signal_detected_on_hdmi = True
                                        signal_detected_on_cvbs = True
                                        if not (NOS_API.grab_picture("HDMI_Image")):
                                            TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                            NOS_API.set_error_message("Video HDMI")
                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                            
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                        
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                                                                    
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                    
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            return
                                        break
            
                            ## Start grabber device with video on CVBS2
                            TEST_CREATION_API.grabber_stop_source()
                            NOS_API.reset_dut()
                            #time.sleep(2)
                            NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.CVBS2)
                            
                            if not(NOS_API.is_signal_present_on_video_source()):
                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                time.sleep(10)
                            if (NOS_API.is_signal_present_on_video_source()):
                                time.sleep(5)
                                if (NOS_API.is_signal_present_on_video_source()):
                                    result = NOS_API.wait_for_multiple_pictures_fast_picture_transition(
                                                    ["black_screen_cvbs", "check_cables_CVBS", "Check_Por_Favor_CVBS", "Check_Por_Favor_CVBS_old", "Scart_Image_foggy_ref"],
                                                    4,
                                                    ["[FULL_SCREEN_576]", "[FULL_SCREEN_576]", "[FULL_SCREEN_576]", "[FULL_SCREEN_576]", "[FULL_SCREEN_576]"],
                                                    [80, 40, 40, 40, 50])
                                    if(result == -1):
                                        signal_detected_on_cvbs = True
                                        if not (NOS_API.grab_picture("Scart_Image")):
                                            TEST_CREATION_API.write_log_to_file("No video SCART.")
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.scart_image_absence_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.scart_image_absence_error_message)
                                            error_codes = NOS_API.test_cases_results_info.scart_image_absence_error_code
                                            error_messages = NOS_API.test_cases_results_info.scart_image_absence_error_message
                                            NOS_API.set_error_message("Video Scart")
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                            
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                        
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                                                                    
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                    
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            return
                                    else:
                                        ## if black screen or check power cable screen
                                        TEST_CREATION_API.grabber_stop_source()
                                        NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                                        continue 
                                else:
                                    TEST_CREATION_API.grabber_stop_source()
                                    NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)                       
                                    continue
                            else:
                                TEST_CREATION_API.grabber_stop_source()
                                NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)                       
                                continue                    
            
                            ## Start grabber device with video on HDMI1
                            TEST_CREATION_API.grabber_stop_source()
                            NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                            
                            time.sleep(5)
                            
                            if not(NOS_API.is_signal_present_on_video_source()):
                                NOS_API.display_dialog("Confirme o cabo HDMI e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                                time.sleep(4)
                                if not(NOS_API.is_signal_present_on_video_source()):
                                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                time.sleep(10)
                            if (NOS_API.is_signal_present_on_video_source()):
                                time.sleep(5)
                                if (NOS_API.is_signal_present_on_video_source()):
                                    result = NOS_API.wait_for_multiple_pictures(
                                                    ["check_cables_HDMI", "Check_Por_Favor_HDMI", "Black_HDMI"],
                                                    3,
                                                    ["[FULL_SCREEN_720]", "[FULL_SCREEN_576]", "[FULL_SCREEN_720]"],
                                                    [80, 70, 80])
                                    if(result == -1):
                                        signal_detected_on_hdmi = True
                                        if not (NOS_API.grab_picture("HDMI_Image")):
                                            TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                            NOS_API.set_error_message("Video HDMI")
                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                            
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                        
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                                                                    
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                    
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            return
                                    elif(result == 2 and signal_detected_on_cvbs == True):
                                        counter_black = counter_black + 1  
                                        time.sleep(10)
                                        if (counter_black < 2):
                                            continue
                                    elif(result == 0 or result == 1 or result == 2):
                                        continue
                            if((signal_detected_on_hdmi == False) and (signal_detected_on_cvbs == True)):
                                TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                NOS_API.set_error_message("Video HDMI")
                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                
                                NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                            
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False
                                                        
                                NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                        
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                return                
            
                            if((signal_detected_on_hdmi == True) and (signal_detected_on_cvbs == True)):
                                break
            
                        if(counter_ended == True):
                            TEST_CREATION_API.write_log_to_file("No boot")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.no_boot_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.no_boot_error_message)
                            NOS_API.set_error_message("Não arranca")
                            error_codes =  NOS_API.test_cases_results_info.no_boot_error_code
                            error_messages = NOS_API.test_cases_results_info.no_boot_error_message
                            NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
            
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                        
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False
                                                    
                            NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                    
                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            return  
                                    
                        if((signal_detected_on_hdmi == True) and (signal_detected_on_cvbs == True)):
                            
                            time.sleep(5)
                                            
                            start_time_standby_mode = time.localtime()
                            delta_time_standby = 0
                            delta_check = 60
                            while (delta_time_standby < SW_UPGRADE_TIMEOUT):
                                delta_time_standby = (time.mktime(time.localtime()) - time.mktime(start_time_standby_mode))     
                                if (NOS_API.is_signal_present_on_video_source()):                        
                                
                                    compare_result = NOS_API.wait_for_multiple_pictures(
                                                                        ["sw_upgrade_loop_3_ref", "sw_upgrade_loop_3_eng_ref", "sw_update_loop_1_720p", "sw_update_loop_2_720p", "sw_update_loop_2_720p_SD", "sw_update_error_720p", "sd_service_720p_ref1", "sd_service_720p_ref2", "sd_service_ref1", "sd_service_ref2", "hd_channel_ref", "hd_channel_ref1", "no_signal_channel_mode_ref", "no_signal_channel_mode_2_ref", "no_signal_channel_mode_720_ref", "no_signal_channel_mode_2_720_ref", "error_message_1080_ref", "menu_576_ref", "menu_720_ref", "menu_1080_ref", "No_Channel_1", "installation_boot_up_ref", "language_installation_mode_ref", "installation_text_installation_mode_ref", "english_installation", "english_termos", "english_language_installation_ref", "installation_boot_up_ref_old", "installation_boot_up_ref_old_1", "Inst_after_upgrade_ref"],
                                                                        delta_check,
                                                                        ["[SW_UPDATE_LOOP_3]", "[SW_UPDATE_LOOP_3]", "[SW_UPDATE_LOOP_720p]", "[SW_UPDATE_LOOP_720p]", "[SW_UPDATE_LOOP_720p]", "[SW_UPDATE_ERROR_720p]", "[HALF_SCREEN]", "[HALF_SCREEN]", "[HALF_SCREEN_SD_CH_1080p]", "[HALF_SCREEN_SD_CH_1080p]", "[HALF_SCREEN_HD]", "[HALF_SCREEN_HD]", "[NO_SIGNAL_CHANNEL_MODE]", "[NO_SIGNAL_CHANNEL_MODE]", "[NO_SIGNAL_CHANNEL_MODE_720p]", "[NO_SIGNAL_CHANNEL_MODE_720p]", "[NO_SIGNAL_CHANNEL_MODE]", "[MENU_576]", "[MENU_720]", "[MENU_1080]", "[No_Channel_1]", "[FTI_AFTER_SW_UPGRADE]", "[LANGUAGE_INSTALLATION_MODE]", "[INSTALLATION_TEXT_FTI]", "[INSTALLATION_ENGLISH]", "[ENGLISH_TERMOS]", "[ENGLISH_INSTALLATION_LANGUAGE]", "[FTI_AFTER_SW_UPGRADE_OLD]", "[FTI_AFTER_SW_UPGRADE_OLD_1]", "[Inst_Success]"],
                                                                        [80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 30, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 80])                       
            
                                    if(compare_result == 0 or compare_result == 1 or compare_result == 2 or compare_result >= 21):
                                        NOS_API.test_cases_results_info.channel_boot_up_state = False 
                                        time.sleep(5)
                                        test_result_boot = True
                                        upgrade = 2
                                    elif(compare_result == 5):                               
                                        TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                        NOS_API.set_error_message("Não Actualiza") 
                                        error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message                               
                                        test_result = "FAIL"
                                        NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                        
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                    
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                                                                
                                        NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                                
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        return                           
                                    elif(compare_result == 3 or compare_result == 4 or compare_result >= 6 and compare_result < 21):
                                        NOS_API.test_cases_results_info.channel_boot_up_state = True
                                        
                                        result = NOS_API.wait_for_multiple_pictures(
                                                                            ["error_channel_mode_ref"],
                                                                            20,
                                                                            ["[ERROR_CHANNEL_MODE]"],
                                                                            [80])
                                            
                                        if(result == -2):
                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                            NOS_API.set_error_message("Reboot")
                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                            
                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                            
                                            return
                                        if(result != -1):
                                            TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                            NOS_API.set_error_message("Não Actualiza") 
                                            error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                                            NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                            
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                        
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                                                                    
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                    
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            return                                   
                                        else:
                                            test_result_boot = True
                                            upgrade = 2
                                                                        
                                    else:
                                        delta_time_standby = (time.mktime(time.localtime()) - time.mktime(start_time_standby_mode))
                                        
                                        if(delta_time_standby < SW_UPGRADE_TIMEOUT):
                                        
                                            TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                            TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                            time.sleep(2)
                                            continue
                                    
                                        result = NOS_API.wait_for_multiple_pictures(
                                                ["searching_for_sw_576_ref", "Check_Por_Favor_CVBS", "Check_Por_Favor_CVBS_old", "searching_for_sw_720_ref", "searching_for_sw_1080_ref", "Por_Favor_Shifted"],
                                                3,
                                                ["[SEARCH_SW_HDMI_576]", "[FULL_SCREEN_576]", "[FULL_SCREEN_576]", "[SEARCH_SW_HDMI_720]", "[SEARCH_SW_HDMI_1080]", "[Por_Favor_Shifted]"],
                                                [30,30,30,80,80,80])
                                        
                                        if(result == -2):
                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                            NOS_API.set_error_message("Reboot")
                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                            
                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                            
                                            return
                                        if(result != -1):
                                            TEST_CREATION_API.write_log_to_file("No boot")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.no_boot_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.no_boot_error_message)
                                            NOS_API.set_error_message("Não arranca")
                                            error_codes =  NOS_API.test_cases_results_info.no_boot_error_code
                                            error_messages = NOS_API.test_cases_results_info.no_boot_error_message
                                            NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                            
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                        
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                                                                    
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                    
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            return
                                        else:                            
                                            TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                            NOS_API.set_error_message("Video HDMI")
                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                            NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                            
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                        
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                                                                    
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                    
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            return
                                    
                                    delta_time_standby = (time.mktime(time.localtime()) - time.mktime(start_time_standby_mode))  
                                    break
                                else:
                                    TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                    time.sleep(5)
                                    if (NOS_API.is_signal_present_on_video_source()):
                                        continue
                                    time.sleep(10)
                            
                            # If STB didn't power on
                            if(delta_time_standby > SW_UPGRADE_TIMEOUT):
                                if not(NOS_API.is_signal_present_on_video_source()):
                                    TEST_CREATION_API.write_log_to_file("No boot")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.no_boot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.no_boot_error_message)
                                    NOS_API.set_error_message("Não arranca")
                                    error_codes =  NOS_API.test_cases_results_info.no_boot_error_code
                                    error_messages = NOS_API.test_cases_results_info.no_boot_error_message
                                    NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                    
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                                                            
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                            
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    return
                        
                    if (NOS_API.is_signal_present_on_video_source() and test_result_boot):
                        ## Check state of STB
                        if (NOS_API.test_cases_results_info.channel_boot_up_state):
                            time.sleep(5)
                            TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                            time.sleep(3)
                    
                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                            
                            TEST_CREATION_API.send_ir_rc_command("[MENU]")
                            time.sleep(1)
                            if not (NOS_API.grab_picture("Check_Nagra")):
                                TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                NOS_API.set_error_message("Video HDMI")
                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                
                                NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                            
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False
                                                        
                                NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                        
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                return
                            
                            if (video_height == "720"):
                                video_result = NOS_API.compare_pictures("Check_Nagra_720_ref", "Check_Nagra", "[Check_Nagra_720]")
                                video_result_1 = NOS_API.compare_pictures("Check_UMA_720_ref", "Check_Nagra", "[Check_UMA_720]")
                                video_result_oposite = NOS_API.compare_pictures("Old_Menu_720_ref", "Check_Nagra", "[Old_Menu_720]")
                            elif (video_height == "1080"):
                                video_result = NOS_API.compare_pictures("Check_Nagra_1080_ref", "Check_Nagra", "[Check_Nagra_1080]")
                                video_result_1 = NOS_API.compare_pictures("Check_UMA_1080_ref", "Check_Nagra", "[Check_UMA_1080]")
                                video_result_oposite = NOS_API.compare_pictures("Old_Menu_1080_ref", "Check_Nagra", "[Old_Menu_1080]")
                            elif (video_height == "576"):
                                video_result == NOS_API.compare_pictures("Check_Nagra_576_ref", "Check_Nagra", "[Check_Nagra_576]")
                            
                            if (video_height == "720" and video_result >= 80 or video_height == "1080" and video_result >= 80 or video_height == "576" and video_result >= 50):
                                if (upgrade == 0 and NOS_API.Upgrade_State == 0):
                                    upgrade = upgrade + 1
                                    continue
                                else:                       
                                    TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                    NOS_API.set_error_message("Não Actualiza") 
                                    error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message 
                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    report_file = ""    
                    
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                    
                                    return
                            
                            if (video_height == "1080" and video_result_1 >= 80 or video_height == "720" and video_result_1 >= 80):
                                TEST_CREATION_API.write_log_to_file("Incorrect SW - UMA")
                                
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.Incorret_SW_UMA_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.Incorret_SW_UMA_error_message)                                        
                                NOS_API.set_error_message("Sw Incorreto - UMA") 
                                error_codes =  NOS_API.test_cases_results_info.Incorret_SW_UMA_error_code
                                error_messages = NOS_API.test_cases_results_info.Incorret_SW_UMA_error_message  
                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                report_file = ""    
                
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                
                                return
                            
                            if (video_result_oposite > 80):
                                if (upgrade == 0 and NOS_API.Upgrade_State == 0):
                                    upgrade = upgrade + 1
                                    continue
                                else:                       
                                    TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                    NOS_API.set_error_message("Não Actualiza") 
                                    error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message 
                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    report_file = ""    
                    
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                    
                                    return
                            
                            TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                            
                            ## Check is resolution different than 1080i
                            if (video_height != "1080"):
                                time.sleep(1)
                                TEST_CREATION_API.send_ir_rc_command("[RESOLUTION_SETTINGS]")
                                if (video_height == "720"):
                                    if not (NOS_API.grab_picture("Resolution_720_Confirmation")):
                                        TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                        NOS_API.set_error_message("Video HDMI")
                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                        
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                    
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                                                                
                                        NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                                
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        return
                                    comparassion_result = NOS_API.compare_pictures("Resolution_Confirmation_ref", "Resolution_720_Confirmation", "[Resolution_Confirmation]")
                                    comparassion_result_1 = NOS_API.compare_pictures("Resolution_Confirmation_1_ref", "Resolution_720_Confirmation", "[Resolution_Confirmation]")
                                    if (comparassion_result >= 80 or comparassion_result_1 >= 80):
                                        TEST_CREATION_API.send_ir_rc_command("[Confirm_720]")
                                        TEST_CREATION_API.send_ir_rc_command("[ReNavigate_Resolution_Settings]")
                                TEST_CREATION_API.send_ir_rc_command("[SET_1080i_FROM_MENU_new]")
                                time.sleep(1)
                                if not (NOS_API.grab_picture("Resolution_Print")):
                                    TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                    NOS_API.set_error_message("Video HDMI")
                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                    
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                                                            
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                            
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    return
                                TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX_NEW]")
                                time.sleep(1)
                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                if (video_height != "1080"):
                                    TEST_CREATION_API.write_log_to_file("STB Resolution: " + video_height)
                                    TEST_CREATION_API.send_ir_rc_command("[RESOLUTION_SETTINGS]")
                                    if (video_height == "720"):
                                        if not (NOS_API.grab_picture("Resolution_720_Confirmation")):
                                            TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                            NOS_API.set_error_message("Video HDMI")
                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                            
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                        
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                                                                    
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                    
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            return
                                        comparassion_result = NOS_API.compare_pictures("Resolution_Confirmation_ref", "Resolution_720_Confirmation", "[Resolution_Confirmation]")
                                        comparassion_result_1 = NOS_API.compare_pictures("Resolution_Confirmation_1_ref", "Resolution_720_Confirmation", "[Resolution_Confirmation]")
                                        if (comparassion_result >= 80 or comparassion_result_1 >= 80):
                                            TEST_CREATION_API.send_ir_rc_command("[Confirm_720]")
                                            TEST_CREATION_API.send_ir_rc_command("[ReNavigate_Resolution_Settings]")
                                    TEST_CREATION_API.send_ir_rc_command("[SET_1080i_FROM_MENU]")
                                    time.sleep(1)
                                    if not (NOS_API.grab_picture("Resolution_Second_Print")):
                                        TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                        NOS_API.set_error_message("Video HDMI")
                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                        
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                    
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                                                                
                                        NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                                
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        return
                                    TEST_CREATION_API.send_ir_rc_command("[BACK_3]")
                                    video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                    TEST_CREATION_API.write_log_to_file("STB Resolution: " + video_height)
                                    if (video_height != "1080"):
                                        NOS_API.set_error_message("Resolução")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.resolution_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.resolution_error_message) 
                                        error_codes = NOS_API.test_cases_results_info.resolution_error_code
                                        error_messages = NOS_API.test_cases_results_info.resolution_error_message
                                        NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - " + str(modulation) + " " + str(frequencia) + " -",
                                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        report_file = ""    
                        
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                                    
                                        return
                                TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                time.sleep(5)
                            ## Check language
                            TEST_CREATION_API.send_ir_rc_command("[SETTINGS]")
                            result = NOS_API.wait_for_multiple_pictures(["settings_english_language_ref", "settings_english_language_no_signal_ref"], 5, ["[ENGLISH_LANGUAGE_DETECTED]", "[ENGLISH_LANGUAGE_DETECTED]"], [80, 80])
                            if(result == -2):
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                
                                return
                            if (result != -1):
                                
                                #TEST_CREATION_API.send_ir_rc_command("[SET_PORTUGAL]")
                                
                                TEST_CREATION_API.send_ir_rc_command("[LANGUAGE_SCREEN]")                    
                                result = NOS_API.wait_for_multiple_pictures(["language_screen_ref", "language_screen_no_signal_ref", "language_screen_english_ref", "language_screen_english_no_signal_ref"], 5, ["[LANGUAGE_SCREEN]", "[LANGUAGE_SCREEN]", "[LANGUAGE_SCREEN]", "[LANGUAGE_SCREEN]"], [80, 80, 80, 80])
                                if(result == -2):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return
                                if (result == -1):
                                    TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX]")
                                    TEST_CREATION_API.send_ir_rc_command("[LANGUAGE_SCREEN_REPEAT]") 
                                    result = NOS_API.wait_for_multiple_pictures(["language_screen_ref", "language_screen_no_signal_ref", "language_screen_english_ref", "language_screen_english_no_signal_ref"], 5, ["[LANGUAGE_SCREEN]", "[LANGUAGE_SCREEN]", "[LANGUAGE_SCREEN]", "[LANGUAGE_SCREEN]"], [80, 80, 80, 80])
                                    if(result == -2):
                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                        NOS_API.set_error_message("Reboot")
                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                        
                                        return
                                    if (result == -1):
                                        TEST_CREATION_API.write_log_to_file("Doesn't Navigate to right place")
                                        NOS_API.set_error_message("Navegação")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                                        error_codes = NOS_API.test_cases_results_info.navigation_error_code
                                        error_messages = NOS_API.test_cases_results_info.navigation_error_message
                                        NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - " + str(modulation) + " " + str(frequencia) + " -",
                                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        report_file = ""    
                        
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)                           
                                                    
                                        return
                                                        
                                TEST_CREATION_API.send_ir_rc_command("[SET_PORTUGAL_FROM_LANGUAGE_SCREEN]")
                                time.sleep(1)
                                
                            TEST_CREATION_API.send_ir_rc_command("[Check_Upgrade]")
                            result = NOS_API.wait_for_multiple_pictures(["sw_version_ref", "sw_version_ref_old", "sw_version_black_ref"], 5, ["[SW_VERSION_SCREEN]", "[SW_VERSION_SCREEN_Two]", "[SW_VERSION_SCREEN]"], [70, 70, 70])
                            if(result == -2):
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                
                                return
                            if (result == -1):
                                if not (NOS_API.grab_picture("Sw_Version_First_Navigation")):
                                    TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                    NOS_API.set_error_message("Video HDMI")
                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                    
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                                                            
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                            
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    return
                                TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX]")
                                TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                time.sleep(5)
                                TEST_CREATION_API.send_ir_rc_command("[Check_Upgrade_Scnd]") 
                                result = NOS_API.wait_for_multiple_pictures(["sw_version_ref", "sw_version_ref_old", "sw_version_black_ref"], 5, ["[SW_VERSION_SCREEN]", "[SW_VERSION_SCREEN_Two]", "[SW_VERSION_SCREEN]"], [70, 70, 70])
                                if(result == -2):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return
                                if (result == -1):
                                    TEST_CREATION_API.write_log_to_file("Doesn't Navigate to right place")
                                    NOS_API.set_error_message("Navegação")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                                    error_codes = NOS_API.test_cases_results_info.navigation_error_code
                                    error_messages = NOS_API.test_cases_results_info.navigation_error_message
                                    NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - " + str(modulation) + " " + str(frequencia) + " -",
                                                                ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    report_file = ""    
                    
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)                           
                                                
                                    return
                            if not(NOS_API.grab_picture("STB_Version")):
                                TEST_CREATION_API.write_log_to_file("HDMI NOK")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                NOS_API.set_error_message("Video HDMI")
                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                report_file = ""    
                
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                
                                return
                            ## Get IRIS version from menu
                            iris_version = TEST_CREATION_API.OCR_recognize_text("STB_Version", "[IRIS_VERSION]", "[OCR_FILTER]")
                            NOS_API.test_cases_results_info.iris_version = iris_version
                            TEST_CREATION_API.write_log_to_file("IRIS version: " + iris_version)
                            NOS_API.update_test_slot_comment("IRIS version: " + iris_version)
                            ## Get SoftWare version from menu
                            sw_version = TEST_CREATION_API.OCR_recognize_text("STB_Version", "[SOFTWARE_VERSION]", "[OCR_FILTER]", "sw_version")
                            TEST_CREATION_API.write_log_to_file("The extracted sc version is: " + sw_version)
                            NOS_API.update_test_slot_comment("SW version: " + NOS_API.test_cases_results_info.firmware_version)
                            NOS_API.test_cases_results_info.firmware_version = str(sw_version)
                            
                            if not(sw_version == sw_version_prod and iris_version == iris_version_prod):
                                if (upgrade == 0 and NOS_API.Upgrade_State == 0):
                                    upgrade = upgrade + 1
                                    continue
                                else:        
                                    TEST_CREATION_API.write_log_to_file("upgrade variable: " + str(upgrade))
                                    TEST_CREATION_API.write_log_to_file("Upgrade_State variable: " + str(NOS_API.Upgrade_State))
                                    TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                    NOS_API.set_error_message("Não Actualiza") 
                                    error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                    error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message 
                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    report_file = ""    
                    
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                    
                                    return
                            TEST_CREATION_API.send_ir_rc_command("[SIGNAL_VALUE_NEW_Ch]")
                            result = NOS_API.wait_for_multiple_pictures(["rede_screen_ref", "rede_screen_no_signal_ref"], 5, ["[REDE_SCREEN]", "[REDE_SCREEN]"], [80, 80])
                            if(result == -2):
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                
                                return
                            if (result == -1):
                                TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX]")
                                TEST_CREATION_API.send_ir_rc_command("[SIGNAL_VALUE_NEW]")
                                time.sleep(2)
                                TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                time.sleep(2)
                                result = NOS_API.wait_for_multiple_pictures(["rede_screen_ref", "rede_screen_no_signal_ref"], 5, ["[REDE_SCREEN]", "[REDE_SCREEN]"], [80, 80])
                                if(result == -2):
                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                    NOS_API.set_error_message("Reboot")
                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                    test_result = "FAIL"
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    report_file = ""
                                    if (test_result != "PASS"):
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                    
                                    return
                                if (result == -1):
                                    TEST_CREATION_API.write_log_to_file("Navigation to rede screen failed")
                                    
                                    NOS_API.set_error_message("Navegação")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                                    error_codes = NOS_API.test_cases_results_info.navigation_error_code
                                    error_messages = NOS_API.test_cases_results_info.navigation_error_message
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    report_file = ""    
                    
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                    
                                    return
                    
                            ## OCR macros
                            #macro_snr =  "[SNR_CHANNEL_BOOT_UP_STATE]"
                            macro_snr =  "[SNR_CHANNEL_BOOT_UP_STATE_1]" # if write: POWER: xdbmV
                            macro_ber =  "[BER_CHANNEL_BOOT_UP_STATE]"
                            
                            TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                            time.sleep(2)
                            
                        else:
                            if not(NOS_API.grab_picture("Check_Signal_Menu")):
                                TEST_CREATION_API.write_log_to_file("HDMI NOK")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                NOS_API.set_error_message("Video HDMI")
                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                test_result = "FAIL"
                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                report_file = ""    
                
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                                
                                return
                            
                            if not(TEST_CREATION_API.compare_pictures("installation_boot_up_ref", "Check_Signal_Menu", "[Check_Signal_Menu]") or TEST_CREATION_API.compare_pictures("english_installation", "Check_Signal_Menu", "[Check_Signal_Menu]")):
                                ## Navigate to the first screen in FTI
                                TEST_CREATION_API.send_ir_rc_command("[NAVIGATE_FTI_SCREEN]")
                    
                            ## OCR macros
                            macro_snr =  "[SNR_INSTALLATION_BOOT_UP_STATE_1]"
                            macro_ber =  "[BER_INSTALLATION_BOOT_UP_STATE]"
                            
                    
                        ## Perform grab picture              
                        if (NOS_API.grab_picture("signal_value")):
                            
                            if (TEST_CREATION_API.compare_pictures("Inst_block_ref", "signal_value", "[Inst_block]") or TEST_CREATION_API.compare_pictures("Inst_block_eng_ref", "signal_value", "[Inst_block]")):
                                TEST_CREATION_API.write_log_to_file("STB Blocks")

                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.block_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.block_error_message)
                                NOS_API.set_error_message("STB bloqueou")
                                error_codes = NOS_API.test_cases_results_info.block_error_code
                                error_messages = NOS_API.test_cases_results_info.block_error_message
                                NOS_API.deinitialize()
                                
                                NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                            
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                                NOS_API.upload_file_report(report_file)
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                            
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                return
                            try:               
                                ## Extract snr text from image
                                snr_value = NOS_API.fix_snr_power_dcr7151(NOS_API.replace_letter_o_with_number_0(TEST_CREATION_API.OCR_recognize_text("signal_value", macro_snr, "[OCR_FILTER]", "Signal_Value")))  ## POWER text
                                TEST_CREATION_API.write_log_to_file("Snr value: " + snr_value)
                                NOS_API.update_test_slot_comment("Snr value: " + snr_value)
                            
                                snr_value = float(snr_value[:(snr_value.find('d'))])
                                NOS_API.test_cases_results_info.power = str(snr_value)
                                
                            except Exception as error:
                                ## Set test result to INCONCLUSIVE
                                TEST_CREATION_API.write_log_to_file(str(error))
                                snr_value = 0
                                NOS_API.test_cases_results_info.power = "-"
                                
                            if (snr_value <= SNR_VALUE_THRESHOLD_LOW or snr_value >= SNR_VALUE_THRESHOLD_HIGH):
                                if (NOS_API.test_cases_results_info.channel_boot_up_state):
                                    result = NOS_API.wait_for_multiple_pictures(["rede_screen_ref", "rede_screen_no_signal_ref"], 5, ["[REDE_SCREEN]", "[REDE_SCREEN]"], [80, 80])
                                    if(result == -2):
                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                        NOS_API.set_error_message("Reboot")
                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                        test_result = "FAIL"
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                        
                                        return
                                    if (result == -1):
                                        TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX]")
                                        TEST_CREATION_API.send_ir_rc_command("[SIGNAL_VALUE_NEW]")
                                        time.sleep(2)
                                        TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                        time.sleep(2)
                                        result = NOS_API.wait_for_multiple_pictures(["rede_screen_ref", "rede_screen_no_signal_ref"], 5, ["[REDE_SCREEN]", "[REDE_SCREEN]"], [80, 80])
                                        if(result == -2):
                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                            NOS_API.set_error_message("Reboot")
                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                            
                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                            
                                            return
                                        if (result == -1):
                                            TEST_CREATION_API.write_log_to_file("Navigation to rede screen failed")
                                            
                                            NOS_API.set_error_message("Navegação")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                                            error_codes = NOS_API.test_cases_results_info.navigation_error_code
                                            error_messages = NOS_API.test_cases_results_info.navigation_error_message
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                                            test_result,
                                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                                            ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                            error_codes,
                                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                            report_file = ""    
                            
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                            
                                            return
                                    else:
                                        TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                NOS_API.display_custom_dialog("Confirme Cabo RF e restantes cabos", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG)
                                time.sleep(5)
                                if not(NOS_API.is_signal_present_on_video_source()):
                                    time.sleep(5)
                                if (NOS_API.grab_picture("signal_value")):
                                    try:             
                                        
                                        ## Extract snr text from image
                                        snr_value = NOS_API.fix_snr_power_dcr7151(NOS_API.replace_letter_o_with_number_0(TEST_CREATION_API.OCR_recognize_text("signal_value", macro_snr, "[OCR_FILTER]", "Signal_Value_2")))  ## POWER text
                                        TEST_CREATION_API.write_log_to_file("Snr value: " + snr_value)
                                        NOS_API.update_test_slot_comment("Snr value: " + snr_value)
                                    
                                        snr_value = float(snr_value[:(snr_value.find('d'))])
                                        
                                        NOS_API.test_cases_results_info.power = str(snr_value)
                                            
                                        
                                    except Exception as error:
                                        ## Set test result to INCONCLUSIVE
                                        TEST_CREATION_API.write_log_to_file(str(error))
                                        snr_value = 0
                                        NOS_API.test_cases_results_info.power = "-"
                                    
                                else:
                                    TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                    NOS_API.set_error_message("Video HDMI")
                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                    
                                    NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    str(snr_value) + " " + str(ber_value) + " - - - - - - - - - - - - - - - " + str(modulation) + " " + str(frequencia) + " -",
                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    report_file = ""    
                    
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    
                                    ## Update test result
                                    TEST_CREATION_API.update_test_result(test_result)
                                    
                                    ## Return DUT to initial state and de-initialize grabber device
                                    NOS_API.deinitialize()
                                    
                                    NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)
                                    
                                    return
                                
                            
                            try:
                                ## Extract ber text from image
                                ber_value = TEST_CREATION_API.OCR_recognize_text("signal_value", macro_ber, "[OCR_FILTER]")
                                ber_value = NOS_API.fix_ber(ber_value)
                                TEST_CREATION_API.write_log_to_file("BER value: " + ber_value)
                                NOS_API.update_test_slot_comment("BER value: " + ber_value)
                                NOS_API.test_cases_results_info.ber = str(ber_value)
                            except Exception as error:
                                ## Set test result to INCONCLUSIVE
                                TEST_CREATION_API.write_log_to_file(str(error))
                                ber_value = "-"
                                NOS_API.test_cases_results_info.ber = "-"
                                
                            if (NOS_API.test_cases_results_info.channel_boot_up_state):
                                try:
                                    frequencia = TEST_CREATION_API.OCR_recognize_text("signal_value", "[FREQUENCIA]", "[OCR_FILTER]")
                                    NOS_API.test_cases_results_info.freq = str(frequencia)
                                    modulation = TEST_CREATION_API.OCR_recognize_text("signal_value", "[MODULATION]", "[OCR_FILTER]")
                                    NOS_API.test_cases_results_info.modulation = str(modulation)
                                    NOS_API.update_test_slot_comment("Frequencia: " + frequencia)
                                    NOS_API.update_test_slot_comment("Modulation: " + modulation)
                                except Exception as error:
                                    ## Set test result to INCONCLUSIVE
                                    TEST_CREATION_API.write_log_to_file(str(error))
                            
                            ## Check if snr value higher than threshold
                            if (snr_value > SNR_VALUE_THRESHOLD_LOW and snr_value < SNR_VALUE_THRESHOLD_HIGH):
                                ## Check if ber value higher than threshold
                                if (NOS_API.check_ber(ber_value, BER_VALUE_THRESHOLD)):
                                    Input_Signal_TestCase = True
                                    #test_result = "PASS"
                                    
                                    if not(NOS_API.test_cases_results_info.channel_boot_up_state):      
                                        
                                        TEST_CREATION_API.send_ir_rc_command("[BACK]")
                                        time.sleep(2)
                                        TEST_CREATION_API.send_ir_rc_command("[OK]")
                                        TEST_CREATION_API.send_ir_rc_command("[UP]")
                                        TEST_CREATION_API.send_ir_rc_command("[OK]") 
                                        
                                        result = NOS_API.wait_for_multiple_pictures(["error_instalation_mode_ref", "error_instalation_mode_ref_old"], 5, ["[ERROR_INSTALLATION_MODE]", "[ERROR_INSTALLATION_MODE]"], [80, 80])
                                        if(result == -2):
                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                            NOS_API.set_error_message("Reboot")
                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                            
                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                            
                                            return
                                        if (result != -1):
                                            if (upgrade == 0 and NOS_API.Upgrade_State == 0):
                                                upgrade = upgrade + 1                                        
                                                continue
                                            else:
                                                TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                            
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                                NOS_API.set_error_message("Não Actualiza") 
                                                error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                                error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                                                
                                                test_result = "FAIL"
                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    str(snr_value) + " " + str(ber_value) + " - - - - - - - - - - - - - - - " + str(modulation) + " " + str(frequencia) + " -",
                                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                report_file = ""    
                                
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                
                                                return                              
                                                
            
                                        ch_installation_fti = False
                                        result = NOS_API.wait_for_multiple_pictures(["channel_installation_fti_finished_ref"], 120, ["[CHANNEL_INSTALLATION_FINISH_FTI]"], [80])
                                        if(result == -2):
                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                            NOS_API.set_error_message("Reboot")
                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                            
                            
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                            
                                            return
                                        if (result == -1):
                                            result = NOS_API.wait_for_multiple_pictures(["channel_installtion_failed_ref"], 3, ["[CHANNEL_INSTALLATION_FINISH_FTI]"], [80])
                                            if(result == -2):
                                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                NOS_API.set_error_message("Reboot")
                                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                
                                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                
                                                return
                                            if (result != -1):
                                                TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                    
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                    
                                                NOS_API.set_error_message("Não Actualiza") 
                                                error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                                error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message
                                                test_result = "FAIL"
                                                Input_Signal_TestCase = False
                                                upgrade = 2
                                            else:
                                                TEST_CREATION_API.send_ir_rc_command("[NAVIGATE_FTI_SCREEN]")
                                                TEST_CREATION_API.send_ir_rc_command("[EXIT_SIGNAL_VALUE_SCREEN_INSTALLATION_BOOT_UP_1_NEW]")
                                                result = NOS_API.wait_for_multiple_pictures(["channel_installation_fti_finished_ref", "channel_installation_fti_finished_2nd_ref"], 120, ["[CHANNEL_INSTALLATION_FINISH_FTI]", "[CHANNEL_INSTALLATION_FINISH_FTI]"], [80, 80])
                                                if(result == -2):
                                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                    NOS_API.set_error_message("Reboot")
                                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                    
                                                    return
                                                if (result == -1):
                                                    TEST_CREATION_API.write_log_to_file("STB doesn't receive IR commands.")
                    
                                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                    NOS_API.set_error_message("IR")
                                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message
                                                    test_result = "FAIL"
                                                    Input_Signal_TestCase = False
                                                    upgrade = 2
                                                else:
                                                    ch_installation_fti = True
                                        else:
                                            ch_installation_fti = True
                                        
                                        if (ch_installation_fti == True):
                                            TEST_CREATION_API.send_ir_rc_command("[OK]")
                                            time.sleep(2)
                                            TEST_CREATION_API.send_ir_rc_command("[OK]")
                                            time.sleep(24)
                                            
                                            TEST_CREATION_API.send_ir_rc_command("[BACK]")
                                            time.sleep(5)
                                            
                                            TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                            time.sleep(3)
                                            
                                            TEST_CREATION_API.send_ir_rc_command("[Check_Upgrade_Inst]")
                                            result = NOS_API.wait_for_multiple_pictures(["sw_version_ref", "sw_version_ref_old"], 5, ["[SW_VERSION_SCREEN]", "[SW_VERSION_SCREEN_Two]"], [70, 70])
                                            if(result == -2):
                                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                NOS_API.set_error_message("Reboot")
                                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                
                                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                
                                                return
                                            if (result == -1):
                                                TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX]")
                                                time.sleep(1)
                                                TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                                time.sleep(3)
                                                TEST_CREATION_API.send_ir_rc_command("[Check_Upgrade_Scnd]") 
                                                result = NOS_API.wait_for_multiple_pictures(["sw_version_ref", "sw_version_ref_old"], 5, ["[SW_VERSION_SCREEN]", "[SW_VERSION_SCREEN_Two]"], [70, 70])
                                                if(result == -2):
                                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                    NOS_API.set_error_message("Reboot")
                                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                    test_result = "FAIL"
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                    
                                                    return
                                                if (result == -1):
                                                    TEST_CREATION_API.write_log_to_file("Doesn't Navigate to right place")
                                                    NOS_API.set_error_message("Navegação")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                                                    error_codes = NOS_API.test_cases_results_info.navigation_error_code
                                                    error_messages = NOS_API.test_cases_results_info.navigation_error_message
                                                    test_result = "FAIL"
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                                test_result,
                                                                                "- - - - - - - - - - - - - - - - - " + str(modulation) + " " + str(frequencia) + " -",
                                                                                ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                                error_codes,
                                                                                error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                    report_file = ""    
                                    
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)                           
                                                                
                                                    return
                                            if not(NOS_API.grab_picture("STB_Version")):
                                                TEST_CREATION_API.write_log_to_file("HDMI NOK")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                NOS_API.set_error_message("Video HDMI")
                                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                test_result = "FAIL"
                                                NOS_API.add_test_case_result_to_file_report(
                                                                                test_result,
                                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                                ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                                error_codes,
                                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                report_file = ""    
                                
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                
                                                return
                                            ## Get IRIS version from menu
                                            iris_version = TEST_CREATION_API.OCR_recognize_text("STB_Version", "[IRIS_VERSION]", "[OCR_FILTER]")
                                            NOS_API.test_cases_results_info.iris_version = iris_version
                                            TEST_CREATION_API.write_log_to_file("IRIS version: " + iris_version)
                                            NOS_API.update_test_slot_comment("IRIS version: " + iris_version)
                                            ## Get SoftWare version from menu
                                            sw_version = TEST_CREATION_API.OCR_recognize_text("STB_Version", "[SOFTWARE_VERSION]", "[OCR_FILTER]", "sw_version")
                                            TEST_CREATION_API.write_log_to_file("The extracted sc version is: " + sw_version)
                                            NOS_API.update_test_slot_comment("SW version: " + NOS_API.test_cases_results_info.firmware_version)
                                            NOS_API.test_cases_results_info.firmware_version = str(sw_version)
                                            
                                            if not(sw_version == sw_version_prod and iris_version == iris_version_prod):
                                                if (upgrade == 0 and NOS_API.Upgrade_State == 0):
                                                    upgrade = upgrade + 1
                                                    continue
                                                else:                       
                                                    TEST_CREATION_API.write_log_to_file("Doesn't upgrade")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.upgrade_nok_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.upgrade_nok_error_message)                                        
                                                    NOS_API.set_error_message("Não Actualiza") 
                                                    error_codes =  NOS_API.test_cases_results_info.upgrade_nok_error_code
                                                    error_messages = NOS_API.test_cases_results_info.upgrade_nok_error_message 
                                                    test_result = "FAIL"
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                                    test_result,
                                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                                    error_codes,
                                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                    report_file = ""    
                                    
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                    
                                                    return

                                            ## Navigate to the screen to check frequency and modulation
                                            TEST_CREATION_API.send_ir_rc_command("[SIGNAL_VALUE_NEW_Ch]")
                                            result = NOS_API.wait_for_multiple_pictures(["rede_screen_ref"], 5, ["[REDE_SCREEN]"], [80])
                                            if(result == -2):
                                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                NOS_API.set_error_message("Reboot")
                                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                
                                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                
                                                return
                                            if (result == -1):
                                                TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX]")
                                                TEST_CREATION_API.send_ir_rc_command("[SIGNAL_VALUE_NEW]")
                                                result = NOS_API.wait_for_multiple_pictures(["rede_screen_ref"], 5, ["[REDE_SCREEN]"], [80])
                                                if(result == -2):
                                                    TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                    NOS_API.set_error_message("Reboot")
                                                    error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                    error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                    
                                                    return
                                                if (result == -1):
                                                    TEST_CREATION_API.write_log_to_file("Navigation to rede screen failed")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                                                    error_codes = NOS_API.test_cases_results_info.navigation_error_code
                                                    error_messages = NOS_API.test_cases_results_info.navigation_error_message
                                                    NOS_API.set_error_message("Navegação")
                                                    
                                                    test_result = "FAIL"
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    str(snr_value) + " " + str(ber_value) + " - - - - - - - - - - - - - - - " + str(modulation) + " " + str(frequencia) + " -",
                                                                    ">50<70 <1.0E-6 - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                    report_file = ""    
                                    
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                    
                                                    return
                                                    
                                            TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                                            time.sleep(2)
                                            if (NOS_API.grab_picture("freq_mod")):
                                                try:
                                                    frequencia = TEST_CREATION_API.OCR_recognize_text("freq_mod", "[FREQUENCIA]", "[OCR_FILTER]")
                                                    NOS_API.test_cases_results_info.freq = str(frequencia)
                                                    modulation = TEST_CREATION_API.OCR_recognize_text("freq_mod", "[MODULATION]", "[OCR_FILTER]")
                                                    NOS_API.test_cases_results_info.modulation = str(modulation)
                                                    NOS_API.update_test_slot_comment("Frequencia: " + frequencia)
                                                    NOS_API.update_test_slot_comment("Modulation: " + modulation)
                                                except Exception as error:
                                                    ## Set test result to INCONCLUSIVE
                                                    TEST_CREATION_API.write_log_to_file(str(error))
                                            else:
                                                TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                NOS_API.set_error_message("Video HDMI")
                                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                test_result = "FAIL"
                                                Input_Signal_TestCase = False
                                                upgrade = 2

                                    TEST_CREATION_API.send_ir_rc_command("[EXIT_SIGNAL_VALUE_SCREEN_CHANNEL_BOOT_UP_NEW]")
                                    upgrade = 2                
                                else:
                                    TEST_CREATION_API.write_log_to_file("BER value is lower than threshold")
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ber_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.ber_error_message)
                                    NOS_API.set_error_message("BER") 
                                    
                                    error_codes = NOS_API.test_cases_results_info.ber_error_code
                                    error_messages = NOS_API.test_cases_results_info.ber_error_message
                                    Input_Signal_TestCase = False
                                    upgrade = 2
                            else:
                                TEST_CREATION_API.write_log_to_file("SNR value is lower than threshold")
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.snr_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.snr_error_message)
                                NOS_API.set_error_message("SNR")
                                error_codes = NOS_API.test_cases_results_info.snr_error_code
                                error_messages = NOS_API.test_cases_results_info.snr_error_message
                                Input_Signal_TestCase = False
                                upgrade = 2
                        else:
                            TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                            NOS_API.set_error_message("Video HDMI")
                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                            Input_Signal_TestCase = False
                            upgrade = 2
                            
                        TEST_CREATION_API.send_ir_rc_command("[EXIT_SIGNAL_VALUE_SCREEN_CHANNEL_BOOT_UP_NEW]")
                        TEST_CREATION_API.send_ir_rc_command("[EXIT_SIGNAL_VALUE_SCREEN_CHANNEL_BOOT_UP_NEW]")
                        upgrade = 2
                    else:
                        TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                        NOS_API.set_error_message("Video HDMI")
                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                        Input_Signal_TestCase = False
                        upgrade = 2
                    
                if (NOS_API.test_cases_results_info.DidUpgrade == 1):    
                    #if not(NOS_API.change_usb_port("USBHUB-10##")):
                    NOS_API.Send_Serial_Key("d", "feito")
                
        ##############################################################################################################################################################################################################################    
        #############################################################################################Serial Number####################################################################################################################    
        ##############################################################################################################################################################################################################################
                
            if(Input_Signal_TestCase): 
                TEST_CREATION_API.write_log_to_file("####Serial Number####")
            
                RX_THRESHOLD_LOW = -20
                RX_THRESHOLD_HIGH = 20
                TX_THRESHOLD = 60
                DOWNLOADSTREAM_SNR_THRESHOLD = 20
                    
                tx_value = "-"
                rx_value = "-"
                downloadstream_snr_value = "-"
                ip_adress = "-"
                sc_number = "-"
                cas_id_number = "-"
                sw_version = "-"
                
                ##########Bebug Telnet###############
                ##error_command_telnet = False
                ##stb_state = False
                ##timeout_telnet = False
                ##first_telnet_test = False
                #####################################

                ## Set test result default to FAIL
                test_result = "FAIL"
                
                error_codes = ""
                error_messages = ""
                
                timer = 0
                
                sw_version_prod = NOS_API.Firmware_Version_DCR_7151
                iris_version_prod = NOS_API.IRIS_Version_DCR_7151
                
                ##############################################################################First Telnet Test##############################################################################
                ##cmd = 'Show cable modem ' + NOS_API.test_cases_results_info.mac_using_barcode
                ###Get start time
                ##startTime = time.localtime()
                ##sid = NOS_API.get_session_id()
                ##while (True):
                ##    response = NOS_API.send_cmd_to_telnet(sid, cmd)
                ##    TEST_CREATION_API.write_log_to_file("response:" + str(response))
                ##    if(response != None):
                ##        if(response.find("Error:") != -1):
                ##            error_command_telnet = True
                ##            break
                ##        if(response == "connect timed out"):
                ##            sn = NOS_API.test_cases_results_info.s_n_using_barcode
                ##            slot = NOS_API.slot_index(NOS_API.get_test_place_name())
                ##            docsisInc = "N"
                ##            
                ##            f = open("C:\\Program Files (x86)\\RT-RK\\RT-Executor Diagnostic Station\\Test_Support\\DocsisInconsistences.txt", "a")
                ##            f.write(sn + " " + slot + " " + docsisInc + "\n")
                ##            f.close()
                ##            NOS_API.quit_session(sid)
                ##            time.sleep(1)
                ##            sid = NOS_API.get_session_id()
                ##            response = NOS_API.send_cmd_to_telnet(sid, cmd)
                ##            TEST_CREATION_API.write_log_to_file("response:" + str(response))
                ##            if(response != None):
                ##                if(response.find("Error:") != -1):
                ##                    error_command_telnet = True
                ##                    break
                ##                if(response == "connect timed out"):
                ##                    TEST_CREATION_API.write_log_to_file("Connect TimeOut")   
                ##                    break
                ##                if(response != "BUSY"):
                ##                    stb_state = NOS_API.is_stb_operational(response)
                ##                    break
                ##            else:
                ##                TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                ##                break
                ##        if(response != "BUSY"):
                ##            stb_state = NOS_API.is_stb_operational(response)
                ##            break    
                ##    else:
                ##        TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                ##        break
                ##        
                ##    time.sleep(5)
                ##        
                ##    #Get current time
                ##    currentTime = time.localtime()
                ##    if((time.mktime(currentTime) - time.mktime(startTime)) > NOS_API.MAX_WAIT_TIME_RESPOND_FROM_TELNET):
                ##        TEST_CREATION_API.write_log_to_file("30s exceeded")
                ##        timeout_telnet = True
                ##        break
                ##
                ##if(error_command_telnet == False):
                ##    if(stb_state == True):    
                ##        cmd = 'Show cable modem ' + NOS_API.test_cases_results_info.mac_using_barcode + ' verbose'
                ##        startTime = time.localtime()
                ##        while (True):
                ##            response = NOS_API.send_cmd_to_telnet(sid, cmd)
                ##            TEST_CREATION_API.write_log_to_file("response:" + str(response))                
                ##            
                ##            if(response != None and response != "BUSY" and response != "connect timed out"):
                ##                data = NOS_API.parse_telnet_cmd1(response)
                ##                break
                ##            if(response == None):
                ##                TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                ##                break
                ##            
                ##            if(response == "connect timed out"):
                ##                sn = NOS_API.test_cases_results_info.s_n_using_barcode
                ##                slot = NOS_API.slot_index(NOS_API.get_test_place_name())
                ##                docsisInc = "N"
                ##                
                ##                f = open("C:\\Program Files (x86)\\RT-RK\\RT-Executor Diagnostic Station\\Test_Support\\DocsisInconsistences.txt", "a")
                ##                f.write(sn + " " + slot + " " + docsisInc + "\n")
                ##                f.close()
                ##                NOS_API.quit_session(sid)
                ##                time.sleep(1)
                ##                sid = NOS_API.get_session_id()
                ##                response = NOS_API.send_cmd_to_telnet(sid, cmd)
                ##                TEST_CREATION_API.write_log_to_file("response:" + str(response))                
                ##            
                ##                if(response != None and response != "BUSY" and response != "connect timed out"):
                ##                    data = NOS_API.parse_telnet_cmd1(response)
                ##                    break
                ##                if(response == None):
                ##                    TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                ##                    break
                ##                
                ##                if(response == "connect timed out"):
                ##                    TEST_CREATION_API.write_log_to_file("Connect TimeOut")
                ##                    break
                ##                
                ##            time.sleep(5)
                ##                
                ##            #Get current time
                ##            currentTime = time.localtime()
                ##            if((time.mktime(currentTime) - time.mktime(startTime)) > NOS_API.MAX_WAIT_TIME_RESPOND_FROM_TELNET):
                ##                TEST_CREATION_API.write_log_to_file("30s exceeded")
                ##                timeout_telnet = True
                ##                break
                ##        
                ##        if(response != None and timeout_telnet != True and response != "connect timed out"):
                ##            if (data[1] == "Operational"):
                ##                NOS_API.test_cases_results_info.ip = data[0]
                ##                first_telnet_test = True
                ##            else:           
                ##                TEST_CREATION_API.write_log_to_file("STB State is not operational")
                ##    else:
                ##        TEST_CREATION_API.write_log_to_file("STB State is not operational")
                ##else:
                ##    if(response != "connect timed out" and response != None and timeout_telnet != True):
                ##        TEST_CREATION_API.write_log_to_file("Error: Invalid Telnet Command")
                ##                                            
                ##NOS_API.quit_session(sid)
                #############################################################################################################################################################################

                if (NOS_API.is_signal_present_on_video_source()):
                     
                    TEST_CREATION_API.send_ir_rc_command("[Change_FTTH_First]")
                    result = NOS_API.wait_for_multiple_pictures(["Conectividade_Black_ref", "Conectividade_ref"], 10, ["[Conectividade]", "[Conectividade]"], [70, 70])
                    if(result == -2):
                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                        NOS_API.set_error_message("Reboot")
                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                        test_result = "FAIL"
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False


                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)

                        return
                    if(result == -1):
                        TEST_CREATION_API.send_ir_rc_command("[Big_Back]")
                        TEST_CREATION_API.send_ir_rc_command("[Change_FTTH_Scnd]")
                        result = NOS_API.wait_for_multiple_pictures(["Conectividade_Black_ref", "Conectividade_ref"], 10, ["[Conectividade]", "[Conectividade]"], [70, 70])
                        if(result == -2):
                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                            NOS_API.set_error_message("Reboot")
                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                            test_result = "FAIL"
                            
                            NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = ""
                            if (test_result != "PASS"):
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False
            
            
                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
            
                            return
                        if(result == -1):
                            TEST_CREATION_API.write_log_to_file("Navigation to Conectivity screen failed")
                            
                            NOS_API.set_error_message("Navegação")
                            
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                            error_codes = NOS_API.test_cases_results_info.navigation_error_code
                            error_messages = NOS_API.test_cases_results_info.navigation_error_message                    
                            
                            NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - " + str(tx_value) + " " + str(rx_value) + " " + str(downloadstream_snr_value) + " - - - - - " + str(cas_id_number) + " " + str(sw_version) + " - " + str(sc_number) + " - - - -",
                                        "- - - - <52 >-10<10 >=34 - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                            
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            report_file = ""    
                            
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)

                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)

                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            return

                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                    
                    ## Navigate to the Modem Docsis
                    TEST_CREATION_API.send_ir_rc_command("[NAVIGATE_MODEM_DOCSIS_NEW2]")
                    TEST_CREATION_API.send_ir_rc_command("[OK]")
                    
                    #MAC_SCREEN
                    result = NOS_API.wait_for_multiple_pictures(["mac_screen_ref", "mac_screen_ref1"], 10, ["[MAC_SCREEN]", "[MAC_SCREEN]"], [70, 70])
                    if(result == -2):
                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                        NOS_API.set_error_message("Reboot")
                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                        test_result = "FAIL"
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False


                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                            test_result,
                            end_time,
                            error_codes,
                            report_file)

                        return
                    if(result == -1):
                        TEST_CREATION_API.send_ir_rc_command("[Big_Back]")
                        TEST_CREATION_API.send_ir_rc_command("[NAVIGATE_MODEM_DOCSIS]")
                        TEST_CREATION_API.send_ir_rc_command("[OK]")
                        
                        result = NOS_API.wait_for_multiple_pictures(["mac_screen_ref", "mac_screen_ref1"], 10, ["[MAC_SCREEN]", "[MAC_SCREEN]"], [70, 70])
                        if(result == -2):
                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                            NOS_API.set_error_message("Reboot")
                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                            test_result = "FAIL"
                            
                            NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = ""
                            if (test_result != "PASS"):
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False
            
            
                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
            
                            return
                        if (result == -1):
                            TEST_CREATION_API.write_log_to_file("Navigation to MAC screen failed")
                            
                            NOS_API.set_error_message("Navegação")
                            
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                            error_codes = NOS_API.test_cases_results_info.navigation_error_code
                            error_messages = NOS_API.test_cases_results_info.navigation_error_message                    
                            
                            NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - " + str(tx_value) + " " + str(rx_value) + " " + str(downloadstream_snr_value) + " - - - - - " + str(cas_id_number) + " " + str(sw_version) + " - " + str(sc_number) + " - - - -",
                                        "- - - - <52 >-10<10 >=34 - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                            
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            report_file = ""    
                            
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)

                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)

                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            return

                    if (NOS_API.grab_picture("mac")):
                 
                        try:          
                            ## Get MAC address from menu
                            #mac_number = TEST_CREATION_API.OCR_recognize_text("zon_box_data", "[MAC]", "[OCR_FILTER]")
                            mac_number = NOS_API.fix_mac_stb_pace(NOS_API.remove_whitespaces(TEST_CREATION_API.OCR_recognize_text("mac", "[MAC]", "[OCR_FILTER]")))
                            NOS_API.test_cases_results_info.mac_number = mac_number
                            TEST_CREATION_API.write_log_to_file("Mac number: " + mac_number)
                            NOS_API.update_test_slot_comment("Mac number: " + mac_number)
                            
                        except Exception as error:
                            ## Set test result to INCONCLUSIVE
                            TEST_CREATION_API.write_log_to_file(str(error))
                            mac_number = ""
                    
                        ## Navigate to the Resumo menu
                        TEST_CREATION_API.send_ir_rc_command("[RESUMO_FROM_MODEM_DOCSIS]")
                        TEST_CREATION_API.send_ir_rc_command("[UP_4]")      
                        
                        result = NOS_API.wait_for_multiple_pictures(["resumo_ref", "resumo_ref1"], 10, ["[RESUMO]", "[RESUMO]"], [70, 70])
                        if(result == -2):
                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                            NOS_API.set_error_message("Reboot")
                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                            test_result = "FAIL"
                            
                            NOS_API.add_test_case_result_to_file_report(
                                            test_result,
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            "- - - - - - - - - - - - - - - - - - - -",
                                            error_codes,
                                            error_messages)
                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            report_file = ""
                            if (test_result != "PASS"):
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False
            
            
                            ## Update test result
                            TEST_CREATION_API.update_test_result(test_result)
                            
                            ## Return DUT to initial state and de-initialize grabber device
                            NOS_API.deinitialize()
                            
                            NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
            
                            return
                        if (result == -1):
                            TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX]")
                            TEST_CREATION_API.send_ir_rc_command("[RESUMO]")
                            TEST_CREATION_API.send_ir_rc_command("[UP_4]") 
                            
                            result = NOS_API.wait_for_multiple_pictures(["resumo_ref", "resumo_ref1"], 10, ["[RESUMO]", "[RESUMO]"], [70, 70])
                            if(result == -2):
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                report_file = ""
                                if (test_result != "PASS"):
                                    report_file = NOS_API.create_test_case_log_file(
                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                    end_time)
                                    NOS_API.upload_file_report(report_file)
                                    NOS_API.test_cases_results_info.isTestOK = False
                
                
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                                
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                
                                return
                            if (result == -1):
                                TEST_CREATION_API.write_log_to_file("Navigation to resumo screen failed")
                                
                                NOS_API.set_error_message("Navegação")
                                
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                                error_codes = NOS_API.test_cases_results_info.navigation_error_code
                                error_messages = NOS_API.test_cases_results_info.navigation_error_message
                                NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - " + str(tx_value) + " " + str(rx_value) + " " + str(downloadstream_snr_value) + " - - - - - " + str(cas_id_number) + " " + str(sw_version) + " - " + str(sc_number) + " - - - -",
                                        "- - - - <52 >-10<10 >=34 - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                            
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                report_file = ""    
                                
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)

                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)

                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                return
                            
                        if (NOS_API.grab_picture("resumo")):
                        
                            try:
                                ## Get IP address from menu
                                ip_adress = NOS_API.replace_missed_chars_with_numbers(TEST_CREATION_API.OCR_recognize_text("resumo", "[IP_ADDRESS]", "[OCR_FILTER]"))
                                TEST_CREATION_API.write_log_to_file("IP address: " + ip_adress)
                                NOS_API.update_test_slot_comment("IP address: " + ip_adress)
                            except Exception as error:
                                ## Set test result to INCONCLUSIVE
                                TEST_CREATION_API.write_log_to_file(str(error))
                                ip_adress = "-"
                                
                            try:
                                ## Get RX value from menu
                                rx_value = TEST_CREATION_API.OCR_recognize_text("resumo", "[RX_VALUE]", "[OCR_FILTER]")
                                TEST_CREATION_API.write_log_to_file("RX value: " + rx_value)
                                NOS_API.update_test_slot_comment("RX value: " + rx_value)
                                
                                ## Extract only digits from RX value
                                rx_value = float(NOS_API.replace_letter_o_with_number_0(rx_value[:(rx_value.find('d'))]))
                                NOS_API.test_cases_results_info.rx = str(rx_value)
                            except Exception as error:
                                ## Set test result to INCONCLUSIVE
                                TEST_CREATION_API.write_log_to_file(str(error))
                                rx_value = -100
                                NOS_API.test_cases_results_info.rx = "-"
                                
                            try:
                                ## Get download stream snr value from menu
                                downloadstream_snr_value = TEST_CREATION_API.OCR_recognize_text("resumo", "[DOWNLOADSTREAM_SNR]", "[OCR_FILTER]")
                                TEST_CREATION_API.write_log_to_file("Downloadstream snr value: " + downloadstream_snr_value)
                                NOS_API.update_test_slot_comment("Downloadstream snr value: " + downloadstream_snr_value)
                                
                                ## Extract only digits from RX value
                                downloadstream_snr_value = float(NOS_API.replace_letter_o_with_number_0(downloadstream_snr_value[:(downloadstream_snr_value.find('d'))]))
                                NOS_API.test_cases_results_info.download_stream_snr = str(downloadstream_snr_value)
                            except Exception as error:
                                ## Set test result to INCONCLUSIVE
                                TEST_CREATION_API.write_log_to_file(str(error))
                                downloadstream_snr_value = 30
                                NOS_API.test_cases_results_info.download_stream_snr = "-"
                            
                            
                            try:
                                ## Get TX value from menu
                                tx_value = TEST_CREATION_API.OCR_recognize_text("resumo", "[TX_VALUE]", "[OCR_FILTER]")                        
                                TEST_CREATION_API.write_log_to_file("TX value: " + str(tx_value))
                                NOS_API.update_test_slot_comment("TX value: " + str(tx_value))
                                
                                ## Extract only digits from TX value
                                tx_value = float(NOS_API.replace_letter_o_with_number_0(tx_value[:(tx_value.find('d'))]))
                                NOS_API.test_cases_results_info.tx = str(tx_value)
                            except Exception as error:
                                ## Set test result to INCONCLUSIVE
                                TEST_CREATION_API.write_log_to_file(str(error))
                                tx_value = 0
                                NOS_API.test_cases_results_info.tx = "-"
                            
                            mac_using_barcode = NOS_API.remove_whitespaces(NOS_API.test_cases_results_info.mac_using_barcode)
                            
                            ## Compare mac address from menu with previously scanned mac address
                            if (NOS_API.ignore_zero_letter_o_during_comparation(mac_number, mac_using_barcode)):
                                if (tx_value < TX_THRESHOLD):
                                    if (rx_value > RX_THRESHOLD_LOW and rx_value < RX_THRESHOLD_HIGH):
                                        if(downloadstream_snr_value >= DOWNLOADSTREAM_SNR_THRESHOLD):
                                            if (ip_adress  != "0.0.0.0"):
                                            #if(1):
                                                if not(NOS_API.grab_picture("Right_Place")):
                                                    TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                    NOS_API.set_error_message("Video HDMI")
                                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                                
                                
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)

                                                    return
                                                start_time = int(time.time())
                                                while not (TEST_CREATION_API.compare_pictures("sc_info_ref1", "Right_Place", "[CAS_ID_RP]") or TEST_CREATION_API.compare_pictures("sc_info_ref2", "Right_Place", "[CAS_ID_RP]") or TEST_CREATION_API.compare_pictures("sc_info_ref3", "Right_Place", "[CAS_ID_RP]") or TEST_CREATION_API.compare_pictures("sc_info_ref4", "Right_Place", "[CAS_ID_RP]")):
                                                    ##Perform Down
                                                    TEST_CREATION_API.send_ir_rc_command("[Down]")
                                                    timeout = int(time.time()) - start_time
                                                    if (timeout > 20):
                                                        TEST_CREATION_API.write_log_to_file("STB couldn't Navigate to right place.")
                                                        
                                                        NOS_API.set_error_message("Navegação")
                                                        
                                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                                            + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                                                        error_codes = NOS_API.test_cases_results_info.navigation_error_code
                                                        error_messages = NOS_API.test_cases_results_info.navigation_error_message
                                                        test_result = "FAIL"
                                                        
                                                        NOS_API.add_test_case_result_to_file_report(
                                                                        test_result,
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        error_codes,
                                                                        error_messages)
                                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                        report_file = ""
                                                        if (test_result != "PASS"):
                                                            report_file = NOS_API.create_test_case_log_file(
                                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                                            end_time)
                                                            NOS_API.upload_file_report(report_file)
                                                            NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                                        ## Update test result
                                                        TEST_CREATION_API.update_test_result(test_result)
                                                        
                                                        ## Return DUT to initial state and de-initialize grabber device
                                                        NOS_API.deinitialize()
                                                        
                                                        NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                        return
                                                    
                                                    if not(NOS_API.grab_picture("Right_Place")):
                                                        TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                        NOS_API.set_error_message("Video HDMI")
                                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                        test_result = "FAIL"
                                                        
                                                        NOS_API.add_test_case_result_to_file_report(
                                                                        test_result,
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        error_codes,
                                                                        error_messages)
                                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                        report_file = ""
                                                        if (test_result != "PASS"):
                                                            report_file = NOS_API.create_test_case_log_file(
                                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                                            end_time)
                                                            NOS_API.upload_file_report(report_file)
                                                            NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                                        ## Update test result
                                                        TEST_CREATION_API.update_test_result(test_result)
                                                        
                                                        ## Return DUT to initial state and de-initialize grabber device
                                                        NOS_API.deinitialize()
                                                        
                                                        NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
            
                                                        return
                                                #### Navigate to the CAS ID
                                                ##TEST_CREATION_API.send_ir_rc_command("[NAVIGATE_SC_MENU_FROM_INFO_ZON_BOX_MENU]")
                                                
                                                ## Perform grab picture
                                                if not(NOS_API.grab_picture("sc_info")):
                                                    TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                    NOS_API.set_error_message("Video HDMI")
                                                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                                
                                
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)

                                                    return    
                                            
                                                video_result1 = NOS_API.compare_pictures("sc_info_ref1", "sc_info", "[SC]")
                                                video_result2 = NOS_API.compare_pictures("sc_info_ref2", "sc_info", "[SC]")
                                                video_result3 = NOS_API.compare_pictures("sc_info_ref3", "sc_info", "[SC]")
                                                video_result4 = NOS_API.compare_pictures("sc_info_ref4", "sc_info", "[SC]")
                                            
                                                ## Check is SC not detected
                                                if (video_result1 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD or video_result2 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD or video_result3 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD or video_result4 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                                                
                                                    NOS_API.display_dialog("Reinsira o cart\xe3o e de seguida pressiona Continuar", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                                                    
                                                    TEST_CREATION_API.send_ir_rc_command("[REDO_SC]")
                                                    
                                                    result = NOS_API.wait_for_multiple_pictures(["resumo_ref", "resumo_ref1"], 10, ["[RESUMO]", "[RESUMO]"], [70, 70])
                                                    if(result == -2):
                                                        TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                        NOS_API.set_error_message("Reboot")
                                                        error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                        error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                        test_result = "FAIL"
                                                        
                                                        NOS_API.add_test_case_result_to_file_report(
                                                                        test_result,
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        error_codes,
                                                                        error_messages)
                                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                        report_file = ""
                                                        if (test_result != "PASS"):
                                                            report_file = NOS_API.create_test_case_log_file(
                                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                                            end_time)
                                                            NOS_API.upload_file_report(report_file)
                                                            NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        
                                                        ## Update test result
                                                        TEST_CREATION_API.update_test_result(test_result)
                                                        
                                                        ## Return DUT to initial state and de-initialize grabber device
                                                        NOS_API.deinitialize()
                                                        
                                                        NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                        
                                                        return
                                                    if (result == -1):
                                                        TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX]")
                                                        TEST_CREATION_API.send_ir_rc_command("[RESUMO]")
                                                        TEST_CREATION_API.send_ir_rc_command("[UP_4]") 
                                                        
                                                        result = NOS_API.wait_for_multiple_pictures(["resumo_ref", "resumo_ref1"], 10, ["[RESUMO]", "[RESUMO]"], [70, 70])
                                                        if(result == -2):
                                                            TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                                            NOS_API.set_error_message("Reboot")
                                                            error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                                            error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                                            test_result = "FAIL"
                                                            
                                                            NOS_API.add_test_case_result_to_file_report(
                                                                            test_result,
                                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                                            error_codes,
                                                                            error_messages)
                                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                            report_file = ""
                                                            if (test_result != "PASS"):
                                                                report_file = NOS_API.create_test_case_log_file(
                                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                                end_time)
                                                                NOS_API.upload_file_report(report_file)
                                                                NOS_API.test_cases_results_info.isTestOK = False
                                            
                                            
                                                            ## Update test result
                                                            TEST_CREATION_API.update_test_result(test_result)
                                                            
                                                            ## Return DUT to initial state and de-initialize grabber device
                                                            NOS_API.deinitialize()
                                                            
                                                            NOS_API.send_report_over_mqtt_test_plan(
                                                                test_result,
                                                                end_time,
                                                                error_codes,
                                                                report_file)
                                            
                                                            return
                                                        if (result == -1):
                                                            TEST_CREATION_API.write_log_to_file("Navigation to resumo screen failed")
                                                            
                                                            NOS_API.set_error_message("Navegação")
                                                            
                                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                                                + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                                                            error_codes = NOS_API.test_cases_results_info.navigation_error_code
                                                            error_messages = NOS_API.test_cases_results_info.navigation_error_message
                                                            NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - " + str(tx_value) + " " + str(rx_value) + " " + str(downloadstream_snr_value) + " - - - - - " + str(cas_id_number) + " " + str(sw_version) + " - " + str(sc_number) + " - - - -",
                                                                    "- - - - <52 >-10<10 >=34 - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                        
                                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                            report_file = ""    
                                                            
                                                            report_file = NOS_API.create_test_case_log_file(
                                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                                            end_time)
                                                            NOS_API.upload_file_report(report_file)
                                                            
                                                            NOS_API.send_report_over_mqtt_test_plan(
                                                                    test_result,
                                                                    end_time,
                                                                    error_codes,
                                                                    report_file)
                                    
                                                            ## Update test result
                                                            TEST_CREATION_API.update_test_result(test_result)
                                    
                                                            ## Return DUT to initial state and de-initialize grabber device
                                                            NOS_API.deinitialize()
                                                            return
                                                    
                                                    if not(NOS_API.grab_picture("Right_Place")):
                                                        TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                        NOS_API.set_error_message("Video HDMI")
                                                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                        test_result = "FAIL"
                                                        
                                                        NOS_API.add_test_case_result_to_file_report(
                                                                        test_result,
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                                        error_codes,
                                                                        error_messages)
                                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                        report_file = ""
                                                        if (test_result != "PASS"):
                                                            report_file = NOS_API.create_test_case_log_file(
                                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                                            end_time)
                                                            NOS_API.upload_file_report(report_file)
                                                            NOS_API.test_cases_results_info.isTestOK = False
                                    
                                    
                                                        ## Update test result
                                                        TEST_CREATION_API.update_test_result(test_result)
                                                        
                                                        ## Return DUT to initial state and de-initialize grabber device
                                                        NOS_API.deinitialize()
                                                        
                                                        NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
            
                                                        return
                                                    start_time = int(time.time())
                                                    while not (TEST_CREATION_API.compare_pictures("sc_info_ref1", "Right_Place", "[CAS_ID_RP]") or TEST_CREATION_API.compare_pictures("sc_info_ref2", "Right_Place", "[CAS_ID_RP]") or TEST_CREATION_API.compare_pictures("sc_info_ref3", "Right_Place", "[CAS_ID_RP]") or TEST_CREATION_API.compare_pictures("sc_info_ref4", "Right_Place", "[CAS_ID_RP]")):
                                                        ##Perform Down
                                                        TEST_CREATION_API.send_ir_rc_command("[Down]")
                                                        timeout = int(time.time()) - start_time
                                                        if (timeout > 20):
                                                            TEST_CREATION_API.write_log_to_file("STB couldn't Navigate to right place.")
                                                            
                                                            NOS_API.set_error_message("Navegação")
                                                            
                                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                                                + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                                                            error_codes = NOS_API.test_cases_results_info.navigation_error_code
                                                            error_messages = NOS_API.test_cases_results_info.navigation_error_message
                                                            test_result = "FAIL"
                                                            
                                                            NOS_API.add_test_case_result_to_file_report(
                                                                            test_result,
                                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                                            error_codes,
                                                                            error_messages)
                                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                            report_file = ""
                                                            if (test_result != "PASS"):
                                                                report_file = NOS_API.create_test_case_log_file(
                                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                                end_time)
                                                                NOS_API.upload_file_report(report_file)
                                                                NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        
                                                            ## Update test result
                                                            TEST_CREATION_API.update_test_result(test_result)
                                                            
                                                            ## Return DUT to initial state and de-initialize grabber device
                                                            NOS_API.deinitialize()
                                                            
                                                            NOS_API.send_report_over_mqtt_test_plan(
                                                                test_result,
                                                                end_time,
                                                                error_codes,
                                                                report_file)
                                                            return
                                                        
                                                        if not(NOS_API.grab_picture("Right_Place")):
                                                            TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                            NOS_API.set_error_message("Video HDMI")
                                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                            test_result = "FAIL"
                                                            
                                                            NOS_API.add_test_case_result_to_file_report(
                                                                            test_result,
                                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                                            error_codes,
                                                                            error_messages)
                                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                            report_file = ""
                                                            if (test_result != "PASS"):
                                                                report_file = NOS_API.create_test_case_log_file(
                                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                                end_time)
                                                                NOS_API.upload_file_report(report_file)
                                                                NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        
                                                            ## Update test result
                                                            TEST_CREATION_API.update_test_result(test_result)
                                                            
                                                            ## Return DUT to initial state and de-initialize grabber device
                                                            NOS_API.deinitialize()
                                                            
                                                            NOS_API.send_report_over_mqtt_test_plan(
                                                                test_result,
                                                                end_time,
                                                                error_codes,
                                                                report_file)
                
                                                            return
                                                    
                                                    
                                                    ## Perform grab picture
                                                    try:
                                                        TEST_CREATION_API.grab_picture("sc_info")
                                                    except: 
                                                        time.sleep(5)
                                                        try:
                                                            TEST_CREATION_API.grab_picture("sc_info")
                                                        except:
                                                            
                                                            TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                            NOS_API.set_error_message("Video HDMI")
                                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                            test_result = "FAIL"
                                                            
                                                            NOS_API.add_test_case_result_to_file_report(
                                                                            test_result,
                                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                                            error_codes,
                                                                            error_messages)
                                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                            report_file = ""
                                                            if (test_result != "PASS"):
                                                                report_file = NOS_API.create_test_case_log_file(
                                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                                end_time)
                                                                NOS_API.upload_file_report(report_file)
                                                                NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        
                                                            ## Update test result
                                                            TEST_CREATION_API.update_test_result(test_result)
                                                            
                                                            ## Return DUT to initial state and de-initialize grabber device
                                                            NOS_API.deinitialize()
                                                            
                                                            NOS_API.send_report_over_mqtt_test_plan(
                                                                test_result,
                                                                end_time,
                                                                error_codes,
                                                                report_file)

                                                            return    
                                                                            
                                                

                                                    video_result1 = NOS_API.compare_pictures("sc_info_ref1", "sc_info", "[SC]")
                                                    video_result2 = NOS_API.compare_pictures("sc_info_ref2", "sc_info", "[SC]")
                                                    video_result3 = NOS_API.compare_pictures("sc_info_ref3", "sc_info", "[SC]")
                                                    video_result4 = NOS_API.compare_pictures("sc_info_ref4", "sc_info", "[SC]")
                                                
                                                    ## Check is SC not detected
                                                    if (video_result1 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD or video_result2 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD or video_result3 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD or video_result4 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                                                    
                                                        TEST_CREATION_API.write_log_to_file("Smart card is not detected")
                                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.sc_not_detected_error_code \
                                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.sc_not_detected_error_message)
                                                        NOS_API.set_error_message("SmartCard")
                                                        error_codes = NOS_API.test_cases_results_info.sc_not_detected_error_code
                                                        error_messages = NOS_API.test_cases_results_info.sc_not_detected_error_message 
                                                    else:
                                                
                                                        ## Extract SC number and CAS ID from image
                                                        sc_number = TEST_CREATION_API.OCR_recognize_text("sc_info", "[SC_NUMBER]", "[OCR_FILTER]", "sc_number")
                                                        cas_id_number = NOS_API.remove_whitespaces(TEST_CREATION_API.OCR_recognize_text("sc_info", "[CAS_ID_NUMBER]", "[OCR_FILTER]", "cas_id_number"))
                                                        NOS_API.test_cases_results_info.cas_id_number = cas_id_number
                                                        NOS_API.test_cases_results_info.sc_number = sc_number
                                                        
                                                        ## Log SC number and CAS ID
                                                        TEST_CREATION_API.write_log_to_file("The extracted sc number is: " + sc_number)
                                                        TEST_CREATION_API.write_log_to_file("The extracted cas id number is: " + cas_id_number)
                                                    
                                                        NOS_API.update_test_slot_comment("SC number: " + NOS_API.test_cases_results_info.sc_number \
                                                                        + "; cas id number: " + NOS_API.test_cases_results_info.cas_id_number)
                                                        
                                                        cas_id_using_barcode = NOS_API.remove_whitespaces(NOS_API.test_cases_results_info.cas_id_using_barcode)
                                                        
                                                        ## Compare CAS ID number with the CAS ID number previously scanned by barcode scanner
                                                        if (NOS_API.ignore_zero_letter_o_during_comparation(cas_id_number, cas_id_using_barcode)):
                                                            
                                                            Serial_Number_TestCase = True
                                                            #test_result = "PASS"
                                                            TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX_NEW]")   
                                                            
                                                        else:
                                                            TEST_CREATION_API.write_log_to_file("CAS ID number and CAS ID number previuosly scanned by barcode scanner is not the same")
                                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.wrong_cas_id_error_code \
                                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.wrong_cas_id_error_message \
                                                                                                    + "; OCR: " + str(cas_id_number))
                                                            NOS_API.set_error_message("CAS ID")
                                                            Serial_Number_TestCase = False
                                                            error_codes = NOS_API.test_cases_results_info.wrong_cas_id_error_code
                                                            error_messages = NOS_API.test_cases_results_info.wrong_cas_id_error_message
                                                            
                                                else:
                                            
                                                    ## Extract SC number and CAS ID from image
                                                    sc_number = TEST_CREATION_API.OCR_recognize_text("sc_info", "[SC_NUMBER]", "[OCR_FILTER]", "sc_number")
                                                    cas_id_number = NOS_API.remove_whitespaces(TEST_CREATION_API.OCR_recognize_text("sc_info", "[CAS_ID_NUMBER]", "[OCR_FILTER]", "cas_id_number"))
                                                    NOS_API.test_cases_results_info.cas_id_number = cas_id_number
                                                    NOS_API.test_cases_results_info.sc_number = sc_number
                                                    
                                                    ## Log SC number and CAS ID
                                                    TEST_CREATION_API.write_log_to_file("The extracted sc number is: " + sc_number)
                                                    TEST_CREATION_API.write_log_to_file("The extracted cas id number is: " + cas_id_number)
                                                
                                                    NOS_API.update_test_slot_comment("SC number: " + NOS_API.test_cases_results_info.sc_number \
                                                                    + "; cas id number: " + NOS_API.test_cases_results_info.cas_id_number)
                                                    
                                                    cas_id_using_barcode = NOS_API.remove_whitespaces(NOS_API.test_cases_results_info.cas_id_using_barcode)
                                                    
                                                    ## Compare CAS ID number with the CAS ID number previously scanned by barcode scanner
                                                    if (NOS_API.ignore_zero_letter_o_during_comparation(cas_id_number, cas_id_using_barcode)):
                                                        #test_result = "PASS"
                                                        Serial_Number_TestCase = True
                                                        TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX_NEW]")                                                
                                                    else:
                                                        TEST_CREATION_API.write_log_to_file("CAS ID number and CAS ID number previuosly scanned by barcode scanner is not the same")
                                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.wrong_cas_id_error_code \
                                                                                                + "; Error message: " + NOS_API.test_cases_results_info.wrong_cas_id_error_message \
                                                                                                + "; OCR: " + str(cas_id_number))
                                                        NOS_API.set_error_message("CAS ID")
                                                        error_codes = NOS_API.test_cases_results_info.wrong_cas_id_error_code
                                                        error_messages = NOS_API.test_cases_results_info.wrong_cas_id_error_message                                                                                                        
                                            else:               
                                                TEST_CREATION_API.write_log_to_file("Ethernet Fail. IP address is 0.0.0.0")
                                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.eth2_nok_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.eth2_nok_error_message)
                                                NOS_API.set_error_message("Eth")
                                                error_codes = NOS_API.test_cases_results_info.eth2_nok_error_code
                                                error_messages = NOS_API.test_cases_results_info.eth2_nok_error_message
                                                #TEST_CREATION_API.write_log_to_file("IP address is 0.0.0.0")
                                                #NOS_API.set_error_message("IP")
                                                #error_codes = NOS_API.test_cases_results_info.ip_error_code
                                                #error_messages = NOS_API.test_cases_results_info.ip_error_message
                                        else:
                                            TEST_CREATION_API.write_log_to_file("Fail SNR")
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.snr_fail_error_code \
                                                                                            + "; Error message: " + NOS_API.test_cases_results_info.snr_fail_error_message)
                                            NOS_API.set_error_message("SNR")
                                            error_codes = NOS_API.test_cases_results_info.snr_fail_error_code
                                            error_messages = NOS_API.test_cases_results_info.snr_fail_error_message                            
                                    else:
                                        TEST_CREATION_API.write_log_to_file("RX value is less than threshold")
                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.rx_fail_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.rx_fail_error_message)
                                        NOS_API.set_error_message("CM Docsis")
                                        error_codes = NOS_API.test_cases_results_info.rx_fail_error_code
                                        error_messages = NOS_API.test_cases_results_info.rx_fail_error_message   
                                else:
                                    TEST_CREATION_API.write_log_to_file("TX value is less than threshold")
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.tx_fail_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.tx_fail_error_message)
                                    NOS_API.set_error_message("CM Docsis")
                                    error_codes = NOS_API.test_cases_results_info.tx_fail_error_code
                                    error_messages = NOS_API.test_cases_results_info.tx_fail_error_message   
                            else:
                                TEST_CREATION_API.write_log_to_file("MAC number is not the same as previous scanned mac number")
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.wrong_mac_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.wrong_mac_error_message)
                                NOS_API.set_error_message("MAC")
                                error_codes = NOS_API.test_cases_results_info.wrong_mac_error_code
                                error_messages = NOS_API.test_cases_results_info.wrong_mac_error_message 
                        else:
                            TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                            NOS_API.set_error_message("Video HDMI")
                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                    else:
                        TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                        NOS_API.set_error_message("Video HDMI")
                        error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                        error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                else:
                    TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                           + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                    NOS_API.set_error_message("Video HDMI")
                    error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                    error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message 

        ##############################################################################################################################################################################################################################    
        #############################################################################################Interfaces#######################################################################################################################    
        ##############################################################################################################################################################################################################################
                    
            if (Serial_Number_TestCase):
                TEST_CREATION_API.write_log_to_file("####Interfaces####")
            
                ## Max record audio time in miliseconds
                MAX_RECORD_AUDIO_TIME = 2000

                MAX_RECORD_VIDEO_TIME = 2000

                THRESHOLD = 70    
                
                ## Set test result default to FAIL
                test_result = "FAIL"
                test_result_hd = False
                error_codes = ""
                error_messages = ""

                hd_counter = 0
                sd_ch_counter = 0
                
                pqm_analyse_check = True        
                
                SPDIF_Result = False
                
                test_result_SCART_video = False
                SCART_Result = False
                
                test_result_res = False
                pqm_analyse_check = True
                
                test_result_HDMI_720 = False
                        
                ##error_command_telnet = False
                ##stb_state = False
                
                test_result_telnet = False
                
                test_result_ButtonLeds = False
                
                HDMI_Result = False
                #################Debug Telnet########################
                #timeout_telnet = False
                #second_telnet_test = False
                #################Debug Telnet########################
                
                ##############################################################################Second Telnet Test##############################################################################
                ##cmd = 'Show cable modem ' + NOS_API.test_cases_results_info.mac_using_barcode
                ###Get start time
                ##startTime = time.localtime()
                ##sid = NOS_API.get_session_id()
                ##while (True):
                ##    response = NOS_API.send_cmd_to_telnet(sid, cmd)
                ##    TEST_CREATION_API.write_log_to_file("response:" + str(response))
                ##    if(response != None):
                ##        if(response.find("Error:") != -1):
                ##            error_command_telnet = True
                ##            break
                ##        if(response == "connect timed out"):
                ##            sn = NOS_API.test_cases_results_info.s_n_using_barcode
                ##            slot = NOS_API.slot_index(NOS_API.get_test_place_name())
                ##            docsisInc = "N"
                ##            
                ##            f = open("C:\\Program Files (x86)\\RT-RK\\RT-Executor Diagnostic Station\\Test_Support\\DocsisInconsistences.txt", "a")
                ##            f.write(sn + " " + slot + " " + docsisInc + "\n")
                ##            f.close()
                ##            NOS_API.quit_session(sid)
                ##            time.sleep(1)
                ##            sid = NOS_API.get_session_id()
                ##            response = NOS_API.send_cmd_to_telnet(sid, cmd)
                ##            TEST_CREATION_API.write_log_to_file("response:" + str(response))
                ##            if(response != None):
                ##                if(response.find("Error:") != -1):
                ##                    error_command_telnet = True
                ##                    break
                ##                if(response == "connect timed out"):
                ##                    TEST_CREATION_API.write_log_to_file("Connect TimeOut")   
                ##                    break
                ##                if(response != "BUSY"):
                ##                    stb_state = NOS_API.is_stb_operational(response)
                ##                    break
                ##            else:
                ##                TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                ##                break
                ##        if(response != "BUSY"):
                ##            stb_state = NOS_API.is_stb_operational(response)
                ##            break
                ##    else:
                ##        TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                ##        break
                ##        
                ##    time.sleep(5)
                ##        
                ##    #Get current time
                ##    currentTime = time.localtime()
                ##    if((time.mktime(currentTime) - time.mktime(startTime)) > NOS_API.MAX_WAIT_TIME_RESPOND_FROM_TELNET):
                ##        TEST_CREATION_API.write_log_to_file("30s exceeded")
                ##        timeout_telnet = True
                ##        break
                ##
                ##if(error_command_telnet == False):
                ##    if(stb_state == True):    
                ##        cmd = 'Show cable modem ' + NOS_API.test_cases_results_info.mac_using_barcode + ' verbose'
                ##        startTime = time.localtime()
                ##        while (True):
                ##            response = NOS_API.send_cmd_to_telnet(sid, cmd)
                ##            TEST_CREATION_API.write_log_to_file("response:" + str(response))                
                ##            
                ##            if(response != None and response != "BUSY" and response != "connect timed out"):
                ##                data = NOS_API.parse_telnet_cmd1(response)
                ##                break
                ##            if(response == None):
                ##                TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                ##                break
                ##            
                ##            if(response == "connect timed out"):
                ##                sn = NOS_API.test_cases_results_info.s_n_using_barcode
                ##                slot = NOS_API.slot_index(NOS_API.get_test_place_name())
                ##                docsisInc = "N"
                ##                
                ##                f = open("C:\\Program Files (x86)\\RT-RK\\RT-Executor Diagnostic Station\\Test_Support\\DocsisInconsistences.txt", "a")
                ##                f.write(sn + " " + slot + " " + docsisInc + "\n")
                ##                f.close()
                ##                NOS_API.quit_session(sid)
                ##                time.sleep(1)
                ##                sid = NOS_API.get_session_id()
                ##                response = NOS_API.send_cmd_to_telnet(sid, cmd)
                ##                TEST_CREATION_API.write_log_to_file("response:" + str(response))                
                ##            
                ##                if(response != None and response != "BUSY" and response != "connect timed out"):
                ##                    data = NOS_API.parse_telnet_cmd1(response)
                ##                    break
                ##                if(response == None):
                ##                    TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                ##                    break
                ##                
                ##                if(response == "connect timed out"):
                ##                    TEST_CREATION_API.write_log_to_file("Connect TimeOut")
                ##                    break
                ##                
                ##            time.sleep(5)
                ##                
                ##            #Get current time
                ##            currentTime = time.localtime()
                ##            if((time.mktime(currentTime) - time.mktime(startTime)) > NOS_API.MAX_WAIT_TIME_RESPOND_FROM_TELNET):
                ##                TEST_CREATION_API.write_log_to_file("30s exceeded")
                ##                timeout_telnet = True
                ##                break
                ##        
                ##        if(response != None and timeout_telnet != True and response != "connect timed out"):
                ##            if (data[1] == "Operational"):
                ##                NOS_API.test_cases_results_info.ip = data[0]
                ##                second_telnet_test = True
                ##            else:           
                ##                TEST_CREATION_API.write_log_to_file("STB State is not operational")
                ##    else:
                ##        TEST_CREATION_API.write_log_to_file("STB State is not operational")
                ##else:
                ##    if(response != "connect timed out" and response != None and timeout_telnet != True):
                ##        TEST_CREATION_API.write_log_to_file("Error: Invalid Telnet Command")
                ##                                            
                ##NOS_API.quit_session(sid)
                ##############################################################################################################################################################################
                
                 ## Initialize grabber device
                #NOS_API.initialize_grabber()
                NOS_API.grabber_stop_video_source()
                time.sleep(1)
                NOS_API.grabber_stop_audio_source()
                time.sleep(1)
            
                TEST_CREATION_API.send_ir_rc_command("[Volume_Half]")
                time.sleep(1)
                TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                time.sleep(1)
                
                TEST_CREATION_API.grabber_start_audio_source(TEST_CREATION_API.AudioInterface.SPDIF_COAX)
                time.sleep(1)

                ## Record audio from digital output (SPDIF COAX)
                TEST_CREATION_API.record_audio("SPDIF_COAX_audio", MAX_RECORD_AUDIO_TIME)

                #############Comparacao com referencia audio OK############################################
                
                ### Compare recorded and expected audio and get result of comparison
                #audio_result1 = NOS_API.compare_audio("SPDIF_COAX_audio_ref1", "SPDIF_COAX_audio")
                #audio_result2 = NOS_API.compare_audio("SPDIF_COAX_audio_ref2", "SPDIF_COAX_audio")
                #
                #if (audio_result1 >= TEST_CREATION_API.AUDIO_THRESHOLD or audio_result2 >= TEST_CREATION_API.AUDIO_THRESHOLD):
                #
                #    ## Check is audio present on channel
                #    if (TEST_CREATION_API.is_audio_present("SPDIF_COAX_audio")):
                #       test_result = "PASS"
                #    else:
                #        TEST_CREATION_API.write_log_to_file("Audio is not present on SPDIF coaxial interface.")
                #        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_code \
                #                                               + "; Error message: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_message)
                #        error_codes = NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_code
                #        error_messages = NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_message 
                #        NOS_API.set_error_message("SPDIF")
                #else:
                #    time.sleep(3)
                #    
                #    NOS_API.display_dialog("Confirme o cabo SPDIF e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                #    
                #    ## Record audio from digital output (SPDIF COAX)
                #    TEST_CREATION_API.record_audio("SPDIF_COAX_audio1", MAX_RECORD_AUDIO_TIME)
                #
                #    ## Compare recorded and expected audio and get result of comparison
                #    audio_result1 = NOS_API.compare_audio("SPDIF_COAX_audio_ref1", "SPDIF_COAX_audio1")
                #    audio_result2 = NOS_API.compare_audio("SPDIF_COAX_audio_ref2", "SPDIF_COAX_audio1")
                #
                #    if (audio_result1 >= TEST_CREATION_API.AUDIO_THRESHOLD or audio_result2 >= TEST_CREATION_API.AUDIO_THRESHOLD):
                #
                #        ## Check is audio present on channel
                #        if (TEST_CREATION_API.is_audio_present("SPDIF_COAX_audio1")):
                #            test_result = "PASS"
                #        else:
                #            TEST_CREATION_API.write_log_to_file("Audio is not present on SPDIF coaxial interface.")
                #            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_code \
                #                                                    + "; Error message: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_message)
                #            error_codes = NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_code
                #            error_messages = NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_message 
                #            NOS_API.set_error_message("SPDIF")
                #    else:           
                #        TEST_CREATION_API.write_log_to_file("Audio with RT-RK pattern is not reproduced correctly on SPDIF coaxial interface.")
                #        NOS_API.update_test_slot_comment("Error codes: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_discontinuities_error_code  \
                #                                                    + ";\n" + NOS_API.test_cases_results_info.spdif_coaxial_signal_interference_error_code  \
                #                                                    + "; Error messages: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_discontinuities_error_message \
                #                                                    + ";\n" + NOS_API.test_cases_results_info.spdif_coaxial_signal_interference_error_message)
                #        error_codes = NOS_API.test_cases_results_info.spdif_coaxial_signal_discontinuities_error_code + " " + NOS_API.test_cases_results_info.spdif_coaxial_signal_interference_error_code
                #        error_messages = NOS_API.test_cases_results_info.spdif_coaxial_signal_discontinuities_error_message + " " +  NOS_API.test_cases_results_info.spdif_coaxial_signal_interference_error_message
                #        NOS_API.set_error_message("SPDIF")
                        
                #############Comparacao com referencia audio NOK############################################
                
                ## Compare recorded and expected audio and get result of comparison
                audio_result1 = NOS_API.compare_audio("No_Both_ref", "SPDIF_COAX_audio")

                if not(audio_result1 >= TEST_CREATION_API.AUDIO_THRESHOLD):

                    ## Check is audio present on channel
                    if (TEST_CREATION_API.is_audio_present("SPDIF_COAX_audio")):
                        SPDIF_Result = True
                    else:
                        TEST_CREATION_API.write_log_to_file("Audio is not present on SPDIF coaxial interface.")
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_code \
                                                            + "; Error message: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_message)
                        error_codes = NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_code
                        error_messages = NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_message 
                        NOS_API.set_error_message("SPDIF")
                else:
                    time.sleep(3)
                    
                    NOS_API.display_dialog("Confirme o cabo SPDIF e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                    
                    ## Record audio from digital output (SPDIF COAX)
                    TEST_CREATION_API.record_audio("SPDIF_COAX_audio1", MAX_RECORD_AUDIO_TIME)
                
                    ## Compare recorded and expected audio and get result of comparison
                    audio_result1 = NOS_API.compare_audio("No_Both_ref", "SPDIF_COAX_audio1")
                
                    if not(audio_result1 >= TEST_CREATION_API.AUDIO_THRESHOLD):
                
                        ## Check is audio present on channel
                        if (TEST_CREATION_API.is_audio_present("SPDIF_COAX_audio1")):
                            SPDIF_Result = True
                        else:
                            TEST_CREATION_API.write_log_to_file("Audio is not present on SPDIF coaxial interface.")
                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_message)
                            error_codes = NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_code
                            error_messages = NOS_API.test_cases_results_info.spdif_coaxial_signal_absence_error_message 
                            NOS_API.set_error_message("SPDIF")
                    else:           
                        TEST_CREATION_API.write_log_to_file("Audio with RT-RK pattern is not reproduced correctly on SPDIF coaxial interface.")
                        NOS_API.update_test_slot_comment("Error codes: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_discontinuities_error_code  \
                                                                    + ";\n" + NOS_API.test_cases_results_info.spdif_coaxial_signal_interference_error_code  \
                                                                    + "; Error messages: " + NOS_API.test_cases_results_info.spdif_coaxial_signal_discontinuities_error_message \
                                                                    + ";\n" + NOS_API.test_cases_results_info.spdif_coaxial_signal_interference_error_message)
                        error_codes = NOS_API.test_cases_results_info.spdif_coaxial_signal_discontinuities_error_code + " " + NOS_API.test_cases_results_info.spdif_coaxial_signal_interference_error_code
                        error_messages = NOS_API.test_cases_results_info.spdif_coaxial_signal_discontinuities_error_message + " " +  NOS_API.test_cases_results_info.spdif_coaxial_signal_interference_error_message
                        NOS_API.set_error_message("SPDIF")
                        
                        
            
            
            
            
            ################################################################################### SCART Test ###################################################################################################################
            
                if(SPDIF_Result):
                
                    NOS_API.grabber_stop_audio_source()
                    time.sleep(1)
                    
                    ## Initialize input interfaces of DUT RT-AV101 device  
                    NOS_API.reset_dut()
                    #time.sleep(2)

                    ## Start grabber device with video on default video source
                    NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.CVBS2)
                    #time.sleep(5)
                    
                    if not(NOS_API.is_signal_present_on_video_source()):
                        NOS_API.display_dialog("Confirme o cabo SCART e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                    
                    
                    if (NOS_API.is_signal_present_on_video_source()):

                        ## Check if video is playing (check if video is not freezed)
                        if (NOS_API.is_video_playing(TEST_CREATION_API.VideoInterface.CVBS2)):
                            video_result = 0
                            i = 0
                            
                            while(i < 3):
                    
                                try:
                                    ## Perform grab picture
                                    TEST_CREATION_API.grab_picture("SCART_video")
                            
                                    ## Compare grabbed and expected image and get result of comparison
                                    video_result = NOS_API.compare_pictures("SCART_video_ref", "SCART_video", "[HALF_SCREEN_576p]")
                            
                                except:
                                    i = i + 1
                                    continue
                            
                                ## Check video analysis results and update comments
                                if (video_result >= NOS_API.DEFAULT_CVBS_VIDEO_THRESHOLD):
                                    ## Set test result to PASS
                                    test_result_SCART_video = True
                                    break
                                i = i + 1
                            if (i >= 3):
                                TEST_CREATION_API.write_log_to_file("Video with RT-RK pattern is not reproduced correctly on SCART interface.")
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.scart_noise_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.scart_noise_error_message \
                                                                    + "; V: " + str(video_result))
                                error_codes = NOS_API.test_cases_results_info.scart_noise_error_code
                                error_messages = NOS_API.test_cases_results_info.scart_noise_error_message
                                NOS_API.set_error_message("Video Scart")
                        else:
                            TEST_CREATION_API.write_log_to_file("Channel with RT-RK color bar pattern was not playing on SCART interface.")
                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.scart_image_freezing_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.scart_image_freezing_error_message)
                            error_codes = NOS_API.test_cases_results_info.scart_image_freezing_error_code
                            error_messages = NOS_API.test_cases_results_info.scart_image_freezing_error_message
                            NOS_API.set_error_message("Video Scart")
                    else:
                        TEST_CREATION_API.write_log_to_file("No video SCART.")
                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.scart_image_absence_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.scart_image_absence_error_message)
                        error_codes = NOS_API.test_cases_results_info.scart_image_absence_error_code
                        error_messages = NOS_API.test_cases_results_info.scart_image_absence_error_message
                        NOS_API.set_error_message("Video Scart")
                        
                        
                        
                    if(test_result_SCART_video):
                    
                        NOS_API.grabber_stop_video_source()
                        time.sleep(0.5)
                    
                        ## Start grabber device with audio on SCART audio source
                        TEST_CREATION_API.grabber_start_audio_source(TEST_CREATION_API.AudioInterface.LINEIN2)
                        time.sleep(2)
                
                        ## Record audio from digital output (SCART)
                        TEST_CREATION_API.record_audio("SCART_audio", MAX_RECORD_AUDIO_TIME)
                        
                        #############Comparacao com referencia audio OK############################################
                        
                        ### Compare recorded and expected audio and get result of comparison
                        #audio_result_1 = NOS_API.compare_audio("SCART_channels_switched", "SCART_audio", "[AUDIO_ANALOG]")
                        #audio_result_2 = NOS_API.compare_audio("SCART_audio_ref2", "SCART_audio", "[AUDIO_ANALOG]")
                        #
                        #if (audio_result_1 >= TEST_CREATION_API.AUDIO_THRESHOLD or audio_result_2 >= TEST_CREATION_API.AUDIO_THRESHOLD):
                        #
                        #    ## Check is audio present on channel
                        #    if (TEST_CREATION_API.is_audio_present("SCART_audio")):
                        #        test_result = "PASS"
                        #    else:
                        #        TEST_CREATION_API.write_log_to_file("Audio is not present on SCART interface.")
                        #        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.scart_signal_absence_error_code \
                        #                                            + "; Error message: " + NOS_API.test_cases_results_info.scart_signal_absence_error_message)
                        #        error_codes = NOS_API.test_cases_results_info.scart_signal_absence_error_code
                        #        error_messages = NOS_API.test_cases_results_info.scart_signal_absence_error_message
                        #        NOS_API.set_error_message("Audio Scart") 
                        #else:
                        #    time.sleep(3)
                        #    
                        #    NOS_API.display_dialog("Confirme o cabo SCART e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                        #    
                        #    ## Record audio from digital output (SCART)
                        #    TEST_CREATION_API.record_audio("SCART_audio1", MAX_RECORD_AUDIO_TIME)
                        #
                        #    ## Compare recorded and expected audio and get result of comparison
                        #    audio_result_1 = NOS_API.compare_audio("SCART_channels_switched", "SCART_audio1", "[AUDIO_ANALOG]")
                        #    audio_result_2 = NOS_API.compare_audio("SCART_audio_ref2", "SCART_audio1", "[AUDIO_ANALOG]")
                        #
                        #    if (audio_result_1 >= TEST_CREATION_API.AUDIO_THRESHOLD or audio_result_2 >= TEST_CREATION_API.AUDIO_THRESHOLD):
                        #
                        #        ## Check is audio present on channel
                        #        if (TEST_CREATION_API.is_audio_present("SCART_audio1")):
                        #            test_result = "PASS"
                        #        else:
                        #            TEST_CREATION_API.write_log_to_file("Audio is not present on SCART interface.")
                        #            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.scart_signal_absence_error_code \
                        #                                                    + "; Error message: " + NOS_API.test_cases_results_info.scart_signal_absence_error_message)
                        #            error_codes = NOS_API.test_cases_results_info.scart_signal_absence_error_code
                        #            error_messages = NOS_API.test_cases_results_info.scart_signal_absence_error_message
                        #            NOS_API.set_error_message("Audio Scart") 
                        #    else:           
                        #        TEST_CREATION_API.write_log_to_file("Audio with RT-RK pattern is not reproduced correctly on SCART interface.")
                        #        NOS_API.update_test_slot_comment("Error codes: " + NOS_API.test_cases_results_info.scart_signal_discontinuities_error_code  \
                        #                                                    + ";\n" + NOS_API.test_cases_results_info.scart_signal_interference_error_code  \
                        #                                                    + "; Error messages: " + NOS_API.test_cases_results_info.scart_signal_discontinuities_error_message \
                        #                                                    + ";\n" + NOS_API.test_cases_results_info.scart_signal_interference_error_message)
                        #        error_codes = NOS_API.test_cases_results_info.scart_signal_discontinuities_error_code + " " + NOS_API.test_cases_results_info.scart_signal_interference_error_code
                        #        error_messages = NOS_API.test_cases_results_info.scart_signal_discontinuities_error_message + " " + NOS_API.test_cases_results_info.scart_signal_interference_error_message
                        #        NOS_API.set_error_message("Audio Scart") 
                                
                        #############Comparacao com referencia audio NOK############################################
                            
                        ## Compare recorded and expected audio and get result of comparison
                        audio_result_1 = NOS_API.compare_audio("No_Left_ref", "SCART_audio", "[AUDIO_ANALOG]")
                        audio_result_2 = NOS_API.compare_audio("No_right_ref", "SCART_audio", "[AUDIO_ANALOG]")
                        audio_result_3 = NOS_API.compare_audio("No_Both_ref", "SCART_audio", "[AUDIO_ANALOG]")
                
                        if not(audio_result_1 >= TEST_CREATION_API.AUDIO_THRESHOLD or audio_result_2 >= TEST_CREATION_API.AUDIO_THRESHOLD or audio_result_3 >= TEST_CREATION_API.AUDIO_THRESHOLD):
                
                            ## Check is audio present on channel
                            if (TEST_CREATION_API.is_audio_present("SCART_audio")):
                                #test_result = "PASS"
                                SCART_Result = True
                            else:
                                TEST_CREATION_API.write_log_to_file("Audio is not present on SCART interface.")
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.scart_signal_absence_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.scart_signal_absence_error_message)
                                error_codes = NOS_API.test_cases_results_info.scart_signal_absence_error_code
                                error_messages = NOS_API.test_cases_results_info.scart_signal_absence_error_message
                                NOS_API.set_error_message("Audio Scart") 
                        else:
                            time.sleep(3)
                            
                            NOS_API.display_dialog("Confirme o cabo SCART e restantes cabos", NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "Continuar"
                            
                            ## Record audio from digital output (SCART)
                            TEST_CREATION_API.record_audio("SCART_audio1", MAX_RECORD_AUDIO_TIME)
                        
                            ## Compare recorded and expected audio and get result of comparison
                            audio_result_1 = NOS_API.compare_audio("No_Left_ref", "SCART_audio1", "[AUDIO_ANALOG]")
                            audio_result_2 = NOS_API.compare_audio("No_right_ref", "SCART_audio1", "[AUDIO_ANALOG]")
                            audio_result_3 = NOS_API.compare_audio("No_Both_ref", "SCART_audio1", "[AUDIO_ANALOG]")
                        
                            if not(audio_result_1 >= TEST_CREATION_API.AUDIO_THRESHOLD or audio_result_2 >= TEST_CREATION_API.AUDIO_THRESHOLD or audio_result_3 >= TEST_CREATION_API.AUDIO_THRESHOLD):
                        
                                ## Check is audio present on channel
                                if (TEST_CREATION_API.is_audio_present("SCART_audio1")):
                                    SCART_Result = True
                                else:
                                    TEST_CREATION_API.write_log_to_file("Audio is not present on SCART interface.")
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.scart_signal_absence_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.scart_signal_absence_error_message)
                                    error_codes = NOS_API.test_cases_results_info.scart_signal_absence_error_code
                                    error_messages = NOS_API.test_cases_results_info.scart_signal_absence_error_message
                                    NOS_API.set_error_message("Audio Scart") 
                            else:           
                                TEST_CREATION_API.write_log_to_file("Audio with RT-RK pattern is not reproduced correctly on SCART interface.")
                                NOS_API.update_test_slot_comment("Error codes: " + NOS_API.test_cases_results_info.scart_signal_discontinuities_error_code  \
                                                                            + ";\n" + NOS_API.test_cases_results_info.scart_signal_interference_error_code  \
                                                                            + "; Error messages: " + NOS_API.test_cases_results_info.scart_signal_discontinuities_error_message \
                                                                            + ";\n" + NOS_API.test_cases_results_info.scart_signal_interference_error_message)
                                error_codes = NOS_API.test_cases_results_info.scart_signal_discontinuities_error_code + " " + NOS_API.test_cases_results_info.scart_signal_interference_error_code
                                error_messages = NOS_API.test_cases_results_info.scart_signal_discontinuities_error_message + " " + NOS_API.test_cases_results_info.scart_signal_interference_error_message
                                NOS_API.set_error_message("Audio Scart") 
                                
                
                
                ################################################################################ HDMI 720p Test ######################################################################################################
                
                    if(SCART_Result):
                    
                        NOS_API.grabber_stop_audio_source()
                        time.sleep(1)
                    
                        ## Start grabber device with video on default video source
                        NOS_API.grabber_start_video_source(TEST_CREATION_API.VideoInterface.HDMI1)
                        TEST_CREATION_API.grabber_start_audio_source(TEST_CREATION_API.AudioInterface.HDMI1)
                        #time.sleep(4)
                        if (NOS_API.is_signal_present_on_video_source()):
                    
                            TEST_CREATION_API.send_ir_rc_command("[SET_RESOLUTION_720p_new]")
                            time.sleep(1)
                            
                            video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                            if (video_height != "720"):
                                TEST_CREATION_API.send_ir_rc_command("[SET_RESOLUTION_720p]")
                                time.sleep(1)
                                
                                video_height = NOS_API.get_av_format_info(TEST_CREATION_API.AudioVideoInfoType.video_height)
                                if (video_height != "720"):
                                    NOS_API.set_error_message("Resolução")
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.resolution_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.resolution_error_message) 
                                    error_codes = NOS_API.test_cases_results_info.resolution_error_code
                                    error_messages = NOS_API.test_cases_results_info.resolution_error_message
                                else:
                                    test_result_res = True  
                            else:
                                test_result_res = True
                            
                        else:
                            TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                            NOS_API.set_error_message("Video HDMI") 
                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message 

                        TEST_CREATION_API.send_ir_rc_command("[CH_1]")
                        time.sleep(2)
                        TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                        time.sleep(1)
                        TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                            
                        if (test_result_res):
                            
                            if not (NOS_API.is_signal_present_on_video_source()):
                                TEST_CREATION_API.write_log_to_file("STB lost Signal.Possible Reboot.")
                                
                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.reboot_error_code \
                                                        + "; Error message: " + NOS_API.test_cases_results_info.reboot_error_message)
                                NOS_API.set_error_message("Reboot")
                                error_codes = NOS_API.test_cases_results_info.reboot_error_code
                                error_messages = NOS_API.test_cases_results_info.reboot_error_message
                                test_result = "FAIL"
                                NOS_API.deinitialize()
                                NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                            
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                                NOS_API.upload_file_report(report_file)
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                    
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)

                                return
                                
                            ## Record video with duration of recording (10 seconds)
                            NOS_API.record_video("video", MAX_RECORD_VIDEO_TIME)
                    
                            ## Instance of PQMAnalyse type
                            pqm_analyse = TEST_CREATION_API.PQMAnalyse()
                    
                            ## Set what algorithms should be checked while analyzing given video file with PQM.
                            # Attributes are set to false by default.
                            pqm_analyse.black_screen_activ = True
                            pqm_analyse.blocking_activ = True
                            pqm_analyse.freezing_activ = True
                    
                            # Name of the video file that will be analysed by PQM.
                            pqm_analyse.file_name = "video"
                    
                            ## Analyse recorded video
                            analysed_video = TEST_CREATION_API.pqm_analysis(pqm_analyse)
                    
                            if (pqm_analyse.black_screen_detected == TEST_CREATION_API.AlgorythmResult.DETECTED):
                                pqm_analyse_check = False
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_image_absence_error_code \
                                        + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_image_absence_error_message)
                                        
                                error_codes = NOS_API.test_cases_results_info.hdmi_720p_image_absence_error_code
                                error_messages = NOS_API.test_cases_results_info.hdmi_720p_image_absence_error_message
                    
                            if (pqm_analyse.blocking_detected == TEST_CREATION_API.AlgorythmResult.DETECTED):
                                pqm_analyse_check = False
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_blocking_error_code \
                                        + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_blocking_error_message)
                                        
                                if (error_codes == ""):
                                    error_codes = NOS_API.test_cases_results_info.hdmi_720p_blocking_error_code
                                else:
                                    error_codes = error_codes + " " + NOS_API.test_cases_results_info.hdmi_720p_blocking_error_code
                                
                                if (error_messages == ""):
                                    error_messages = NOS_API.test_cases_results_info.hdmi_720p_blocking_error_message
                                else:
                                    error_messages = error_messages + " " + NOS_API.test_cases_results_info.hdmi_720p_blocking_error_message
                            
                            if (pqm_analyse.freezing_detected == TEST_CREATION_API.AlgorythmResult.DETECTED):
                                pqm_analyse_check = False
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_code \
                                        + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_message)
                                        
                                if (error_codes == ""):
                                    error_codes = NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_code
                                else:
                                    error_codes = error_codes + " " + NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_code
                                    
                                if (error_messages == ""):
                                    error_messages = NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_message
                                else:
                                    error_messages = error_messages + " " + NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_message
                            
                            if not(pqm_analyse_check):  
                                NOS_API.set_error_message("Video HDMI")
                                NOS_API.deinitialize()
                                NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                            
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                            end_time)
                                NOS_API.upload_file_report(report_file)
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)
                                
                                return
                            
                            if not(analysed_video):
                                TEST_CREATION_API.write_log_to_file("Could'n't Record Video")
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.grabber_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.grabber_error_message)
                                error_codes = NOS_API.test_cases_results_info.grabber_error_code
                                error_messages = NOS_API.test_cases_results_info.grabber_error_message
                                NOS_API.set_error_message("Inspection")
                                
                                NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                report_file = NOS_API.create_test_case_log_file(
                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                end_time)
                                NOS_API.upload_file_report(report_file)
                                NOS_API.test_cases_results_info.isTestOK = False
                                
                                NOS_API.send_report_over_mqtt_test_plan(
                                        test_result,
                                        end_time,
                                        error_codes,
                                        report_file)
                        
                                ## Update test result
                                TEST_CREATION_API.update_test_result(test_result)
                            
                                ## Return DUT to initial state and de-initialize grabber device
                                NOS_API.deinitialize()
                                return            
                            
                            ## Check if video is playing (check if video is not freezed)
                            if (NOS_API.is_video_playing()):
                        
                                video_result1 = 0
                                video_result2 = 0
                                video_result3 = 0
                                
                                i = 0
                                
                                while(i < 3):
                        
                                    try:
                                        ## Perform grab picture
                                        TEST_CREATION_API.grab_picture("HDMI_video")
                                    
                                        ## Compare grabbed and expected image and get result of comparison
                                        video_result1 = NOS_API.compare_pictures("HDMI_video_ref1", "HDMI_video", "[HALF_SCREEN]")
                                        video_result2 = NOS_API.compare_pictures("HDMI_video_ref2", "HDMI_video", "[HALF_SCREEN]")
                                        video_result3 = NOS_API.compare_pictures("HDMI_video_ref3", "HDMI_video", "[HALF_SCREEN]")
                                    
                                    except:
                                        i = i + 1
                                        continue
                                    
                                    ## Check video analysis results and update comments
                                    if (video_result1 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD or video_result2 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD or \
                                        video_result3 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                                        i = 0
                                        if (analysed_video):            
                                            test_result_HDMI_720 = True
                                        else:
                                            NOS_API.set_error_message("Video HDMI") 
                                        break
                                    i = i + 1
                                if (i >= 3):  
                                    TEST_CREATION_API.write_log_to_file("Video with RT-RK pattern is not reproduced correctly on HDMI 720p.")
                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_noise_error_message)
                                    error_codes = NOS_API.test_cases_results_info.hdmi_720p_noise_error_code
                                    error_messages = NOS_API.test_cases_results_info.hdmi_720p_noise_error_message
                                    NOS_API.set_error_message("Video HDMI") 
                            else:
                                TEST_CREATION_API.write_log_to_file("Channel with RT-RK color bar pattern was not playing on HDMI 720p.")
                                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_message)
                                error_codes = NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_code
                                error_messages = NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_message
                                NOS_API.set_error_message("Video HDMI") 
                                
                        ################################################################################ Audio HDMI ######################################################################################################
                            if (test_result_HDMI_720):
                                TEST_CREATION_API.record_audio("HDMI_audio_720", MAX_RECORD_AUDIO_TIME)
                                
                                audio_result_1 = NOS_API.compare_audio("No_Both_ref", "HDMI_audio_720")
            
                                if not(audio_result_1 < TEST_CREATION_API.AUDIO_THRESHOLD):
                                    
                                    TEST_CREATION_API.send_ir_rc_command("[CH+]")
                                    TEST_CREATION_API.send_ir_rc_command("[CH-]")
                                    time.sleep(5)
                                    ## Record audio from digital output (HDMI)
                                    TEST_CREATION_API.record_audio("HDMI_audio_720_1", MAX_RECORD_AUDIO_TIME)
                        
                                    ## Compare recorded and expected audio and get result of comparison
                                    audio_result_1 = NOS_API.compare_audio("No_Both_ref", "HDMI_audio_720_1")
                        
                                if not(audio_result_1 >= TEST_CREATION_API.AUDIO_THRESHOLD):
                                    HDMI_Result = True                                                       
                                else:
                                    if (TEST_CREATION_API.is_audio_present("HDMI_audio_720")):
                                        TEST_CREATION_API.write_log_to_file("Audio Absence on HDMI.")
                                        NOS_API.set_error_message("Audio HDMI")
                                        NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_message)
                                        error_codes = NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_code
                                        error_messages = NOS_API.test_cases_results_info.hdmi_720p_image_freezing_error_message
                                    else:
                                        TEST_CREATION_API.write_log_to_file("Audio with RT-RK pattern is not reproduced correctly on hdmi 720p interface.")
                                        NOS_API.set_error_message("Audio HDMI")
                                        NOS_API.update_test_slot_comment("Error codes: " + NOS_API.test_cases_results_info.hdmi_720p_signal_discontinuities_error_code  \
                                                                                + ";\n" + NOS_API.test_cases_results_info.hdmi_720p_signal_interference_error_code  \
                                                                                + "; Error messages: " + NOS_API.test_cases_results_info.hdmi_720p_signal_discontinuities_error_message \
                                                                                + ";\n" + NOS_API.test_cases_results_info.hdmi_720p_signal_discontinuities_error_message)
                                        error_codes = NOS_API.test_cases_results_info.hdmi_720p_signal_discontinuities_error_code + " " + NOS_API.test_cases_results_info.hdmi_720p_signal_interference_error_code
                                        error_messages = NOS_API.test_cases_results_info.hdmi_720p_signal_discontinuities_error_message + " " + NOS_API.test_cases_results_info.hdmi_720p_signal_interference_error_message
                            
                    ################################################################################ Telnet Test ######################################################################################################          
                            
                            if (HDMI_Result):        
                                
                                error_command_telnet = False
                                stb_state = False
                                
                                cmd = 'Show cable modem ' + NOS_API.test_cases_results_info.mac_using_barcode
                                #Get start time
                                startTime = time.localtime()
                                sid = NOS_API.get_session_id()
                                while (True):
                                    response = NOS_API.send_cmd_to_telnet(sid, cmd)
                                    TEST_CREATION_API.write_log_to_file("response:" + str(response))
                                    if(response != None):
                                        if(response.find("Error:") != -1):
                                            error_command_telnet = True
                                            break
                                        if(response == "connect timed out"):
                                            #sn = NOS_API.test_cases_results_info.s_n_using_barcode
                                            #slot = NOS_API.slot_index(NOS_API.get_test_place_name())
                                            #docsisInc = "N"
                                            #
                                            #f = open("C:\\Program Files (x86)\\RT-RK\\RT-Executor Diagnostic Station\\Test_Support\\DocsisInconsistences.txt", "a")
                                            #f.write(sn + " " + slot + " " + docsisInc + "\n")
                                            #f.close()
                                            NOS_API.quit_session(sid)
                                            time.sleep(1)
                                            sid = NOS_API.get_session_id()
                                            response = NOS_API.send_cmd_to_telnet(sid, cmd)
                                            TEST_CREATION_API.write_log_to_file("response:" + str(response))
                                            if(response != None):
                                                if(response.find("Error:") != -1):
                                                    error_command_telnet = True
                                                    break
                                                if(response == "connect timed out"):
                                                    NOS_API.set_error_message("Telnet timeout")
                                                    TEST_CREATION_API.write_log_to_file("Connect TimeOut")
                                                    
                                                    error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                                    error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                                        
                                                    NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                    report_file = ""    
                                                    
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)  
                                                    return
                                                if(response != "BUSY"):
                                                    stb_state = NOS_API.is_stb_operational(response)
                                                    break
                                            else:
                                                NOS_API.set_error_message("Telnet timeout")
                                                TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                                                
                                                error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                                error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                                    
                                                NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                report_file = ""    
                                            
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                            
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)  
                                                return
                                        if(response != "BUSY"):
                                            stb_state = NOS_API.is_stb_operational(response)
                                            break    
                                    else:
                                        NOS_API.set_error_message("Telnet timeout")
                                        TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                                        
                                        error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                        error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                            
                                        NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        report_file = ""    
                                    
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)  
                                        return
                                        
                                    time.sleep(5)
                                        
                                    #Get current time
                                    currentTime = time.localtime()
                                    if((time.mktime(currentTime) - time.mktime(startTime)) > NOS_API.MAX_WAIT_TIME_RESPOND_FROM_TELNET):
                                        NOS_API.set_error_message("Telnet timeout")
                                        TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                                        
                                        error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                        error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                        
                                        NOS_API.add_test_case_result_to_file_report(
                                                test_result,
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                "- - - - - - - - - - - - - - - - - - - -",
                                                error_codes,
                                                error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        report_file = ""    
                                    
                                        report_file = NOS_API.create_test_case_log_file(
                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                        end_time)
                                        NOS_API.upload_file_report(report_file)
                                        NOS_API.test_cases_results_info.isTestOK = False
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)
                                    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)  
                                        return
                                
                                if(error_command_telnet == False):
                                    if(stb_state == True):    
                                        cmd = 'Show cable modem ' + NOS_API.test_cases_results_info.mac_using_barcode + ' verbose'
                                        startTime = time.localtime()
                                        while (True):
                                    
                                            response = NOS_API.send_cmd_to_telnet(sid, cmd)
                                            TEST_CREATION_API.write_log_to_file("response:" + str(response))                
                                            
                                            if(response != None and response != "BUSY" and response != "connect timed out"):
                                                data = NOS_API.parse_telnet_cmd1(response)
                                                break
                                            if(response == None):
                                                NOS_API.set_error_message("Telnet timeout")
                                                TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                                                
                                                error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                                error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                                    
                                                NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                report_file = ""    
                                                
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)  
                                                return
                                            
                                            if(response == "connect timed out"):
                                                #sn = NOS_API.test_cases_results_info.s_n_using_barcode
                                                #slot = NOS_API.slot_index(NOS_API.get_test_place_name())
                                                #docsisInc = "N"
                                                #
                                                #f = open("C:\\Program Files (x86)\\RT-RK\\RT-Executor Diagnostic Station\\Test_Support\\DocsisInconsistences.txt", "a")
                                                #f.write(sn + " " + slot + " " + docsisInc + "\n")
                                                #f.close()
                                                NOS_API.quit_session(sid)
                                                response = NOS_API.send_cmd_to_telnet(sid, cmd)
                                                TEST_CREATION_API.write_log_to_file("response:" + str(response))                
                                                
                                                if(response != None and response != "BUSY" and response != "connect timed out"):
                                                    data = NOS_API.parse_telnet_cmd1(response)
                                                    break
                                                if(response == None):
                                                    NOS_API.set_error_message("Telnet timeout")
                                                    TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                                                    
                                                    error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                                    error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                                        
                                                    NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                    report_file = ""    
                                                    
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)  
                                                    return
                                                
                                                if(response == "connect timed out"):
                                                    NOS_API.set_error_message("Telnet timeout")
                                                    TEST_CREATION_API.write_log_to_file("Connect TimeOut")
                                                    
                                                    error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                                    error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                                        
                                                    NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                    report_file = ""    
                                                    
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                            test_result,
                                                            end_time,
                                                            error_codes,
                                                            report_file)
                                                    
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)  
                                                    return
                                                
                                            time.sleep(5)
                                                
                                            #Get current time
                                            currentTime = time.localtime()
                                            if((time.mktime(currentTime) - time.mktime(startTime)) > NOS_API.MAX_WAIT_TIME_RESPOND_FROM_TELNET):
                                                NOS_API.set_error_message("Telnet timeout")
                                                TEST_CREATION_API.write_log_to_file("Didn't establish/Lost Telnet communication with CMTS")
                                                
                                                error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                                error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                                    
                                                NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                report_file = ""    
                                                
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)  
                                                
                                                return
          
                                        if (data[1] == "Operational"):
                                            NOS_API.test_cases_results_info.ip = data[0]
                                            test_result_telnet = True
                                        else:           
                                            TEST_CREATION_API.write_log_to_file("STB State is not operational")
                                            NOS_API.set_error_message("CM Docsis")
                                            error_codes = NOS_API.test_cases_results_info.ip_error_code
                                            error_messages = NOS_API.test_cases_results_info.ip_error_message  
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.ip_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.ip_error_message)
                                    else:
                                        TEST_CREATION_API.write_log_to_file("STB State is not operational")
                                        NOS_API.set_error_message("CM Docsis")
                                        error_codes = NOS_API.test_cases_results_info.ip_error_code
                                        error_messages = NOS_API.test_cases_results_info.ip_error_message  
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.ip_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.ip_error_message)
                                else:
                                    NOS_API.set_error_message("Telnet timeout")
                                    TEST_CREATION_API.write_log_to_file("Error: Invalid Telnet Command")
                                    
                                    error_codes = NOS_API.test_cases_results_info.cmts_error_code
                                    error_messages = NOS_API.test_cases_results_info.cmts_error_message  
                                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.cmts_error_code \
                                                                + "; Error message: " + NOS_API.test_cases_results_info.cmts_error_message)
                                                                            
                                NOS_API.quit_session(sid)
                                ######################################################Debug Telnet##########################################################
                                ##if(test_result_telnet == False and (second_telnet_test == True or first_telnet_test == True)):
                                ##    sn = NOS_API.test_cases_results_info.s_n_using_barcode
                                ##    slot = NOS_API.slot_index(NOS_API.get_test_place_name())
                                ##    docsisInc = "S"
                                ##    
                                ##    f = open("C:\\Program Files (x86)\\RT-RK\\RT-Executor Diagnostic Station\\Test_Support\\DocsisInconsistences.txt", "a")
                                ##    f.write(sn + " " + slot + " " + docsisInc + "\n")
                                ##    f.close()
                                #############################################################################################################################
                                
                    ################################################################################ Buttons/Led's Test ###################################################################################################### 
                    
                                if(test_result_telnet):
                                    #if not(NOS_API.display_custom_dialog("O Led Rede est\xe1 ligado?", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                                    #    TEST_CREATION_API.write_log_to_file("Led Rede NOK")
                                    #    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.led_net_nok_error_code \
                                    #                                    + "; Error message: " + NOS_API.test_cases_results_info.led_net_nok_error_message)
                                    #    NOS_API.set_error_message("Led's")
                                    #    error_codes = NOS_API.test_cases_results_info.led_net_nok_error_code
                                    #    error_messages = NOS_API.test_cases_results_info.led_net_nok_error_message
                                    #    test_result = "FAIL"
                                    #    
                                    #    NOS_API.add_test_case_result_to_file_report(
                                    #                    test_result,
                                    #                    "- - - - - - - - - - - - - - - - - - - -",
                                    #                    "- - - - - - - - - - - - - - - - - - - -",
                                    #                    error_codes,
                                    #                    error_messages)
                                    #    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                    #    report_file = ""
                                    #    if (test_result != "PASS"):
                                    #        report_file = NOS_API.create_test_case_log_file(
                                    #                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                    #                        NOS_API.test_cases_results_info.nos_sap_number,
                                    #                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                    #                        NOS_API.test_cases_results_info.mac_using_barcode,
                                    #                        end_time)
                                    #        NOS_API.upload_file_report(report_file)
                                    #        NOS_API.test_cases_results_info.isTestOK = False
                                    #
                                    #
                                    #    ## Update test result
                                    #    TEST_CREATION_API.update_test_result(test_result)
                                    #    
                                    #    ## Return DUT to initial state and de-initialize grabber device
                                    #    NOS_API.deinitialize()
                                    #    
                                    #    NOS_API.send_report_over_mqtt_test_plan(
                                    #        test_result,
                                    #        end_time,
                                    #        error_codes,
                                    #        report_file)
                                    #
                                    #    return
                                    NOS_API.display_custom_dialog("Pressione no bot\xe3o 'Power'", 1, ["Continuar"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) 
                                    time.sleep(2)
                                    if (NOS_API.is_signal_present_on_video_source()):
                                        TEST_CREATION_API.write_log_to_file("Power button NOK")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_button_nok_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.power_button_nok_error_message)
                                        NOS_API.set_error_message("Botões")   
                                        error_codes = NOS_API.test_cases_results_info.power_button_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.power_button_nok_error_message  
                                        test_result = "FAIL"
                                        NOS_API.add_test_case_result_to_file_report(
                                                        test_result,
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        "- - - - - - - - - - - - - - - - - - - -",
                                                        error_codes,
                                                        error_messages)
                                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                        report_file = ""
                                        if (test_result != "PASS"):
                                            report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                            NOS_API.upload_file_report(report_file)
                                            NOS_API.test_cases_results_info.isTestOK = False
                    
                    
                                        ## Update test result
                                        TEST_CREATION_API.update_test_result(test_result)
                                        
                                        ## Return DUT to initial state and de-initialize grabber device
                                        NOS_API.deinitialize()
                                        
                                        NOS_API.send_report_over_mqtt_test_plan(
                                            test_result,
                                            end_time,
                                            error_codes,
                                            report_file)

                                        return
                                    if (NOS_API.display_custom_dialog("O Led Vermelho/Laranja est\xe1 ligado?", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                                        if (NOS_API.display_custom_dialog("O Display est\xe1 ligado?", 2, ["OK", "NOK"], NOS_API.WAIT_TIME_TO_CLOSE_DIALOG) == "OK"):
                                            TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                            time.sleep(10)
                                            if not(NOS_API.is_signal_present_on_video_source()):
                                                TEST_CREATION_API.send_ir_rc_command("[POWER]")
                                                time.sleep(10)
                                                if not(NOS_API.is_signal_present_on_video_source()):
                                                    TEST_CREATION_API.write_log_to_file("STB doesn't receive IR commands.")
                                                    NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.ir_nok_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.ir_nok_error_message)
                                                    NOS_API.set_error_message("IR")
                                                    error_codes = NOS_API.test_cases_results_info.ir_nok_error_code
                                                    error_messages = NOS_API.test_cases_results_info.ir_nok_error_message
                                                    test_result = "FAIL"
                                                    
                                                    NOS_API.add_test_case_result_to_file_report(
                                                                    test_result,
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                                    error_codes,
                                                                    error_messages)
                                                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                    report_file = ""
                                                    if (test_result != "PASS"):
                                                        report_file = NOS_API.create_test_case_log_file(
                                                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                        NOS_API.test_cases_results_info.nos_sap_number,
                                                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                        NOS_API.test_cases_results_info.mac_using_barcode,
                                                                        end_time)
                                                        NOS_API.upload_file_report(report_file)
                                                        NOS_API.test_cases_results_info.isTestOK = False
                                
                                
                                                    ## Update test result
                                                    TEST_CREATION_API.update_test_result(test_result)
                                                    
                                                    ## Return DUT to initial state and de-initialize grabber device
                                                    NOS_API.deinitialize()
                                                    
                                                    NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)

                                                    return
                                                else:
                                                    test_result_ButtonLeds = True
                                            else:
                                                test_result_ButtonLeds = True
                                        else:
                                            TEST_CREATION_API.write_log_to_file("Display NOK")
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.display_nok_error_code \
                                                                            + "; Error message: " + NOS_API.test_cases_results_info.display_nok_error_message)
                                            NOS_API.set_error_message("Display")
                                            error_codes = NOS_API.test_cases_results_info.display_nok_error_code
                                            error_messages = NOS_API.test_cases_results_info.display_nok_error_message
                                    else:
                                        TEST_CREATION_API.write_log_to_file("Led POWER Red NOK")
                                        NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.led_power_red_nok_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.led_power_red_nok_error_message)
                                        NOS_API.set_error_message("Led's")
                                        error_codes = NOS_API.test_cases_results_info.led_power_red_nok_error_code
                                        error_messages = NOS_API.test_cases_results_info.led_power_red_nok_error_message
                                    
                                    if(test_result_ButtonLeds):
                                        TEST_CREATION_API.send_ir_rc_command("[EXIT]")
                                        time.sleep(1)
                                        TEST_CREATION_API.send_ir_rc_command("[Factory_Reset]")
                                        if not(NOS_API.grab_picture("Factory_Reset")):
                                            TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                            NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                            NOS_API.set_error_message("Video HDMI")
                                            error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                            error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                            test_result = "FAIL"
                                            
                                            NOS_API.add_test_case_result_to_file_report(
                                                            test_result,
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            "- - - - - - - - - - - - - - - - - - - -",
                                                            error_codes,
                                                            error_messages)
                                            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                            report_file = ""
                                            if (test_result != "PASS"):
                                                report_file = NOS_API.create_test_case_log_file(
                                                                NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                NOS_API.test_cases_results_info.nos_sap_number,
                                                                NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                NOS_API.test_cases_results_info.mac_using_barcode,
                                                                end_time)
                                                NOS_API.upload_file_report(report_file)
                                                NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                                            ## Update test result
                                            TEST_CREATION_API.update_test_result(test_result)
                                            
                                            ## Return DUT to initial state and de-initialize grabber device
                                            NOS_API.deinitialize()
                                            
                                            NOS_API.send_report_over_mqtt_test_plan(
                                                test_result,
                                                end_time,
                                                error_codes,
                                                report_file)

                                            return
                                        
                                        video_result = NOS_API.compare_pictures("Factory_Reset_ref", "Factory_Reset", "[Factory_Check]")
                                        video_result_1 = NOS_API.compare_pictures("Factory_Reset_black_ref", "Factory_Reset", "[Factory_Check]")
                                        
                                        if not(video_result >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD or video_result_1 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                                            TEST_CREATION_API.send_ir_rc_command("[EXIT_ZON_BOX]")
                                            TEST_CREATION_API.send_ir_rc_command("[Factory_Reset]")
                                            if not(NOS_API.grab_picture("Factory_Reset_1")):
                                                TEST_CREATION_API.write_log_to_file("Image is not displayed on HDMI")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.image_absence_hdmi_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.image_absence_hdmi_error_message)
                                                NOS_API.set_error_message("Video HDMI")
                                                error_codes = NOS_API.test_cases_results_info.image_absence_hdmi_error_code
                                                error_messages = NOS_API.test_cases_results_info.image_absence_hdmi_error_message
                                                test_result = "FAIL"
                                                
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False

                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                                                    
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()

                                                return
                                            
                                            video_result_2 = NOS_API.compare_pictures("Factory_Reset_ref", "Factory_Reset_1", "[Factory_Check]")
                                            video_result_3 = NOS_API.compare_pictures("Factory_Reset_black_ref", "Factory_Reset_1", "[Factory_Check]")
                                            
                                            if not(video_result_2 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD or video_result_3 >= TEST_CREATION_API.DEFAULT_HDMI_VIDEO_THRESHOLD):
                                                TEST_CREATION_API.write_log_to_file("Navigation to resumo screen failed")
                                                NOS_API.set_error_message("Navegação")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.navigation_error_code \
                                                                                    + "; Error message: " + NOS_API.test_cases_results_info.navigation_error_message) 
                                                error_codes = NOS_API.test_cases_results_info.navigation_error_code
                                                error_messages = NOS_API.test_cases_results_info.navigation_error_message
                                                NOS_API.add_test_case_result_to_file_report(
                                                                test_result,
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                "- - - - - - - - - - - - - - - - - - - -",
                                                                error_codes,
                                                                error_messages)
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                                                report_file = ""
                                                if (test_result != "PASS"):
                                                    report_file = NOS_API.create_test_case_log_file(
                                                                    NOS_API.test_cases_results_info.s_n_using_barcode,
                                                                    NOS_API.test_cases_results_info.nos_sap_number,
                                                                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                                    NOS_API.test_cases_results_info.mac_using_barcode,
                                                                    end_time)
                                                    NOS_API.upload_file_report(report_file)
                                                    NOS_API.test_cases_results_info.isTestOK = False
                                                                       
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                    test_result,
                                                    end_time,
                                                    error_codes,
                                                    report_file)
                            
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()

                                                return
                                            else:
                                                TEST_CREATION_API.send_ir_rc_command("[OK]")
                                        else:
                                            TEST_CREATION_API.send_ir_rc_command("[OK]")
                                        
                                        if (NOS_API.wait_for_no_signal_present(20)):
                                            time.sleep(10)
                                            test_result = "PASS"
                                            NOS_API.configure_power_switch_by_inspection()
                                            if not(NOS_API.power_off()): 
                                                TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                                                
                                                NOS_API.set_error_message("POWER SWITCH")
                                                NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_switch_error_code \
                                                                                + "; Error message: " + NOS_API.test_cases_results_info.power_switch_error_message)
                                                error_codes = NOS_API.test_cases_results_info.power_switch_error_code
                                                error_messages = NOS_API.test_cases_results_info.power_switch_error_message
                                                ## Return DUT to initial state and de-initialize grabber device
                                                NOS_API.deinitialize()
                                                NOS_API.add_test_case_result_to_file_report(
                                                    test_result,
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    "- - - - - - - - - - - - - - - - - - - -",
                                                    error_codes,
                                                    error_messages)
                                        
                                                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                report_file = NOS_API.create_test_case_log_file(
                                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                                            NOS_API.test_cases_results_info.nos_sap_number,
                                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                                            NOS_API.test_cases_results_info.mac_using_barcode,
                                                            end_time)
                                                NOS_API.upload_file_report(report_file)
                                                
                                                NOS_API.send_report_over_mqtt_test_plan(
                                                        test_result,
                                                        end_time,
                                                        error_codes,
                                                        report_file)
                                                
                                                ## Update test result
                                                TEST_CREATION_API.update_test_result(test_result)
                                                
                                                return 
                                        else: 
                                            TEST_CREATION_API.write_log_to_file("Factory Reset Fail")
                                            NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.measure_boot_time_error_code \
                                                                        + "; Error message: " + NOS_API.test_cases_results_info.measure_boot_time_error_message)
                                            NOS_API.set_error_message("Factory Reset")  
                                            error_codes = NOS_API.test_cases_results_info.measure_boot_time_error_code
                                            error_messages = NOS_API.test_cases_results_info.measure_boot_time_error_message
        
            System_Failure = 2
        except Exception as error:
            if(System_Failure == 0):
                System_Failure = System_Failure + 1 
                NOS_API.Inspection = True
                if(System_Failure == 1):
                    try:
                        TEST_CREATION_API.write_log_to_file(error)
                    except: 
                        pass
                    try:
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        TEST_CREATION_API.write_log_to_file(error)
                    except: 
                        pass
                if (NOS_API.configure_power_switch_by_inspection()):
                    if not(NOS_API.power_off()): 
                        TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        NOS_API.set_error_message("Inspection")
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            "",
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        
                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                    
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                                    test_result,
                                    end_time,
                                    error_codes,
                                    report_file)

                        return
                    time.sleep(10)
                    ## Power on STB with energenie
                    if not(NOS_API.power_on()):
                        TEST_CREATION_API.write_log_to_file("Comunication with PowerSwitch Fails")
                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                        NOS_API.set_error_message("Inspection")
                        
                        NOS_API.add_test_case_result_to_file_report(
                                        test_result,
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        "- - - - - - - - - - - - - - - - - - - -",
                                        error_codes,
                                        error_messages)
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        report_file = ""
                        if (test_result != "PASS"):
                            report_file = NOS_API.create_test_case_log_file(
                                            NOS_API.test_cases_results_info.s_n_using_barcode,
                                            NOS_API.test_cases_results_info.nos_sap_number,
                                            NOS_API.test_cases_results_info.cas_id_using_barcode,
                                            "",
                                            end_time)
                            NOS_API.upload_file_report(report_file)
                            NOS_API.test_cases_results_info.isTestOK = False
                        
                        test_result = "FAIL"
                        
                        ## Update test result
                        TEST_CREATION_API.update_test_result(test_result)
                    
                        ## Return DUT to initial state and de-initialize grabber device
                        NOS_API.deinitialize()
                        
                        NOS_API.send_report_over_mqtt_test_plan(
                                test_result,
                                end_time,
                                error_codes,
                                report_file)
                        
                        return
                    time.sleep(10)
                else:
                    TEST_CREATION_API.write_log_to_file("Incorrect test place name")
                    
                    NOS_API.update_test_slot_comment("Error code = " + NOS_API.test_cases_results_info.power_switch_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.power_switch_error_message)
                    NOS_API.set_error_message("Inspection")
                    
                    NOS_API.add_test_case_result_to_file_report(
                                    test_result,
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    "- - - - - - - - - - - - - - - - - - - -",
                                    error_codes,
                                    error_messages)
                    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
                    report_file = ""
                    if (test_result != "PASS"):
                        report_file = NOS_API.create_test_case_log_file(
                                        NOS_API.test_cases_results_info.s_n_using_barcode,
                                        NOS_API.test_cases_results_info.nos_sap_number,
                                        NOS_API.test_cases_results_info.cas_id_using_barcode,
                                        "",
                                        end_time)
                        NOS_API.upload_file_report(report_file)
                        NOS_API.test_cases_results_info.isTestOK = False
                    
                    test_result = "FAIL"
                    ## Update test result
                    TEST_CREATION_API.update_test_result(test_result)
                    
                
                    ## Return DUT to initial state and de-initialize grabber device
                    NOS_API.deinitialize()
                    
                    NOS_API.send_report_over_mqtt_test_plan(
                        test_result,
                        end_time,
                        error_codes,
                        report_file)
                    
                    return
                
                NOS_API.Inspection = False
            else:
                test_result = "FAIL"
                TEST_CREATION_API.write_log_to_file(error)
                NOS_API.update_test_slot_comment("Error code: " + NOS_API.test_cases_results_info.grabber_error_code \
                                                                    + "; Error message: " + NOS_API.test_cases_results_info.grabber_error_message)
                error_codes = NOS_API.test_cases_results_info.grabber_error_code
                error_messages = NOS_API.test_cases_results_info.grabber_error_message
                NOS_API.set_error_message("Inspection")
                System_Failure = 2    
####################################################################################################################################################################################################################
   
    NOS_API.add_test_case_result_to_file_report(
                    test_result,
                    str(snr_value) + " " + str(ber_value) + " - - " + str(tx_value) + " " + str(rx_value) + " " + str(downloadstream_snr_value) + " - - - - - " + str(cas_id_number) + " " + str(sw_version) + " - " + str(sc_number) + " - - - -",
                    ">50<70 <1.0E-6 - - <60 >-20<20 >=20 - - - - - - - - - - - - -",
                    error_codes,
                    error_messages)
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report_file = ""    

    report_file = NOS_API.create_test_case_log_file(
                    NOS_API.test_cases_results_info.s_n_using_barcode,
                    NOS_API.test_cases_results_info.nos_sap_number,
                    NOS_API.test_cases_results_info.cas_id_using_barcode,
                    NOS_API.test_cases_results_info.mac_using_barcode,
                    end_time)
    NOS_API.upload_file_report(report_file)
    NOS_API.test_cases_results_info.isTestOK = False
    
    NOS_API.send_report_over_mqtt_test_plan(
            test_result,
            end_time,
            error_codes,
            report_file)

    ## Update test result
    TEST_CREATION_API.update_test_result(test_result)

    ## Return DUT to initial state and de-initialize grabber device
    NOS_API.deinitialize()
        