# -*- coding: utf-8 -*-
# Merged Protocol Buffer definitions for xMaSrY_BoT
# This file combines all generated pb2 modules into one.

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# ============================================================================
# File: DEcwHisPErMsG_pb2.py (DecodeWhisperMsg)
# ============================================================================
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    30,
    0,
    '',
    'DecodeWhisperMsg.proto'
)

_sym_db = _symbol_database.Default()

DESCRIPTOR_DECODE_WHISPER = _descriptor_pool.Default().AddSerializedFile(b'\n\x16\x44\x65\x63odeWhisperMsg.proto\"\xa8\x02\n\rDecodeWhisper\x12$\n\x04\x44\x61ta\x18\x05 \x01(\x0b\x32\x16.DecodeWhisper.Nested1\x1a\xf0\x01\n\x07Nested1\x12\x0b\n\x03uid\x18\x01 \x01(\x04\x12\x0f\n\x07\x43hat_ID\x18\x02 \x01(\x04\x12\x11\n\tchat_type\x18\x03 \x01(\x05\x12\x0b\n\x03msg\x18\x04 \x01(\t\x12/\n\x07\x44\x65tails\x18\t \x01(\x0b\x32\x1e.DecodeWhisper.Nested1.Nested2\x12\x35\n\rPlatform_Info\x18\r \x01(\x0b\x32\x1e.DecodeWhisper.Nested1.Nested3\x1a\x1b\n\x07Nested2\x12\x10\n\x08Nickname\x18\x01 \x01(\t\x1a\"\n\x07Nested3\x12\x17\n\x0fprofile_pic_url\x18\x01 \x01(\tb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR_DECODE_WHISPER, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR_DECODE_WHISPER, 'DecodeWhisperMsg_pb2', globals())
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR_DECODE_WHISPER._loaded_options = None
    globals()['_DECODEWHISPER']._serialized_start = 27
    globals()['_DECODEWHISPER']._serialized_end = 323
    globals()['_DECODEWHISPER_NESTED1']._serialized_start = 83
    globals()['_DECODEWHISPER_NESTED1']._serialized_end = 323
    globals()['_DECODEWHISPER_NESTED1_NESTED2']._serialized_start = 260
    globals()['_DECODEWHISPER_NESTED1_NESTED2']._serialized_end = 287
    globals()['_DECODEWHISPER_NESTED1_NESTED3']._serialized_start = 289
    globals()['_DECODEWHISPER_NESTED1_NESTED3']._serialized_end = 323

# ============================================================================
# File: Fo_pb2.py (Friends)
# ============================================================================
# (No runtime version validation - older style)

_sym_db = _symbol_database.Default()

DESCRIPTOR_FRIENDS = _descriptor_pool.Default().AddSerializedFile(b'\n\rFriends.proto\"\"\n\x06\x46riend\x12\n\n\x02ID\x18\x01 \x01(\x03\x12\x0c\n\x04Name\x18\x03 \x01(\t\"#\n\x07\x46riends\x12\x18\n\x07\x66ield_1\x18\x01 \x03(\x0b\x32\x07.Friendb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR_FRIENDS, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR_FRIENDS, 'Friends_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR_FRIENDS._options = None
    globals()['_FRIEND']._serialized_start = 17
    globals()['_FRIEND']._serialized_end = 51
    globals()['_FRIENDS']._serialized_start = 53
    globals()['_FRIENDS']._serialized_end = 88

# ============================================================================
# File: GenWhisperMsg_pb2.py (GenWhisper)
# ============================================================================
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    30,
    0,
    '',
    'GenWhisperMsg.proto'
)

_sym_db = _symbol_database.Default()

DESCRIPTOR_GEN_WHISPER = _descriptor_pool.Default().AddSerializedFile(b'\n\x13GenWhisperMsg.proto\"\x85\x06\n\nGenWhisper\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12!\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x13.GenWhisper.Nested2\x1a\xc5\x05\n\x07Nested2\x12\x0b\n\x03uid\x18\x01 \x01(\x04\x12\x0f\n\x07\x63hat_id\x18\x02 \x01(\x04\x12\x11\n\tchat_type\x18\x03 \x01(\x05\x12\x0b\n\x03msg\x18\x04 \x01(\t\x12\x11\n\ttimestamp\x18\x05 \x01(\x03\x12+\n\x06\x66ield9\x18\t \x01(\x0b\x32\x1b.GenWhisper.Nested2.Nested9\x12\x10\n\x08language\x18\n \x01(\t\x12-\n\x07\x66ield13\x18\r \x01(\x0b\x32\x1c.GenWhisper.Nested2.Nested13\x12\x31\n\x0b\x65mpty_field\x18\x0e \x01(\x0b\x32\x1c.GenWhisper.Nested2.Nested14\x12\x11\n\tCelebrity\x18\x10 \x01(\x04\x1a\n\n\x08Nested14\x1a\xff\x01\n\x07Nested9\x12\x10\n\x08Nickname\x18\x01 \x01(\t\x12\x11\n\tavatar_id\x18\x02 \x01(\x03\x12\x11\n\tbanner_id\x18\x03 \x01(\x03\x12\x0c\n\x04rank\x18\x04 \x01(\x05\x12\r\n\x05\x62\x61\x64ge\x18\x05 \x01(\x05\x12\x11\n\tClan_Name\x18\x08 \x01(\t\x12\x0f\n\x07\x66ield10\x18\n \x01(\x05\x12\x17\n\x0fglobal_rank_pos\x18\x0b \x01(\x05\x12\x30\n\x07\x66ield13\x18\r \x01(\x0b\x32\x1f.GenWhisper.Nested2.NestedBadge\x12\x30\n\x07\x66ield14\x18\x0e \x01(\x0b\x32\x1f.GenWhisper.Nested2.NestedPrime\x1a\x1c\n\x0bNestedBadge\x12\r\n\x05value\x18\x01 \x01(\x05\x1aH\n\x0bNestedPrime\x12\x11\n\tprime_uid\x18\x01 \x01(\x05\x12\x13\n\x0bprime_level\x18\x02 \x01(\x05\x12\x11\n\tprime_hex\x18\x03 \x01(\t\x1a?\n\x08Nested13\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x10\n\x08url_type\x18\x02 \x01(\x05\x12\x14\n\x0curl_platform\x18\x03 \x01(\x05\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR_GEN_WHISPER, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR_GEN_WHISPER, 'GenWhisperMsg_pb2', globals())
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR_GEN_WHISPER._loaded_options = None
    globals()['_GENWHISPER']._serialized_start = 24
    globals()['_GENWHISPER']._serialized_end = 797
    globals()['_GENWHISPER_NESTED2']._serialized_start = 88
    globals()['_GENWHISPER_NESTED2']._serialized_end = 797
    globals()['_GENWHISPER_NESTED2_NESTED14']._serialized_start = 360
    globals()['_GENWHISPER_NESTED2_NESTED14']._serialized_end = 370
    globals()['_GENWHISPER_NESTED2_NESTED9']._serialized_start = 373
    globals()['_GENWHISPER_NESTED2_NESTED9']._serialized_end = 628
    globals()['_GENWHISPER_NESTED2_NESTEDBADGE']._serialized_start = 630
    globals()['_GENWHISPER_NESTED2_NESTEDBADGE']._serialized_end = 658
    globals()['_GENWHISPER_NESTED2_NESTEDPRIME']._serialized_start = 660
    globals()['_GENWHISPER_NESTED2_NESTEDPRIME']._serialized_end = 732
    globals()['_GENWHISPER_NESTED2_NESTED13']._serialized_start = 734
    globals()['_GENWHISPER_NESTED2_NESTED13']._serialized_end = 797

# ============================================================================
# File: MajoRLoGinrEq_pb2.py (MajorLoginReq)
# ============================================================================
# (No runtime version validation)

_sym_db = _symbol_database.Default()

DESCRIPTOR_MAJOR_LOGIN_REQ = _descriptor_pool.Default().AddSerializedFile(b'\n\x13MajorLoginReq.proto\"\xfa\n\n\nMajorLogin\x12\x12\n\nevent_time\x18\x03 \x01(\t\x12\x11\n\tgame_name\x18\x04 \x01(\t\x12\x13\n\x0bplatform_id\x18\x05 \x01(\x05\x12\x16\n\x0e\x63lient_version\x18\x07 \x01(\t\x12\x17\n\x0fsystem_software\x18\x08 \x01(\t\x12\x17\n\x0fsystem_hardware\x18\t \x01(\t\x12\x18\n\x10telecom_operator\x18\n \x01(\t\x12\x14\n\x0cnetwork_type\x18\x0b \x01(\t\x12\x14\n\x0cscreen_width\x18\x0c \x01(\r\x12\x15\n\rscreen_height\x18\r \x01(\r\x12\x12\n\nscreen_dpi\x18\x0e \x01(\t\x12\x19\n\x11processor_details\x18\x0f \x01(\t\x12\x0e\n\x06memory\x18\x10 \x01(\r\x12\x14\n\x0cgpu_renderer\x18\x11 \x01(\t\x12\x13\n\x0bgpu_version\x18\x12 \x01(\t\x12\x18\n\x10unique_device_id\x18\x13 \x01(\t\x12\x11\n\tclient_ip\x18\x14 \x01(\t\x12\x10\n\x08language\x18\x15 \x01(\t\x12\x0f\n\x07open_id\x18\x16 \x01(\t\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0b\x64\x65vice_type\x18\x18 \x01(\t\x12\'\n\x10memory_available\x18\x19 \x01(\x0b\x32\r.GameSecurity\x12\x14\n\x0c\x61\x63\x63\x65ss_token\x18\x1d \x01(\t\x12\x17\n\x0fplatform_sdk_id\x18\x1e \x01(\x05\x12\x1a\n\x12network_operator_a\x18) \x01(\t\x12\x16\n\x0enetwork_type_a\x18* \x01(\t\x12\x1c\n\x14\x63lient_using_version\x18\x39 \x01(\t\x12\x1e\n\x16\x65xternal_storage_total\x18< \x01(\x05\x12\"\n\x1a\x65xternal_storage_available\x18= \x01(\x05\x12\x1e\n\x16internal_storage_total\x18> \x01(\x05\x12\"\n\x1ainternal_storage_available\x18? \x01(\x05\x12#\n\x1bgame_disk_storage_available\x18@ \x01(\x05\x12\x1f\n\x17game_disk_storage_total\x18\x41 \x01(\x05\x12%\n\x1d\x65xternal_sdcard_avail_storage\x18\x42 \x01(\x05\x12%\n\x1d\x65xternal_sdcard_total_storage\x18\x43 \x01(\x05\x12\x10\n\x08login_by\x18I \x01(\x05\x12\x14\n\x0clibrary_path\x18J \x01(\t\x12\x12\n\nreg_avatar\x18L \x01(\x05\x12\x15\n\rlibrary_token\x18M \x01(\t\x12\x14\n\x0c\x63hannel_type\x18N \x01(\x05\x12\x10\n\x08\x63pu_type\x18O \x01(\x05\x12\x18\n\x10\x63pu_architecture\x18Q \x01(\t\x12\x1b\n\x13\x63lient_version_code\x18S \x01(\t\x12\x14\n\x0cgraphics_api\x18V \x01(\t\x12\x1d\n\x15supported_astc_bitset\x18W \x01(\r\x12\x1a\n\x12login_open_id_type\x18X \x01(\x05\x12\x18\n\x10\x61nalytics_detail\x18Y \x01(\x0c\x12\x14\n\x0cloading_time\x18\\ \x01(\r\x12\x17\n\x0frelease_channel\x18] \x01(\t\x12\x12\n\nextra_info\x18^ \x01(\t\x12 \n\x18\x61ndroid_engine_init_flag\x18_ \x01(\r\x12\x0f\n\x07if_push\x18\x61 \x01(\x05\x12\x0e\n\x06is_vpn\x18\x62 \x01(\x05\x12\x1c\n\x14origin_platform_type\x18\x63 \x01(\t\x12\x1d\n\x15primary_platform_type\x18\x64 \x01(\t\"5\n\x0cGameSecurity\x12\x0f\n\x07version\x18\x06 \x01(\x05\x12\x14\n\x0chidden_value\x18\x08 \x01(\x04\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR_MAJOR_LOGIN_REQ, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR_MAJOR_LOGIN_REQ, 'MajorLoginReq_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR_MAJOR_LOGIN_REQ._options = None
    globals()['_MAJORLOGIN']._serialized_start = 24
    globals()['_MAJORLOGIN']._serialized_end = 1426
    globals()['_GAMESECURITY']._serialized_start = 1428
    globals()['_GAMESECURITY']._serialized_end = 1481

# ============================================================================
# File: MajoRLoGinrEs_pb2.py (MajorLoginRes)
# ============================================================================
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    30,
    0,
    '',
    'MajorLoginRes.proto'
)

_sym_db = _symbol_database.Default()

DESCRIPTOR_MAJOR_LOGIN_RES = _descriptor_pool.Default().AddSerializedFile(b'\n\x13MajorLoginRes.proto\"|\n\rMajorLoginRes\x12\x13\n\x0b\x61\x63\x63ount_uid\x18\x01 \x01(\x04\x12\x0e\n\x06region\x18\x02 \x01(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03url\x18\n \x01(\t\x12\x11\n\ttimestamp\x18\x15 \x01(\x03\x12\x0b\n\x03key\x18\x16 \x01(\x0c\x12\n\n\x02iv\x18\x17 \x01(\x0c\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR_MAJOR_LOGIN_RES, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR_MAJOR_LOGIN_RES, 'MajorLoginRes_pb2', globals())
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR_MAJOR_LOGIN_RES._loaded_options = None
    globals()['_MAJORLOGINRES']._serialized_start = 23
    globals()['_MAJORLOGINRES']._serialized_end = 147

# ============================================================================
# File: PorTs_pb2.py (GetLoginDataRes)
# ============================================================================
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    30,
    0,
    '',
    'GetLoginDataRes.proto'
)

_sym_db = _symbol_database.Default()

DESCRIPTOR_GET_LOGIN_DATA = _descriptor_pool.Default().AddSerializedFile(b'\n\x15GetLoginDataRes.proto\"\xa4\x01\n\x0cGetLoginData\x12\x12\n\nAccountUID\x18\x01 \x01(\x04\x12\x0e\n\x06Region\x18\x03 \x01(\t\x12\x13\n\x0b\x41\x63\x63ountName\x18\x04 \x01(\t\x12\x16\n\x0eOnline_IP_Port\x18\x0e \x01(\t\x12\x0f\n\x07\x43lan_ID\x18\x14 \x01(\x03\x12\x16\n\x0e\x41\x63\x63ountIP_Port\x18  \x01(\t\x12\x1a\n\x12\x43lan_Compiled_Data\x18\x37 \x01(\tb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR_GET_LOGIN_DATA, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR_GET_LOGIN_DATA, 'GetLoginDataRes_pb2', globals())
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR_GET_LOGIN_DATA._loaded_options = None
    globals()['_GETLOGINDATA']._serialized_start = 26
    globals()['_GETLOGINDATA']._serialized_end = 190

# ============================================================================
# File: sQ_pb2.py (recieved_chat)
# ============================================================================
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    30,
    0,
    '',
    'recieved_chat.proto'
)

_sym_db = _symbol_database.Default()

DESCRIPTOR_RECIEVED_CHAT = _descriptor_pool.Default().AddSerializedFile(b'\n\x13recieved_chat.proto\"\x80\x01\n\rrecieved_chat\x12\x13\n\x0bpacket_type\x18\x04 \x01(\x03\x12&\n\x07\x64\x65tails\x18\x05 \x01(\x0b\x32\x15.recieved_chat.nested\x1a\x32\n\x06nested\x12\x12\n\nplayer_uid\x18\x01 \x01(\x03\x12\x14\n\x0cteam_session\x18\x0e \x01(\tb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR_RECIEVED_CHAT, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR_RECIEVED_CHAT, 'recieved_chat_pb2', globals())
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR_RECIEVED_CHAT._loaded_options = None
    globals()['_RECIEVED_CHAT']._serialized_start = 24
    globals()['_RECIEVED_CHAT']._serialized_end = 152
    globals()['_RECIEVED_CHAT_NESTED']._serialized_start = 102
    globals()['_RECIEVED_CHAT_NESTED']._serialized_end = 152

# ============================================================================
# File: Team_msg_pb2.py (Team_msg)
# ============================================================================
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    30,
    0,
    '',
    'Team_msg.proto'
)

_sym_db = _symbol_database.Default()

DESCRIPTOR_TEAM_MSG = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eTeam_msg.proto\"\x94\x06\n\x0eGenTeamWhisper\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12%\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x17.GenTeamWhisper.Nested2\x1a\xcc\x05\n\x07Nested2\x12\x0b\n\x03uid\x18\x01 \x01(\x03\x12\x0f\n\x07\x63hat_id\x18\x02 \x01(\x03\x12\x0b\n\x03msg\x18\x04 \x01(\t\x12\x11\n\ttimestamp\x18\x05 \x01(\x03\x12\x11\n\tchat_type\x18\x07 \x01(\x05\x12\r\n\x05title\x18\x08 \x01(\x05\x12/\n\x06\x66ield9\x18\t \x01(\x0b\x32\x1f.GenTeamWhisper.Nested2.Nested9\x12\x10\n\x08language\x18\n \x01(\t\x12\x31\n\x07\x66ield13\x18\r \x01(\x0b\x32 .GenTeamWhisper.Nested2.Nested13\x12\x35\n\x0b\x65mpty_field\x18\x0e \x01(\x0b\x32 .GenTeamWhisper.Nested2.Nested14\x1a\n\n\x08Nested14\x1a\xf2\x02\n\x07Nested9\x12\x10\n\x08Nickname\x18\x01 \x01(\t\x12\x11\n\tavatar_id\x18\x02 \x01(\x03\x12\x0c\n\x04rank\x18\x04 \x01(\x05\x12\r\n\x05\x62\x61\x64ge\x18\x05 \x01(\x05\x12\x11\n\tClan_Name\x18\x08 \x01(\t\x12\x0f\n\x07\x66ield10\x18\n \x01(\x05\x12\x17\n\x0fglobal_rank_pos\x18\x0b \x01(\x05\x12?\n\nbadge_info\x18\r \x01(\x0b\x32+.GenTeamWhisper.Nested2.Nested9.NestedBadge\x12?\n\nprime_info\x18\x0e \x01(\x0b\x32+.GenTeamWhisper.Nested2.Nested9.NestedPrime\x1a\x1c\n\x0bNestedBadge\x12\r\n\x05value\x18\x01 \x01(\x05\x1aH\n\x0bNestedPrime\x12\x11\n\tprime_uid\x18\x01 \x01(\x05\x12\x13\n\x0bprime_level\x18\x02 \x01(\x05\x12\x11\n\tprime_hex\x18\x03 \x01(\t\x1a\x33\n\x08Nested13\x12\x10\n\x08url_type\x18\x02 \x01(\x05\x12\x15\n\rcurl_platform\x18\x03 \x01(\x05\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR_TEAM_MSG, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR_TEAM_MSG, 'Team_msg_pb2', globals())
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR_TEAM_MSG._loaded_options = None
    globals()['_GENTEAMWHISPER']._serialized_start = 19
    globals()['_GENTEAMWHISPER']._serialized_end = 807
    globals()['_GENTEAMWHISPER_NESTED2']._serialized_start = 91
    globals()['_GENTEAMWHISPER_NESTED2']._serialized_end = 807
    globals()['_GENTEAMWHISPER_NESTED2_NESTED14']._serialized_start = 371
    globals()['_GENTEAMWHISPER_NESTED2_NESTED14']._serialized_end = 381
    globals()['_GENTEAMWHISPER_NESTED2_NESTED9']._serialized_start = 384
    globals()['_GENTEAMWHISPER_NESTED2_NESTED9']._serialized_end = 754
    globals()['_GENTEAMWHISPER_NESTED2_NESTED9_NESTEDBADGE']._serialized_start = 652
    globals()['_GENTEAMWHISPER_NESTED2_NESTED9_NESTEDBADGE']._serialized_end = 680
    globals()['_GENTEAMWHISPER_NESTED2_NESTED9_NESTEDPRIME']._serialized_start = 682
    globals()['_GENTEAMWHISPER_NESTED2_NESTED9_NESTEDPRIME']._serialized_end = 754
    globals()['_GENTEAMWHISPER_NESTED2_NESTED13']._serialized_start = 756
    globals()['_GENTEAMWHISPER_NESTED2_NESTED13']._serialized_end = 807

# @@protoc_insertion_point(module_scope)