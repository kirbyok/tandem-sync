#!/usr/bin/env python3

import unittest
from tconnectsync.domain.bolus import Bolus
from tconnectsync.parser.tconnect import TConnectEntry, UnknownBasalSuspensionEventException, UnknownCIQActivityEventException

class TestTConnectEntryBasal(unittest.TestCase):
    def test_parse_ciq_basal_entry(self):
        self.assertEqual(
            TConnectEntry.parse_ciq_basal_entry({
                "y": 0.8,
                "duration": 1221,
                "x": 1615878000
            }),
            {
                "time": "2021-03-16 00:00:00-04:00",
                "delivery_type": "",
                "duration_mins": 1221/60,
                "basal_rate": 0.8,
            }
        )

        self.assertEqual(
            TConnectEntry.parse_ciq_basal_entry({
                "y": 0.797,
                "duration": 300,
                "x": 1615879521
            }, delivery_type="algorithmDelivery"),
            {
                "time": "2021-03-16 00:25:21-04:00",
                "delivery_type": "algorithmDelivery",
                "duration_mins": 5,
                "basal_rate": 0.797,
            }
        )

class TestTConnectEntrySuspension(unittest.TestCase):
    def test_parse_suspension_entry(self):
        self.assertEqual(
            TConnectEntry.parse_suspension_entry({
                "suspendReason": "control-iq",
                "continuation": None,
                "x": 1615879821
            }),
            {
                "time": "2021-03-16 00:30:21-04:00",
                "continuation": None,
                "suspendReason": "control-iq"
            }
        )
        self.assertEqual(
            TConnectEntry.parse_suspension_entry({
                "suspendReason": "control-iq",
                "continuation": "previous",
                "x": 1634022000
            }),
            {
                "time": "2021-10-12 00:00:00-04:00",
                "continuation": "previous",
                "suspendReason": "control-iq"
            }
        )

class TestTConnectEntrySuspensionToBasal(unittest.TestCase):
    def test_manual_suspension_to_basal_entry(self):
        suspension = {
            "time": "2021-03-16 00:30:21-04:00",
            "continuation": None,
            "suspendReason": "manual"
        }

        self.assertEqual(
            TConnectEntry.manual_suspension_to_basal_entry(
                suspension,
                seconds=300
            ), {
                "time": "2021-03-16 00:30:21-04:00",
                "delivery_type": "manual suspension",
                "duration_mins": 5.0,
                "basal_rate": 0.0
            }
        )

class TestTConnectEntryCGM(unittest.TestCase):
    def test_parse_cgm_entry(self):
        self.assertEqual(
            TConnectEntry.parse_cgm_entry({
                "DeviceType": "t:slim X2 Insulin Pump",
                "SerialNumber": "11111111",
                "Description": "EGV",
                "EventDateTime": "2021-10-12T00:01:12",
                "Readings (CGM / BGM)": "131"
            }),
            {
                "time": "2021-10-12 00:01:12-04:00",
                "reading": "131",
                "reading_type": "EGV"
            }
        )

class TestTConnectEntryIOB(unittest.TestCase):
    entry1 = {
        "Type": "IOB",
        "EventID": "81",
        "EventDateTime": "2021-10-12T00:00:30",
        "IOB": "6.91"
    }
    def test_parse_iob_entry1(self):
        self.assertEqual(
            TConnectEntry.parse_iob_entry(self.entry1),
            {
                "time": "2021-10-12 00:00:30-04:00",
                "iob": "6.91",
                "event_id": "81"
            }
        )

    entry2 = {
        "Type": "IOB",
        "EventID": "9",
        "EventDateTime": "2021-10-12T00:10:30",
        "IOB": "6.80"
    }
    def test_parse_iob_entry2(self):
        self.assertEqual(
            TConnectEntry.parse_iob_entry(self.entry2),
            {
                "time": "2021-10-12 00:10:30-04:00",
                "iob": "6.80",
                "event_id": "9"
            }
        )

