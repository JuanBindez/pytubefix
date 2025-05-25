# All credits to https://github.com/LuanRT/googlevideo

from pytubefix.sabr.proto import BinaryWriter, BinaryReader


class ClientAbrState:

    @staticmethod
    def create_base_client_abr_state():
        return {
            "timeSinceLastManualFormatSelectionMs": 0,
            "lastManualDirection": 0,
            "lastManualSelectedResolution": 0,
            "detailedNetworkType": 0,
            "clientViewportWidth": 0,
            "clientViewportHeight": 0,
            "clientBitrateCapBytesPerSec": 0,
            "stickyResolution": 0,
            "clientViewportIsFlexible": False,
            "bandwidthEstimate": 0,
            "minAudioQuality": 0,
            "maxAudioQuality": 0,
            "videoQualitySetting": 0,
            "audioRoute": 0,
            "playerTimeMs": 0,
            "timeSinceLastSeek": 0,
            "dataSaverMode": False,
            "networkMeteredState": 0,
            "visibility": 0,
            "playbackRate": 0,
            "elapsedWallTimeMs": 0,
            "mediaCapabilities": bytearray(),
            "timeSinceLastActionMs": 0,
            "enabledTrackTypesBitfield": 0,
            "maxPacingRate": 0,
            "playerState": 0,
            "drcEnabled": False,
            "Jda": 0,
            "qw": 0,
            "Ky": 0,
            "sabrReportRequestCancellationInfo": 0,
            "l": False,
            "G7": 0,
            "preferVp9": False,
            "qj": 0,
            "Hx": 0,
            "isPrefetch": False,
            "sabrSupportQualityConstraints": 0,
            "sabrLicenseConstraint": bytearray(),
            "allowProximaLiveLatency": 0,
            "sabrForceProxima": 0,
            "Tqb": 0,
            "sabrForceMaxNetworkInterruptionDurationMs": 0,
            "audioTrackId": ""
        }

    @staticmethod
    def encode(message: dict, writer=None):
        if writer is None:
            writer = BinaryWriter()

        if message.get("timeSinceLastManualFormatSelectionMs", 0):
            writer.uint32(104).int64(message["timeSinceLastManualFormatSelectionMs"])
        if message.get("lastManualDirection", 0):
            writer.uint32(112).sint32(message["lastManualDirection"])
        if message.get("lastManualSelectedResolution", 0):
            writer.uint32(128).int32(message["lastManualSelectedResolution"])
        if message.get("detailedNetworkType", 0):
            writer.uint32(136).int32(message["detailedNetworkType"])
        if message.get("clientViewportWidth", 0):
            writer.uint32(144).int32(message["clientViewportWidth"])
        if message.get("clientViewportHeight", 0):
            writer.uint32(152).int32(message["clientViewportHeight"])
        if message.get("clientBitrateCapBytesPerSec", 0):
            writer.uint32(160).int64(message["clientBitrateCapBytesPerSec"])
        if message.get("stickyResolution", 0):
            writer.uint32(168).int32(message["stickyResolution"])
        if message.get("clientViewportIsFlexible", False):
            writer.uint32(176).bool(message["clientViewportIsFlexible"])
        if message.get("bandwidthEstimate", 0):
            writer.uint32(184).int64(message["bandwidthEstimate"])
        if message.get("minAudioQuality", 0):
            writer.uint32(192).int32(message["minAudioQuality"])
        if message.get("maxAudioQuality", 0):
            writer.uint32(200).int32(message["maxAudioQuality"])
        if message.get("videoQualitySetting", 0):
            writer.uint32(208).int32(message["videoQualitySetting"])
        if message.get("audioRoute", 0):
            writer.uint32(216).int32(message["audioRoute"])
        if message.get("playerTimeMs", 0):
            writer.uint32(224).int64(message["playerTimeMs"])
        if message.get("timeSinceLastSeek", 0):
            writer.uint32(232).int64(message["timeSinceLastSeek"])
        if message.get("dataSaverMode", False):
            writer.uint32(240).bool(message["dataSaverMode"])
        if message.get("networkMeteredState", 0):
            writer.uint32(256).int32(message["networkMeteredState"])
        if message.get("visibility", 0):
            writer.uint32(272).int32(message["visibility"])
        if message.get("playbackRate", 0):
            writer.uint32(285).float(message["playbackRate"])
        if message.get("elapsedWallTimeMs", 0):
            writer.uint32(288).int64(message["elapsedWallTimeMs"])
        if message.get("mediaCapabilities", b''):
            writer.uint32(306).bytes(message["mediaCapabilities"])
        if message.get("timeSinceLastActionMs", 0):
            writer.uint32(312).int64(message["timeSinceLastActionMs"])
        if message.get("enabledTrackTypesBitfield", 0):
            writer.uint32(320).int32(message["enabledTrackTypesBitfield"])
        if message.get("maxPacingRate", 0):
            writer.uint32(344).int32(message["maxPacingRate"])
        if message.get("playerState", 0):
            writer.uint32(352).int64(message["playerState"])
        if message.get("drcEnabled", False):
            writer.uint32(368).bool(message["drcEnabled"])
        if message.get("Jda", 0):
            writer.uint32(384).int32(message["Jda"])
        if message.get("qw", 0):
            writer.uint32(400).int32(message["qw"])
        if message.get("Ky", 0):
            writer.uint32(408).int32(message["Ky"])
        if message.get("sabrReportRequestCancellationInfo", 0):
            writer.uint32(432).int32(message["sabrReportRequestCancellationInfo"])
        if message.get("l", False):
            writer.uint32(448).bool(message["l"])
        if message.get("G7", 0):
            writer.uint32(456).int64(message["G7"])
        if message.get("preferVp9", False):
            writer.uint32(464).bool(message["preferVp9"])
        if message.get("qj", 0):
            writer.uint32(472).int32(message["qj"])
        if message.get("Hx", 0):
            writer.uint32(480).int32(message["Hx"])
        if message.get("isPrefetch", False):
            writer.uint32(488).bool(message["isPrefetch"])
        if message.get("sabrSupportQualityConstraints", 0):
            writer.uint32(496).int32(message["sabrSupportQualityConstraints"])
        if message.get("sabrLicenseConstraint", b''):
            writer.uint32(506).bytes(message["sabrLicenseConstraint"])
        if message.get("allowProximaLiveLatency", 0):
            writer.uint32(512).int32(message["allowProximaLiveLatency"])
        if message.get("sabrForceProxima", 0):
            writer.uint32(528).int32(message["sabrForceProxima"])
        if message.get("Tqb", 0):
            writer.uint32(536).int32(message["Tqb"])
        if message.get("sabrForceMaxNetworkInterruptionDurationMs", 0):
            writer.uint32(544).int64(message["sabrForceMaxNetworkInterruptionDurationMs"])
        if message.get("audioTrackId", ""):
            writer.uint32(554).string(message["audioTrackId"])

        return writer

    @staticmethod
    def decode(input_data, length=None):
        reader = input_data if isinstance(input_data, BinaryReader) else BinaryReader(input_data)
        end = reader.len if length is None else reader.pos + length
        message = ClientAbrState.create_base_client_abr_state()

        while reader.pos < end:
            tag = reader.uint32()
            field_number = tag >> 3

            if field_number == 13 and tag == 104:
                message['timeSinceLastManualFormatSelectionMs'] = long_to_number(reader.int64())
                continue
            elif field_number == 14 and tag == 112:
                message['lastManualDirection'] = reader.sint32()
                continue
            elif field_number == 16 and tag == 128:
                message['lastManualSelectedResolution'] = reader.int32()
                continue
            elif field_number == 17 and tag == 136:
                message['detailedNetworkType'] = reader.int32()
                continue
            elif field_number == 18 and tag == 144:
                message['clientViewportWidth'] = reader.int32()
                continue
            elif field_number == 19 and tag == 152:
                message['clientViewportHeight'] = reader.int32()
                continue
            elif field_number == 20 and tag == 160:
                message['clientBitrateCapBytesPerSec'] = long_to_number(reader.int64())
                continue
            elif field_number == 21 and tag == 168:
                message['stickyResolution'] = reader.int32()
                continue
            elif field_number == 22 and tag == 176:
                message['clientViewportIsFlexible'] = reader.bool()
                continue
            elif field_number == 23 and tag == 184:
                message['bandwidthEstimate'] = long_to_number(reader.int64())
                continue
            elif field_number == 24 and tag == 192:
                message['minAudioQuality'] = reader.int32()
                continue
            elif field_number == 25 and tag == 200:
                message['maxAudioQuality'] = reader.int32()
                continue
            elif field_number == 26 and tag == 208:
                message['videoQualitySetting'] = reader.int32()
                continue
            elif field_number == 27 and tag == 216:
                message['audioRoute'] = reader.int32()
                continue
            elif field_number == 28 and tag == 224:
                message['playerTimeMs'] = long_to_number(reader.int64())
                continue
            elif field_number == 29 and tag == 232:
                message['timeSinceLastSeek'] = long_to_number(reader.int64())
                continue
            elif field_number == 30 and tag == 240:
                message['dataSaverMode'] = reader.bool()
                continue
            elif field_number == 32 and tag == 256:
                message['networkMeteredState'] = reader.int32()
                continue
            elif field_number == 34 and tag == 272:
                message['visibility'] = reader.int32()
                continue
            elif field_number == 35 and tag == 285:
                message['playbackRate'] = reader.float()
                continue
            elif field_number == 36 and tag == 288:
                message['elapsedWallTimeMs'] = long_to_number(reader.int64())
                continue
            elif field_number == 38 and tag == 306:
                message['mediaCapabilities'] = reader.bytes()
                continue
            elif field_number == 39 and tag == 312:
                message['timeSinceLastActionMs'] = long_to_number(reader.int64())
                continue
            elif field_number == 40 and tag == 320:
                message['enabledTrackTypesBitfield'] = reader.int32()
                continue
            elif field_number == 43 and tag == 344:
                message['maxPacingRate'] = reader.int32()
                continue
            elif field_number == 44 and tag == 352:
                message['playerState'] = long_to_number(reader.int64())
                continue
            elif field_number == 46 and tag == 368:
                message['drcEnabled'] = reader.bool()
                continue
            elif field_number == 48 and tag == 384:
                message['Jda'] = reader.int32()
                continue
            elif field_number == 50 and tag == 400:
                message['qw'] = reader.int32()
                continue
            elif field_number == 51 and tag == 408:
                message['Ky'] = reader.int32()
                continue
            elif field_number == 54 and tag == 432:
                message['sabrReportRequestCancellationInfo'] = reader.int32()
                continue
            elif field_number == 56 and tag == 448:
                message['l'] = reader.bool()
                continue
            elif field_number == 57 and tag == 456:
                message['G7'] = long_to_number(reader.int64())
                continue
            elif field_number == 58 and tag == 464:
                message['preferVp9'] = reader.bool()
                continue
            elif field_number == 59 and tag == 472:
                message['qj'] = reader.int32()
                continue
            elif field_number == 60 and tag == 480:
                message['Hx'] = reader.int32()
                continue
            elif field_number == 61 and tag == 488:
                message['isPrefetch'] = reader.bool()
                continue
            elif field_number == 62 and tag == 496:
                message['sabrSupportQualityConstraints'] = reader.int32()
                continue
            elif field_number == 63 and tag == 506:
                message['sabrLicenseConstraint'] = reader.bytes()
                continue
            elif field_number == 64 and tag == 512:
                message['allowProximaLiveLatency'] = reader.int32()
                continue
            elif field_number == 66 and tag == 528:
                message['sabrForceProxima'] = reader.int32()
                continue
            elif field_number == 67 and tag == 536:
                message['Tqb'] = reader.int32()
                continue
            elif field_number == 68 and tag == 544:
                message['sabrForceMaxNetworkInterruptionDurationMs'] = long_to_number(reader.int64())
                continue
            elif field_number == 69 and tag == 554:
                message['audioTrackId'] = reader.string()
                continue
            else:
                if (tag & 7) == 4 or tag == 0:
                    break
                reader.skip(tag & 7)

        return message

def long_to_number(int64_value):
    value = int(str(int64_value))
    if value > (2 ** 53 - 1):
        raise OverflowError("Value is larger than 9007199254740991")
    if value < -(2 ** 53 - 1):
        raise OverflowError("Value is smaller than -9007199254740991")
    return value