class TestTConnectEntryBolus(unittest.TestCase):
    entryStdCorrection = {
        "Type": "Bolus",
        "Description": "Standard/Correction",
        "BG": "141",
        "IOB": "",
        "BolusRequestID": "7001.000",
        "BolusCompletionID": "7001.000",
        "CompletionDateTime": "2021-04-01T12:58:26",
        "InsulinDelivered": "13.53",
        "FoodDelivered": "12.50",
        "CorrectionDelivered": "1.03",
        "CompletionStatusID": "3",
        "CompletionStatusDesc": "Completed",
        "BolusIsComplete": "1",
        "BolexCompletionID": "",
        "BolexSize": "",
        "BolexStartDateTime": "",
        "BolexCompletionDateTime": "",
        "BolexInsulinDelivered": "",
        "BolexIOB": "",
        "BolexCompletionStatusID": "",
        "BolexCompletionStatusDesc": "",
        "ExtendedBolusIsComplete": "",
        "EventDateTime": "2021-04-01T12:53:36",
        "RequestDateTime": "2021-04-01T12:53:36",
        "BolusType": "Carb",
        "BolusRequestOptions": "Standard/Correction",
        "StandardPercent": "100.00",
        "Duration": "0",
        "CarbSize": "75",
        "UserOverride": "0",
        "TargetBG": "110",
        "CorrectionFactor": "30.00",
        "FoodBolusSize": "12.50",
        "CorrectionBolusSize": "1.03",
        "ActualTotalBolusRequested": "13.53",
        "IsQuickBolus": "0",
        "EventHistoryReportEventDesc": "0",
        "EventHistoryReportDetails": "Correction & Food Bolus",
        "NoteID": "CF 1:30 - Carb Ratio 1:6 - Target BG 110",
        "IndexID": "0",
        "Note": "1181649"
    }
    def test_parse_bolus_entry_std_correction(self):
        self.assertEqual(
            TConnectEntry.parse_bolus_entry(self.entryStdCorrection),
            Bolus(**{
                "description": "Standard/Correction",
                "complete": "1",
                "completion": "Completed",
                "request_time": "2021-04-01 12:53:36-04:00",
                "completion_time": "2021-04-01 12:58:26-04:00",
                "insulin": "13.53",
                "requested_insulin": "13.53",
                "carbs": "75",
                "bg": "141",
                "user_override": "0",
                "extended_bolus": "",
                "bolex_completion_time": None,
                "bolex_start_time": None
        }))
    
    entryStd = {
        "Type": "Bolus",
        "Description": "Standard",
        "BG": "159",
        "IOB": "2.13",
        "BolusRequestID": "7007.000",
        "BolusCompletionID": "7007.000",
        "CompletionDateTime": "2021-04-01T23:23:17",
        "InsulinDelivered": "1.25",
        "FoodDelivered": "0.00",
        "CorrectionDelivered": "0.00",
        "CompletionStatusID": "3",
        "CompletionStatusDesc": "Completed",
        "BolusIsComplete": "1",
        "BolexCompletionID": "",
        "BolexSize": "",
        "BolexStartDateTime": "",
        "BolexCompletionDateTime": "",
        "BolexInsulinDelivered": "",
        "BolexIOB": "",
        "BolexCompletionStatusID": "",
        "BolexCompletionStatusDesc": "",
        "ExtendedBolusIsComplete": "",
        "EventDateTime": "2021-04-01T23:21:58",
        "RequestDateTime": "2021-04-01T23:21:58",
        "BolusType": "Carb",
        "BolusRequestOptions": "Standard",
        "StandardPercent": "100.00",
        "Duration": "0",
        "CarbSize": "0",
        "UserOverride": "1",
        "TargetBG": "110",
        "CorrectionFactor": "30.00",
        "FoodBolusSize": "0.00",
        "CorrectionBolusSize": "0.00",
        "ActualTotalBolusRequested": "1.25",
        "IsQuickBolus": "0",
        "EventHistoryReportEventDesc": "0",
        "EventHistoryReportDetails": "Food Bolus",
        "NoteID": "CF 1:30 - Carb Ratio 1:6 - Target BG 110 | Override: Pump calculated Bolus = 0.0 units",
        "IndexID": "0",
        "Note": "1182867"
    }
    def test_parse_bolus_entry_std(self):
        self.assertEqual(
            TConnectEntry.parse_bolus_entry(self.entryStd),
            Bolus(**{
                "description": "Standard",
                "complete": "1",
                "completion": "Completed",
                "request_time": "2021-04-01 23:21:58-04:00",
                "completion_time": "2021-04-01 23:23:17-04:00",
                "insulin": "1.25",
                "requested_insulin": "1.25",
                "carbs": "0",
                "bg": "159",
                "user_override": "1",
                "extended_bolus": "",
                "bolex_completion_time": None,
                "bolex_start_time": None
        }))
    
    entryStdAutomatic = {
        "Type": "Bolus",
        "Description": "Automatic Bolus/Correction",
        "BG": "",
        "IOB": "3.24",
        "BolusRequestID": "7010.000",
        "BolusCompletionID": "7010.000",
        "CompletionDateTime": "2021-04-02T01:00:47",
        "InsulinDelivered": "1.70",
        "FoodDelivered": "0.00",
        "CorrectionDelivered": "1.70",
        "CompletionStatusID": "3",
        "CompletionStatusDesc": "Completed",
        "BolusIsComplete": "1",
        "BolexCompletionID": "",
        "BolexSize": "",
        "BolexStartDateTime": "",
        "BolexCompletionDateTime": "",
        "BolexInsulinDelivered": "",
        "BolexIOB": "",
        "BolexCompletionStatusID": "",
        "BolexCompletionStatusDesc": "",
        "ExtendedBolusIsComplete": "",
        "EventDateTime": "2021-04-02T00:59:13",
        "RequestDateTime": "2021-04-02T00:59:13",
        "BolusType": "Automatic Correction",
        "BolusRequestOptions": "Automatic Bolus/Correction",
        "StandardPercent": "100.00",
        "Duration": "0",
        "CarbSize": "0",
        "UserOverride": "0",
        "TargetBG": "160",
        "CorrectionFactor": "30.00",
        "FoodBolusSize": "0.00",
        "CorrectionBolusSize": "1.70",
        "ActualTotalBolusRequested": "1.70",
        "IsQuickBolus": "0",
        "EventHistoryReportEventDesc": "0",
        "EventHistoryReportDetails": "Correction Bolus",
        "NoteID": "CF 1:30 - Carb Ratio 1:0 - Target BG 160",
        "IndexID": "0",
        "Note": "1183132"
    }
    def test_parse_bolus_entry_std_automatic(self):
        self.assertEqual(
            TConnectEntry.parse_bolus_entry(self.entryStdAutomatic),
            Bolus(**{
                "description": "Automatic Bolus/Correction",
                "complete": "1",
                "completion": "Completed",
                "request_time": "2021-04-02 00:59:13-04:00",
                "completion_time": "2021-04-02 01:00:47-04:00",
                "insulin": "1.70",
                "requested_insulin": "1.70",
                "carbs": "0",
                "bg": "",
                "user_override": "0",
                "extended_bolus": "",
                "bolex_completion_time": None,
                "bolex_start_time": None
        }))
    
    entryStdIncompleteZero = {
        "Type": "Bolus",
        "Description": "Standard",
        "BG": "144",
        "IOB": "1.20",
        "BolusRequestID": "9694.000",
        "BolusCompletionID": "9694.000",
        "CompletionDateTime": "2021-10-08T15:47:02",
        "InsulinDelivered": "0.00",
        "FoodDelivered": "0.00",
        "CorrectionDelivered": "0.00",
        "CompletionStatusID": "0",
        "CompletionStatusDesc": "User Aborted",
        "BolusIsComplete": "0",
        "BolexCompletionID": "",
        "BolexSize": "",
        "BolexStartDateTime": "",
        "BolexCompletionDateTime": "",
        "BolexInsulinDelivered": "",
        "BolexIOB": "",
        "BolexCompletionStatusID": "",
        "BolexCompletionStatusDesc": "",
        "ExtendedBolusIsComplete": "",
        "EventDateTime": "2021-10-08T15:46:56",
        "RequestDateTime": "2021-10-08T15:46:56",
        "BolusType": "Carb",
        "BolusRequestOptions": "Standard",
        "StandardPercent": "100.00",
        "Duration": "0",
        "CarbSize": "0",
        "UserOverride": "1",
        "TargetBG": "110",
        "CorrectionFactor": "30.00",
        "FoodBolusSize": "0.00",
        "CorrectionBolusSize": "0.00",
        "ActualTotalBolusRequested": "0.50",
        "IsQuickBolus": "0",
        "EventHistoryReportEventDesc": "0",
        "EventHistoryReportDetails": "Food Bolus",
        "NoteID": "CF 1:30 - Carb Ratio 1:6 - Target BG 110 | Override: Pump calculated Bolus = 0.0 units",
        "IndexID": "0",
        "Note": "1669328"
    }
    def test_parse_bolus_entry_std_incomplete_zero(self):
        self.assertEqual(
            TConnectEntry.parse_bolus_entry(self.entryStdIncompleteZero),
            Bolus(**{
                "description": "Standard",
                "complete": "",
                "completion": "User Aborted",
                "request_time": "2021-10-08 15:46:56-04:00",
                "completion_time": "2021-10-08 15:47:02-04:00",
                "insulin": "0.00",
                "requested_insulin": "0.50",
                "carbs": "0",
                "bg": "144",
                "user_override": "1",
                "extended_bolus": "",
                "bolex_completion_time": None,
                "bolex_start_time": None
            }))
    
    entryStdIncompletePartial = {
        "Type": "Bolus",
        "Description": "Standard/Correction",
        "BG": "189",
        "IOB": "",
        "BolusRequestID": "9261.000",
        "BolusCompletionID": "9261.000",
        "CompletionDateTime": "2021-09-06T12:24:47",
        "InsulinDelivered": "1.82",
        "FoodDelivered": "0.00",
        "CorrectionDelivered": "1.82",
        "CompletionStatusID": "1",
        "CompletionStatusDesc": "Terminated by Alarm",
        "BolusIsComplete": "0",
        "BolexCompletionID": "",
        "BolexSize": "",
        "BolexStartDateTime": "",
        "BolexCompletionDateTime": "",
        "BolexInsulinDelivered": "",
        "BolexIOB": "",
        "BolexCompletionStatusID": "",
        "BolexCompletionStatusDesc": "",
        "ExtendedBolusIsComplete": "",
        "EventDateTime": "2021-09-06T12:23:23",
        "RequestDateTime": "2021-09-06T12:23:23",
        "BolusType": "Carb",
        "BolusRequestOptions": "Standard/Correction",
        "StandardPercent": "100.00",
        "Duration": "0",
        "CarbSize": "0",
        "UserOverride": "0",
        "TargetBG": "110",
        "CorrectionFactor": "30.00",
        "FoodBolusSize": "0.00",
        "CorrectionBolusSize": "2.63",
        "ActualTotalBolusRequested": "2.63",
        "IsQuickBolus": "0",
        "EventHistoryReportEventDesc": "0",
        "EventHistoryReportDetails": "Correction & Food Bolus",
        "NoteID": "CF 1:30 - Carb Ratio 1:6 - Target BG 110",
        "IndexID": "0",
        "Note": "1589227"
    }
    def test_parse_bolus_entry_std_incomplete_partial(self):
        self.assertEqual(
            TConnectEntry.parse_bolus_entry(self.entryStdIncompletePartial),
            Bolus(**{
                "description": "Standard/Correction",
                "complete": "",
                "completion": "Terminated by Alarm",
                "request_time": "2021-09-06 12:23:23-04:00",
                "completion_time": "2021-09-06 12:24:47-04:00",
                "insulin": "1.82",
                "requested_insulin": "2.63",
                "carbs": "0",
                "bg": "189",
                "user_override": "0",
                "extended_bolus": "",
                "bolex_completion_time": None,
                "bolex_start_time": None
            }))


    entryExtendedComplete = {
        "Type": "Bolus",
        "Description": "Extended 50.00%/0.00",
        "BG": "131",
        "IOB": "5.87",
        "BolusRequestID": "3636.000",
        "BolusCompletionID": "3636.000",
        "CompletionDateTime": "2022-08-09T23:20:04",
        "InsulinDelivered": "0.20",
        "FoodDelivered": "0.00",
        "CorrectionDelivered": "0.00",
        "CompletionStatusID": "3",
        "CompletionStatusDesc": "Completed",
        "BolusIsComplete": "1",
        "BolexCompletionID": "16757133",
        "BolexSize": "0.20",
        "BolexStartDateTime": "2022-08-09T23:20:04",
        "BolexCompletionDateTime": "2022-08-09T23:35:03",
        "BolexInsulinDelivered": "0.20",
        "BolexIOB": "5.7",
        "BolexCompletionStatusID": "3.00",
        "BolexCompletionStatusDesc": "Completed",
        "ExtendedBolusIsComplete": "1",
        "EventDateTime": "2022-08-09T23:19:15",
        "RequestDateTime": "2022-08-09T23:19:15",
        "BolusType": "Carb",
        "BolusRequestOptions": "Extended",
        "StandardPercent": "50.00",
        "Duration": "15",
        "CarbSize": "0",
        "UserOverride": "1",
        "TargetBG": "110",
        "CorrectionFactor": "30.00",
        "FoodBolusSize": "0.00",
        "CorrectionBolusSize": "0.00",
        "ActualTotalBolusRequested": "0.40",
        "IsQuickBolus": "0",
        "EventHistoryReportEventDesc": "0",
        "EventHistoryReportDetails": "Food Bolus: 50% Extended 15 mins",
        "NoteID": "CF 1:30 - Carb Ratio 1:6 - Target BG 110 | Override: Pump calculated Bolus = 0.0 units",
        "IndexID": "0",
        "Note": "631597"
    }
    def test_parse_bolus_entry_extended_complete(self):
        self.assertEqual(
            TConnectEntry.parse_bolus_entry(self.entryExtendedComplete),
            Bolus(**{
                "description": "Extended 50.00%/0.00",
                "complete": "1",
                "completion": "Completed",
                "request_time": None,
                "completion_time": None,
                "insulin": "0.20",
                "requested_insulin": "0.40",
                "carbs": "0",
                "bg": "131",
                "user_override": "1",
                "extended_bolus": "1",
                "bolex_completion_time": "2022-08-09 23:35:03-04:00",
                "bolex_start_time": "2022-08-09 23:20:04-04:00"
            }))



class TestTConnectEntryReading(unittest.TestCase):
    entry1 = {
        "DeviceType": "t:slim X2 Insulin Pump",
        "SerialNumber": "90556643",
        "Description": "EGV",
        "EventDateTime": "2021-10-23T12:55:53",
        "Readings (CGM / BGM)": "135"
    }
    def test_parse_reading_entry1(self):
        self.assertEqual(
            TConnectEntry.parse_reading_entry(self.entry1),
            {
                "time": "2021-10-23 12:55:53-04:00",
                "bg": "135",
                "type": "EGV"
            }
        )

    entry2 = {
        "DeviceType": "t:slim X2 Insulin Pump",
        "SerialNumber": "90556643",
        "Description": "EGV",
        "EventDateTime": "2021-10-23T16:15:52",
        "Readings (CGM / BGM)": "93"
    }
    def test_parse_reading_entry2(self):
        self.assertEqual(
            TConnectEntry.parse_reading_entry(self.entry2),
            {
                "time": "2021-10-23 16:15:52-04:00",
                "bg": "93",
                "type": "EGV"
            }
        )

    entry3 = {
        "DeviceType": "t:slim X2 Insulin Pump",
        "SerialNumber": "90556643",
        "Description": "EGV",
        "EventDateTime": "2021-10-23T16:20:52",
        "Readings (CGM / BGM)": "100"
    }
    def test_parse_reading_entry3(self):
        self.assertEqual(
            TConnectEntry.parse_reading_entry(self.entry3),
            {
                "time": "2021-10-23 16:20:52-04:00",
                "bg": "100",
                "type": "EGV"
            }
        )

    entry4 = {
        "DeviceType": "t:slim X2 Insulin Pump",
        "SerialNumber": "90556643",
        "Description": "EGV",
        "EventDateTime": "2021-10-23T16:25:52",
        "Readings (CGM / BGM)": "107"
    }
    def test_parse_reading_entry4(self):
        self.assertEqual(
            TConnectEntry.parse_reading_entry(self.entry4),
            {
                "time": "2021-10-23 16:25:52-04:00",
                "bg": "107",
                "type": "EGV"
            }
        )


class TestTConnectEntryCIQEvent(unittest.TestCase):
    def test_parse_ciq_activity_event_sleep(self):
        self.assertEqual(
            TConnectEntry.parse_ciq_activity_event({
                "continuation": None,
                "duration": 30661,
                "eventType": 1,
                "timeZoneId": "America/Los_Angeles",
                "x": 1638091836
            }),
            {
                "time": "2021-11-28 01:30:36-05:00",
                "duration_mins": (30661 / 60),
                "event_type": "Sleep"
            }
        )

    def test_parse_ciq_activity_event_exercise(self):
        self.assertEqual(
            TConnectEntry.parse_ciq_activity_event({
                "duration": 1200,
                "eventType": 2,
                "continuation": None, 
                "timeZoneId": "America/Los_Angeles",
                "x": 1619901912
            }),
            {
                "time": "2021-05-01 13:45:12-04:00",
                "duration_mins": 20,
                "event_type": "Exercise"
            }
        )
    
    def test_parse_ciq_activity_event_unknown_id(self):
        self.assertRaises(
            UnknownCIQActivityEventException, 
            TConnectEntry.parse_ciq_activity_event,
            {
                "duration": 1200,
                "eventType": 5,
                "continuation": None, 
                "timeZoneId": "America/Los_Angeles",
                "x": 1619901912
            }
        )

class TestTConnectEntryBasalSuspensionEvent(unittest.TestCase):
    def test_parse_basalsuspension_event_sitecart(self):
        self.assertEqual(
            TConnectEntry.parse_basalsuspension_event({
                'EventDateTime': '/Date(1638663490000-0000)/',
                'SuspendReason': 'site-cart'
            }),
            {
                "time": "2021-12-04 16:18:10-05:00",
                "event_type": "Site/Cartridge Change"
            }
        )

    def test_parse_basalsuspension_event_alarm(self):
        self.assertEqual(
            TConnectEntry.parse_basalsuspension_event({
                'EventDateTime': '/Date(1637863616000-0000)/',
                'SuspendReason': 'alarm'
            }),
            {
                "time": "2021-11-25 10:06:56-05:00",
                "event_type": "Empty Cartridge/Pump Shutdown"
            }
        )

    def test_parse_basalsuspension_event_manual(self):
        self.assertEqual(
            TConnectEntry.parse_basalsuspension_event({
                'EventDateTime': '/Date(1638662852000-0000)/',
                'SuspendReason': 'manual'
            }),
            {
                "time": "2021-12-04 16:07:32-05:00",
                "event_type": "User Suspended"
            }
        )

    def test_parse_basalsuspension_event_tempprofile(self):
        self.assertEqual(
            TConnectEntry.parse_basalsuspension_event({
                'EventDateTime': '/Date(1640541521000-0000)/',
                'SuspendReason': 'temp-profile'
            }),
            {
                "time": "2021-12-26 09:58:41-05:00",
                "event_type": "Basal Rate Change"
            }
        )

    def test_parse_basalsuspension_event_basalprofile_skipped(self):
        self.assertIsNone(
            TConnectEntry.parse_basalsuspension_event({
                'EventDateTime': '/Date(1638659343000-0000)/',
                'SuspendReason': 'basal-profile',
            })
        )

    def test_parse_basalsuspension_event_previous_skipped(self):
        self.assertIsNone(
            TConnectEntry.parse_basalsuspension_event({
                'Continuation': 'continuation',
                'EventDateTime': '/Date(1638604800000-0000)/',
                'SuspendReason': 'previous',
            })
        )
    
    def test_parse_basalsuspension_event_unknown_suspendreason(self):
        self.assertRaises(
            UnknownBasalSuspensionEventException, 
            TConnectEntry.parse_basalsuspension_event,
            {
                'EventDateTime': '/Date(1638604800000-0000)/',
                'SuspendReason': 'unknown',
            }
        )


if __name__ == '__main__':
    unittest.main()