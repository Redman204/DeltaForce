# ------------------------------------------------------  # noqa: D100
# 🐍 Standard Python Libraries (Included by Default) 🐍
# ------------------------------------------------------
import os
import sys
import ast
import json
import time
import enum
import signal
import shutil
import logging
import hashlib
import textwrap
import tempfile
import winsound
import threading
import subprocess
import webbrowser
from pathlib import Path
from operator import attrgetter
from collections.abc import Callable
from types import FrameType, TracebackType
from typing import Literal, NamedTuple, ClassVar, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

# --------------------------------------------
# 📦 External/Third-party Python Libraries 📦
# --------------------------------------------
import psutil
import colorama
import requests
import qdarkstyle
import geoip2.errors
import geoip2.database
from prettytable import PrettyTable, TableStyle
from colorama import Fore
from rich.text import Text
from rich.console import Console
from rich.traceback import Traceback
from packaging.version import Version
# pylint: disable=no-name-in-module
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QAbstractTableModel, QItemSelectionModel, QItemSelection, QPoint, QModelIndex, QPropertyAnimation, QEasingCurve, QTimer, QObject, QEvent
from PyQt6.QtWidgets import QApplication, QTableView, QVBoxLayout, QWidget, QSizePolicy, QLabel, QFrame, QHeaderView, QMenu, QInputDialog, QMainWindow, QMessageBox, QDialog, QPushButton, QSpacerItem, QHBoxLayout, QToolTip
from PyQt6.QtGui import QBrush, QColor, QFont, QCloseEvent, QKeyEvent, QClipboard, QMouseEvent, QAction, QPixmap, QIcon, QHoverEvent
# pylint: enable=no-name-in-module

# -----------------------------------------------------
# 📚 Local Python Libraries (Included with Project) 📚
# -----------------------------------------------------
from modules.constants.standalone import TITLE, GITHUB_RELEASES_URL, NETWORK_ADAPTER_DISABLED, TSHARK_RECOMMENDED_FULL_VERSION, TSHARK_RECOMMENDED_VERSION_NUMBER
from modules.constants.standard import SETTINGS_PATH
from modules.constants.local import PYPROJECT_DATA, VERSION, BIN_PATH, SETUP_PATH
from modules.constants.external import LOCAL_TZ
from modules.utils import is_pyinstaller_compiled, clear_screen, set_window_title, pluralize, validate_file, remove_duplicates_from_list
from modules.msgbox import MsgBox
from modules.networking.oui_lookup import MacLookup
from modules.networking.unsafe_https import s
from modules.networking.utils import is_valid_non_special_ipv4, is_ipv4_address, is_mac_address, format_mac_address
from modules.capture.tshark_capture import PacketCapture, Packet, TSharkCrashExceptionError
from modules.capture.utils.tshark_validator import TSharkNotFoundError, TSharkVersionNotFoundError, InvalidTSharkVersionError, validate_tshark_path
from modules.capture.utils.npcap_checker import is_npcap_installed
from modules.capture.interface_selection import InterfaceSelectionData, show_interface_selection_dialog
from modules.launcher.package_checker import check_packages_version, get_dependencies_from_pyproject, get_dependencies_from_requirements
from modules.guis.utils import get_screen_size

if sys.version_info < (3, 12):
    print("\nTo use this script, your Python version must be 3.12 or higher.")
    input("\nPress {ANY KEY} to exit...")
    sys.exit(0)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M",
    handlers=[
        logging.FileHandler("error.log"),
    ],
)
logging.captureWarnings(capture=True)
logger = logging.getLogger(__name__)


class ExceptionInfo(NamedTuple):
    exc_type: type[BaseException]
    exc_value: BaseException
    exc_traceback: TracebackType | None


def terminate_script(
    terminate_method: Literal["EXIT", "SIGINT", "THREAD_RAISED"],
    msgbox_crash_text: str | None = None,
    stdout_crash_text: str | None = None,
    exception_info: ExceptionInfo | None = None,
    *,
    terminate_gracefully: bool = True,
    force_terminate_errorlevel: int | Literal[False] | None = False,
):
    from modules.utils import terminate_process_tree

    def should_terminate_gracefully():
        if terminate_gracefully is False:
            return False

        for thread_name in ("capture_core__thread", "rendering_core__thread", "hostname_core__thread", "iplookup_core__thread", "pinger_core__thread"):
            if thread_name in globals():
                thread = globals()[thread_name]
                if isinstance(thread, threading.Thread) and thread.is_alive():
                    return False

        # TODO(BUZZARDGTA): Gracefully exit the script even when the `cature` module is running.
        return not ("capture" in globals() and capture is not None and isinstance(capture, PacketCapture))

    ScriptControl.set_crashed(None if stdout_crash_text is None else f"\n\n{stdout_crash_text}\n")

    if exception_info:
        logger.error("Uncaught exception", exc_info=(exception_info.exc_type, exception_info.exc_value, exception_info.exc_traceback))

        console = Console()

        traceback_message = Traceback.from_exception(exception_info.exc_type, exception_info.exc_value, exception_info.exc_traceback)
        console.print(traceback_message)

        error_message = Text.from_markup(
            (
                "\n\n\nAn unexpected (uncaught) error occurred. [bold]Please kindly report it to:[/bold]\n"
                "[link=https://github.com/BUZZARDGTA/Session-Sniffer/issues]"
                "https://github.com/BUZZARDGTA/Session-Sniffer/issues[/link].\n\n"
                "DEBUG:\n"
                f"VERSION={globals().get('VERSION', 'Unknown Version')}"  # Define a default value for VERSION if it's not defined
            ),
            style="white",
        )
        console.print(error_message)

    if stdout_crash_text is not None:
        print(ScriptControl.get_message())

    if msgbox_crash_text is not None:
        msgbox_title = TITLE
        msgbox_message = msgbox_crash_text
        msgbox_style = MsgBox.Style.MB_OK | MsgBox.Style.MB_ICONERROR | MsgBox.Style.MB_SYSTEMMODAL

        MsgBox.show(msgbox_title, msgbox_message, msgbox_style)
        time.sleep(1)

    # If the termination method is "EXIT", do not sleep unless crash messages are present
    need_sleep = True
    if terminate_method == "EXIT" and msgbox_crash_text is None and stdout_crash_text is None:
        need_sleep = False
    if need_sleep:
        time.sleep(3)

    if should_terminate_gracefully():
        if force_terminate_errorlevel is False:
            errorlevel = 1 if terminate_method == "THREAD_RAISED" else 0
        else:
            errorlevel = force_terminate_errorlevel
        sys.exit(errorlevel)

    terminate_process_tree()


def handle_exception(exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None):
    """Handle exceptions for the main script (not threads)."""
    if issubclass(exc_type, KeyboardInterrupt):
        return

    exception_info = ExceptionInfo(exc_type, exc_value, exc_traceback)
    terminate_script("EXIT", "An unexpected (uncaught) error occurred.\n\nPlease kindly report it to:\nhttps://github.com/BUZZARDGTA/Session-Sniffer/issues", exception_info=exception_info)


def handle_sigint(_sig: int, _frame: FrameType | None):
    if not ScriptControl.has_crashed():
        # Block CTRL+C if script is already crashing under control
        print(f"\n{Fore.YELLOW}Ctrl+C pressed. Exiting script ...{Fore.RESET}")
        terminate_script("SIGINT")


sys.excepthook = handle_exception
signal.signal(signal.SIGINT, handle_sigint)


class PacketCaptureOverflowError(Exception):
    pass


class ScriptControl:
    _lock = threading.Lock()
    _crashed = False
    _message = None

    @classmethod
    def set_crashed(cls, message: str | None = None):
        with cls._lock:
            cls._crashed = True
            cls._message = message

    @classmethod
    def reset_crashed(cls):
        with cls._lock:
            cls._crashed = False
            cls._message = None

    @classmethod
    def has_crashed(cls):
        with cls._lock:
            return cls._crashed

    @classmethod
    def get_message(cls):
        with cls._lock:
            return cls._message


class ThreadsExceptionHandler:
    """Handle exceptions raised within threads and provide additional functionality for managing thread execution.

    This class is designed to overcome the limitation where threads run independently from the main process, which continues execution without waiting for thread completion.

    Attributes:
        raising_function (str): The name of the function where the exception was raised.
        raising_exc_type (type): The type of the exception raised.
        raising_exc_value (Exception): The value of the exception raised.
        raising_exc_traceback (TracebackType): The traceback information for the raised exception.
    """
    raising_function = None
    raising_exc_type = None
    raising_exc_value = None
    raising_exc_traceback = None

    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, exc_traceback: TracebackType | None):
        """Exit method called upon exiting the 'with' block.

        Args:
            exc_type: The type of the exception raised.
            exc_value: The value of the exception raised.
            exc_traceback: The traceback information of the exception raised.

        Returns:
            bool: True to suppress the exception from propagating further.
        """
        if exc_type:
            ThreadsExceptionHandler.raising_exc_type = exc_type
            ThreadsExceptionHandler.raising_exc_value = exc_value
            ThreadsExceptionHandler.raising_exc_traceback = exc_traceback

            tb = exc_traceback
            while tb.tb_next:
                tb = tb.tb_next
            # Set the failed function name
            ThreadsExceptionHandler.raising_function = tb.tb_frame.f_code.co_name

            exception_info = ExceptionInfo(exc_type, exc_value, exc_traceback)
            terminate_script("THREAD_RAISED", "An unexpected (uncaught) error occurred.\n\nPlease kindly report it to:\nhttps://github.com/BUZZARDGTA/Session-Sniffer/issues", exception_info=exception_info)

            return True  # Prevent exceptions from propagating
        return False


@dataclass
class DefaultSettings:
    """Class containing default setting values."""
    CAPTURE_NETWORK_INTERFACE_CONNECTION_PROMPT = True
    CAPTURE_INTERFACE_NAME: str | None = None
    CAPTURE_IP_ADDRESS: str | None = None
    CAPTURE_MAC_ADDRESS: str | None = None
    CAPTURE_ARP = True
    CAPTURE_BLOCK_THIRD_PARTY_SERVERS = True
    CAPTURE_PROGRAM_PRESET: str | None = None
    CAPTURE_VPN_MODE = False
    CAPTURE_OVERFLOW_TIMER = 3.0
    CAPTURE_PREPEND_CUSTOM_CAPTURE_FILTER: str | None = None
    CAPTURE_PREPEND_CUSTOM_DISPLAY_FILTER: str | None = None
    GUI_SESSIONS_LOGGING = True
    GUI_RESET_PORTS_ON_REJOINS = True
    GUI_FIELDS_TO_HIDE = ["PPM", "Avg PPM", "Intermediate Ports", "First Port", "Continent", "R. Code", "City", "District", "ZIP Code", "Lat", "Lon", "Time Zone", "Offset", "Currency", "Organization", "ISP", "AS", "ASN"]  # TODO(BUZZARDGTA): Add type hint `list[str]`
    GUI_DATE_FIELDS_SHOW_DATE = False
    GUI_DATE_FIELDS_SHOW_TIME = False
    GUI_DATE_FIELDS_SHOW_ELAPSED = True
    GUI_FIELD_SHOW_COUNTRY_CODE = True
    GUI_FIELD_SHOW_CONTINENT_CODE = True
    GUI_FIELD_CONNECTED_PLAYERS_SORTED_BY = "Last Rejoin"
    GUI_FIELD_DISCONNECTED_PLAYERS_SORTED_BY = "Last Seen"
    GUI_DISCONNECTED_PLAYERS_TIMER = 10.0
    DISCORD_PRESENCE = True
    SHOW_DISCORD_POPUP = True
    UPDATER_CHANNEL = "Stable"


class Settings(DefaultSettings):
    gui_fields_mapping = {
        "Usernames": "userip.usernames",
        "First Seen": "datetime.first_seen",
        "Last Rejoin": "datetime.last_rejoin",
        "Last Seen": "datetime.last_seen",
        "Rejoins": "rejoins",
        "T. Packets": "total_packets",
        "Packets": "packets",
        "PPS": "pps.rate",
        # "Avg PPS": "pps.get_average()",
        "PPM": "ppm.rate",
        # "Avg PPM": "ppm.get_average()",
        "IP Address": "ip",
        "Hostname": "hostname",
        "Last Port": "ports.last",
        "Intermediate Ports": "ports.intermediate",
        "First Port": "ports.first",
        "Continent": "iplookup.ipapi.continent",
        "Country": "iplookup.geolite2.country",
        "Region": "iplookup.ipapi.region",
        "R. Code": "iplookup.ipapi.region_code",
        "City": "iplookup.geolite2.city",
        "District": "iplookup.ipapi.district",
        "ZIP Code": "iplookup.ipapi.zip_code",
        "Lat": "iplookup.ipapi.lat",
        "Lon": "iplookup.ipapi.lon",
        "Time Zone": "iplookup.ipapi.time_zone",
        "Offset": "iplookup.ipapi.offset",
        "Currency": "iplookup.ipapi.currency",
        "Organization": "iplookup.ipapi.org",
        "ISP": "iplookup.ipapi.isp",
        "ASN / ISP": "iplookup.geolite2.asn",
        "AS": "iplookup.ipapi.asn",
        "ASN": "iplookup.ipapi.as_name",
        "Mobile": "iplookup.ipapi.mobile",
        "VPN": "iplookup.ipapi.proxy",
        "Hosting": "iplookup.ipapi.hosting",
        "Pinging": "ping.is_pinging",
    }
    gui_forced_fields           = ["Usernames", "First Seen", "Last Rejoin", "Last Seen", "Rejoins", "T. Packets", "Packets", "IP Address"]
    gui_hideable_fields         = ["PPS", "Avg PPS", "PPM", "Avg PPM", "Hostname", "Last Port", "Intermediate Ports", "First Port", "Continent", "Country", "Region", "R. Code", "City", "District", "ZIP Code", "Lat", "Lon", "Time Zone", "Offset", "Currency", "Organization", "ISP", "ASN / ISP", "AS", "ASN", "Mobile", "VPN", "Hosting", "Pinging"]
    gui_all_connected_fields    = ["Usernames", "First Seen", "Last Rejoin",              "Rejoins", "T. Packets", "Packets", "PPS", "Avg PPS", "PPM", "Avg PPM", "IP Address", "Hostname", "Last Port", "Intermediate Ports", "First Port", "Continent", "Country", "Region", "R. Code", "City", "District", "ZIP Code", "Lat", "Lon", "Time Zone", "Offset", "Currency", "Organization", "ISP", "ASN / ISP", "AS", "ASN", "Mobile", "VPN", "Hosting", "Pinging"]
    gui_all_disconnected_fields = ["Usernames", "First Seen", "Last Rejoin", "Last Seen", "Rejoins", "T. Packets", "Packets",                                     "IP Address", "Hostname", "Last Port", "Intermediate Ports", "First Port", "Continent", "Country", "Region", "R. Code", "City", "District", "ZIP Code", "Lat", "Lon", "Time Zone", "Offset", "Currency", "Organization", "ISP", "ASN / ISP", "AS", "ASN", "Mobile", "VPN", "Hosting", "Pinging"]

    @classmethod
    def iterate_over_settings(cls):
        _allowed_settings_types = (type(None), Path, bool, list, str, float, int)

        for attr_name, attr_value in vars(DefaultSettings).items():
            if (
                callable(attr_value)
                or attr_name.startswith("_")
                or attr_name in {"gui_fields_mapping", "gui_forced_fields", "gui_hideable_fields", "gui_all_connected_fields", "gui_all_disconnected_fields"}
                or not attr_name.isupper()
                or not isinstance(attr_value, _allowed_settings_types)
            ):
                continue

            # Get the value from Settings if it exists, otherwise from DefaultSettings
            current_value = getattr(cls, attr_name, attr_value)
            yield attr_name, current_value

    @classmethod
    def get_settings_length(cls):
        return sum(1 for _ in cls.iterate_over_settings())

    @classmethod
    def has_setting(cls, setting_name: str):
        return hasattr(cls, setting_name)

    @staticmethod
    def reconstruct_settings():
        print('\nCorrect reconstruction of "Settings.ini" ...')
        text = textwrap.dedent(f"""
            ;;-----------------------------------------------------------------------------
            ;; {TITLE} Configuration Settings
            ;;-----------------------------------------------------------------------------
            ;; Lines starting with \";\" or \"#\" symbols are commented lines.
            ;;
            ;; For detailed explanations of each setting, please refer to the following documentation:
            ;; https://github.com/BUZZARDGTA/Session-Sniffer/?tab=readme-ov-file#editing-settings
            ;;-----------------------------------------------------------------------------
        """.removeprefix("\n"))
        for setting_name, setting_value in Settings.iterate_over_settings():
            text += f"{setting_name}={setting_value}\n"
        SETTINGS_PATH.write_text(text, encoding="utf-8")

    @staticmethod
    def parse_settings_ini_file(ini_path: Path):
        from modules.constants.standard import RE_SETTINGS_INI_PARSER_PATTERN

        def process_ini_line_output(line: str):
            return line.rstrip("\n")

        validate_file(ini_path)

        ini_data = ini_path.read_text("utf-8")

        need_rewrite_ini = False
        ini_database: dict[str, str] = {}

        for line in map(process_ini_line_output, ini_data.splitlines(keepends=False)):
            corrected_line = line.strip()
            if corrected_line != line:
                need_rewrite_ini = True

            match = RE_SETTINGS_INI_PARSER_PATTERN.search(corrected_line)
            if not match:
                continue

            setting_name = match.group("key")
            if not isinstance(setting_name, str):
                raise TypeError(f'Expected "str" object, got "{type(setting_name).__name__}"')
            setting_value = match.group("value")
            if not isinstance(setting_value, str):
                raise TypeError(f'Expected "str" object, got "{type(setting_value).__name__}"')

            corrected_setting_name = setting_name.strip()
            if corrected_setting_name == "":
                continue

            if corrected_setting_name != setting_name:
                need_rewrite_ini = True

            corrected_setting_value = setting_value.strip()
            if corrected_setting_value == "":
                continue

            if corrected_setting_value != setting_value:
                need_rewrite_ini = True

            if corrected_setting_name in ini_database:
                need_rewrite_ini = True  # Settings file needs to be rewritten as it contains duplicate settings
                continue

            ini_database[corrected_setting_name] = corrected_setting_value

        return ini_database, need_rewrite_ini

    @staticmethod
    def load_from_settings_file(settings_path: Path):
        from modules.networking.utils import is_mac_address
        from modules.utils import InvalidBooleanValueError, InvalidNoneTypeValueError, NoMatchFoundError, custom_str_to_bool, custom_str_to_nonetype, check_case_insensitive_and_exact_match

        matched_settings_count = 0

        try:
            settings, need_rewrite_settings = Settings.parse_settings_ini_file(settings_path)
        except FileNotFoundError:
            need_rewrite_settings = True
        else:
            for setting_name, setting_value in settings.items():
                if not Settings.has_setting(setting_name):
                    need_rewrite_settings = True
                    continue

                matched_settings_count += 1
                need_rewrite_current_setting = False

                if setting_name == "CAPTURE_NETWORK_INTERFACE_CONNECTION_PROMPT":
                    try:
                        Settings.CAPTURE_NETWORK_INTERFACE_CONNECTION_PROMPT, need_rewrite_current_setting = custom_str_to_bool(setting_value)
                    except InvalidBooleanValueError:
                        need_rewrite_settings = True
                elif setting_name == "CAPTURE_INTERFACE_NAME":
                    try:
                        Settings.CAPTURE_INTERFACE_NAME, need_rewrite_current_setting = custom_str_to_nonetype(setting_value)
                    except InvalidNoneTypeValueError:
                        Settings.CAPTURE_INTERFACE_NAME = setting_value
                elif setting_name == "CAPTURE_IP_ADDRESS":
                    try:
                        Settings.CAPTURE_IP_ADDRESS, need_rewrite_current_setting = custom_str_to_nonetype(setting_value)
                    except InvalidNoneTypeValueError:
                        if is_ipv4_address(setting_value):
                            Settings.CAPTURE_IP_ADDRESS = setting_value
                        else:
                            need_rewrite_settings = True
                elif setting_name == "CAPTURE_MAC_ADDRESS":
                    try:
                        Settings.CAPTURE_MAC_ADDRESS, need_rewrite_current_setting = custom_str_to_nonetype(setting_value)
                    except InvalidNoneTypeValueError:
                        formatted_mac_address = format_mac_address(setting_value)
                        if is_mac_address(formatted_mac_address):
                            if formatted_mac_address != setting_value:
                                need_rewrite_settings = True
                            Settings.CAPTURE_MAC_ADDRESS = formatted_mac_address
                        else:
                            need_rewrite_settings = True
                elif setting_name == "CAPTURE_ARP":
                    try:
                        Settings.CAPTURE_ARP, need_rewrite_current_setting = custom_str_to_bool(setting_value)
                    except InvalidBooleanValueError:
                        need_rewrite_settings = True
                elif setting_name == "CAPTURE_BLOCK_THIRD_PARTY_SERVERS":
                    try:
                        Settings.CAPTURE_BLOCK_THIRD_PARTY_SERVERS, need_rewrite_current_setting = custom_str_to_bool(setting_value)
                    except InvalidBooleanValueError:
                        need_rewrite_settings = True
                elif setting_name == "CAPTURE_PROGRAM_PRESET":
                    try:
                        Settings.CAPTURE_PROGRAM_PRESET, need_rewrite_current_setting = custom_str_to_nonetype(setting_value)
                    except InvalidNoneTypeValueError:
                        try:
                            case_sensitive_match, normalized_match = check_case_insensitive_and_exact_match(setting_value, ["GTA5", "Minecraft"])
                            Settings.CAPTURE_PROGRAM_PRESET = normalized_match
                            if not case_sensitive_match:
                                need_rewrite_current_setting = True
                        except NoMatchFoundError:
                            need_rewrite_settings = True
                elif setting_name == "CAPTURE_VPN_MODE":
                    try:
                        Settings.CAPTURE_VPN_MODE, need_rewrite_current_setting = custom_str_to_bool(setting_value)
                    except InvalidBooleanValueError:
                        need_rewrite_settings = True
                elif setting_name == "CAPTURE_OVERFLOW_TIMER":
                    try:
                        CAPTURE_OVERFLOW_TIMER = float(setting_value)
                    except (ValueError, TypeError):
                        need_rewrite_settings = True
                    else:
                        if CAPTURE_OVERFLOW_TIMER >= 1:
                            Settings.CAPTURE_OVERFLOW_TIMER = CAPTURE_OVERFLOW_TIMER
                        else:
                            need_rewrite_settings = True
                elif setting_name == "CAPTURE_PREPEND_CUSTOM_CAPTURE_FILTER":
                    try:
                        Settings.CAPTURE_PREPEND_CUSTOM_CAPTURE_FILTER, need_rewrite_current_setting = custom_str_to_nonetype(setting_value)
                    except InvalidNoneTypeValueError:
                        updated_setting_value = setting_value.strip().strip("\"'")

                        # Continuously remove outer parentheses until none remain
                        while updated_setting_value.startswith("(") and updated_setting_value.endswith(")"):
                            updated_setting_value = updated_setting_value[1:-1]

                        if setting_value != updated_setting_value:
                            need_rewrite_settings = True

                        Settings.CAPTURE_PREPEND_CUSTOM_CAPTURE_FILTER = updated_setting_value
                elif setting_name == "CAPTURE_PREPEND_CUSTOM_DISPLAY_FILTER":
                    try:
                        Settings.CAPTURE_PREPEND_CUSTOM_DISPLAY_FILTER, need_rewrite_current_setting = custom_str_to_nonetype(setting_value)
                    except InvalidNoneTypeValueError:
                        updated_setting_value = setting_value.strip().strip("\"'")

                        # Continuously remove outer parentheses until none remain
                        while updated_setting_value.startswith("(") and updated_setting_value.endswith(")"):
                            updated_setting_value = updated_setting_value[1:-1]

                        if setting_value != updated_setting_value:
                            need_rewrite_settings = True

                        Settings.CAPTURE_PREPEND_CUSTOM_DISPLAY_FILTER = updated_setting_value
                elif setting_name == "GUI_SESSIONS_LOGGING":
                    try:
                        Settings.GUI_SESSIONS_LOGGING, need_rewrite_current_setting = custom_str_to_bool(setting_value)
                    except InvalidBooleanValueError:
                        need_rewrite_settings = True
                elif setting_name == "GUI_RESET_PORTS_ON_REJOINS":
                    try:
                        Settings.GUI_RESET_PORTS_ON_REJOINS, need_rewrite_current_setting = custom_str_to_bool(setting_value)
                    except InvalidBooleanValueError:
                        need_rewrite_settings = True
                elif setting_name == "GUI_FIELDS_TO_HIDE":
                    try:
                        gui_fields_to_hide: list[str] = ast.literal_eval(setting_value)
                    except (ValueError, SyntaxError):
                        need_rewrite_settings = True
                    else:
                        if isinstance(gui_fields_to_hide, list) and all(isinstance(item, str) for item in gui_fields_to_hide):
                            filtered_gui_fields_to_hide: list[str] = []

                            for value in gui_fields_to_hide:
                                try:
                                    case_sensitive_match, normalized_match = check_case_insensitive_and_exact_match(value, Settings.gui_hideable_fields)
                                    filtered_gui_fields_to_hide.append(normalized_match)
                                    if not case_sensitive_match:
                                        need_rewrite_current_setting = True
                                except NoMatchFoundError:
                                    need_rewrite_settings = True

                            Settings.GUI_FIELDS_TO_HIDE = filtered_gui_fields_to_hide
                        else:
                            need_rewrite_settings = True
                elif setting_name == "GUI_DATE_FIELDS_SHOW_DATE":
                    try:
                        Settings.GUI_DATE_FIELDS_SHOW_DATE, need_rewrite_current_setting = custom_str_to_bool(setting_value)
                    except InvalidBooleanValueError:
                        need_rewrite_settings = True
                elif setting_name == "GUI_DATE_FIELDS_SHOW_TIME":
                    try:
                        Settings.GUI_DATE_FIELDS_SHOW_TIME, need_rewrite_current_setting = custom_str_to_bool(setting_value)
                    except InvalidBooleanValueError:
                        need_rewrite_settings = True
                elif setting_name == "GUI_DATE_FIELDS_SHOW_ELAPSED":
                    try:
                        Settings.GUI_DATE_FIELDS_SHOW_ELAPSED, need_rewrite_current_setting = custom_str_to_bool(setting_value)
                    except InvalidBooleanValueError:
                        need_rewrite_settings = True
                elif setting_name == "GUI_FIELD_SHOW_CONTINENT_CODE":
                    try:
                        Settings.GUI_FIELD_SHOW_CONTINENT_CODE, need_rewrite_current_setting = custom_str_to_bool(setting_value)
                    except InvalidBooleanValueError:
                        need_rewrite_settings = True
                elif setting_name == "GUI_FIELD_SHOW_COUNTRY_CODE":
                    try:
                        Settings.GUI_FIELD_SHOW_COUNTRY_CODE, need_rewrite_current_setting = custom_str_to_bool(setting_value)
                    except InvalidBooleanValueError:
                        need_rewrite_settings = True
                elif setting_name == "GUI_FIELD_CONNECTED_PLAYERS_SORTED_BY":
                    try:
                        case_sensitive_match, normalized_match = check_case_insensitive_and_exact_match(setting_value, Settings.gui_all_connected_fields)
                        Settings.GUI_FIELD_CONNECTED_PLAYERS_SORTED_BY = normalized_match
                        if not case_sensitive_match:
                            need_rewrite_current_setting = True
                    except NoMatchFoundError:
                        need_rewrite_settings = True
                elif setting_name == "GUI_FIELD_DISCONNECTED_PLAYERS_SORTED_BY":
                    try:
                        case_sensitive_match, normalized_match = check_case_insensitive_and_exact_match(setting_value, Settings.gui_all_disconnected_fields)
                        Settings.GUI_FIELD_DISCONNECTED_PLAYERS_SORTED_BY = normalized_match
                        if not case_sensitive_match:
                            need_rewrite_current_setting = True
                    except NoMatchFoundError:
                        need_rewrite_settings = True
                elif setting_name == "GUI_DISCONNECTED_PLAYERS_TIMER":
                    try:
                        player_disconnected_timer = float(setting_value)
                    except (ValueError, TypeError):
                        need_rewrite_settings = True
                    else:
                        if player_disconnected_timer >= 3.0:  # noqa: PLR2004
                            Settings.GUI_DISCONNECTED_PLAYERS_TIMER = player_disconnected_timer
                        else:
                            need_rewrite_settings = True
                elif setting_name == "DISCORD_PRESENCE":
                    try:
                        Settings.DISCORD_PRESENCE, need_rewrite_current_setting = custom_str_to_bool(setting_value)
                    except InvalidBooleanValueError:
                        need_rewrite_settings = True
                elif setting_name == "SHOW_DISCORD_POPUP":
                    try:
                        Settings.SHOW_DISCORD_POPUP, need_rewrite_current_setting = custom_str_to_bool(setting_value)
                    except InvalidBooleanValueError:
                        need_rewrite_settings = True
                elif setting_name == "UPDATER_CHANNEL":
                    try:
                        Settings.UPDATER_CHANNEL, need_rewrite_current_setting = custom_str_to_nonetype(setting_value)
                    except InvalidNoneTypeValueError:
                        try:
                            case_sensitive_match, normalized_match = check_case_insensitive_and_exact_match(setting_value, ["Stable", "RC"])
                            Settings.UPDATER_CHANNEL = normalized_match
                            if not case_sensitive_match:
                                need_rewrite_current_setting = True
                        except NoMatchFoundError:
                            need_rewrite_settings = True

                if need_rewrite_current_setting:
                    need_rewrite_settings = True

            if matched_settings_count != Settings.get_settings_length():
                need_rewrite_settings = True

        if need_rewrite_settings:
            Settings.reconstruct_settings()

        for field_name in Settings.GUI_FIELDS_TO_HIDE:
            for sort_field_name, sort_field_value, default_sort_value in (
                ("GUI_FIELD_CONNECTED_PLAYERS_SORTED_BY", Settings.GUI_FIELD_CONNECTED_PLAYERS_SORTED_BY, DefaultSettings.GUI_FIELD_CONNECTED_PLAYERS_SORTED_BY),
                ("GUI_FIELD_DISCONNECTED_PLAYERS_SORTED_BY", Settings.GUI_FIELD_DISCONNECTED_PLAYERS_SORTED_BY, DefaultSettings.GUI_FIELD_DISCONNECTED_PLAYERS_SORTED_BY),
            ):
                if field_name in sort_field_value:
                    need_rewrite_settings = True

                    msgbox_title = TITLE
                    msgbox_message = textwrap.dedent(f"""
                        ERROR in your custom \"Settings.ini\" file:

                        You cannot sort players in the output from a hidden gui field (<GUI_FIELDS_TO_HIDE>).

                        Would you like to replace:
                        {sort_field_name}={sort_field_value}
                        with its default value:
                        {sort_field_name}={default_sort_value}
                    """.removeprefix("\n").removesuffix("\n"))
                    msgbox_style = MsgBox.Style.MB_YESNO | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SETFOREGROUND
                    errorlevel = MsgBox.show(msgbox_title, msgbox_message, msgbox_style)

                    if errorlevel != MsgBox.ReturnValues.IDYES:
                        terminate_script("EXIT")

                    setattr(Settings, sort_field_name, getattr(DefaultSettings, sort_field_name))  # Replace the incorrect field with its default value
                    Settings.reconstruct_settings()

        if Settings.GUI_DATE_FIELDS_SHOW_DATE is False and Settings.GUI_DATE_FIELDS_SHOW_TIME is False and Settings.GUI_DATE_FIELDS_SHOW_ELAPSED is False:
            msgbox_title = TITLE
            msgbox_message = textwrap.dedent("""
                ERROR in your custom \"Settings.ini\" file:

                At least one of these settings must be set to \"True\" value:
                <GUI_DATE_FIELDS_SHOW_DATE>
                <GUI_DATE_FIELDS_SHOW_TIME>
                <GUI_DATE_FIELDS_SHOW_ELAPSED>

                Would you like to apply their default values and continue?
            """.removeprefix("\n").removesuffix("\n"))
            msgbox_style = MsgBox.Style.MB_YESNO | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SETFOREGROUND
            errorlevel = MsgBox.show(msgbox_title, msgbox_message, msgbox_style)

            if errorlevel != MsgBox.ReturnValues.IDYES:
                terminate_script("EXIT")

            for setting_name in ("GUI_DATE_FIELDS_SHOW_DATE", "GUI_DATE_FIELDS_SHOW_TIME", "GUI_DATE_FIELDS_SHOW_ELAPSED"):
                setattr(Settings, setting_name, getattr(DefaultSettings, setting_name))

            Settings.reconstruct_settings()


@dataclass(slots=True, kw_only=True, eq=True)
class ARPEntry:
    ip_address: str
    mac_address: str
    manufacturer: str | None = None


@dataclass(slots=True, kw_only=True)
class Interface:
    index:        int
    ip_enabled:   bool | None    = None
    state:        int  | None    = None
    name:         str  | None    = None
    mac_address:  str  | None    = None
    manufacturer: str  | None    = None
    packets_sent: int  | None    = None
    packets_recv: int  | None    = None
    descriptions: list[str]      = field(default_factory=list)
    ip_addresses: list[str]      = field(default_factory=list)
    arp_entries:  list[ARPEntry] = field(default_factory=list)

    def add_arp_entry(self, arp_entry: ARPEntry):
        """Add an ARP entry for the given interface."""
        if arp_entry in self.arp_entries:
            return False

        self.arp_entries.append(arp_entry)
        return True

    def get_arp_entries(self):
        """Get ARP entries for the given interface."""
        return self.arp_entries

    def is_interface_inactive(self):
        """Determine if an interface is inactive based on lack of traffic, IP addresses, and identifying details."""
        # Check if interface is disabled
        if self.ip_enabled is False or self.state == NETWORK_ADAPTER_DISABLED:
            return True

        # Check if all identifying details and traffic data are missing
        return (
            self.mac_address is None
            and self.packets_sent in {None, 0}
            and self.packets_recv in {None, 0}
            and not self.descriptions
            and not self.ip_addresses
            and not self.arp_entries
        )

    # ─────────────────────────────────────────────────────────────
    # Update/Add Methods
    # ─────────────────────────────────────────────────────────────

    def update_ip_enabled(self, new_value: bool | None):
        if new_value is None:
            return False

        if self.ip_enabled is not None and self.ip_enabled != new_value:
            raise ValueError(f"ip_enabled mismatch: existing={self.ip_enabled}, new={new_value}")
        self.ip_enabled = new_value
        return True

    def update_state(self, new_value: int | None):
        if new_value is None:
            return False

        if self.state is not None and self.state != new_value:
            raise ValueError(f"state mismatch: existing={self.state}, new={new_value}")
        self.state = new_value
        return True

    def update_name(self, new_value: str | None):
        if new_value is None:
            return False

        if self.name is not None and self.name != new_value:
            raise ValueError(f"name mismatch: existing={self.name}, new={new_value}")
        self.name = new_value
        return True

    def update_mac_address(self, new_value: str | None):
        if new_value is None:
            return False

        if self.mac_address is not None and self.mac_address != new_value:
            raise ValueError(f"mac_address mismatch: existing={self.mac_address}, new={new_value}")
        self.mac_address = new_value
        return True

    def update_manufacturer(self, new_value: str | None):
        if new_value is None:
            return False

        if self.manufacturer is not None and self.manufacturer != new_value:
            raise ValueError(f"manufacturer mismatch: existing={self.manufacturer}, new={new_value}")
        self.manufacturer = new_value
        return True

    def update_packets_sent(self, new_value: int | None):
        if new_value is None:
            return False

        if self.packets_sent is not None and self.packets_sent != new_value:
            raise ValueError(f"packets_sent mismatch: existing={self.packets_sent}, new={new_value}")
        self.packets_sent = new_value
        return True

    def update_packets_recv(self, new_value: int | None):
        if new_value is None:
            return False

        if self.packets_recv is not None and self.packets_recv != new_value:
            raise ValueError(f"packets_recv mismatch: existing={self.packets_recv}, new={new_value}")
        self.packets_recv = new_value
        return True

    def add_description(self, new_value: str | None):
        if new_value is None:
            return False

        normalized_new = new_value.casefold()
        if normalized_new not in {desc.casefold() for desc in self.descriptions}:
            self.descriptions.append(new_value)
            return True

        return False

    def add_ip_address(self, new_value: str | None):
        if new_value is None:
            return False

        if new_value not in self.ip_addresses:
            self.ip_addresses.append(new_value)
            return True

        return False


class AllInterfaces:
    all_interfaces: ClassVar[dict[int, Interface]] = {}
    _name_map: ClassVar[dict[str, int]] = {}

    @classmethod
    def iterate(cls):
        """Yield each interface from `all_interfaces`.

        This is an iterator that will provide all interfaces stored in the dictionary.
        The iteration will be done over the dictionary values (the Interface objects).

        Yields:
            Interface: Each interface from `all_interfaces`.
        """
        yield from cls.all_interfaces.values()

    @classmethod
    def get_interface(cls, index: int):
        """Retrieve an interface by its `index`.

        Args:
            index (int): The index of the interface to retrieve.

        Returns:
            Interface | None: The interface matching the index, or None if not found.
        """
        return cls.all_interfaces.get(index)

    @classmethod
    def get_interface_by_name(cls, name: str):
        """Retrieve an interface by its `name`, case-insensitively.

        Args:
            name (str): The name of the interface to retrieve.

        Returns:
            Interface | None: The interface matching the name, or None if not found.
        """
        normalized_name = name.casefold()
        index = cls._name_map.get(normalized_name)
        if index is not None:
            return cls.get_interface(index)
        return None

    @classmethod
    def add_interface(cls, new_interface: Interface):
        """Add a new interface to the dictionary if it doesn't already exist.

        Args:
            new_interface (Interface): The interface object to add.

        Returns:
            bool: True if the interface was added, False if it already exists.
        """
        if new_interface.index not in cls.all_interfaces:
            cls.all_interfaces[new_interface.index] = new_interface
            if new_interface.name:
                cls._name_map[new_interface.name.casefold()] = new_interface.index
            return True
        return False

    @classmethod
    def delete_interface(cls, index: int):
        """Delete an interface by its `index`.

        Args:
            index (int): The index of the interface to delete.

        Returns:
            bool: True if the interface was deleted, False if no matching interface was found.
        """
        interface = cls.all_interfaces.pop(index, None)
        if interface:
            if interface.name:
                cls._name_map.pop(interface.name.casefold(), None)
            return True
        return False


class ThirdPartyServers(enum.Enum):
    PC_DISCORD = ("66.22.196.0/22", "66.22.200.0/21", "66.22.208.0/20", "66.22.224.0/20", "66.22.240.0/21", "66.22.248.0/24")
    PC_VALVE = ("103.10.124.0/23", "103.28.54.0/23", "146.66.152.0/21", "155.133.224.0/19", "162.254.192.0/21", "185.25.180.0/22", "205.196.6.0/24")  # Valve = Steam
    PC_GOOGLE = ("34.0.0.0/9", "34.128.0.0/10", "35.184.0.0/13", "35.192.0.0/11", "35.224.0.0/12", "35.240.0.0/13")
    PC_MULTICAST = ("224.0.0.0/4",)
    PC_UK_MINISTRY_OF_DEFENCE = ("25.0.0.0/8",)
    PC_SERVERS_COM = ("173.237.26.0/24",)
    PC_OTHERS = ("113.117.15.193/32",)
    PS_SONY_INTERACTIVE  = ("104.142.128.0/17",)
    PS_AMAZON = ("34.192.0.0/10", "44.192.0.0/10", "52.0.0.0/10", "52.64.0.0/12", "52.80.0.0/13", "52.88.0.0/14")
    GTAV_TAKETWO = ("104.255.104.0/22", "185.56.64.0/22", "192.81.240.0/21")
    GTAV_PC_MICROSOFT = ("52.139.128.0/18",)
    GTAV_PC_DOD_NETWORK_INFORMATION_CENTER = ("26.0.0.0/8",)
    GTAV_PC_BATTLEYE = ("51.89.97.102/32", "51.89.99.255/32")
    GTAV_XBOXONE_MICROSOFT = ("40.74.0.0/18", "52.159.128.0/17", "52.160.0.0/16")
    MINECRAFTBEDROCKEDITION_PC_PS3_MICROSOFT = ("20.202.0.0/24", "20.224.0.0/16", "168.61.142.128/25", "168.61.143.0/24", "168.61.144.0/20", "168.61.160.0/19")

    @classmethod
    def get_all_ip_ranges(cls):
        """Return a flat list of all IP ranges from the Enum."""
        return [ip_range for server in cls for ip_range in server.value]


@dataclass
class PlayerReverseDNS:
    is_initialized = False

    hostname: Literal["..."] | str = "..."


class PlayerPPS:
    def __init__(self):
        self._initialize()

    def _initialize(self):
        self.is_first_calculation = True
        self.last_pps_values: list[int] = []  # Stores last 3 PPS values
        self.last_update_time = time.monotonic()
        self.counter = 0
        self.rate = 0
        self.avg_rate = 0

    def reset(self):
        self._initialize()

    def update_average(self, player_pps_rate: int):
        """Safely updates the last PPS values list, keeping only the latest 3 values."""
        from modules.constants.standalone import MAX_PPS_VALUES

        if len(self.last_pps_values) >= MAX_PPS_VALUES:
            self.last_pps_values.pop(0)  # Keep only the last 3 values
        self.last_pps_values.append(player_pps_rate)

    def get_average(self):
        """Return the average of the last 3 PPS values (or fewer if not enough data)."""
        return round(sum(self.last_pps_values) / len(self.last_pps_values)) if self.last_pps_values else 0


class PlayerPPM:
    def __init__(self):
        self._initialize()

    def _initialize(self):
        self.is_first_calculation = True
        self.last_ppm_values: list[int] = []  # Stores last 3 PPM values
        self.last_update_time = time.monotonic()
        self.counter = 0
        self.rate = 0
        self.avg_rate = 0

    def reset(self):
        self._initialize()

    def update_average(self, player_ppm_counter: int):
        """Safely updates the last PPM values list, keeping only the latest 3 values."""
        from modules.constants.standalone import MAX_PPM_VALUES

        if len(self.last_ppm_values) >= MAX_PPM_VALUES:
            self.last_ppm_values.pop(0)  # Keep only the last 3 values
        self.last_ppm_values.append(player_ppm_counter)

    def get_average(self):
        """Return the average of the last 3 PPM values (or fewer if not enough data)."""
        return round(sum(self.last_ppm_values) / len(self.last_ppm_values)) if self.last_ppm_values else 0


class PlayerPorts:
    def __init__(self, port: int):
        self._initialize(port)

    def _initialize(self, port: int):
        self.list = [port]
        self.first = port
        self.intermediate: list[int] = []
        self.last = port

    def reset(self, port: int):
        self._initialize(port)


class PlayerDateTime:
    def __init__(self, packet_datetime: datetime):
        self._initialize(packet_datetime)

    def _initialize(self, packet_datetime: datetime):
        self.first_seen = packet_datetime
        self.last_rejoin = packet_datetime
        self.last_seen = packet_datetime
        self.left: datetime | None = None

    def reset(self, packet_datetime: datetime):
        self._initialize(packet_datetime)


@dataclass
class PlayerGeoLite2:
    is_initialized = False

    country:      Literal["..."] | str = "..."
    country_code: Literal["..."] | str = "..."
    city:         Literal["..."] | str = "..."
    asn:          Literal["..."] | str = "..."


@dataclass
class PlayerIPAPI:
    is_initialized = False

    continent:      Literal["N/A", "..."] | str         = "..."
    continent_code: Literal["N/A", "..."] | str         = "..."
    country:        Literal["N/A", "..."] | str         = "..."
    country_code:   Literal["N/A", "..."] | str         = "..."
    region:         Literal["N/A", "..."] | str         = "..."
    region_code:    Literal["N/A", "..."] | str         = "..."
    city:           Literal["N/A", "..."] | str         = "..."
    district:       Literal["N/A", "..."] | str         = "..."
    zip_code:       Literal["N/A", "..."] | str         = "..."
    lat:            Literal["N/A", "..."] | float | int = "..."
    lon:            Literal["N/A", "..."] | float | int = "..."
    time_zone:      Literal["N/A", "..."] | str         = "..."
    offset:         Literal["N/A", "..."] | int         = "..."
    currency:       Literal["N/A", "..."] | str         = "..."
    org:            Literal["N/A", "..."] | str         = "..."
    isp:            Literal["N/A", "..."] | str         = "..."
    asn:            Literal["N/A", "..."] | str         = "..."
    as_name:        Literal["N/A", "..."] | str         = "..."
    mobile:         Literal["N/A", "..."] | bool        = "..."
    proxy:          Literal["N/A", "..."] | bool        = "..."
    hosting:        Literal["N/A", "..."] | bool        = "..."


class PlayerCountryFlag:
    def __init__(self, pixmap: QPixmap, icon: QIcon):
        self.pixmap = pixmap
        self.icon = icon


class PlayerIPLookup:
    def __init__(self):
        self.country_flag: PlayerCountryFlag | None = None
        self.geolite2 = PlayerGeoLite2()
        self.ipapi = PlayerIPAPI()


@dataclass
class PlayerPing:
    is_initialized = False

    is_pinging:          Literal["..."] | bool         = "..."
    ping_times:          Literal["..."] | list[float]  = "..."
    packets_transmitted: Literal["..."] | int   | None = "..."
    packets_received:    Literal["..."] | int   | None = "..."
    packet_loss:         Literal["..."] | float | None = "..."
    packet_errors:       Literal["..."] | int   | None = "..."
    rtt_min:             Literal["..."] | float | None = "..."
    rtt_avg:             Literal["..."] | float | None = "..."
    rtt_max:             Literal["..."] | float | None = "..."
    rtt_mdev:            Literal["..."] | float | None = "..."


@dataclass
class PlayerUserIPDetection:
    time: str
    date_time: str

    as_processed_task: bool = True
    type: Literal["Static IP"] = "Static IP"


@dataclass
class PlayerModMenus:
    usernames: list[str] = field(default_factory=list)


class Player:
    def __init__(self, ip: str, port: int, packet_datetime: datetime):
        self.is_player_just_registered = True
        self._initialize(ip, port, packet_datetime)

    def _initialize(self, ip: str, port: int, packet_datetime: datetime):
        self.ip = ip
        self.rejoins = 0
        self.packets = 1
        self.total_packets = 1
        self.usernames: list[str] = []

        self.reverse_dns = PlayerReverseDNS()
        self.pps = PlayerPPS()
        self.ppm = PlayerPPM()
        self.ports = PlayerPorts(port)
        self.datetime = PlayerDateTime(packet_datetime)
        self.iplookup = PlayerIPLookup()
        self.ping = PlayerPing()
        self.userip: UserIP | None = None
        self.userip_detection: PlayerUserIPDetection | None = None
        self.mod_menus: PlayerModMenus | None = None

    def reset(self, port: int, packet_datetime: datetime):
        self.packets = 1
        self.pps.reset()
        self.ppm.reset()
        self.ports.reset(port)
        self.datetime.reset(packet_datetime)


class PlayersRegistry:
    players_registry: ClassVar[dict[str, Player]] = {}

    _sorted_players_cache: ClassVar[list[Player]] = []
    _cache_lock = threading.Lock()

    # Constant for the default sort order
    DEFAULT_SORT_ORDER = "datetime.last_rejoin"

    @classmethod
    def add_player(cls, player: Player):
        if player.ip in cls.players_registry:
            raise ValueError(f'Player with IP "{player.ip}" already exists.')
        cls.players_registry[player.ip] = player
        return player

    @classmethod
    def get_player(cls, ip: str):
        return cls.players_registry.get(ip)

    @classmethod
    def iterate_players_from_registry(cls, sort_order: str = DEFAULT_SORT_ORDER, *, reverse: bool = False):
        yield from sorted(
            cls.players_registry.values(),
            key=attrgetter(sort_order),
            reverse=reverse,
        )

    @classmethod
    def _update_sorted_cache_core(cls, sort_order: str = DEFAULT_SORT_ORDER, *, reverse: bool = False):
        """Refresh the cached sorted player list every second."""
        with ThreadsExceptionHandler():
            while not gui_closed__event.is_set():
                with cls._cache_lock:
                    cls._sorted_players_cache = sorted(
                        cls.players_registry.values(),
                        key=attrgetter(sort_order),
                        reverse=reverse,
                    )
                gui_closed__event.wait(1)  # Sleep for 1 second

    @classmethod
    def get_sorted_players(cls, sort_order: str = DEFAULT_SORT_ORDER, *, reverse: bool = False):
        """Return the cached sorted players list (thread-safe)."""
        with cls._cache_lock:
            if sort_order == cls.DEFAULT_SORT_ORDER:
                # Return the list as is if the default sort order is requested
                return cls._sorted_players_cache.copy()
            return sorted(cls._sorted_players_cache, key=attrgetter(sort_order), reverse=reverse)

    @classmethod
    def start_cache_updater_thread(cls, sort_order: str = DEFAULT_SORT_ORDER, *, reverse: bool = False):
        """Start the background thread to update the player cache."""
        thread = threading.Thread(target=cls._update_sorted_cache_core, kwargs={"sort_order": sort_order, "reverse": reverse}, daemon=True)
        thread.start()


class SessionHost:
    player: ClassVar[Player | None] = None
    search_player = ClassVar[False]
    players_pending_for_disconnection: ClassVar[list[Player]] = []

    @staticmethod
    def get_host_player(session_connected: list[Player]):
        from modules.utils import take
        from modules.constants.standalone import MINIMUM_PACKETS_FOR_SESSION_HOST

        connected_players: list[Player] = take(2, sorted(session_connected, key=attrgetter("datetime.last_rejoin")))

        potential_session_host_player = None

        if len(connected_players) == 1:
            potential_session_host_player = connected_players[0]
        elif len(connected_players) == 2:  # noqa: PLR2004
            time_difference = connected_players[1].datetime.last_rejoin - connected_players[0].datetime.last_rejoin
            if time_difference >= timedelta(milliseconds=200):
                potential_session_host_player = connected_players[0]
        else:
            raise ValueError(f"Unexpected number of connected players: {len(connected_players)}")

        if (
            not potential_session_host_player
            # Skip players remaining to be disconnected from the previous session.
            or potential_session_host_player in SessionHost.players_pending_for_disconnection
            # The lower this value, the riskier it becomes, as it could potentially flag a player who ultimately isn't part of the newly discovered session.
            # In such scenarios, a better approach might involve checking around 25-100 packets.
            # However, increasing this value also increases the risk, as the host may have already disconnected.
            or potential_session_host_player.packets < MINIMUM_PACKETS_FOR_SESSION_HOST
        ):
            return

        SessionHost.player = potential_session_host_player
        SessionHost.search_player = False


class UserIPSettings(NamedTuple):
    """Class to represent settings with attributes for each setting key."""
    ENABLED: bool
    COLOR: QColor
    LOG: bool
    NOTIFICATIONS: bool
    VOICE_NOTIFICATIONS: str | Literal["False"]
    PROTECTION: Literal["Suspend_Process", "Exit_Process", "Restart_Process", "Shutdown_PC", "Restart_PC", False]
    PROTECTION_PROCESS_PATH: Path | None
    PROTECTION_RESTART_PROCESS_PATH: Path | None
    PROTECTION_SUSPEND_PROCESS_MODE: int | float | Literal["Auto", "Manual"]


class UserIP(NamedTuple):
    """Class representing information associated with a specific IP, including settings and usernames."""
    ip: str
    database_path: Path
    settings: UserIPSettings
    usernames: list[str]


class UserIPDatabases:
    _update_userip_database_lock = threading.Lock()

    userip_databases: ClassVar[list[tuple[Path, UserIPSettings, dict[str, list[str]]]]] = []
    ips_set: ClassVar[set[str]] = set()
    notified_settings_corrupted: ClassVar[set[Path]] = set()
    notified_ip_invalid: ClassVar[set[str]] = set()
    notified_ip_conflicts: ClassVar[set[str]] = set()

    @staticmethod
    def _notify_conflict(
        initial_userip_database: Path,
        initial_userip_usernames: list[str],
        initial_userip_ip: str,
        conflicting_userip_database: Path,
        conflicting_userip_username: str,
        conflicting_userip_ip: str,
    ):
        from modules.constants.standard import USERIP_DATABASES_PATH

        msgbox_title = TITLE
        msgbox_message = textwrap.indent(textwrap.dedent(f"""
            ERROR:
                UserIP databases IP conflict

            INFOS:
                The same IP cannot be assigned to multiple
                databases.
                Users assigned to this IP will be ignored until
                the conflict is resolved.

            DEBUG:
                \"{initial_userip_database.relative_to(USERIP_DATABASES_PATH).with_suffix("")}\":
                {', '.join(initial_userip_usernames)}={initial_userip_ip}

                \"{conflicting_userip_database.relative_to(USERIP_DATABASES_PATH).with_suffix("")}\":
                {conflicting_userip_username}={conflicting_userip_ip}
        """.removeprefix("\n").removesuffix("\n")), "    ")
        msgbox_style = MsgBox.Style.MB_OK | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SYSTEMMODAL
        threading.Thread(target=MsgBox.show, args=(msgbox_title, msgbox_message, msgbox_style), daemon=True).start()

    @classmethod
    def populate(cls, database_entries: list[tuple[Path, UserIPSettings, dict[str, list[str]]]]):
        """Replace `cls.userip_databases` with a new set of databases.

        Args:
            database_entries: A list of tuples containing database_path, settings, and user_ips.
        """
        with cls._update_userip_database_lock:
            cls.userip_databases = [
                (database_path, settings, user_ips)
                for database_path, settings, user_ips in database_entries
                if settings.ENABLED
            ]

    @classmethod
    def build(cls):
        """Build the userip_infos_by_ip dictionary dynamically from the current databases.

        This method updates the dictionaries without clearing their content entirely and avoids duplicates.
        """
        with cls._update_userip_database_lock:
            ips_set: set[str] = set()
            ip_to_userip: dict[str, UserIP] = {}
            unresolved_conflicts: set[str] = set()

            for database_path, settings, user_ips in cls.userip_databases:
                for username, ips in user_ips.items():
                    for ip in ips:
                        # If the IP is already assigned to a different database, it's a conflict.
                        if ip in ip_to_userip and ip_to_userip[ip].database_path != database_path:
                            if ip not in cls.notified_ip_conflicts:
                                cls._notify_conflict(
                                    initial_userip_database=ip_to_userip[ip].database_path,
                                    initial_userip_usernames=ip_to_userip[ip].usernames,
                                    initial_userip_ip=ip_to_userip[ip].ip,
                                    conflicting_userip_database=database_path,
                                    conflicting_userip_username=username,
                                    conflicting_userip_ip=ip,
                                )
                                cls.notified_ip_conflicts.add(ip)
                            unresolved_conflicts.add(ip)
                            continue

                        ips_set.add(ip)

                        # If it's a new entry, add it
                        if ip not in ip_to_userip:
                            ip_to_userip[ip] = UserIP(
                                ip=ip,
                                database_path=database_path,
                                settings=settings,
                                usernames=[username],
                            )
                        elif username not in ip_to_userip[ip].usernames:  # Append username if it doesn't already exist
                            ip_to_userip[ip].usernames.append(username)

                        # Assign the UserIP object to the PlayerRegistry if applicable
                        if player := PlayersRegistry.get_player(ip):
                            player.userip = ip_to_userip[ip]

            # Remove resolved conflicts
            resolved_conflicts = cls.notified_ip_conflicts - unresolved_conflicts
            for resolved_ip in resolved_conflicts:
                cls.notified_ip_conflicts.remove(resolved_ip)

            cls.ips_set = ips_set

    @classmethod
    def get_userip_database_filepaths(cls):
        with cls._update_userip_database_lock:
            return [database_path for database_path, _, _ in cls.userip_databases]


def check_for_updates():
    from modules.utils import format_project_version

    def get_updater_json_response():
        from modules.constants.standalone import GITHUB_VERSIONS_URL

        while True:
            try:
                response = s.get(GITHUB_VERSIONS_URL)
                response.raise_for_status()
            except requests.exceptions.RequestException:
                msgbox_title = TITLE
                msgbox_message = textwrap.dedent(f"""
                    ERROR:
                    Failed to check for updates.

                    Do you want to open the \"{TITLE}\" project download page ?
                    You can then download and run the latest version from there.
                """.removeprefix("\n").removesuffix("\n"))
                msgbox_style = MsgBox.Style.MB_ABORTRETRYIGNORE | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SETFOREGROUND
                errorlevel = MsgBox.show(msgbox_title, msgbox_message, msgbox_style)

                if errorlevel == MsgBox.ReturnValues.IDABORT:
                    webbrowser.open(GITHUB_RELEASES_URL)
                    sys.exit(0)
                elif errorlevel == MsgBox.ReturnValues.IDRETRY:
                    continue
                elif errorlevel == MsgBox.ReturnValues.IDIGNORE:
                    webbrowser.open(GITHUB_RELEASES_URL)
                    return None
            else:
                versions_json: dict[str, str] = response.json()
                if not isinstance(versions_json, dict):
                    raise TypeError(f'Expected "dict" object, got "{type(versions_json).__name__}"')

                return versions_json

    versions_json = get_updater_json_response()
    if versions_json is None:
        return

    current_version = Version(PYPROJECT_DATA["project"]["version"])

    # Get versions from the response
    latest_stable_version = Version(versions_json["latest_stable"]["version"])
    latest_rc_version = Version(versions_json["latest_prerelease"]["version"])

    # Check for updates based on the current version
    is_new_stable_version_available = latest_stable_version > current_version
    is_new_rc_version_available = latest_rc_version > current_version

    # Determine which version to display based on the user's channel setting
    if is_new_stable_version_available or (Settings.UPDATER_CHANNEL == "RC" and is_new_rc_version_available):
        update_channel = "pre-release" if (Settings.UPDATER_CHANNEL == "RC" and is_new_rc_version_available) else "stable release"
        latest_version = latest_rc_version if (Settings.UPDATER_CHANNEL == "RC" and is_new_rc_version_available) else latest_stable_version

        msgbox_title = TITLE
        msgbox_message = textwrap.dedent(f"""
            New {update_channel} version found. Do you want to update?

            Current version: {format_project_version(current_version)}
            Latest version: {format_project_version(latest_version)}
        """.removeprefix("\n").removesuffix("\n"))

        msgbox_style = MsgBox.Style.MB_YESNO | MsgBox.Style.MB_ICONQUESTION | MsgBox.Style.MB_SETFOREGROUND
        errorlevel = MsgBox.show(msgbox_title, msgbox_message, msgbox_style)

        if errorlevel == MsgBox.ReturnValues.IDYES:
            webbrowser.open(GITHUB_RELEASES_URL)
            sys.exit(0)


def populate_network_interfaces_info():
    """Populate the AllInterfaces collection with network interface details."""
    from modules.networking.wmi_utils import (
        iterate_project_network_adapter_details,
        iterate_project_legacy_network_adapter_details,
        iterate_project_network_ip_details,
        iterate_project_legacy_network_ip_details,
        iterate_project_network_neighbor_details,
    )

    def validate_and_format_mac_address(mac_address: str | None):
        """Validate the MAC address, ensuring it is in the correct format."""
        if mac_address in (None, ""):
            return None

        formatted_mac_address = format_mac_address(mac_address)
        if not is_mac_address(formatted_mac_address):
            stdout_crash_text = textwrap.dedent(f"""
                ERROR:
                    Developer didn't expect this scenario to be possible.

                INFOS:
                    The value does not appear to be a valid MAC address.

                DEBUG:
                    mac_address={mac_address}
                    formatted_mac_address={formatted_mac_address}
            """.removeprefix("\n").removesuffix("\n"))
            terminate_script("EXIT", stdout_crash_text, stdout_crash_text)

        return formatted_mac_address

    def validate_ip_address(ip_address: str | None):
        """Validate the IP address, ensuring it is a valid IPv4 address."""
        if ip_address in (None, ""):
            return None

        if not is_ipv4_address(ip_address):
            stdout_crash_text = textwrap.dedent(f"""
                ERROR:
                    Developer didn't expect this scenario to be possible.

                INFOS:
                    The value does not appear to be a valid IPv4 address.

                DEBUG:
                    ip_address={ip_address}
            """.removeprefix("\n").removesuffix("\n"))
            terminate_script("EXIT", stdout_crash_text, stdout_crash_text)

        return ip_address

    def _populate_network_adapter_details():
        """Populate AllInterfaces collection with network adapter details from MSFT_NetAdapter."""
        for interface_index, name, interface_description, state in iterate_project_network_adapter_details():
            interface = AllInterfaces.get_interface(interface_index)
            if not interface:
                AllInterfaces.add_interface(Interface(
                    index=interface_index,
                    state=state,
                    name=name,
                    descriptions=[interface_description],
                ))
                continue

            interface.update_state(state)
            interface.update_name(name)
            interface.add_description(interface_description)

    def _populate_legacy_network_adapter_details():
        """Populate AllInterfaces collection with legacy network adapter details."""
        for interface_index, net_connection_id, description, mac_address, manufacturer in iterate_project_legacy_network_adapter_details():
            validated_and_formatted_mac_address = validate_and_format_mac_address(mac_address)

            interface = AllInterfaces.get_interface(interface_index)
            if not interface:
                AllInterfaces.add_interface(Interface(
                    index=interface_index,
                    name=net_connection_id,
                    mac_address=validated_and_formatted_mac_address,
                    manufacturer=manufacturer,
                    descriptions=[description],
                ))
                continue

            interface.update_name(net_connection_id)
            interface.update_mac_address(validated_and_formatted_mac_address)
            interface.update_manufacturer(manufacturer)
            interface.add_description(description)

    def _populate_network_ip_details():
        """Populate AllInterfaces collection with network IP address details."""
        for interface_index, interface_alias, ipv4_address in iterate_project_network_ip_details():
            validated_ip_address = validate_ip_address(ipv4_address)

            interface = AllInterfaces.get_interface(interface_index)
            if not interface:
                AllInterfaces.add_interface(Interface(
                    index=interface_index,
                    name=interface_alias,
                    ip_addresses=[validated_ip_address] if validated_ip_address else [],
                ))
                continue

            interface.update_name(interface_alias)
            interface.add_ip_address(validated_ip_address)

    def _populate_legacy_network_ip_details():
        """Populate AllInterfaces collection with legacy network IP address details."""
        for interface_index, description, mac_address, ip_address, ip_enabled in iterate_project_legacy_network_ip_details():
            validated_ip_addresses: list[str] = [
                validated_ip_address
                for ip in remove_duplicates_from_list(
                    [ip for ip in ip_address if is_ipv4_address(ip)]
                    if ip_address is not None else [],
                )
                if (validated_ip_address := validate_ip_address(ip))
            ]
            validated_and_formatted_mac_address = validate_and_format_mac_address(mac_address)

            interface = AllInterfaces.get_interface(interface_index)
            if not interface:
                AllInterfaces.add_interface(Interface(
                    index=interface_index,
                    ip_enabled=ip_enabled,
                    mac_address=validated_and_formatted_mac_address,
                    ip_addresses=validated_ip_addresses,
                    descriptions=[description],
                ))
                continue

            interface.update_ip_enabled(ip_enabled)
            interface.update_mac_address(validated_and_formatted_mac_address)
            interface.add_description(description)
            for ip in validated_ip_addresses:
                interface.add_ip_address(ip)

    def _update_network_io_stats():
        """Update network interface statistics like packets sent and received."""
        net_io_stats = psutil.net_io_counters(pernic=True)
        for interface_name, interface_stats in net_io_stats.items():
            interface = AllInterfaces.get_interface_by_name(interface_name)
            if not interface:
                continue

            interface.update_packets_sent(interface_stats.packets_sent)
            interface.update_packets_recv(interface_stats.packets_recv)

    def _populate_arp_cache_details():
        """Populate ARP cache information for each interface."""
        for interface_index, ip_address, mac_address in iterate_project_network_neighbor_details():
            interface = AllInterfaces.get_interface(interface_index)
            if not interface:
                continue

            validated_ip_address = validate_ip_address(ip_address)
            validated_and_formatted_mac_address = validate_and_format_mac_address(mac_address)

            if (
                validated_ip_address is None
                or validated_and_formatted_mac_address is None
                or validated_and_formatted_mac_address in {"00:00:00:00:00:00", "FF:FF:FF:FF:FF:FF"}  # Skip ARP entries with known placeholder MAC addresses
                or not is_valid_non_special_ipv4(validated_ip_address)
            ):
                continue

            interface.add_arp_entry(ARPEntry(
                ip_address=validated_ip_address,
                mac_address=validated_and_formatted_mac_address,
                manufacturer=mac_lookup.get_mac_address_organization_name(validated_and_formatted_mac_address) or "N/A",
            ))

    _populate_network_adapter_details()
    _populate_legacy_network_adapter_details()
    _populate_network_ip_details()
    _populate_legacy_network_ip_details()
    _update_network_io_stats()
    if Settings.CAPTURE_ARP:
        _populate_arp_cache_details()


def get_filtered_tshark_interfaces():
    """Retrieve a list of available TShark interfaces, excluding a list of exclusions.

    Returns:
        A list of tuples containing:
        - Index (int)
        - Device name (str)
        - Interface name (str)
    """
    from modules.constants.standalone import EXCLUDED_CAPTURE_NETWORK_INTERFACES, INTERFACE_PARTS_LENGTH

    def process_stdout(stdout_line: str):
        parts = stdout_line.strip().split(" ", maxsplit=INTERFACE_PARTS_LENGTH - 1)

        if len(parts) != INTERFACE_PARTS_LENGTH:
            raise ValueError(f'Expected "{INTERFACE_PARTS_LENGTH}" parts, got "{len(parts)}" in "{stdout_line}"')

        index = int(parts[0].removesuffix("."))
        device_name = parts[1]
        name = parts[2].removeprefix("(").removesuffix(")")

        return index, device_name, name

    stdout = subprocess.check_output([tshark_path, "-D"], encoding="utf-8", text=True)

    if not isinstance(stdout, str):
        raise TypeError(f'Expected "str", got "{type(stdout).__name__}"')

    return [
        (index, device_name, name)
        for index, device_name, name in map(process_stdout, stdout.splitlines())
        if name not in EXCLUDED_CAPTURE_NETWORK_INTERFACES
    ]


def select_interface(interfaces_selection_data: list[InterfaceSelectionData], screen_width: int, screen_height: int):
    """Select the best matching interface based on given settings.

    If no interface matches, show the selection dialog to prompt the user.
    """

    def select_best_settings_matching_interface():
        """Select the interface with the highest priority based on the given settings.

        Returns None if no interface matches.
        """

        def calculate_interface_priority(interface: InterfaceSelectionData):
            """Calculate the priority of an interface based on the given settings.

            Priority increases for each matching setting.
            """
            priority = 0

            if Settings.CAPTURE_INTERFACE_NAME is not None and interface.name == Settings.CAPTURE_INTERFACE_NAME:
                priority += 1
            if Settings.CAPTURE_MAC_ADDRESS is not None and interface.mac_address == Settings.CAPTURE_MAC_ADDRESS:
                priority += 1
            if Settings.CAPTURE_IP_ADDRESS is not None and interface.ip_address == Settings.CAPTURE_IP_ADDRESS:
                priority += 1

            return priority

        # First, try to select the best matching interface based on priority
        max_priority = 0
        selected_interface_index = None

        for interface in interfaces_selection_data:
            priority = calculate_interface_priority(interface)

            if priority == max_priority:
                selected_interface_index = None  # If multiple matches found, reset selection
            elif priority > max_priority:
                max_priority = priority
                selected_interface_index = interface.selection_index

        if selected_interface_index is not None:
            return interfaces_selection_data[selected_interface_index]

        return None

    # First try to select the best matching interface based on settings
    if (
        # Check if the network interface prompt is disabled
        not Settings.CAPTURE_NETWORK_INTERFACE_CONNECTION_PROMPT
        # Check if any capture setting is defined
        and any(setting is not None for setting in {Settings.CAPTURE_INTERFACE_NAME, Settings.CAPTURE_MAC_ADDRESS, Settings.CAPTURE_IP_ADDRESS})
    ):
        selected_interface = select_best_settings_matching_interface()
        if selected_interface is not None:
            return selected_interface

    # If no suitable interface was found, prompt the user to select an interface
    selected_interface = show_interface_selection_dialog(screen_width, screen_height, interfaces_selection_data)
    if selected_interface is None:
        sys.exit(0)  # Exit if no selection is made

    return selected_interface


def update_and_initialize_geolite2_readers():
    def update_geolite2_databases():
        from modules.constants.standalone import GITHUB_RELEASE_API__GEOLITE2__URL, ERROR_USER_MAPPED_FILE  # TODO(BUZZARDGTA): Implement adding: `, GITHUB_RELEASE_API__GEOLITE2__BACKUP__URL` in case the first one fails.
        from modules.constants.standard import GEOLITE2_DATABASES_FOLDER_PATH

        geolite2_version_file_path = GEOLITE2_DATABASES_FOLDER_PATH / "version.json"
        geolite2_databases: dict[str, dict[str, str | None]] = {
            f"GeoLite2-{db}.mmdb": {
                "current_version": None,
                "last_version": None,
                "download_url": None,
            }
            for db in ("ASN", "City", "Country")
        }

        try:
            with geolite2_version_file_path.open("r", encoding="utf-8") as f:
                loaded_data = json.load(f)
        except FileNotFoundError:
            pass
        else:
            if isinstance(loaded_data, dict):
                for database_name, database_info in loaded_data.items():
                    if not isinstance(database_name, str):
                        continue
                    if not isinstance(database_info, dict):
                        continue
                    if database_name not in geolite2_databases:
                        continue

                    geolite2_databases[database_name]["current_version"] = database_info.get("version", None)

        try:
            response = s.get(GITHUB_RELEASE_API__GEOLITE2__URL)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {
                "exception": e,
                "url": GITHUB_RELEASE_API__GEOLITE2__URL,
                "http_code": getattr(e.response, "status_code", None),
            }

        release_data = response.json()
        if not isinstance(release_data, dict):
            raise TypeError(f'Expected "dict" object, got "{type(release_data).__name__}"')

        for asset in release_data["assets"]:
            asset_name = asset["name"]
            if not isinstance(asset_name, str):
                continue
            if asset_name not in geolite2_databases:
                continue

            geolite2_databases[asset_name].update({
                "last_version": asset["updated_at"],
                "download_url": asset["browser_download_url"],
            })

        failed_fetching_flag_list: list[str] = []
        for database_name, database_info in geolite2_databases.items():
            if database_info["last_version"]:
                if database_info["current_version"] != database_info["last_version"]:
                    try:
                        response = s.get(database_info["download_url"])
                        response.raise_for_status()
                    except requests.exceptions.RequestException as e:
                        return {
                            "exception": e,
                            "url": database_info["download_url"],
                            "http_code": getattr(e.response, "status_code", None),
                        }

                    if not isinstance(response.content, bytes):
                        raise TypeError(f'Expected "bytes" object, got "{type(response.content).__name__}"')

                    GEOLITE2_DATABASES_FOLDER_PATH.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist
                    destination_file_path = GEOLITE2_DATABASES_FOLDER_PATH / database_name

                    # [Bug-Fix]: https://github.com/BUZZARDGTA/Session-Sniffer/issues/28
                    if destination_file_path.is_file():
                        if hashlib.sha256(destination_file_path.read_bytes()).hexdigest() == hashlib.sha256(response.content).hexdigest():
                            geolite2_databases[database_name]["current_version"] = database_info["last_version"]
                        else:
                            temp_path = Path(tempfile.gettempdir()) / database_name
                            temp_path.write_bytes(response.content)

                            try:
                                shutil.move(temp_path, destination_file_path)
                            except OSError as e:
                                # The file is currently open and in use by another process. Abort updating this database.
                                if e.winerror == ERROR_USER_MAPPED_FILE:
                                    if temp_path.is_file():
                                        temp_path.unlink()
                                    geolite2_databases[database_name]["current_version"] = database_info["current_version"]
                    else:
                        destination_file_path.write_bytes(response.content)
                        geolite2_databases[database_name]["current_version"] = database_info["last_version"]
            else:
                failed_fetching_flag_list.append(database_name)

        if failed_fetching_flag_list:
            msgbox_title = TITLE
            msgbox_message = textwrap.indent(textwrap.dedent(f"""
                ERROR:
                    Failed fetching MaxMind \"{'", "'.join(failed_fetching_flag_list)}" database{pluralize(len(failed_fetching_flag_list))}.

                INFOS:
                    These MaxMind GeoLite2 database{pluralize(len(failed_fetching_flag_list))} will not be updated.

                DEBUG:
                    GITHUB_RELEASE_API__GEOLITE2__URL={GITHUB_RELEASE_API__GEOLITE2__URL}
                    failed_fetching_flag_list={failed_fetching_flag_list}
            """.removeprefix("\n").removesuffix("\n")), "    ")
            msgbox_style = MsgBox.Style.MB_OK | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SYSTEMMODAL
            threading.Thread(target=MsgBox.show, args=(msgbox_title, msgbox_message, msgbox_style), daemon=True).start()

        # Create the data dictionary, where each name maps to its version info
        data = {
            name: {"version": info["current_version"]}
            for name, info in geolite2_databases.items()
        }

        # Convert the data to a JSON formatted string with proper indentation
        json_data = json.dumps(data, indent=4)

        # Write the JSON formatted string to the GeoLite2 version file
        geolite2_version_file_path.write_text(json_data, encoding="utf-8")

        return {
            "exception": None,
            "url": None,
            "http_code": None,
        }

    def initialize_geolite2_readers():
        from modules.constants.standard import GEOLITE2_DATABASES_FOLDER_PATH

        try:
            geolite2_asn_reader = geoip2.database.Reader(GEOLITE2_DATABASES_FOLDER_PATH / "GeoLite2-ASN.mmdb")
            geolite2_city_reader = geoip2.database.Reader(GEOLITE2_DATABASES_FOLDER_PATH / "GeoLite2-City.mmdb")
            geolite2_country_reader = geoip2.database.Reader(GEOLITE2_DATABASES_FOLDER_PATH / "GeoLite2-Country.mmdb")

            geolite2_asn_reader.asn("1.1.1.1")
            geolite2_city_reader.city("1.1.1.1")
            geolite2_country_reader.country("1.1.1.1")

            exception = None
        except geoip2.errors.GeoIP2Error as e:
            geolite2_asn_reader = None
            geolite2_city_reader = None
            geolite2_country_reader = None

            exception = e

        return exception, geolite2_asn_reader, geolite2_city_reader, geolite2_country_reader

    update_geolite2_databases__dict = update_geolite2_databases()
    exception__initialize_geolite2_readers, geolite2_asn_reader, geolite2_city_reader, geolite2_country_reader = initialize_geolite2_readers()

    show_error = False
    msgbox_message = ""

    if update_geolite2_databases__dict["exception"]:
        msgbox_message += f"Exception Error: {update_geolite2_databases__dict['exception']}\n\n"
        show_error = True
    if update_geolite2_databases__dict["url"]:
        msgbox_message += f'Error: Failed fetching url: "{update_geolite2_databases__dict['url']}".'
        if update_geolite2_databases__dict["http_code"]:
            msgbox_message += f" (http_code: {update_geolite2_databases__dict['http_code']})"
        msgbox_message += "\nImpossible to keep Maxmind's GeoLite2 IP to Country, City and ASN resolutions feature up-to-date.\n\n"
        show_error = True

    if exception__initialize_geolite2_readers:
        msgbox_message += f"Exception Error: {exception__initialize_geolite2_readers}\n\n"
        msgbox_message += "Now disabling MaxMind's GeoLite2 IP to Country, City and ASN resolutions feature.\n"
        msgbox_message += "Countrys, Citys and ASN from players won't shows up from the players fields."
        geoip2_enabled = False
        show_error = True
    else:
        geoip2_enabled = True

    if show_error:
        msgbox_title = TITLE
        msgbox_message = msgbox_message.rstrip("\n")
        msgbox_style = MsgBox.Style.MB_OK | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SETFOREGROUND
        MsgBox.show(msgbox_title, msgbox_message, msgbox_style)

    return geoip2_enabled, geolite2_asn_reader, geolite2_city_reader, geolite2_country_reader


colorama.init(autoreset=True)

if is_pyinstaller_compiled():
    SCRIPT_DIR = Path(sys.executable).parent
else:
    SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)

if not is_pyinstaller_compiled():
    clear_screen()
    set_window_title(f'Checking that your Python packages versions matches with file "requirements.txt" - {TITLE}')
    print('\nChecking that your Python packages versions matches with file "requirements.txt" ...\n')

    if outdated_packages := check_packages_version(get_dependencies_from_pyproject() or get_dependencies_from_requirements()):
        msgbox_message = "The following packages have version mismatches:\n\n"

        # Iterate over outdated packages and add each package's information to the message box text
        for package_name, required_version, installed_version in outdated_packages:
            msgbox_message += f"{package_name} (required {required_version}, installed {installed_version})\n"

        # Add additional message box text
        msgbox_message += f'\nKeeping your packages synced with "{TITLE}" ensures smooth script execution and prevents compatibility issues.'
        msgbox_message += "\n\nDo you want to ignore this warning and continue with script execution?"

        # Show message box
        msgbox_style = MsgBox.Style.MB_YESNO | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SETFOREGROUND
        msgbox_title = TITLE
        errorlevel = MsgBox.show(msgbox_title, msgbox_message, msgbox_style)
        if errorlevel != MsgBox.ReturnValues.IDYES:
            sys.exit(0)

clear_screen()
set_window_title(f'Applying your custom settings from "Settings.ini" - {TITLE}')
print('\nApplying your custom settings from "Settings.ini" ...\n')
Settings.load_from_settings_file(SETTINGS_PATH)

clear_screen()
set_window_title(f"Searching for a new update - {TITLE}")
print("\nSearching for a new update ...\n")
check_for_updates()

clear_screen()
set_window_title(f'Checking that "Npcap" driver is installed on your system - {TITLE}')
print('\nChecking that "Npcap" driver is installed on your system ...\n')

while not is_npcap_installed():
    webbrowser.open("https://nmap.org/npcap/")
    msgbox_title = TITLE
    msgbox_message = textwrap.dedent("""
        ERROR:
        Could not detect \"Npcap\" driver installed on your system.

        Opening the \"Npcap\" setup installer for you.
    """.removeprefix("\n").removesuffix("\n"))
    msgbox_style = MsgBox.Style.MB_OK | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SETFOREGROUND
    MsgBox.show(msgbox_title, msgbox_message, msgbox_style)

    subprocess.run([SETUP_PATH / "npcap-1.78.exe"], shell=True, check=True)

clear_screen()
set_window_title(f'Applying your custom settings from "Settings.ini" - {TITLE}')
print('\nApplying your custom settings from "Settings.ini" ...\n')
Settings.load_from_settings_file(SETTINGS_PATH)

clear_screen()
set_window_title(f'Verifying "Tshark (Wireshark) v{TSHARK_RECOMMENDED_VERSION_NUMBER}" in script directories and version match - {TITLE}')
print(f'\nVerifying "Tshark (Wireshark) v{TSHARK_RECOMMENDED_VERSION_NUMBER}" in script directories and version match ...\n')

while True:
    try:
        tshark_path, tshark_version = validate_tshark_path(BIN_PATH / "WiresharkPortable64/App/Wireshark/tshark.exe")
        break
    except TSharkNotFoundError:
        webbrowser.open(GITHUB_RELEASES_URL)

        msgbox_title = TITLE
        msgbox_message = textwrap.dedent(f"""
            ERROR:
            \"TShark\" could not be found within the script directories.

            Opening {TITLE} download page for you.
            Please download and reinstall it, then restart the application.
        """.removeprefix("\n").removesuffix("\n"))
        msgbox_style = MsgBox.Style.MB_OK | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SETFOREGROUND
        MsgBox.show(msgbox_title, msgbox_message, msgbox_style)
        sys.exit(0)
    except TSharkVersionNotFoundError:
        webbrowser.open(GITHUB_RELEASES_URL)

        msgbox_title = TITLE
        msgbox_message = textwrap.dedent(f"""
            ERROR:
            Could not determine the version of \"TShark (Wireshark)\".

            Opening {TITLE} download page for you.
            Please download and reinstall it, then restart the application.
        """).strip()
        msgbox_style = MsgBox.Style.MB_OK | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SETFOREGROUND
        MsgBox.show(msgbox_title, msgbox_message, msgbox_style)
        sys.exit(0)
    except InvalidTSharkVersionError as unsupported_tshark:
        webbrowser.open(GITHUB_RELEASES_URL)

        msgbox_title = TITLE
        msgbox_message = textwrap.dedent(f"""
            ERROR:
            Detected an unsupported \"Tshark (Wireshark)\" version installed on your system.

            Detected version: {unsupported_tshark.version}
            Recommended version: {TSHARK_RECOMMENDED_FULL_VERSION}

            Opening {TITLE} download page for you.
            Please download and reinstall it, then restart the application.
        """.removeprefix("\n").removesuffix("\n"))
        msgbox_style = MsgBox.Style.MB_ABORTRETRYIGNORE | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SETFOREGROUND
        errorlevel = MsgBox.show(msgbox_title, msgbox_message, msgbox_style)
        if errorlevel == MsgBox.ReturnValues.IDABORT:
            sys.exit(0)
        elif errorlevel == MsgBox.ReturnValues.IDIGNORE:
            tshark_path = unsupported_tshark.path
            tshark_version = unsupported_tshark.version
            break

clear_screen()
set_window_title(f"Initializing and updating MaxMind's GeoLite2 Country, City and ASN databases - {TITLE}")
print("\nInitializing and updating MaxMind's GeoLite2 Country, City and ASN databases ...\n")
geoip2_enabled, geolite2_asn_reader, geolite2_city_reader, geolite2_country_reader = update_and_initialize_geolite2_readers()

clear_screen()
set_window_title(f"Initializing MacLookup module - {TITLE}")
print("\nInitializing MacLookup module ...\n")
mac_lookup = MacLookup(load_on_init=True)

clear_screen()
set_window_title(f"Capture network interface selection - {TITLE}")
print("\nCapture network interface selection ...\n")
populate_network_interfaces_info()

tshark_interfaces = [
    i for _, _, name in get_filtered_tshark_interfaces()
    if (i := AllInterfaces.get_interface_by_name(name)) and not i.is_interface_inactive()
]

# Create a QApplication instance
app = QApplication([])  # Passing an empty list for application arguments
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
screen_width, screen_height = get_screen_size(app)

interfaces_selection_data: list[InterfaceSelectionData] = []

for interface in tshark_interfaces:
    if (
        Settings.CAPTURE_INTERFACE_NAME is not None
        and interface.name.casefold() == Settings.CAPTURE_INTERFACE_NAME.casefold()
        and interface.name != Settings.CAPTURE_INTERFACE_NAME
    ):
        Settings.CAPTURE_INTERFACE_NAME = interface.name
        Settings.reconstruct_settings()

    manufacturer = "N/A" if interface.manufacturer is None else interface.manufacturer
    packets_sent = "N/A" if interface.packets_sent is None else interface.packets_sent
    packets_recv = "N/A" if interface.packets_recv is None else interface.packets_recv

    if interface.ip_addresses:
        for ip_address in interface.ip_addresses:
            interfaces_selection_data.append(InterfaceSelectionData(len(interfaces_selection_data), interface.name, ", ".join(interface.descriptions), packets_sent, packets_recv, ip_address, interface.mac_address, manufacturer))
    else:
        interfaces_selection_data.append(InterfaceSelectionData(len(interfaces_selection_data), interface.name, ", ".join(interface.descriptions), packets_sent, packets_recv, "N/A", interface.mac_address, manufacturer))

    if Settings.CAPTURE_ARP:
        for arp_entry in interface.get_arp_entries():
            manufacturer = "N/A" if arp_entry.manufacturer is None else arp_entry.manufacturer

            interfaces_selection_data.append(InterfaceSelectionData(len(interfaces_selection_data), interface.name, ", ".join(interface.descriptions), "N/A", "N/A", arp_entry.ip_address, arp_entry.mac_address, manufacturer, is_arp=True))

selected_interface = select_interface(interfaces_selection_data, screen_width, screen_height)
if not isinstance(selected_interface.name, str):
    raise TypeError(f'Expected "str" object, got "{type(selected_interface.name).__name__}"')

clear_screen()
set_window_title(f"Initializing addresses and establishing connection to your PC / Console - {TITLE}")
print("\nInitializing addresses and establishing connection to your PC / Console ...\n")
need_rewrite_settings = False
fixed__capture_mac_address = selected_interface.mac_address
fixed__capture_ip_address = selected_interface.ip_address

if (
    Settings.CAPTURE_INTERFACE_NAME is None
    or selected_interface.name != Settings.CAPTURE_INTERFACE_NAME
):
    Settings.CAPTURE_INTERFACE_NAME = selected_interface.name
    need_rewrite_settings = True

if fixed__capture_mac_address != Settings.CAPTURE_MAC_ADDRESS:
    Settings.CAPTURE_MAC_ADDRESS = fixed__capture_mac_address
    need_rewrite_settings = True

if fixed__capture_ip_address != Settings.CAPTURE_IP_ADDRESS:
    Settings.CAPTURE_IP_ADDRESS = fixed__capture_ip_address
    need_rewrite_settings = True

if need_rewrite_settings:
    Settings.reconstruct_settings()

capture_filter: list[str] = ["ip", "udp"]
display_filter: list[str] = []
excluded_protocols: list[str] = []

if Settings.CAPTURE_IP_ADDRESS:
    capture_filter.append(f"((src host {Settings.CAPTURE_IP_ADDRESS} and (not (dst net 10.0.0.0/8 or 100.64.0.0/10 or 172.16.0.0/12 or 192.168.0.0/16 or 224.0.0.0/4))) or (dst host {Settings.CAPTURE_IP_ADDRESS} and (not (src net 10.0.0.0/8 or 100.64.0.0/10 or 172.16.0.0/12 or 192.168.0.0/16 or 224.0.0.0/4))))")

force_enable_capture_vpn_mode = False
if not Settings.CAPTURE_VPN_MODE:
    from modules.capture.utils.check_tshark_filters import check_broadcast_multicast_support

    if all(check_broadcast_multicast_support(tshark_path, Settings.CAPTURE_INTERFACE_NAME)):
        capture_filter.append("not (broadcast or multicast)")
    else:
        force_enable_capture_vpn_mode = True

capture_filter.append("not (portrange 0-1023 or port 5353)")

if Settings.CAPTURE_PROGRAM_PRESET:
    if Settings.CAPTURE_PROGRAM_PRESET == "GTA5":
        capture_filter.append("(len >= 71 and len <= 1032)")
    elif Settings.CAPTURE_PROGRAM_PRESET == "Minecraft":
        capture_filter.append("(len >= 49 and len <= 1498)")

    # If the <CAPTURE_PROGRAM_PRESET> setting is set, automatically blocks RTCP connections.
    # In case RTCP can be useful to get someone IP, I decided not to block them without using a <CAPTURE_PROGRAM_PRESET>.
    # RTCP is known to be for example the Discord's server IP while you are in a call there.
    # The "not rtcp" Display Filter have been heavily tested and I can confirm that it's indeed working correctly.
    # I know that eventually you will see their corresponding IPs time to time but I can guarantee that it does the job it is supposed to do.
    # It filters RTCP but some connections are STILL made out of it, but those are not RTCP ¯\_(ツ)_/¯.
    # And that's exactly why the "Discord" (`class ThirdPartyServers`) IP ranges Capture Filters are useful for.
    excluded_protocols.append("rtcp")

if Settings.CAPTURE_BLOCK_THIRD_PARTY_SERVERS:
    capture_filter.append(f"not (net {' or '.join(ThirdPartyServers.get_all_ip_ranges())})")

    # Here I'm trying to exclude various UDP protocols that are usefless for the srcipt.
    # But there can be a lot more, those are just a couples I could find on my own usage.
    excluded_protocols.extend(["ssdp", "raknet", "dtls", "nbns", "pcp", "bt-dht", "uaudp", "classicstun", "dhcp", "mdns", "llmnr"])

if excluded_protocols:
    display_filter.append(
        f"not ({' or '.join(excluded_protocols)})",
    )

if Settings.CAPTURE_PREPEND_CUSTOM_CAPTURE_FILTER:
    capture_filter.insert(0, f"({Settings.CAPTURE_PREPEND_CUSTOM_CAPTURE_FILTER})")

if Settings.CAPTURE_PREPEND_CUSTOM_DISPLAY_FILTER:
    display_filter.insert(0, f"({Settings.CAPTURE_PREPEND_CUSTOM_DISPLAY_FILTER})")

CAPTURE_FILTER = " and ".join(capture_filter) if capture_filter else None
DISPLAY_FILTER = " and ".join(display_filter) if display_filter else None

capture = PacketCapture(
    interface=Settings.CAPTURE_INTERFACE_NAME,
    capture_filter=CAPTURE_FILTER,
    display_filter=DISPLAY_FILTER,
    tshark_path=tshark_path,
    tshark_version=tshark_version,
)

gui_closed__event = threading.Event()
_userip_logging_file_write_lock: threading.Lock = threading.Lock()


def process_userip_task(
    player: Player,
    connection_type: Literal["connected", "disconnected"],
):
    with ThreadsExceptionHandler():
        from modules.constants.standard import USERIP_LOGGING_PATH, SHUTDOWN_EXE
        from modules.constants.local import TTS_PATH
        from modules.utils import get_pid_by_path, terminate_process_tree, write_lines_to_file

        if not isinstance(player.userip_detection, PlayerUserIPDetection):
            raise TypeError(f'Expected "UserIPDetection" object, got "{type(player.userip_detection).__name__}"')

        timeout = 10
        start_time = time.monotonic()

        while not isinstance(player.userip, UserIP):
            if time.monotonic() - start_time > timeout:
                raise TypeError(f'Expected "UserIP" object, got "{type(player.userip).__name__}"')
            time.sleep(0.01)  # Sleep to prevent high CPU usage

        def suspend_process_for_duration_or_mode(process_pid: int, duration_or_mode: float | Literal["Auto", "Manual"]):
            """Suspends the specified process for a given duration or until a specified condition is met.

            Args:
                process_pid: The process ID of the process to be suspended.
                duration_or_mode: Specifies how long the process should be suspended.
                    - If a float, it defines the duration (in seconds) to suspend the process.
                    - If "Manual", the process remains suspended until manually resumed.
                    - If "Auto", the process resumes when the player is flagged as "disconnected".
            """
            process = psutil.Process(process_pid)
            process.suspend()

            if isinstance(duration_or_mode, (int, float)):
                gui_closed__event.wait(duration_or_mode)
                process.resume()
                return

            if duration_or_mode == "Manual":
                return
            if duration_or_mode == "Auto":
                while not player.datetime.left:
                    gui_closed__event.wait(0.1)
                process.resume()
                return

        # We wants to run this as fast as possible so it's on top of the function.
        if connection_type == "connected" and player.userip.settings.PROTECTION:
            if player.userip.settings.PROTECTION == "Suspend_Process" and isinstance(player.userip.settings.PROTECTION_PROCESS_PATH, Path):
                if process_pid := get_pid_by_path(player.userip.settings.PROTECTION_PROCESS_PATH):
                    threading.Thread(
                        target=suspend_process_for_duration_or_mode,
                        args=(process_pid, player.userip.settings.PROTECTION_SUSPEND_PROCESS_MODE),
                        daemon=True,
                    ).start()

            elif player.userip.settings.PROTECTION in {"Exit_Process", "Restart_Process"} and isinstance(player.userip.settings.PROTECTION_PROCESS_PATH, Path):
                if process_pid := get_pid_by_path(player.userip.settings.PROTECTION_PROCESS_PATH):
                    terminate_process_tree(process_pid)

                    if player.userip.settings.PROTECTION == "Restart_Process" and isinstance(player.userip.settings.PROTECTION_RESTART_PROCESS_PATH, Path):
                        subprocess.Popen([str(player.userip.settings.PROTECTION_RESTART_PROCESS_PATH.absolute())])

            elif player.userip.settings.PROTECTION in {"Shutdown_PC", "Restart_PC"}:
                validate_file(SHUTDOWN_EXE)

                subprocess.Popen([str(SHUTDOWN_EXE), "/s" if player.userip.settings.PROTECTION == "Shutdown_PC" else "/r"])

        if player.userip.settings.VOICE_NOTIFICATIONS:
            if player.userip.settings.VOICE_NOTIFICATIONS == "Male":
                voice_name = "Liam"
            elif player.userip.settings.VOICE_NOTIFICATIONS == "Female":
                voice_name = "Jane"
            else:
                voice_name = None

            if not isinstance(voice_name, str):
                raise TypeError(f'Expected "str" object, got "{type(voice_name).__name__}"')

            tts_file_path = TTS_PATH / f"{voice_name} ({connection_type}).wav"
            validate_file(tts_file_path)

            winsound.PlaySound(str(tts_file_path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)

        if connection_type == "connected":
            while not player.datetime.left and (datetime.now(tz=LOCAL_TZ) - player.datetime.last_seen) < timedelta(seconds=10):
                if player.userip.usernames and player.iplookup.geolite2.is_initialized:
                    break
                gui_closed__event.wait(0.1)
            else:
                return

            from modules.constants.standard import USERIP_DATABASES_PATH
            relative_database_path = player.userip.database_path.relative_to(USERIP_DATABASES_PATH).with_suffix("")

            with _userip_logging_file_write_lock:
                write_lines_to_file(USERIP_LOGGING_PATH, "a", [(
                    f"User{pluralize(len(player.userip.usernames))}:{', '.join(player.userip.usernames)} | "
                    f"IP:{player.ip} | Ports:{', '.join(map(str, reversed(player.ports.list)))} | "
                    f"Time:{player.userip_detection.date_time} | Country:{player.iplookup.geolite2.country} | "
                    f"Detection Type: {player.userip_detection.type} | "
                    f"Database:{relative_database_path}"
                )])

            if player.userip.settings.NOTIFICATIONS:
                while not player.datetime.left and (datetime.now(tz=LOCAL_TZ) - player.datetime.last_seen) < timedelta(seconds=10):
                    if player.iplookup.ipapi.is_initialized:
                        break
                    gui_closed__event.wait(0.1)
                else:
                    return

                msgbox_title = TITLE
                msgbox_message = textwrap.indent(textwrap.dedent(f"""
                    #### UserIP detected at {player.userip_detection.time} ####
                    User{pluralize(len(player.userip.usernames))}: {', '.join(player.userip.usernames)}
                    IP: {player.ip}
                    Port{pluralize(len(player.ports.list))}: {', '.join(map(str, reversed(player.ports.list)))}
                    Country Code: {player.iplookup.geolite2.country_code}
                    Detection Type: {player.userip_detection.type}
                    Database: {relative_database_path}
                    ############# IP Lookup ##############
                    Continent: {player.iplookup.ipapi.continent}
                    Country: {player.iplookup.geolite2.country}
                    Region: {player.iplookup.ipapi.region}
                    City: {player.iplookup.geolite2.city}
                    Organization: {player.iplookup.ipapi.org}
                    ISP: {player.iplookup.ipapi.isp}
                    ASN / ISP: {player.iplookup.geolite2.asn}
                    ASN: {player.iplookup.ipapi.as_name}
                    Mobile (cellular) connection: {player.iplookup.ipapi.mobile}
                    Proxy, VPN or Tor exit address: {player.iplookup.ipapi.proxy}
                    Hosting, colocated or data center: {player.iplookup.ipapi.hosting}
                """.removeprefix("\n").removesuffix("\n")), "    ")
                msgbox_style = MsgBox.Style.MB_OK | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SYSTEMMODAL
                threading.Thread(target=MsgBox.show, args=(msgbox_title, msgbox_message, msgbox_style), daemon=True).start()


def iplookup_core():
    with ThreadsExceptionHandler():
        def throttle_until(requests_remaining: int, throttle_time: int):
            # Calculate sleep time only if there are remaining requests
            sleep_time = throttle_time / requests_remaining if requests_remaining > 0 else throttle_time

            # We sleep x seconds (just in case) to avoid triggering a "429" status code.
            gui_closed__event.wait(sleep_time)

        # Following values taken from https://ip-api.com/docs/api:batch the 03/04/2024.
        #MAX_REQUESTS = 15
        #MAX_THROTTLE_TIME = 60
        MAX_BATCH_IP_API_IPS = 100
        FIELDS_TO_LOOKUP = "continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,mobile,proxy,hosting,query"

        def validate_and_get_iplookup_field(
            player_ip: str,
            iplookup: dict[str, Any],
            json_key: str,
            expected_types: tuple[type[Any], ...],
        ):
            """Retrieve a field from a dictionary and validate its type."""
            result = iplookup.get(json_key, "N/A")

            if result != "N/A" and not isinstance(result, expected_types):
                expected_names = " or ".join(t.__name__ for t in expected_types)
                raise TypeError(f'Expected "{expected_names}" for "{json_key}", got "{type(result).__name__}" ({player_ip})')

            return result

        while not gui_closed__event.is_set():
            if ScriptControl.has_crashed():
                return

            ips_to_lookup: list[str] = []

            for player in PlayersRegistry.get_sorted_players():
                if player.iplookup.ipapi.is_initialized:
                    continue

                ips_to_lookup.append(player.ip)

                if len(ips_to_lookup) == MAX_BATCH_IP_API_IPS:
                    break

            if not ips_to_lookup:
                gui_closed__event.wait(1)
                continue

            try:
                response = s.post(
                    f"http://ip-api.com/batch?fields={FIELDS_TO_LOOKUP}",
                    headers={"Content-Type": "application/json"},
                    json=ips_to_lookup,
                    timeout=3,
                )
                response.raise_for_status()
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                gui_closed__event.wait(1)
                continue
            except requests.exceptions.HTTPError as e:
                if isinstance(e.response, requests.Response) and e.response.status_code == requests.codes.too_many_requests:  # Handle rate limiting
                    throttle_until(int(e.response.headers["X-Rl"]), int(e.response.headers["X-Ttl"]))
                    continue
                raise  # Re-raise other HTTP errors

            iplookup_results: list[dict[str, Any]] = response.json()
            if not isinstance(iplookup_results, list):
                raise TypeError(f'Expected "list" object, got "{type(iplookup_results).__name__}"')

            for iplookup in iplookup_results:
                if not isinstance(iplookup, dict):
                    raise TypeError(f'Expected "dict" object, got "{type(iplookup).__name__}"')

                player_ip = iplookup.get("query")
                if not isinstance(player_ip, str):
                    raise TypeError(f'Expected "str" object, got "{type(player_ip).__name__}"')

                if player := PlayersRegistry.get_player(player_ip):
                    player.iplookup.ipapi.is_initialized = True

                    field_mappings: dict[str, tuple[str, tuple[type[Any], ...]]] = {
                        "continent": ("continent", (str,)),
                        "continent_code": ("continentCode", (str,)),
                        "country": ("country", (str,)),
                        "country_code": ("countryCode", (str,)),
                        "region": ("regionName", (str,)),
                        "region_code": ("region", (str,)),
                        "city": ("city", (str,)),
                        "district": ("district", (str,)),
                        "zip_code": ("zip", (str,)),
                        "lat": ("lat", (float, int)),
                        "lon": ("lon", (float, int)),
                        "time_zone": ("timezone", (str,)),
                        "offset": ("offset", (int,)),
                        "currency": ("currency", (str,)),
                        "isp": ("isp", (str,)),
                        "org": ("org", (str,)),
                        "asn": ("as", (str,)),
                        "as_name": ("asname", (str,)),
                        "mobile": ("mobile", (bool,)),
                        "proxy": ("proxy", (bool,)),
                        "hosting": ("hosting", (bool,)),
                    }

                    for attr, (json_key, expected_types) in field_mappings.items():
                        setattr(player.iplookup.ipapi, attr, validate_and_get_iplookup_field(player_ip, iplookup, json_key, expected_types))

            throttle_until(int(response.headers["X-Rl"]), int(response.headers["X-Ttl"]))


def hostname_core():
    with ThreadsExceptionHandler():
        from concurrent.futures import ThreadPoolExecutor, Future
        from modules.networking.reverse_dns import lookup as reverse_dns_lookup

        with ThreadPoolExecutor(max_workers=32) as executor:
            futures: dict[Future, str] = {}  # Maps futures to their corresponding IPs
            pending_ips: set[str] = set()   # Tracks IPs currently being processed

            while not gui_closed__event.is_set():
                if ScriptControl.has_crashed():
                    return

                for player in PlayersRegistry.get_sorted_players():
                    if player.reverse_dns.is_initialized or player.ip in pending_ips:
                        continue

                    future = executor.submit(reverse_dns_lookup, player.ip)
                    futures[future] = player.ip
                    pending_ips.add(player.ip)

                if not futures:
                    gui_closed__event.wait(1)
                    continue

                for future, ip in list(futures.items()):
                    if not future.done():
                        continue

                    futures.pop(future)

                    hostname: str = future.result()
                    if not isinstance(hostname, str):
                        raise TypeError(f'Expected "str" object, got "{type(hostname).__name__}"')

                    if player := PlayersRegistry.get_player(ip):
                        player.reverse_dns.is_initialized = True

                        player.reverse_dns.hostname = hostname

                gui_closed__event.wait(0.1)


def pinger_core():
    with ThreadsExceptionHandler():
        from concurrent.futures import ThreadPoolExecutor, Future
        from modules.networking.endpoint_ping_manager import AllEndpointsExhaustedError, PingResult, fetch_and_parse_ping

        with ThreadPoolExecutor(max_workers=32) as executor:
            futures: dict[Future, str] = {}  # Maps futures to their corresponding IPs
            pending_ips: set[str] = set()   # Tracks IPs currently being processed

            while not gui_closed__event.is_set():
                if ScriptControl.has_crashed():
                    return

                for player in PlayersRegistry.get_sorted_players():
                    if player.ping.is_initialized or player.ip in pending_ips:
                        continue

                    future = executor.submit(fetch_and_parse_ping, player.ip)
                    futures[future] = player.ip
                    pending_ips.add(player.ip)

                if not futures:
                    gui_closed__event.wait(1)
                    continue

                for future, ip in list(futures.items()):
                    if not future.done():
                        continue

                    futures.pop(future)
                    pending_ips.remove(ip)

                    try:
                        ping_result: PingResult | None = future.result()
                    except AllEndpointsExhaustedError:
                        continue

                    if ping_result is None:
                        continue

                    if not isinstance(ping_result, PingResult):
                        raise TypeError(f'Expected "PingResult" object, got "{type(ping_result).__name__}"')

                    if player := PlayersRegistry.get_player(ip):
                        player.ping.is_initialized = True
                        player.ping.is_pinging = ping_result.packets_received is not None and ping_result.packets_received > 0

                        player.ping.ping_times = ping_result.ping_times
                        player.ping.packets_transmitted = ping_result.packets_transmitted
                        player.ping.packets_received = ping_result.packets_received
                        player.ping.packet_loss = ping_result.packet_loss
                        player.ping.packet_errors = ping_result.packet_errors
                        player.ping.rtt_min = ping_result.rtt_min
                        player.ping.rtt_avg = ping_result.rtt_avg
                        player.ping.rtt_max = ping_result.rtt_max
                        player.ping.rtt_mdev = ping_result.rtt_mdev

                gui_closed__event.wait(0.1)


def capture_core():
    with ThreadsExceptionHandler():
        def packet_callback(packet: Packet):
            from modules.networking.utils import is_private_device_ipv4

            global tshark_restarted_times, global_pps_counter  # noqa: PLW0603

            packet_datetime = packet.frame.datetime

            packet_latency = datetime.now(tz=LOCAL_TZ) - packet_datetime
            tshark_packets_latencies.append((packet_datetime, packet_latency))
            if packet_latency >= timedelta(seconds=Settings.CAPTURE_OVERFLOW_TIMER):
                tshark_restarted_times += 1
                raise PacketCaptureOverflowError("Packet capture time exceeded 3 seconds.")

            if Settings.CAPTURE_IP_ADDRESS:
                if packet.ip.src == Settings.CAPTURE_IP_ADDRESS:
                    target_ip = packet.ip.dst
                    target_port = packet.udp.dstport
                elif packet.ip.dst == Settings.CAPTURE_IP_ADDRESS:
                    target_ip = packet.ip.src
                    target_port = packet.udp.srcport
                else:
                    return  # Neither source nor destination matches the specified `Settings.CAPTURE_IP_ADDRESS`.
            else:
                is_src_private_ip = is_private_device_ipv4(packet.ip.src)
                is_dst_private_ip = is_private_device_ipv4(packet.ip.dst)

                if is_src_private_ip and is_dst_private_ip:
                    return  # Both source and destination are private IPs, no action needed.

                if is_src_private_ip:
                    target_ip = packet.ip.dst
                    target_port = packet.udp.dstport
                elif is_dst_private_ip:
                    target_ip = packet.ip.src
                    target_port = packet.udp.srcport
                else:
                    return  # Neither source nor destination is a private IP address.

            global_pps_counter += 1

            if (player := PlayersRegistry.get_player(target_ip)) is None:
                player = PlayersRegistry.add_player(
                    Player(target_ip, target_port, packet_datetime),
                )

            if target_ip in UserIPDatabases.ips_set and (
                not player.userip_detection
                or not player.userip_detection.as_processed_task
            ):
                player.userip_detection = PlayerUserIPDetection(
                    time=packet_datetime.strftime("%H:%M:%S"),
                    date_time=packet_datetime.strftime("%Y-%m-%d_%H:%M:%S"),
                )
                threading.Thread(target=process_userip_task, args=(player, "connected"), daemon=True).start()

            if player.is_player_just_registered:
                player.is_player_just_registered = False
                return

            # No matter what:
            player.datetime.last_seen = packet_datetime
            player.total_packets += 1
            player.pps.counter += 1
            player.ppm.counter += 1

            if player.datetime.left:  # player left, rejoined now.
                player.datetime.left = None
                player.datetime.last_rejoin = packet_datetime
                player.rejoins += 1
                player.packets = 1

                if Settings.GUI_RESET_PORTS_ON_REJOINS:
                    player.ports.reset(target_port)
                    return
            else:
                player.packets += 1

            # player connected, has not been reset
            if target_port not in player.ports.list:
                player.ports.list.append(target_port)
            player.ports.last = target_port

        while not gui_closed__event.is_set():
            try:
                capture.apply_on_packets(callback=packet_callback)
            except TSharkCrashExceptionError:
                if gui_closed__event.wait(3):
                    break
                raise
            except PacketCaptureOverflowError:
                continue


tshark_packets_latencies: list[tuple[datetime, timedelta]] = []


class CellColor(NamedTuple):
    foreground: QColor
    background: QColor


class ThreadSafeMeta(type):
    """Metaclass that ensures thread-safe access to class attributes."""

    # Define a lock for the metaclass itself to be shared across all instances of classes using this metaclass.
    _lock = threading.Lock()

    def __getattr__(cls, name: str):
        """Thread-safe getter for attributes."""
        with cls._lock:
            if hasattr(cls, name):
                return getattr(cls, name)
            raise AttributeError(f"'{cls.__name__}' object has no attribute '{name}'")

    def __setattr__(cls, name: str, value: object):
        """Thread-safe setter for attributes."""
        with cls._lock:
            super().__setattr__(name, value)


class AbstractGUIRenderingData:
    FIELDS_TO_HIDE: set[str]
    GUI_CONNECTED_PLAYERS_TABLE__FIELD_NAMES: list[str]
    GUI_DISCONNECTED_PLAYERS_TABLE__FIELD_NAMES: list[str]

    header_text: str
    SESSION_CONNECTED_TABLE__NUM_COLS: int
    session_connected_table__num_rows: int
    session_connected_table__processed_data: list[list[str]]
    session_connected_table__compiled_colors: list[list[str]]
    SESSION_DISCONNECTED_TABLE__NUM_COLS: int
    session_disconnected_table__num_rows: int
    session_disconnected_table__processed_data: list[list[str]]
    session_disconnected_table__compiled_colors: list[list[str]]

    session_connected_sorted_column_name: str
    session_connected_sort_order: Qt.SortOrder
    session_disconnected_sorted_column_name: str
    session_disconnected_sort_order: Qt.SortOrder


class GUIrenderingData(AbstractGUIRenderingData, metaclass=ThreadSafeMeta):
    gui_rendering_ready_event: threading.Event = threading.Event()


def rendering_core():
    with ThreadsExceptionHandler():
        def compile_tables_header_field_names():
            gui_connected_players_table__field_names = [
                field_name
                for field_name in Settings.gui_all_connected_fields
                if field_name not in GUIrenderingData.FIELDS_TO_HIDE
            ]
            gui_disconnected_players_table__field_names = [
                field_name
                for field_name in Settings.gui_all_disconnected_fields
                if field_name not in GUIrenderingData.FIELDS_TO_HIDE
            ]
            logging_connected_players_table__field_names = list(Settings.gui_all_connected_fields)
            logging_disconnected_players_table__field_names = list(Settings.gui_all_disconnected_fields)

            return (
                gui_connected_players_table__field_names,
                gui_disconnected_players_table__field_names,
                logging_connected_players_table__field_names,
                logging_disconnected_players_table__field_names,
            )

        def sort_session_table(session_list: list[Player], sorted_column_name: str, sort_order: Qt.SortOrder):
            """Sort a list of players based on the given column name and sort order.

            Args:
                session_list: The list of players to sort.
                sorted_column_name: The column name to sort by.
                sort_order: The sort order ("ascending" or "descending").

            Returns:
                The sorted list of players.
            """

            def sort_order_to_reverse(sort_order: Qt.SortOrder):
                """Convert a Qt.SortOrder to a reverse parameter for sorted().

                Args:
                    sort_order: The sort order from Qt (Ascending or Descending).
                """
                return sort_order == Qt.SortOrder.DescendingOrder

            def get_nested_attr(item: object, attr_path: str):
                """Retrieve a nested attribute from an object using a dot-separated path."""
                for attr in attr_path.split("."):
                    item = getattr(item, attr, None)
                    if item is None:
                        break
                return item

            if sorted_column_name == "Avg PPS":
                return sorted(
                    session_list,
                    key=lambda player: player.pps.get_average(),
                    reverse=sort_order_to_reverse(sort_order),
                )
            if sorted_column_name == "Avg PPM":
                return sorted(
                    session_list,
                    key=lambda player: player.ppm.get_average(),
                    reverse=sort_order_to_reverse(sort_order),
                )
            if sorted_column_name == "IP Address":
                import ipaddress

                return sorted(
                    session_list,
                    key=lambda player: ipaddress.ip_address(player.ip),
                    reverse=sort_order_to_reverse(sort_order),
                )
            if sorted_column_name in {"First Seen", "Last Rejoin", "Last Seen"}:
                return sorted(
                    session_list,
                    key=attrgetter(Settings.gui_fields_mapping[sorted_column_name]),
                    reverse=not sort_order_to_reverse(sort_order),
                )
            # Force sorting those fields as strings as they contain both bools AND strings.
            if sorted_column_name in {"Mobile", "VPN", "Hosting", "Pinging"}:
                return sorted(
                    session_list,
                    key=lambda item: str(get_nested_attr(item, Settings.gui_fields_mapping[sorted_column_name])).casefold(),
                    reverse=not sort_order_to_reverse(sort_order),
                )
            # Handle sorting for other columns
            return sorted(
                session_list,
                key=attrgetter(Settings.gui_fields_mapping[sorted_column_name]),
                reverse=sort_order_to_reverse(sort_order),
            )

        def parse_userip_ini_file(ini_path: Path, unresolved_ip_invalid: set[str]):
            def process_ini_line_output(line: str):
                return line.strip()

            from modules.constants.standalone import USERIP_INI_SETTINGS
            from modules.constants.standard import RE_SETTINGS_INI_PARSER_PATTERN, RE_USERIP_INI_PARSER_PATTERN
            from modules.utils import InvalidBooleanValueError, InvalidNoneTypeValueError, NoMatchFoundError, custom_str_to_bool, custom_str_to_nonetype, check_case_insensitive_and_exact_match

            validate_file(ini_path)

            settings: dict[str, Any] = {}
            userip: dict[str, list[str]] = {}
            current_section = None
            matched_settings: list[str] = []
            ini_data = ini_path.read_text("utf-8")
            corrected_ini_data_lines: list[str] = []

            for line in map(process_ini_line_output, ini_data.splitlines(keepends=True)):
                corrected_ini_data_lines.append(line)

                if line.startswith("[") and line.endswith("]"):
                    # we basically adding a newline if the previous line is not a newline for eyes visiblitly or idk how we say that
                    if (
                        corrected_ini_data_lines
                        and len(corrected_ini_data_lines) > 1
                        and corrected_ini_data_lines[-2] != ""
                    ):
                        corrected_ini_data_lines.insert(-1, "")  # Insert an empty string before the last line
                    current_section = line[1:-1]
                    continue

                if current_section is None:
                    continue

                if current_section == "Settings":
                    match = RE_SETTINGS_INI_PARSER_PATTERN.search(line)
                    if not match:
                        # If it's a newline or a comment we don't really care about rewritting at this point.
                        if not line.startswith((";", "#")) or line == "":
                            corrected_ini_data_lines = corrected_ini_data_lines[:-1]
                        continue

                    setting = match.group("key")
                    if setting is None:
                        if corrected_ini_data_lines:
                            corrected_ini_data_lines = corrected_ini_data_lines[:-1]
                        continue
                    if not isinstance(setting, str):
                        raise TypeError(f'Expected "str" object, got "{type(setting).__name__}"')
                    value = match.group("value")
                    if value is None:
                        if corrected_ini_data_lines:
                            corrected_ini_data_lines = corrected_ini_data_lines[:-1]
                        continue
                    if not isinstance(value, str):
                        raise TypeError(f'Expected "str" object, got "{type(value).__name__}"')

                    setting = setting.strip()
                    if not setting:
                        if corrected_ini_data_lines:
                            corrected_ini_data_lines = corrected_ini_data_lines[:-1]
                        continue
                    value = value.strip()
                    if not value:
                        if corrected_ini_data_lines:
                            corrected_ini_data_lines = corrected_ini_data_lines[:-1]
                        continue

                    if setting not in USERIP_INI_SETTINGS:
                        if corrected_ini_data_lines:
                            corrected_ini_data_lines = corrected_ini_data_lines[:-1]
                        continue

                    if setting in settings:
                        if corrected_ini_data_lines:
                            corrected_ini_data_lines = corrected_ini_data_lines[:-1]
                        continue

                    matched_settings.append(setting)
                    need_rewrite_current_setting = False
                    is_setting_corrupted = False

                    if setting == "ENABLED":
                        try:
                            settings[setting], need_rewrite_current_setting = custom_str_to_bool(value)
                        except InvalidBooleanValueError:
                            is_setting_corrupted = True
                    elif setting == "COLOR":
                        if (q_color := QColor(value)).isValid():
                            settings[setting] = q_color
                        else:
                            is_setting_corrupted = True
                    elif setting in {"LOG", "NOTIFICATIONS"}:
                        try:
                            settings[setting], need_rewrite_current_setting = custom_str_to_bool(value)
                        except InvalidBooleanValueError:
                            is_setting_corrupted = True
                    elif setting == "VOICE_NOTIFICATIONS":
                        try:
                            settings[setting], need_rewrite_current_setting = custom_str_to_bool(value, only_match_against=False)
                        except InvalidBooleanValueError:
                            try:
                                case_sensitive_match, normalized_match = check_case_insensitive_and_exact_match(value, ["Male", "Female"])
                                settings[setting] = normalized_match
                                if not case_sensitive_match:
                                    need_rewrite_current_setting = True
                            except NoMatchFoundError:
                                is_setting_corrupted = True
                    elif setting == "PROTECTION":
                        try:
                            settings[setting], need_rewrite_current_setting = custom_str_to_bool(value, only_match_against=False)
                        except InvalidBooleanValueError:
                            try:
                                case_sensitive_match, normalized_match = check_case_insensitive_and_exact_match(value, ["Suspend_Process", "Exit_Process", "Restart_Process", "Shutdown_PC", "Restart_PC"])
                                settings[setting] = normalized_match
                                if not case_sensitive_match:
                                    need_rewrite_current_setting = True
                            except NoMatchFoundError:
                                is_setting_corrupted = True
                    elif setting in {"PROTECTION_PROCESS_PATH", "PROTECTION_RESTART_PROCESS_PATH"}:
                        try:
                            settings[setting], need_rewrite_current_setting = custom_str_to_nonetype(value)
                        except InvalidNoneTypeValueError:
                            stripped_value = value.strip("\"'")
                            if value != stripped_value:
                                is_setting_corrupted = True
                            settings[setting] = Path(stripped_value)
                    elif setting == "PROTECTION_SUSPEND_PROCESS_MODE":
                        try:
                            case_sensitive_match, normalized_match = check_case_insensitive_and_exact_match(value, ["Auto", "Manual"])
                            settings[setting] = normalized_match
                            if not case_sensitive_match:
                                need_rewrite_current_setting = True
                        except NoMatchFoundError:
                            try:
                                if "." in value:
                                    protection_suspend_process_mode = float(value)
                                else:
                                    protection_suspend_process_mode = int(value)
                            except (ValueError, TypeError):
                                is_setting_corrupted = True
                            else:
                                if protection_suspend_process_mode >= 0:
                                    settings[setting] = protection_suspend_process_mode
                                else:
                                    is_setting_corrupted = True

                    if is_setting_corrupted:
                        if ini_path not in UserIPDatabases.notified_settings_corrupted:
                            UserIPDatabases.notified_settings_corrupted.add(ini_path)
                            msgbox_title = TITLE
                            msgbox_message = textwrap.indent(textwrap.dedent(f"""
                                ERROR:
                                    Corrupted UserIP Database File (Settings)

                                INFOS:
                                    UserIP database file:
                                    \"{ini_path}\"
                                    has an invalid settings value:

                                    {setting}={value}

                                    For more information on formatting, please refer to the
                                    documentation:
                                    https://github.com/BUZZARDGTA/Session-Sniffer?tab=readme-ov-file#userip_ini_databases_tutorial
                            """.removeprefix("\n").removesuffix("\n")), "    ")
                            msgbox_style = MsgBox.Style.MB_OK | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SETFOREGROUND
                            threading.Thread(target=MsgBox.show, args=(msgbox_title, msgbox_message, msgbox_style), daemon=True).start()
                        return None, None

                    if need_rewrite_current_setting:
                        corrected_ini_data_lines[-1] = f"{setting}={settings[setting]}"

                elif current_section == "UserIP":
                    match = RE_USERIP_INI_PARSER_PATTERN.search(line)
                    if not match:
                        continue
                    username = match.group("username")
                    if username is None:
                        continue
                    if not isinstance(username, str):
                        raise TypeError(f'Expected "str" object, got "{type(username).__name__}"')
                    ip = match.group("ip")
                    if ip is None:
                        continue
                    if not isinstance(ip, str):
                        raise TypeError(f'Expected "str" object, got "{type(ip).__name__}"')

                    username = username.strip()
                    if not username:
                        continue
                    ip = ip.strip()
                    if not ip:
                        continue

                    if not is_ipv4_address(ip):
                        unresolved_ip_invalid.add(f"{ini_path}={username}={ip}")
                        if f"{ini_path}={username}={ip}" not in UserIPDatabases.notified_ip_invalid:
                            msgbox_title = TITLE
                            msgbox_message = textwrap.indent(textwrap.dedent(f"""
                                ERROR:
                                    UserIP databases invalid IP address

                                INFOS:
                                    The IP address from an entry is invalid (not an IP address).

                                DEBUG:
                                    \"{ini_path}\":
                                    {username}={ip}
                            """.removeprefix("\n").removesuffix("\n")), "    ")
                            msgbox_style = MsgBox.Style.MB_OK | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SYSTEMMODAL
                            threading.Thread(target=MsgBox.show, args=(msgbox_title, msgbox_message, msgbox_style), daemon=True).start()
                            UserIPDatabases.notified_ip_invalid.add(f"{ini_path}={username}={ip}")
                        continue

                    if username in userip:
                        if ip not in userip[username]:
                            userip[username].append(ip)
                    else:
                        userip[username] = [ip]

            list_of_missing_settings = [setting for setting in USERIP_INI_SETTINGS if setting not in matched_settings]
            number_of_settings_missing = len(list_of_missing_settings)

            if number_of_settings_missing > 0:
                if ini_path not in UserIPDatabases.notified_settings_corrupted:
                    UserIPDatabases.notified_settings_corrupted.add(ini_path)
                    msgbox_title = TITLE
                    msgbox_message = textwrap.indent(textwrap.dedent(f"""
                        ERROR:
                            Missing setting{pluralize(number_of_settings_missing)} in UserIP Database File

                        INFOS:
                            {number_of_settings_missing} missing setting{pluralize(number_of_settings_missing)} in UserIP database file:
                            \"{ini_path}\"

                            {"\n                ".join(f"<{setting.upper()}>" for setting in list_of_missing_settings)}

                            For more information on formatting, please refer to the
                            documentation:
                            https://github.com/BUZZARDGTA/Session-Sniffer?tab=readme-ov-file#userip_ini_databases_tutorial
                    """.removeprefix("\n").removesuffix("\n")), "    ")
                    msgbox_style = MsgBox.Style.MB_OK | MsgBox.Style.MB_ICONEXCLAMATION | MsgBox.Style.MB_SETFOREGROUND
                    threading.Thread(target=MsgBox.show, args=(msgbox_title, msgbox_message, msgbox_style), daemon=True).start()
                return None, None

            if ini_path in UserIPDatabases.notified_settings_corrupted:
                UserIPDatabases.notified_settings_corrupted.remove(ini_path)

            # Basically always have a newline ending
            if (
                len(corrected_ini_data_lines) > 1
                and corrected_ini_data_lines[-1] != ""
            ):
                corrected_ini_data_lines.append("")

            fixed_ini_data = "\n".join(corrected_ini_data_lines)

            if ini_data != fixed_ini_data:
                ini_path.write_text(fixed_ini_data, encoding="utf-8")

            return UserIPSettings(
                settings["ENABLED"],
                settings["COLOR"],
                settings["LOG"],
                settings["NOTIFICATIONS"],
                settings["VOICE_NOTIFICATIONS"],
                settings["PROTECTION"],
                settings["PROTECTION_PROCESS_PATH"],
                settings["PROTECTION_RESTART_PROCESS_PATH"],
                settings["PROTECTION_SUSPEND_PROCESS_MODE"],
            ), userip

        def update_userip_databases():
            from modules.constants.standard import USERIP_DATABASES_PATH

            DEFAULT_USERIP_FILE_HEADER = textwrap.dedent(f"""
                ;;-----------------------------------------------------------------------------
                ;; {TITLE} User IP default database file
                ;;-----------------------------------------------------------------------------
                ;; Lines starting with \";\" or \"#\" symbols are commented lines.
                ;;
                ;; For detailed explanations of each setting, please refer to the following documentation:
                ;; https://github.com/BUZZARDGTA/Session-Sniffer/?tab=readme-ov-file#editing-settings
                ;;-----------------------------------------------------------------------------
                [Settings]
            """.removeprefix("\n").removesuffix("\n"))

            DEFAULT_USERIP_FILES_SETTINGS = {
                USERIP_DATABASES_PATH / "Blacklist.ini": """
                    ENABLED=True
                    COLOR=RED
                    LOG=True
                    NOTIFICATIONS=True
                    VOICE_NOTIFICATIONS=Male
                    PROTECTION=False
                    PROTECTION_PROCESS_PATH=None
                    PROTECTION_RESTART_PROCESS_PATH=None
                    PROTECTION_SUSPEND_PROCESS_MODE=Auto
                """,
                USERIP_DATABASES_PATH / "Enemylist.ini": """
                    ENABLED=True
                    COLOR=DARKGOLDENROD
                    LOG=True
                    NOTIFICATIONS=True
                    VOICE_NOTIFICATIONS=Male
                    PROTECTION=False
                    PROTECTION_PROCESS_PATH=None
                    PROTECTION_RESTART_PROCESS_PATH=None
                    PROTECTION_SUSPEND_PROCESS_MODE=Auto
                """,
                USERIP_DATABASES_PATH / "Friendlist.ini": """
                    ENABLED=True
                    COLOR=GREEN
                    LOG=True
                    NOTIFICATIONS=False
                    VOICE_NOTIFICATIONS=Female
                    PROTECTION=False
                    PROTECTION_PROCESS_PATH=None
                    PROTECTION_RESTART_PROCESS_PATH=None
                    PROTECTION_SUSPEND_PROCESS_MODE=Auto
                """,
                USERIP_DATABASES_PATH / "Randomlist.ini": """
                    ENABLED=True
                    COLOR=BLACK
                    LOG=True
                    NOTIFICATIONS=False
                    VOICE_NOTIFICATIONS=Female
                    PROTECTION=False
                    PROTECTION_PROCESS_PATH=None
                    PROTECTION_RESTART_PROCESS_PATH=None
                    PROTECTION_SUSPEND_PROCESS_MODE=Auto
                """,
                USERIP_DATABASES_PATH / "Searchlist.ini": """
                    ENABLED=True
                    COLOR=BLUE
                    LOG=True
                    NOTIFICATIONS=False
                    VOICE_NOTIFICATIONS=Female
                    PROTECTION=False
                    PROTECTION_PROCESS_PATH=None
                    PROTECTION_RESTART_PROCESS_PATH=None
                    PROTECTION_SUSPEND_PROCESS_MODE=Auto
                """,
            }

            DEFAULT_USERIP_FILE_FOOTER = textwrap.dedent("""
                [UserIP]
                # Add users below in this format: username=IP
                # Examples:
                # username1=192.168.1.1
                # username2=127.0.0.1
                # username3=255.255.255.255
            """.removeprefix("\n"))

            USERIP_DATABASES_PATH.mkdir(parents=True, exist_ok=True)

            for userip_path, settings in DEFAULT_USERIP_FILES_SETTINGS.items():
                if not userip_path.is_file():
                    file_content = f"{DEFAULT_USERIP_FILE_HEADER}\n\n{settings}\n\n{DEFAULT_USERIP_FILE_FOOTER}"
                    userip_path.write_text(file_content, encoding="utf-8")

            # Remove deleted files from notified settings conflicts
            # TODO(BUZZARDGTA): I should also warn again on another error, but it'd probably require a DICT then.
            for file_path in set(UserIPDatabases.notified_settings_corrupted):
                if not file_path.is_file():
                    UserIPDatabases.notified_settings_corrupted.remove(file_path)

            new_databases: list[tuple[Path, UserIPSettings, dict[str, list[str]]]] = []
            unresolved_ip_invalid: set[str] = set()

            for userip_path in USERIP_DATABASES_PATH.rglob("*.ini"):
                parsed_settings, parsed_data = parse_userip_ini_file(userip_path, unresolved_ip_invalid)
                if None in (parsed_settings, parsed_data):
                    continue
                new_databases.append((userip_path, parsed_settings, parsed_data))

            UserIPDatabases.populate(new_databases)

            resolved_ip_invalids = UserIPDatabases.notified_ip_invalid - unresolved_ip_invalid
            for resolved_database_entry in resolved_ip_invalids:
                UserIPDatabases.notified_ip_invalid.remove(resolved_database_entry)

            UserIPDatabases.build()

            return time.monotonic()

        def get_country_info(ip_address: str):
            country_name = "N/A"
            country_code = "N/A"

            if geoip2_enabled:
                try:
                    response = geolite2_country_reader.country(ip_address)
                except geoip2.errors.AddressNotFoundError:
                    pass
                else:
                    country_name = str(response.country.name)
                    country_code = str(response.country.iso_code)

            return country_name, country_code

        def get_city_info(ip_address: str):
            city = "N/A"

            if geoip2_enabled:
                try:
                    response = geolite2_city_reader.city(ip_address)
                except geoip2.errors.AddressNotFoundError:
                    pass
                else:
                    city = str(response.city.name)

            return city

        def get_asn_info(ip_address: str):
            asn = "N/A"

            if geoip2_enabled:
                try:
                    response = geolite2_asn_reader.asn(ip_address)
                except geoip2.errors.AddressNotFoundError:
                    pass
                else:
                    asn = str(response.autonomous_system_organization)

            return asn

        def get_minimum_padding(var: str | float | bool, max_padding: int, padding: int):
            current_padding = len(str(var))

            if current_padding <= padding:
                max_padding = max(max_padding, current_padding)

            return max_padding

        def process_session_logging():
            def format_player_logging_datetime(datetime_object: datetime):
                return datetime_object.strftime("%m/%d/%Y %H:%M:%S.%f")[:-3]

            def format_player_logging_usernames(player_usernames: list[str]):
                return ", ".join(player_usernames) if player_usernames else "N/A"

            def format_player_logging_ip(player_ip: str):
                if SessionHost.player and SessionHost.player.ip == player_ip:
                    return f"{player_ip} 👑"
                return player_ip

            def format_player_logging_intermediate_ports(player_ports: PlayerPorts):
                player_ports.intermediate = [port for port in reversed(player_ports.list) if port not in {player_ports.first, player_ports.last}]
                if player_ports.intermediate:
                    return ", ".join(map(str, player_ports.intermediate))
                return ""

            def add_sort_arrow_char_to_sorted_logging_table_field(field_names: list[str], sorted_field: str, sort_order: Qt.SortOrder):
                arrow = " \u2193" if sort_order == Qt.SortOrder.DescendingOrder else " \u2191"  # Down arrow for descending, up arrow for ascending
                return [
                    field + arrow if field == sorted_field else field
                    for field in field_names
                ]

            logging_connected_players__field_names__with_down_arrow = add_sort_arrow_char_to_sorted_logging_table_field(LOGGING_CONNECTED_PLAYERS_TABLE__FIELD_NAMES, GUIrenderingData.session_connected_sorted_column_name, GUIrenderingData.session_connected_sort_order)
            logging_disconnected_players__field_names__with_down_arrow = add_sort_arrow_char_to_sorted_logging_table_field(LOGGING_DISCONNECTED_PLAYERS_TABLE__FIELD_NAMES, GUIrenderingData.session_disconnected_sorted_column_name, GUIrenderingData.session_disconnected_sort_order)
            row_texts: list[str] = []

            logging_connected_players_table = PrettyTable()
            logging_connected_players_table.set_style(TableStyle.SINGLE_BORDER)
            logging_connected_players_table.title = f"Player{pluralize(len(session_connected_sorted))} connected in your session ({len(session_connected_sorted)}):"
            logging_connected_players_table.field_names = logging_connected_players__field_names__with_down_arrow
            logging_connected_players_table.align = "l"
            for player in session_connected_sorted:
                row_texts = []
                row_texts.append(f"{format_player_logging_usernames(player.usernames)}")
                row_texts.append(f"{format_player_logging_datetime(player.datetime.first_seen)}")
                row_texts.append(f"{format_player_logging_datetime(player.datetime.last_rejoin)}")
                row_texts.append(f"{player.rejoins}")
                row_texts.append(f"{player.total_packets}")
                row_texts.append(f"{player.packets}")
                row_texts.append(f"{player.pps.rate}")
                row_texts.append(f"{player.pps.get_average()}")
                row_texts.append(f"{player.ppm.rate}")
                row_texts.append(f"{player.ppm.get_average()}")
                row_texts.append(f"{format_player_logging_ip(player.ip)}")
                row_texts.append(f"{player.reverse_dns.hostname}")
                row_texts.append(f"{player.ports.last}")
                row_texts.append(f"{format_player_logging_intermediate_ports(player.ports)}")
                row_texts.append(f"{player.ports.first}")
                row_texts.append(f"{player.iplookup.ipapi.continent:<{session_connected__padding_continent_name}} ({player.iplookup.ipapi.continent_code})")
                row_texts.append(f"{player.iplookup.geolite2.country:<{session_connected__padding_country_name}} ({player.iplookup.geolite2.country_code})")
                row_texts.append(f"{player.iplookup.ipapi.region}")
                row_texts.append(f"{player.iplookup.ipapi.region_code}")
                row_texts.append(f"{player.iplookup.geolite2.city}")
                row_texts.append(f"{player.iplookup.ipapi.district}")
                row_texts.append(f"{player.iplookup.ipapi.zip_code}")
                row_texts.append(f"{player.iplookup.ipapi.lat}")
                row_texts.append(f"{player.iplookup.ipapi.lon}")
                row_texts.append(f"{player.iplookup.ipapi.time_zone}")
                row_texts.append(f"{player.iplookup.ipapi.offset}")
                row_texts.append(f"{player.iplookup.ipapi.currency}")
                row_texts.append(f"{player.iplookup.ipapi.org}")
                row_texts.append(f"{player.iplookup.ipapi.isp}")
                row_texts.append(f"{player.iplookup.geolite2.asn}")
                row_texts.append(f"{player.iplookup.ipapi.asn}")
                row_texts.append(f"{player.iplookup.ipapi.as_name}")
                row_texts.append(f"{player.iplookup.ipapi.mobile}")
                row_texts.append(f"{player.iplookup.ipapi.proxy}")
                row_texts.append(f"{player.iplookup.ipapi.hosting}")
                row_texts.append(f"{player.ping.is_pinging}")
                logging_connected_players_table.add_row(row_texts)

            logging_disconnected_players_table = PrettyTable()
            logging_disconnected_players_table.set_style(TableStyle.SINGLE_BORDER)
            logging_disconnected_players_table.title = f"Player{pluralize(len(session_disconnected_sorted))} who've left your session ({len(session_disconnected_sorted)}):"
            logging_disconnected_players_table.field_names = logging_disconnected_players__field_names__with_down_arrow
            logging_disconnected_players_table.align = "l"
            for player in session_disconnected_sorted:
                row_texts = []
                row_texts.append(f"{format_player_logging_usernames(player.usernames)}")
                row_texts.append(f"{format_player_logging_datetime(player.datetime.first_seen)}")
                row_texts.append(f"{format_player_logging_datetime(player.datetime.last_rejoin)}")
                row_texts.append(f"{format_player_logging_datetime(player.datetime.last_seen)}")
                row_texts.append(f"{player.rejoins}")
                row_texts.append(f"{player.total_packets}")
                row_texts.append(f"{player.packets}")
                row_texts.append(f"{player.ip}")
                row_texts.append(f"{player.reverse_dns.hostname}")
                row_texts.append(f"{player.ports.last}")
                row_texts.append(f"{format_player_logging_intermediate_ports(player.ports)}")
                row_texts.append(f"{player.ports.first}")
                row_texts.append(f"{player.iplookup.ipapi.continent:<{session_disconnected__padding_continent_name}} ({player.iplookup.ipapi.continent_code})")
                row_texts.append(f"{player.iplookup.geolite2.country:<{session_disconnected__padding_country_name}} ({player.iplookup.geolite2.country_code})")
                row_texts.append(f"{player.iplookup.ipapi.region}")
                row_texts.append(f"{player.iplookup.ipapi.region_code}")
                row_texts.append(f"{player.iplookup.geolite2.city}")
                row_texts.append(f"{player.iplookup.ipapi.district}")
                row_texts.append(f"{player.iplookup.ipapi.zip_code}")
                row_texts.append(f"{player.iplookup.ipapi.lat}")
                row_texts.append(f"{player.iplookup.ipapi.lon}")
                row_texts.append(f"{player.iplookup.ipapi.time_zone}")
                row_texts.append(f"{player.iplookup.ipapi.offset}")
                row_texts.append(f"{player.iplookup.ipapi.currency}")
                row_texts.append(f"{player.iplookup.ipapi.org}")
                row_texts.append(f"{player.iplookup.ipapi.isp}")
                row_texts.append(f"{player.iplookup.geolite2.asn}")
                row_texts.append(f"{player.iplookup.ipapi.asn}")
                row_texts.append(f"{player.iplookup.ipapi.as_name}")
                row_texts.append(f"{player.iplookup.ipapi.mobile}")
                row_texts.append(f"{player.iplookup.ipapi.proxy}")
                row_texts.append(f"{player.iplookup.ipapi.hosting}")
                row_texts.append(f"{player.ping.is_pinging}")
                logging_disconnected_players_table.add_row(row_texts)

            from modules.constants.standard import SESSIONS_LOGGING_PATH

            # Check if the directories exist, if not create them
            if not SESSIONS_LOGGING_PATH.parent.is_dir():
                SESSIONS_LOGGING_PATH.parent.mkdir(parents=True)  # Create the directories if they don't exist

            # Check if the file exists, if not create it
            if not SESSIONS_LOGGING_PATH.is_file():
                SESSIONS_LOGGING_PATH.touch()  # Create the file if it doesn't exist

            SESSIONS_LOGGING_PATH.write_text(logging_connected_players_table.get_string() + "\n" + logging_disconnected_players_table.get_string(), encoding="utf-8")

        def process_gui_session_tables_rendering():
            def format_player_gui_datetime(datetime_object: datetime):
                formatted_elapsed = None

                if Settings.GUI_DATE_FIELDS_SHOW_ELAPSED:
                    elapsed_time = datetime.now(tz=LOCAL_TZ) - datetime_object

                    hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
                    minutes, remainder = divmod(remainder, 60)
                    seconds, milliseconds = divmod(remainder * 1000, 1000)

                    elapsed_parts: list[str] = []
                    if hours >= 1:
                        elapsed_parts.append(f"{int(hours):02}h")
                    if elapsed_parts or minutes >= 1:
                        elapsed_parts.append(f"{int(minutes):02}m")
                    if elapsed_parts or seconds >= 1:
                        elapsed_parts.append(f"{int(seconds):02}s")
                    if not elapsed_parts and milliseconds > 0:
                        elapsed_parts.append(f"{int(milliseconds):03}ms")

                    formatted_elapsed = " ".join(elapsed_parts)

                    if Settings.GUI_DATE_FIELDS_SHOW_DATE is False and Settings.GUI_DATE_FIELDS_SHOW_TIME is False:
                        return formatted_elapsed

                parts: list[str] = []
                if Settings.GUI_DATE_FIELDS_SHOW_DATE:
                    parts.append(datetime_object.strftime("%m/%d/%Y"))
                if Settings.GUI_DATE_FIELDS_SHOW_TIME:
                    parts.append(datetime_object.strftime("%H:%M:%S.%f")[:-3])
                if not parts:
                    raise ValueError("Invalid settings: Both date and time are disabled.")

                formatted_datetime = " ".join(parts)

                if formatted_elapsed:
                    formatted_datetime += f" ({formatted_elapsed})"

                return formatted_datetime

            def format_player_gui_usernames(player_usernames: list[str]):
                return ", ".join(player_usernames) if player_usernames else "N/A"

            def format_player_gui_ip(player_ip: str):
                if SessionHost.player and SessionHost.player.ip == player_ip:
                    return f"{player_ip} 👑"
                return player_ip

            def format_player_gui_intermediate_ports(player_ports: PlayerPorts):
                player_ports.intermediate = [port for port in reversed(player_ports.list) if port not in {player_ports.first, player_ports.last}]
                if player_ports.intermediate:
                    return ", ".join(map(str, player_ports.intermediate))
                return ""

            def get_player_rate_color(color: QColor, rate: int, *, is_first_calculation: bool):
                """Determine the color for player rates based on given thresholds."""
                from modules.constants.standalone import RATE_ZERO, RATE_LOW, RATE_MAX

                if not is_first_calculation:
                    if rate == RATE_ZERO:
                        return QColor("red")
                    if RATE_LOW <= rate <= RATE_MAX:
                        return QColor("yellow")
                return color

            from modules.constants.external import HARDCODED_DEFAULT_TABLE_BACKGROUND_CELL_COLOR

            row_texts: list[str] = []
            session_connected_table__processed_data: list[list[str]] = []
            session_connected_table__compiled_colors: list[list[CellColor]] = []
            session_disconnected_table__processed_data: list[list[str]] = []
            session_disconnected_table__compiled_colors: list[list[CellColor]] = []

            for player in session_connected_sorted:
                if player.userip and player.userip.usernames:
                    row_fg_color = QColor("white")
                    row_bg_color = player.userip.settings.COLOR
                else:
                    row_fg_color = QColor("lime")
                    row_bg_color = HARDCODED_DEFAULT_TABLE_BACKGROUND_CELL_COLOR

                # Initialize a list for cell colors for the current row, creating a new CellColor object for each column
                row_colors = [
                    CellColor(foreground=row_fg_color, background=row_bg_color)
                    for _ in range(GUIrenderingData.SESSION_CONNECTED_TABLE__NUM_COLS)
                ]

                row_texts = []
                row_texts.append(f"{format_player_gui_usernames(player.usernames)}")
                row_texts.append(f"{format_player_gui_datetime(player.datetime.first_seen)}")
                row_texts.append(f"{format_player_gui_datetime(player.datetime.last_rejoin)}")
                row_texts.append(f"{player.rejoins}")
                row_texts.append(f"{player.total_packets}")
                row_texts.append(f"{player.packets}")
                if "PPS" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_colors[CONNECTED_COLUMN_MAPPING["PPS"]] = row_colors[CONNECTED_COLUMN_MAPPING["PPS"]]._replace(foreground=get_player_rate_color(row_fg_color, player.pps.rate, is_first_calculation=player.pps.is_first_calculation))
                    row_texts.append(f"{player.pps.rate}")
                if "Avg PPS" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_colors[CONNECTED_COLUMN_MAPPING["Avg PPS"]] = row_colors[CONNECTED_COLUMN_MAPPING["Avg PPS"]]._replace(foreground=get_player_rate_color(row_fg_color, player.pps.rate, is_first_calculation=player.pps.is_first_calculation))
                    row_texts.append(f"{player.pps.get_average()}")
                if "PPM" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_colors[CONNECTED_COLUMN_MAPPING["PPM"]] = row_colors[CONNECTED_COLUMN_MAPPING["PPM"]]._replace(foreground=get_player_rate_color(row_fg_color, player.ppm.rate, is_first_calculation=player.ppm.is_first_calculation))
                    row_texts.append(f"{player.ppm.rate}")
                if "Avg PPM" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_colors[CONNECTED_COLUMN_MAPPING["Avg PPM"]] = row_colors[CONNECTED_COLUMN_MAPPING["Avg PPM"]]._replace(foreground=get_player_rate_color(row_fg_color, player.ppm.rate, is_first_calculation=player.ppm.is_first_calculation))
                    row_texts.append(f"{player.ppm.get_average()}")
                row_texts.append(f"{format_player_gui_ip(player.ip)}")
                if "Hostname" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.reverse_dns.hostname}")
                if "Last Port" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.ports.last}")
                if "Intermediate Ports" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{format_player_gui_intermediate_ports(player.ports)}")
                if "First Port" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.ports.first}")
                if "Continent" not in GUIrenderingData.FIELDS_TO_HIDE:
                    if Settings.GUI_FIELD_SHOW_CONTINENT_CODE:
                        row_texts.append(f"{player.iplookup.ipapi.continent} ({player.iplookup.ipapi.continent_code})")
                    else:
                        row_texts.append(f"{player.iplookup.ipapi.continent}")
                if "Country" not in GUIrenderingData.FIELDS_TO_HIDE:
                    if Settings.GUI_FIELD_SHOW_COUNTRY_CODE:
                        row_texts.append(f"{player.iplookup.geolite2.country} ({player.iplookup.geolite2.country_code})")
                    else:
                        row_texts.append(f"{player.iplookup.geolite2.country}")
                if "Region" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.region}")
                if "R. Code" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.region_code}")
                if "City" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.geolite2.city}")
                if "District" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.district}")
                if "ZIP Code" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.zip_code}")
                if "Lat" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.lat}")
                if "Lon" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.lon}")
                if "Time Zone" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.time_zone}")
                if "Offset" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.offset}")
                if "Currency" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.currency}")
                if "Organization" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.org}")
                if "ISP" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.isp}")
                if "ASN / ISP" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.geolite2.asn}")
                if "AS" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.asn}")
                if "ASN" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.as_name}")
                if "Mobile" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.mobile}")
                if "VPN" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.proxy}")
                if "Hosting" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.hosting}")
                if "Pinging" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.ping.is_pinging}")

                session_connected_table__processed_data.append(row_texts)
                session_connected_table__compiled_colors.append(row_colors)

            for player in session_disconnected_sorted:
                if player.userip and player.userip.usernames:
                    row_fg_color = QColor("white")
                    row_bg_color = player.userip.settings.COLOR
                else:
                    row_fg_color = QColor("red")
                    row_bg_color = HARDCODED_DEFAULT_TABLE_BACKGROUND_CELL_COLOR

                # Initialize a list for cell colors for the current row, creating a new CellColor object for each column
                row_colors = [CellColor(foreground=row_fg_color, background=row_bg_color) for _ in range(GUIrenderingData.SESSION_DISCONNECTED_TABLE__NUM_COLS)]

                row_texts = []
                row_texts.append(f"{format_player_gui_usernames(player.usernames)}")
                row_texts.append(f"{format_player_gui_datetime(player.datetime.first_seen)}")
                row_texts.append(f"{format_player_gui_datetime(player.datetime.last_rejoin)}")
                row_texts.append(f"{format_player_gui_datetime(player.datetime.last_seen)}")
                row_texts.append(f"{player.rejoins}")
                row_texts.append(f"{player.total_packets}")
                row_texts.append(f"{player.packets}")
                row_texts.append(f"{player.ip}")
                if "Hostname" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.reverse_dns.hostname}")
                if "Last Port" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.ports.last}")
                if "Intermediate Ports" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{format_player_gui_intermediate_ports(player.ports)}")
                if "First Port" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.ports.first}")
                if "Continent" not in GUIrenderingData.FIELDS_TO_HIDE:
                    if Settings.GUI_FIELD_SHOW_CONTINENT_CODE:
                        row_texts.append(f"{player.iplookup.ipapi.continent} ({player.iplookup.ipapi.continent_code})")
                    else:
                        row_texts.append(f"{player.iplookup.ipapi.continent}")
                if "Country" not in GUIrenderingData.FIELDS_TO_HIDE:
                    if Settings.GUI_FIELD_SHOW_COUNTRY_CODE:
                        row_texts.append(f"{player.iplookup.geolite2.country} ({player.iplookup.geolite2.country_code})")
                    else:
                        row_texts.append(f"{player.iplookup.geolite2.country}")
                if "Region" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.region}")
                if "R. Code" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.region_code}")
                if "City" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.geolite2.city}")
                if "District" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.district}")
                if "ZIP Code" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.zip_code}")
                if "Lat" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.lat}")
                if "Lon" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.lon}")
                if "Time Zone" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.time_zone}")
                if "Offset" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.offset}")
                if "Currency" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.currency}")
                if "Organization" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.org}")
                if "ISP" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.isp}")
                if "ASN / ISP" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.geolite2.asn}")
                if "AS" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.asn}")
                if "ASN" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.as_name}")
                if "Mobile" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.mobile}")
                if "VPN" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.proxy}")
                if "Hosting" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.iplookup.ipapi.hosting}")
                if "Pinging" not in GUIrenderingData.FIELDS_TO_HIDE:
                    row_texts.append(f"{player.ping.is_pinging}")

                session_disconnected_table__processed_data.append(row_texts)
                session_disconnected_table__compiled_colors.append(row_colors)

            return (
                len(session_connected_table__processed_data),
                session_connected_table__processed_data,
                session_connected_table__compiled_colors,
                len(session_disconnected_table__processed_data),
                session_disconnected_table__processed_data,
                session_disconnected_table__compiled_colors,
            )

        def generate_gui_header_text(global_pps_last_update_time: float, global_pps_rate: int):
            global global_pps_counter  # noqa: PLW0603

            from modules.constants.standalone import PPS_THRESHOLD_WARNING, PPS_THRESHOLD_CRITICAL

            if capture.extracted_tshark_version == TSHARK_RECOMMENDED_VERSION_NUMBER:
                tshark_version_color = '<span style="color: green;">'
            else:
                tshark_version_color = '<span style="color: yellow;">'

            one_second_ago = datetime.now(tz=LOCAL_TZ) - timedelta(seconds=1)

            # Filter packets received in the last second
            recent_packets = [(pkt_time, pkt_latency) for pkt_time, pkt_latency in tshark_packets_latencies if pkt_time >= one_second_ago]

            # Update latencies list to only keep recent packets
            tshark_packets_latencies[:] = recent_packets

            # Calculate average latency
            if recent_packets:
                total_latency_seconds = sum(pkt_latency.total_seconds() for _, pkt_latency in recent_packets)
                avg_latency_seconds = total_latency_seconds / len(recent_packets)
                avg_latency_rounded = round(avg_latency_seconds, 1)
            else:
                avg_latency_seconds = 0.0
                avg_latency_rounded = 0.0

            # Determine latency color
            if avg_latency_seconds >= 0.90 * Settings.CAPTURE_OVERFLOW_TIMER:
                latency_color = '<span style="color: red;">'
            elif avg_latency_seconds >= 0.75 * Settings.CAPTURE_OVERFLOW_TIMER:
                latency_color = '<span style="color: yellow;">'
            else:
                latency_color = '<span style="color: green;">'

            if (time.monotonic() - global_pps_last_update_time) >= 1.0:
                global_pps_rate = global_pps_counter
                global_pps_counter = 0
                global_pps_last_update_time = time.monotonic()

            # For reference, in a GTA Online session, the packets per second (PPS) typically range from 0 (solo session) to 1500 (public session, 32 players).
            # If the packet rate exceeds these ranges, we flag them with yellow or red color to indicate potential issues (such as scanning unwanted packets outside of the GTA game).
            # Also these values averagely indicates the max performances my script can run at during my testings. Luckely it's just enough to process GTA V game.
            if global_pps_rate >= PPS_THRESHOLD_CRITICAL:
                pps_color = '<span style="color: red;">'
            elif global_pps_rate >= PPS_THRESHOLD_WARNING:
                pps_color = '<span style="color: yellow;">'
            else:
                pps_color = '<span style="color: green;">'

            is_vpn_mode_enabled = "Enabled" if Settings.CAPTURE_VPN_MODE or force_enable_capture_vpn_mode else "Disabled"
            is_arp_enabled = "Enabled" if selected_interface.is_arp else "Disabled"
            displayed_capture_ip_address = Settings.CAPTURE_IP_ADDRESS if Settings.CAPTURE_IP_ADDRESS else "N/A"
            color_tshark_restarted_time = '<span style="color: green;">' if tshark_restarted_times == 0 else '<span style="color: red;">'
            if Settings.DISCORD_PRESENCE:
                rpc_message = ' RPC:<span style="color: green;">Connected</span>' if discord_rpc_manager.connection_status.is_set() else ' RPC:<span style="color: yellow;">Waiting for Discord</span>'
            else:
                rpc_message = ""

            num_of_userip_files = len(UserIPDatabases.get_userip_database_filepaths())
            invalid_ip_count = len(UserIPDatabases.notified_ip_invalid)
            conflict_ip_count = len(UserIPDatabases.notified_ip_conflicts)
            corrupted_settings_count = len(UserIPDatabases.notified_settings_corrupted)

            header = f"""
            <div style="background: linear-gradient(90deg, #2e3440, #4c566a); color: white; padding: 20px; border: 2px solid #88c0d0; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);">
                <div>
                    <span style="font-size: 24px; color: #88c0d0">Welcome to {TITLE}</span>&nbsp;&nbsp;<span style="font-size: 14px; color: #aaa">{VERSION}</span>
                </div>
                <p style="font-size: 16px; margin: 5px 0;">
                    The best FREE and Open-Source packet sniffer, aka IP grabber, works WITHOUT mods.
                </p>
                <p style="font-size: 14px; margin: 5px 0;">
                    Scanning with TShark {tshark_version_color}v{capture.extracted_tshark_version}</span> on Interface <span style="color: yellow;">{capture.interface}</span> | IP:<span style="color: yellow;">{displayed_capture_ip_address}</span> | ARP:<span style="color: yellow;">{is_arp_enabled}</span> | VPN:<span style="color: yellow;">{is_vpn_mode_enabled}</span> | Preset:<span style="color: yellow;">{Settings.CAPTURE_PROGRAM_PRESET}</span>
                </p>
                <p style="font-size: 14px; margin: 5px 0;">
                    Packets latency per sec:{latency_color}{avg_latency_rounded}</span>/<span style="color: green;">{Settings.CAPTURE_OVERFLOW_TIMER}</span> (tshark restart{pluralize(tshark_restarted_times)}:{color_tshark_restarted_time}{tshark_restarted_times}</span>) PPS:{pps_color}{global_pps_rate}</span>{rpc_message}
                </p>
            </div>
            """

            if any([invalid_ip_count, conflict_ip_count, corrupted_settings_count]):
                header += "───────────────────────────────────────────────────────────────────────────────────────────────────<br>"
                if invalid_ip_count:
                    header += f'Number of invalid IP{pluralize(invalid_ip_count)} in UserIP file{pluralize(num_of_userip_files)}: <span style="color: red;">{invalid_ip_count}</span><br>'
                if conflict_ip_count:
                    header += f'Number of conflicting IP{pluralize(conflict_ip_count)} in UserIP file{pluralize(num_of_userip_files)}: <span style="color: red;">{conflict_ip_count}</span><br>'
                if corrupted_settings_count:
                    header += f'Number of corrupted setting(s) in UserIP file{pluralize(num_of_userip_files)}: <span style="color: red;">{corrupted_settings_count}</span><br>'
                header += "───────────────────────────────────────────────────────────────────────────────────────────────────"
            return header, global_pps_last_update_time, global_pps_rate

        from modules.constants.standard import TWO_TAKE_ONE__PLUGIN__LOG_PATH, STAND__PLUGIN__LOG_PATH, RE_MODMENU_LOGS_USER_PATTERN
        from modules.constants.local import CHERAX__PLUGIN__LOG_PATH, IMAGES_PATH
        from modules.utils import concat_lists_no_duplicates

        GUIrenderingData.FIELDS_TO_HIDE = set(Settings.GUI_FIELDS_TO_HIDE)
        (
            GUIrenderingData.GUI_CONNECTED_PLAYERS_TABLE__FIELD_NAMES,
            GUIrenderingData.GUI_DISCONNECTED_PLAYERS_TABLE__FIELD_NAMES,
            LOGGING_CONNECTED_PLAYERS_TABLE__FIELD_NAMES,
            LOGGING_DISCONNECTED_PLAYERS_TABLE__FIELD_NAMES,
        ) = compile_tables_header_field_names()

        GUIrenderingData.SESSION_CONNECTED_TABLE__NUM_COLS = len(GUIrenderingData.GUI_CONNECTED_PLAYERS_TABLE__FIELD_NAMES)
        GUIrenderingData.SESSION_DISCONNECTED_TABLE__NUM_COLS = len(GUIrenderingData.GUI_DISCONNECTED_PLAYERS_TABLE__FIELD_NAMES)
        # Define the column name to index mapping for connected and disconnected players
        CONNECTED_COLUMN_MAPPING = {header: index for index, header in enumerate(GUIrenderingData.GUI_CONNECTED_PLAYERS_TABLE__FIELD_NAMES)}
        # DISCONNECTED_COLUMN_MAPPING = {header: index for index, header in enumerate(GUIrenderingData.GUI_DISCONNECTED_PLAYERS_TABLE__FIELD_NAMES)}

        global_pps_last_update_time = time.monotonic()
        global_pps_rate = 0
        last_userip_parse_time = None
        last_mod_menus_logs_parse_time = None
        last_session_logging_processing_time = None

        if Settings.DISCORD_PRESENCE:
            from modules.discord.rpc import DiscordRPC
            from modules.constants.standalone import DISCORD_APPLICATION_ID

            discord_rpc_manager = DiscordRPC(client_id=DISCORD_APPLICATION_ID)

        modmenu__plugins__ip_to_usernames: dict[str, list[str]] = {}
        file_mod_time_cache: dict[Path, float] = {}

        while not gui_closed__event.is_set():
            if ScriptControl.has_crashed():
                return

            # Wait for sorting fields to be initialized from the GUI
            while (
                GUIrenderingData.session_connected_sorted_column_name is None
                or GUIrenderingData.session_disconnected_sorted_column_name is None
                or GUIrenderingData.session_disconnected_sort_order is None
                or GUIrenderingData.session_connected_sort_order is None
            ):
                gui_closed__event.wait(0.1)
                continue

            session_connected: list[Player] = []
            session_disconnected: list[Player] = []

            if last_mod_menus_logs_parse_time is None or time.monotonic() - last_mod_menus_logs_parse_time >= 1.0:
                last_mod_menus_logs_parse_time = time.monotonic()

                for log_path in (STAND__PLUGIN__LOG_PATH, CHERAX__PLUGIN__LOG_PATH, TWO_TAKE_ONE__PLUGIN__LOG_PATH):
                    if not log_path.is_file():
                        continue

                    # Check modification time
                    mod_time = log_path.stat().st_mtime
                    if file_mod_time_cache.get(log_path) == mod_time:
                        continue  # Skip unchanged files

                    file_mod_time_cache[log_path] = mod_time

                    # Read the content and split it into lines
                    for line in log_path.read_text(encoding="utf-8").splitlines():
                        match = RE_MODMENU_LOGS_USER_PATTERN.fullmatch(line)
                        if not match:
                            continue

                        username = match.group("username")
                        if not isinstance(username, str):
                            continue

                        ip = match.group("ip")
                        if not isinstance(ip, str):
                            continue

                        if username not in modmenu__plugins__ip_to_usernames.setdefault(ip, []):
                            modmenu__plugins__ip_to_usernames[ip].append(username)

            if last_userip_parse_time is None or time.monotonic() - last_userip_parse_time >= 1.0:
                last_userip_parse_time = update_userip_databases()

            if Settings.GUI_SESSIONS_LOGGING:
                session_connected__padding_country_name = 0
                session_connected__padding_continent_name = 0
                session_disconnected__padding_country_name = 0
                session_disconnected__padding_continent_name = 0

            for player in PlayersRegistry.get_sorted_players():
                if player.userip and player.ip not in UserIPDatabases.ips_set:
                    player.userip = None
                    player.userip_detection = None

                if (
                    player.mod_menus
                    and modmenu__plugins__ip_to_usernames
                    and player.ip in modmenu__plugins__ip_to_usernames
                ):
                    for username in modmenu__plugins__ip_to_usernames[player.ip]:
                        if username not in player.mod_menus.usernames:
                            player.mod_menus.usernames.append(username)

                player.usernames = concat_lists_no_duplicates(
                    player.mod_menus.usernames if player.mod_menus else [],
                    player.userip.usernames if player.userip else [],
                )

                if player.iplookup.country_flag is None:
                    country_code = (
                        player.iplookup.geolite2.country_code
                        if player.iplookup.geolite2.country_code != "..."
                        else player.iplookup.ipapi.country_code
                        if player.iplookup.ipapi.country_code != "..."
                        else None
                    )
                    if country_code:
                        flag_path = IMAGES_PATH / f"country_flags/{country_code.upper()}.png"
                        if flag_path.exists():
                            pixmap = QPixmap()  # Create a new QPixmap
                            pixmap.loadFromData(flag_path.read_bytes())  # Load the data into the QPixmap
                            player.iplookup.country_flag = PlayerCountryFlag(
                                pixmap=pixmap,  # Assign the pixmap to the object
                                icon=QIcon(pixmap),  # Create QIcon from QPixmap
                            )

                if (
                    not player.datetime.left
                    and (datetime.now(tz=LOCAL_TZ) - player.datetime.last_seen).total_seconds() >= Settings.GUI_DISCONNECTED_PLAYERS_TIMER
                ):
                    player.datetime.left = player.datetime.last_seen
                    if player.userip_detection and player.userip_detection.as_processed_task:
                        player.userip_detection.as_processed_task = False
                        threading.Thread(target=process_userip_task, args=(player, "disconnected"), daemon=True).start()

                if not player.iplookup.geolite2.is_initialized:
                    player.iplookup.geolite2.country, player.iplookup.geolite2.country_code = get_country_info(player.ip)
                    player.iplookup.geolite2.city = get_city_info(player.ip)
                    player.iplookup.geolite2.asn = get_asn_info(player.ip)

                    player.iplookup.geolite2.is_initialized = True

                if player.datetime.left:
                    session_disconnected.append(player)

                    if Settings.GUI_SESSIONS_LOGGING:
                        session_disconnected__padding_country_name = get_minimum_padding(player.iplookup.geolite2.country, session_disconnected__padding_country_name, 27)
                        session_disconnected__padding_continent_name = get_minimum_padding(player.iplookup.ipapi.continent, session_disconnected__padding_continent_name, 13)
                else:
                    session_connected.append(player)

                    if Settings.GUI_SESSIONS_LOGGING:
                        session_connected__padding_country_name = get_minimum_padding(player.iplookup.geolite2.country, session_connected__padding_country_name, 27)
                        session_connected__padding_continent_name = get_minimum_padding(player.iplookup.ipapi.continent, session_connected__padding_continent_name, 13)

                    # Calculate PPS every second
                    if (time.monotonic() - player.pps.last_update_time) >= 1.0:
                        player.pps.rate = player.pps.counter  # Count of packets in the last second
                        player.pps.update_average(player.pps.rate)
                        player.pps.counter = 0
                        player.pps.last_update_time = time.monotonic()
                        player.pps.is_first_calculation = False

                    # Calculate PPM every minute
                    if (time.monotonic() - player.ppm.last_update_time) >= 60.0:  # noqa: PLR2004
                        player.ppm.rate = player.ppm.counter  # Count of packets in the last minute
                        player.ppm.update_average(player.ppm.rate)
                        player.ppm.counter = 0
                        player.ppm.last_update_time = time.monotonic()
                        player.ppm.is_first_calculation = False

            if Settings.CAPTURE_PROGRAM_PRESET == "GTA5":
                if SessionHost.player and SessionHost.player.datetime.left:
                    SessionHost.player = None
                # TODO(BUZZARDGTA): We should also potentially needs to check that not more then 1s passed before each disconnected
                if SessionHost.players_pending_for_disconnection and all(player.datetime.left for player in SessionHost.players_pending_for_disconnection):
                    SessionHost.player = None
                    SessionHost.search_player = True
                    SessionHost.players_pending_for_disconnection.clear()

                if len(session_connected) == 0:
                    SessionHost.player = None
                    SessionHost.search_player = True
                    SessionHost.players_pending_for_disconnection.clear()
                elif len(session_connected) >= 1 and all(not player.pps.is_first_calculation and player.pps.rate == 0 for player in session_connected):
                    SessionHost.players_pending_for_disconnection = session_connected
                elif SessionHost.search_player:
                    SessionHost.get_host_player(session_connected)

            session_connected_sorted = sort_session_table(
                session_connected,
                GUIrenderingData.session_connected_sorted_column_name,
                GUIrenderingData.session_connected_sort_order,
            )
            session_disconnected_sorted = sort_session_table(
                session_disconnected,
                GUIrenderingData.session_disconnected_sorted_column_name,
                GUIrenderingData.session_disconnected_sort_order,
            )

            if Settings.GUI_SESSIONS_LOGGING and (last_session_logging_processing_time is None or (time.monotonic() - last_session_logging_processing_time) >= 1.0):
                process_session_logging()
                last_session_logging_processing_time = time.monotonic()

            if Settings.DISCORD_PRESENCE and (discord_rpc_manager.last_update_time is None or (time.monotonic() - discord_rpc_manager.last_update_time) >= 3.0):  # noqa: PLR2004
                discord_rpc_manager.update(f"{len(session_connected_sorted)} player{pluralize(len(session_connected_sorted))} connected")

            GUIrenderingData.header_text, global_pps_last_update_time, global_pps_rate = generate_gui_header_text(global_pps_last_update_time, global_pps_rate)
            (
                GUIrenderingData.session_connected_table__num_rows,
                GUIrenderingData.session_connected_table__processed_data,
                GUIrenderingData.session_connected_table__compiled_colors,
                GUIrenderingData.session_disconnected_table__num_rows,
                GUIrenderingData.session_disconnected_table__processed_data,
                GUIrenderingData.session_disconnected_table__compiled_colors,
            ) = process_gui_session_tables_rendering()
            GUIrenderingData.gui_rendering_ready_event.set()

            gui_closed__event.wait(1)


clear_screen()
set_window_title(f"DEBUG CONSOLE - {TITLE}")

tshark_restarted_times = 0
global_pps_counter = 0

PlayersRegistry.start_cache_updater_thread()

rendering_core__thread = threading.Thread(target=rendering_core, daemon=True)
rendering_core__thread.start()

hostname_core__thread = threading.Thread(target=hostname_core, daemon=True)
hostname_core__thread.start()

iplookup_core__thread = threading.Thread(target=iplookup_core, daemon=True)
iplookup_core__thread.start()

pinger_core__thread = threading.Thread(target=pinger_core, daemon=True)
pinger_core__thread.start()

capture_core__thread = threading.Thread(target=capture_core, daemon=True)
capture_core__thread.start()


class SessionTableModel(QAbstractTableModel):
    def __init__(self, headers: list[str]):
        super().__init__()
        self._headers = headers  # The column headers
        self._data: list[list[str]] = []  # The data to be displayed in the table

        # Custom Variables
        self._view: SessionTableView | None = None  # Initially, no view is attached
        self._compiled_colors: list[list[CellColor]] = []  # The compiled colors for the table
        self.IP_COLUMN_INDEX = self._headers.index("IP Address")  # pylint: disable=invalid-name

    # pylint: disable=invalid-name,unused-argument
    def rowCount(self, parent: QModelIndex | None = None):  # noqa: ARG002, N802
        return len(self._data)  # The number of rows in the model

    def columnCount(self, parent: QModelIndex | None = None):  # noqa: ARG002, N802
        return len(self._headers)  # The number of columns in the model
    # pylint: enable=unused-argument

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        """Override data method to customize data retrieval and alignment."""
        if not index.isValid():
            return None

        row_idx = index.row()
        col_idx = index.column()

        # Check bounds
        if row_idx >= len(self._data) or col_idx >= len(self._data[row_idx]):
            return None  # Return None for invalid index

        if role == Qt.ItemDataRole.DecorationRole:  # noqa: SIM102
            if self.get_column_index("Country") == col_idx:
                ip = self._data[row_idx][self.IP_COLUMN_INDEX]
                if not isinstance(ip, str):
                    raise TypeError(f'Expected "str", got "{type(ip).__name__}"')
                ip = ip.removesuffix(" 👑")

                player = PlayersRegistry.get_player(ip)
                if not isinstance(player, Player):
                    raise TypeError(f'Expected "Player", got "{type(player).__name__}"')

                if player.iplookup.country_flag is not None:
                    return player.iplookup.country_flag.icon

        if role == Qt.ItemDataRole.DisplayRole:
            # Return the cell's text
            return self._data[row_idx][col_idx]

        if role == Qt.ItemDataRole.ForegroundRole:  # noqa: SIM102
            # Return the cell's foreground color
            if row_idx < len(self._compiled_colors) and col_idx < len(self._compiled_colors[row_idx]):
                return QBrush(self._compiled_colors[row_idx][col_idx].foreground)

        if role == Qt.ItemDataRole.BackgroundRole:  # noqa: SIM102
            # Return the cell's background color
            if row_idx < len(self._compiled_colors) and col_idx < len(self._compiled_colors[row_idx]):
                return QBrush(self._compiled_colors[row_idx][col_idx].background)

        if role == Qt.ItemDataRole.ToolTipRole:
            # Ensure the view is attached
            if self._view is None:
                return None

            # Get the column resize mode
            horizontal_header = self._view.horizontalHeader()
            if not isinstance(horizontal_header, QHeaderView):
                raise TypeError(f'Expected "QHeaderView", got "{type(horizontal_header).__name__}"')
            resize_mode = horizontal_header.sectionResizeMode(index.column())

            # Return None if the column resize mode isn't set to Stretch, as it shouldn't be truncated
            if resize_mode != QHeaderView.ResizeMode.Stretch:
                return None

            cell_text = self._data[row_idx][col_idx]

            font_metrics = self._view.fontMetrics()
            text_width = font_metrics.horizontalAdvance(cell_text)
            column_width = self._view.columnWidth(index.column())

            TEXT_TRUNCATION_MARGIN = 8
            if text_width > column_width - TEXT_TRUNCATION_MARGIN:
                return cell_text

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        from modules.constants.standalone import GUI_COLUMN_HEADERS_TOOLTIPS

        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self._headers[section]  # Display the header name
            if role == Qt.ItemDataRole.ToolTipRole:
                # Fetch the header name and return the corresponding tooltip
                header_name = self._headers[section]
                return GUI_COLUMN_HEADERS_TOOLTIPS.get(header_name, None)

        return None

    def setData(self, index: QModelIndex, value: str, role: int = Qt.ItemDataRole.EditRole):  # noqa: N802
        if not index.isValid():
            return False

        if role == Qt.ItemDataRole.EditRole:
            self._data[index.row()][index.column()] = value  # Set the data at the specified index
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])  # Notify the view of data change
            return True

        return False

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder):
        """Sort the table by a specific column.

        Args:
            column: The column index to sort by.
            order: The order (ascending/descending) to sort in.
        """
        if not self._data:
            if self._compiled_colors:
                raise ValueError("Inconsistent state: It's not possible to have colors if there's no data.")
            return  # No data to process, exit early.

        if not self._compiled_colors:
            raise ValueError("Inconsistent state: It's not possible to have data without colors.")

        self.layoutAboutToBeChanged.emit()

        sorted_column_name = self._headers[column]
        # Combine data and colors for sorting
        combined = list(zip(self._data, self._compiled_colors, strict=True))
        if not combined:
            raise ValueError("Inconsistent state: 'combined' is unexpectedly empty at this point.")
        sort_order_bool = order == Qt.SortOrder.DescendingOrder

        if sorted_column_name == "IP Address":
            import ipaddress

            # Sort by IP address
            combined.sort(
                key=lambda row: ipaddress.ip_address(row[0][column].removesuffix(" 👑")),
                reverse=sort_order_bool,
            )
        elif sorted_column_name in {"First Seen", "Last Rejoin", "Last Seen"}:
            # Retrieve the player datetime object from the IP column
            def extract_datetime_for_ip(ip: str):
                """Extract a datetime object for a given IP address."""
                player = PlayersRegistry.get_player(ip)
                if not isinstance(player, Player):
                    raise TypeError(f'Expected "Player", got "{type(player).__name__}"')

                # Retrieve the player datetime attribute name for the selected column
                # Mapping column names to player datetime attributes
                datetime_attribute = {
                    "First Seen": "first_seen",
                    "Last Rejoin": "last_rejoin",
                    "Last Seen": "last_seen",
                }.get(self._headers[column], None)
                if not isinstance(datetime_attribute, str):
                    raise TypeError(f'Expected "str", got "{type(datetime_attribute).__name__}"')

                # Safely retrieve the attribute using `getattr`
                return getattr(player.datetime, datetime_attribute)

            combined.sort(
                key=lambda row: extract_datetime_for_ip(row[0][self.IP_COLUMN_INDEX].removesuffix(" 👑")),
                reverse=not sort_order_bool,
            )
        else:
            # Sort by other columns: numerically if the strings represent numbers, otherwise case-insensitively
            combined.sort(
                key=lambda row: (
                    float(row[0][column]) if row[0][column].replace(".", "", 1).isdigit() else row[0][column].casefold()
                ),
                reverse=sort_order_bool,
            )

        # Unpack the sorted data
        self._data, self._compiled_colors = map(list, zip(*combined, strict=True))

        self.layoutChanged.emit()
    # pylint: enable=invalid-name

    # Custom Methods:

    def set_view(self, view: "SessionTableView"):
        self._view = view

    def get_column_index(self, column_name: str):
        """Get the table index of a specified column.

        Args:
            column_name: The column name to look for.

        Returns:
            The table column index.
        """
        return self._headers.index(column_name)

    def get_row_index_by_ip(self, ip: str):
        """Find the row index for the given IP address.

        Args:
            ip: The IP address to search for.

        Returns:
            The index of the row containing the IP address, or None if not found.
        """
        for row_index, row_data in enumerate(self._data):
            if row_data[self.IP_COLUMN_INDEX].removesuffix(" 👑") == ip:
                return row_index
        return None

    def sort_current_column(self):
        """Call the sort method with the current column index and order.

        Ensures sorting reflects the current state of the header.
        """
        if not isinstance(self._view, SessionTableView):
            raise TypeError(f'Expected "SessionTableView", got "{type(self._view).__name__}"')

        # Retrieve the current sort column and order
        horizontal_header = self._view.horizontalHeader()
        if not isinstance(horizontal_header, QHeaderView):
            raise TypeError(f'Expected "QHeaderView", got "{type(horizontal_header).__name__}"')
        sort_column = horizontal_header.sortIndicatorSection()
        sort_order = horizontal_header.sortIndicatorOrder()

        # Call the sort function with the retrieved arguments
        self.sort(sort_column, sort_order)

    def add_row_without_refresh(self, row_data: list[str], row_colors: list[CellColor]):
        """Add a new row to the model without notifying the view in real time.

        Args:
            row_data: The data for the new row.
            row_colors: A list of `CellColor` objects corresponding to the row's colors.
        """
        # Only update internal data without triggering signals
        self._data.append(row_data)
        self._compiled_colors.append(row_colors)

    def update_row_without_refresh(self, row_index: int, row_data: list[str], row_colors: list[CellColor]):
        """Update an existing row in the model with new data and colors without notifying the view in real time.

        Args:
            row_index: The index of the row to update.
            row_data: The new data for the row.
            row_colors: A list of `CellColor` objects corresponding to the row's colors.
        """
        if 0 <= row_index < self.rowCount():
            self._data[row_index] = row_data
            self._compiled_colors[row_index] = row_colors

    def delete_row(self, row_index: int):
        """Delete a row from the model along with its associated colors.

        If any items are selected under this row, their selection moves one row up.

        Args:
            row_index: The index of the row to delete.
        """
        if 0 <= row_index < self.rowCount():
            if not isinstance(self._view, SessionTableView):
                raise TypeError(f'Expected "SessionTableView", got "{type(self._view).__name__}"')

            selection_model = self._view.selectionModel()
            if not isinstance(selection_model, QItemSelectionModel):
                raise TypeError(f'Expected "QItemSelectionModel", got "{type(selection_model).__name__}"')

            # Adjust selection for the deleted row
            for index in selection_model.selection().indexes():
                if index.row() == row_index:  # Row to be deleted
                    # Deselect the row because it's about to be deleted
                    # Select the row to be deleted
                    selection = QItemSelection(
                        self.index(index.row(), index.column()),
                        self.index(index.row(), index.column()),
                    )
                    selection_model.select(selection, QItemSelectionModel.SelectionFlag.Deselect)

            # Notify the view that rows are about to be removed
            self.beginRemoveRows(self.index(row_index, 0), row_index, row_index)

            # Remove the data and compiled colors at the specified index
            self._data.pop(row_index)
            self._compiled_colors.pop(row_index)

            # Adjust selection for rows below the deleted one
            for index in selection_model.selection().indexes():
                if index.row() > row_index:  # Items below the deleted row
                    # Deselect the original row
                    selection_to_deselect = QItemSelection(
                        self.index(index.row(), index.column()),  # Original row
                        self.index(index.row(), index.column()),
                    )
                    selection_model.select(selection_to_deselect, QItemSelectionModel.SelectionFlag.Deselect)

                    # Move the selection up by one row
                    selection_to_select = QItemSelection(
                        self.index(index.row() - 1, index.column()),  # New row after deletion
                        self.index(index.row() - 1, index.column()),
                    )
                    selection_model.select(selection_to_select, QItemSelectionModel.SelectionFlag.Select)

            # Notify the view that the rows have been removed
            self.endRemoveRows()

            # NOTE: Fixes a weird UI bug that when someone leaves, it makes it an empty row
            if not self._data:
                # Begin resetting the model to indicate it's empty
                self.beginResetModel()
                self._data = []
                self._compiled_colors = []
                # End reset and notify the view that the model has been reset
                self.endResetModel()

            # Ensure the view resizes properly after a row is removed
            # if self._view:
            #     self._view.resizeRowsToContents()
            #     self._view.viewport().update()

    def refresh_view(self):
        """Notifies the view to refresh and reflect all changes made to the model."""
        self.layoutAboutToBeChanged.emit()
        self.layoutChanged.emit()


class SessionTableView(QTableView):
    def __init__(self, model: SessionTableModel, sort_column: int, sort_order: Qt.SortOrder):
        super().__init__()
        self.setModel(model)
        self._is_dragging = False  # Track if the mouse is being dragged with Ctrl key
        self._previous_sort_section_index: int | None = None

        self.setMouseTracking(True)  # Track mouse without clicks
        viewport = self.viewport()
        if not isinstance(viewport, QWidget):
            raise TypeError(f'Expected "QWidget", got "{type(viewport).__name__}"')
        viewport.installEventFilter(self)  # Install event filter
        # Configure table view settings
        vertical_header = self.verticalHeader()
        if not isinstance(vertical_header, QHeaderView):
            raise TypeError(f'Expected "QHeaderView", got "{type(vertical_header).__name__}"')
        vertical_header.setVisible(False)  # Hide row index
        self.setAlternatingRowColors(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        horizontal_header = self.horizontalHeader()
        if not isinstance(horizontal_header, QHeaderView):
            raise TypeError(f'Expected "QHeaderView", got "{type(horizontal_header).__name__}"')
        horizontal_header.setSectionsClickable(True)
        horizontal_header.sectionClicked.connect(self.on_section_clicked)
        horizontal_header.setSectionsMovable(True)
        self.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        # Set the sort indicator for the specified column
        self.setSortingEnabled(False)
        horizontal_header.setSortIndicator(sort_column, sort_order)
        horizontal_header.setSortIndicatorShown(True)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    # pylint: disable=invalid-name
    def eventFilter(self, obj: QObject, event: QEvent):  # noqa: N802
        if isinstance(obj, QWidget) and isinstance(event, QHoverEvent):
            index = self.indexAt(event.position().toPoint())  # Get hovered cell
            if index.isValid():
                col_idx = index.column()
                model = self.model()
                if not isinstance(model, SessionTableModel):
                    raise TypeError(f'Expected "SessionTableModel", got "{type(model).__name__}"')

                if model.get_column_index("Country") == col_idx:
                    ip = model.data(model.index(index.row(), model.IP_COLUMN_INDEX))
                    if not isinstance(ip, str):
                        raise TypeError(f'Expected "str", got "{type(ip).__name__}"')
                    ip = ip.removesuffix(" 👑")

                    player = PlayersRegistry.get_player(ip)
                    if player is not None and player.iplookup.country_flag is not None:
                        self.show_flag_tooltip(event, index, player)

        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent):  # noqa: N802
        """Handle key press events to capture Ctrl+A for selecting all and Ctrl+C for copying selected data to the clipboard.

        Fall back to default behavior for other key presses.
        """
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:  # Check for Ctrl+C key combination and copy selection
            if event.key() == Qt.Key.Key_A:
                self.select_all_cells()
            elif event.key() == Qt.Key.Key_C:
                selected_model = self.model()
                if not isinstance(selected_model, SessionTableModel):
                    raise TypeError(f'Expected "SessionTableModel", got "{type(selected_model).__name__}"')

                selection_model = self.selectionModel()
                if not isinstance(selection_model, QItemSelectionModel):
                    raise TypeError(f'Expected "QItemSelectionModel", got "{type(selection_model).__name__}"')

                selected_indexes = selection_model.selectedIndexes()

                self.copy_selected_cells(selected_model, selected_indexes)
            return

        # Fall back to default behavior
        super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent):  # noqa: N802
        """Handle mouse press events for selecting multiple items with Ctrl or single items otherwise.

        Fall back to default behavior for non-cell areas.
        """
        index = self.indexAt(event.pos())  # Determine the index of the clicked item
        if index.isValid():
            selection_model = self.selectionModel()
            if not isinstance(selection_model, QItemSelectionModel):
                raise TypeError(f'Expected "QItemSelectionModel", got "{type(selection_model).__name__}"')

            selection_flag = None

            if event.button() == Qt.MouseButton.RightButton:
                if not selection_model.isSelected(index):
                    selection_model.select(index, QItemSelectionModel.SelectionFlag.ClearAndSelect)
                    return

            elif event.button() == Qt.MouseButton.LeftButton:
                # Determine selection flag based on modifier keys
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    # Toggle selection while keeping other selections
                    selection_flag = (
                        QItemSelectionModel.SelectionFlag.Deselect
                        if selection_model.isSelected(index)
                        else QItemSelectionModel.SelectionFlag.Select
                    )
                    self._is_dragging = True  # Start tracking dragging
                elif event.modifiers() == Qt.KeyboardModifier.NoModifier:
                    was_selection_index_selected = selection_model.isSelected(index)

                    # Clear existing selections
                    selection_model.clearSelection()

                    # Select or Deselect the clicked cell
                    selection_flag = (
                        QItemSelectionModel.SelectionFlag.Deselect
                        if was_selection_index_selected
                        else QItemSelectionModel.SelectionFlag.Select
                    )

            if selection_flag is not None:
                # Apply the determined selection flag
                selection_model.select(index, selection_flag)
                return

        # Fall back to default behavior
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):  # noqa: N802
        """Handle mouse move events for selecting multiple items while holding the Ctrl key."""
        if self._is_dragging and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            index = self.indexAt(event.pos())  # Get the index under the cursor
            if index.isValid():
                selection_model = self.selectionModel()
                if not isinstance(selection_model, QItemSelectionModel):
                    raise TypeError(f'Expected "QItemSelectionModel", got "{type(selection_model).__name__}"')

                # Select the current cell
                selection_model.select(index, QItemSelectionModel.SelectionFlag.Select)
                return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):  # noqa: N802
        """Reset dragging state when the mouse button is released."""
        self._is_dragging = False

        super().mouseReleaseEvent(event)
    # pylint: enable=invalid-name

    # Custom Methods:

    def adjust_table_column_widths(self):
        """Adjust the column widths of a QTableView to fit content."""
        model = self.model()
        if not isinstance(model, SessionTableModel):
            raise TypeError(f'Expected "SessionTableModel", got "{type(model).__name__}"')

        horizontal_header = self.horizontalHeader()
        if not isinstance(horizontal_header, QHeaderView):
            raise TypeError(f'Expected "QHeaderView", got "{type(horizontal_header).__name__}"')

        for column in range(model.columnCount()):
            # Get the header label for the column
            header_label = model.headerData(column, Qt.Orientation.Horizontal)

            if header_label == "Usernames":
                # Check if the column contains any data other than "N/A"
                contains_non_na = any(
                    model.data(model.index(row, column)) != "N/A"
                    for row in range(model.rowCount())
                )

                if contains_non_na:
                    horizontal_header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
                else:
                    horizontal_header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
            elif header_label in {"First Seen", "Last Rejoin", "Last Seen", "Rejoins", "T. Packets", "Packets", "PPS", "Avg PPS", "PPM", "Avg PPM", "IP Address", "First Port", "Last Port", "Mobile", "VPN", "Hosting", "Pinging"}:
                horizontal_header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
            else:
                horizontal_header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)

    def get_sorted_column(self):
        """Get the currently sorted column and its order for this table view."""
        model = self.model()
        if not isinstance(model, SessionTableModel):
            raise TypeError(f'Expected "SessionTableModel", got "{type(model).__name__}"')

        horizontal_header = self.horizontalHeader()
        if horizontal_header is None:
            raise TypeError(f'Expected "QHeaderView", got "{type(horizontal_header).__name__}"')

        # Get the index of the currently sorted column
        sorted_column_index = horizontal_header.sortIndicatorSection()

        # Get the sort order (ascending or descending)
        sort_order = horizontal_header.sortIndicatorOrder()

        # Get the name of the sorted column from the model
        sorted_column_name = model.headerData(sorted_column_index, Qt.Orientation.Horizontal)
        if not isinstance(sorted_column_name, str):
            raise TypeError(f'Expected "str", got "{type(sorted_column_name).__name__}"')

        return sorted_column_name, sort_order

    def handle_menu_hovered(self, action: QAction):
        # Fixes: https://stackoverflow.com/questions/21725119/why-wont-qtooltips-appear-on-qactions-within-a-qmenu
        action_parent = action.parent()
        if isinstance(action_parent, QMenu):
            action_parent.setToolTip(action.toolTip())

    def on_section_clicked(self, section_index: int):
        model = self.model()
        if not isinstance(model, SessionTableModel):
            raise TypeError(f'Expected "SessionTableModel", got "{type(model).__name__}"')

        horizontal_header = self.horizontalHeader()
        if not isinstance(horizontal_header, QHeaderView):
            raise TypeError(f'Expected "QHeaderView", got "{type(horizontal_header).__name__}"')

        # Clear selections when a header section is clicked
        selection_model = self.selectionModel()
        if not isinstance(selection_model, QItemSelectionModel):
            raise TypeError(f'Expected "QItemSelectionModel", got "{type(selection_model).__name__}"')

        selection_model.clearSelection()

        # If it's the first click or sorting is being toggled
        if self._previous_sort_section_index is None or self._previous_sort_section_index != section_index:
            horizontal_header.setSortIndicator(section_index, Qt.SortOrder.DescendingOrder)

        # Sort the model
        model.sort(section_index, horizontal_header.sortIndicatorOrder())
        self._previous_sort_section_index = section_index

    def show_flag_tooltip(self, event: QHoverEvent, index: QModelIndex, player: Player):
        """Show tooltip only if hovering exactly over the flag."""
        # TODO(BUZZARDGTA): Make the tooltip appear precisely when hovering over the flag, using the pixmap or QIcon object if possible.
        cell_rect = self.visualRect(index)   # Get cell rectangle
        flag_x_start = cell_rect.left() + 4  # Assuming flag starts with a 4px horizontal padding
        flag_x_end = flag_x_start + 14       # Assuming flag ends with a 14px horizontal padding
        flag_y_start = cell_rect.top() + 10  # Assuming flag starts with a 10px vertical padding
        flag_y_end = flag_y_start + 10       # Assuming flag ends with a 10px vertical padding
        # Check if the mouse is over the flag both horizontally and vertically
        if flag_x_start <= event.position().toPoint().x() <= flag_x_end and flag_y_start <= event.position().toPoint().y() <= flag_y_end:
            QToolTip.showText(event.globalPosition().toPoint(), player.iplookup.geolite2.country, self)
        else:
            QToolTip.hideText()

    def show_context_menu(self, pos: QPoint):
        """Show the context menu at the specified position with options to interact with the table's content."""
        from modules.constants.standard import CUSTOM_CONTEXT_MENU_STYLESHEET, USERIP_DATABASES_PATH

        def add_action(
            menu: QMenu,
            label: str,
            shortcut: str | None = None,
            tooltip: str | None = None,
            handler: Callable[..., None] | None = None,
            enabled: bool | None = None,
        ):
            """Helper to create and configure a QAction."""
            action = menu.addAction(label)
            if not isinstance(action, QAction):
                raise TypeError(f'Expected "QAction", got "{type(action).__name__}"')

            if shortcut:
                action.setShortcut(shortcut)
            if tooltip:
                action.setToolTip(tooltip)
            if enabled is False:
                action.setEnabled(enabled)
            elif handler:
                action.triggered.connect(handler)

            return action

        def add_menu(parent_menu: QMenu, label: str, tooltip: str | None = None):
            """Helper to create and configure a QMenu."""
            menu = parent_menu.addMenu(label)
            if not isinstance(menu, QMenu):
                raise TypeError(f'Expected "QMenu", got "{type(menu).__name__}"')

            if tooltip:
                menu.setToolTip(tooltip)

            return menu

        # Determine the index at the clicked position
        index = self.indexAt(pos)
        if not index.isValid():
            return  # Do nothing if the click is outside valid cells

        selected_model = self.model()
        if not isinstance(selected_model, SessionTableModel):
            raise TypeError(f'Expected "SessionTableModel", got "{type(selected_model).__name__}"')

        selection_model = self.selectionModel()
        if not isinstance(selection_model, QItemSelectionModel):
            raise TypeError(f'Expected "QItemSelectionModel", got "{type(selection_model).__name__}"')

        selected_indexes = selection_model.selectedIndexes()

        # Create the main context menu
        context_menu = QMenu(self)
        context_menu.setStyleSheet(CUSTOM_CONTEXT_MENU_STYLESHEET)
        context_menu.setToolTipsVisible(True)
        context_menu.hovered.connect(self.handle_menu_hovered)

        # Add "Copy Selection" action
        add_action(
            context_menu,
            "Copy Selection",
            shortcut="Ctrl+C",
            tooltip="Copy selected cells to your clipboard.",
            handler=lambda: self.copy_selected_cells(selected_model, selected_indexes),
        )
        context_menu.addSeparator()

        # "Select" submenu
        select_menu = add_menu(context_menu, "Select  ")
        add_action(
            select_menu,
            "Select All",
            shortcut="Ctrl+A",
            tooltip="Select all cells in the table.",
            handler=self.select_all_cells,
        )
        add_action(
            select_menu,
            "Select Row",
            tooltip="Select all cells in this row.",
            handler=lambda: self.select_row_cells(index.row()),
        )
        add_action(
            select_menu,
            "Select Column",
            tooltip="Select all cells in this column.",
            handler=lambda: self.select_column_cells(index.column()),
        )

        # "Unselect" submenu
        unselect_menu = add_menu(context_menu, "Unselect")
        add_action(
            unselect_menu,
            "Unselect All",
            tooltip="Unselect all cells in the table.",
            handler=self.unselect_all_cells,
        )
        add_action(
            unselect_menu,
            "Unselect Row",
            tooltip="Unselect all cells in this row.",
            handler=lambda: self.unselect_row_cells(index.row()),
        )
        add_action(
            unselect_menu,
            "Unselect Column",
            tooltip="Unselect all cells in this column.",
            handler=lambda: self.unselect_column_cells(index.column()),
        )
        context_menu.addSeparator()

        # Process if one cell is selected
        if len(selected_indexes) == 1:
            selected_column = selected_indexes[0].column()

            column_name = selected_model.headerData(selected_column, Qt.Orientation.Horizontal)
            if not isinstance(column_name, str):
                raise TypeError(f'Expected "str", got "{type(column_name).__name__}"')

            if column_name == "IP Address":
                # Get the IP address from the selected cell
                ip = selected_model.data(selected_indexes[0])
                if not isinstance(ip, str):
                    return  # Added this return cuz some rare times it would raise.
                    # raise TypeError(f'Expected "str", got "{type(ip).__name__}"')
                ip = ip.removesuffix(" 👑")

                userip_database_filepaths = UserIPDatabases.get_userip_database_filepaths()
                player = PlayersRegistry.get_player(ip)
                if not isinstance(player, Player):
                    raise TypeError(f'Expected "Player", got "{type(player).__name__}"')

                add_action(
                    context_menu,
                    "IP Lookup Details",
                    tooltip="Displays a notification with a detailed IP lookup report for selected player.",
                    handler=lambda: self.show_detailed_ip_lookup_player_cell(ip),
                )

                ping_menu = add_menu(context_menu, "Ping    ")
                add_action(
                    ping_menu,
                    "Normal",
                    tooltip="Checks if selected IP address responds to pings.",
                    handler=lambda: self.ping(ip),
                )
                add_action(
                    ping_menu,
                    "Spoofed (check-host.net API)",
                    tooltip="Checks if selected IP address responds to pings from 'check-host.net'.\n\nNOTE: This only works if Python is installed on your system.",
                    handler=lambda: self.ping_spoofed(ip),
                )
                add_action(
                    ping_menu,
                    "TCP Port (paping.exe)",
                    tooltip="Checks if selected IP address responds to TCP pings on a given port.",
                    handler=lambda: self.tcp_port_ping(ip),
                )

                userip_menu = add_menu(context_menu, "UserIP  ")

                if not player.userip:
                    add_userip_menu = add_menu(userip_menu, "Add     ", "Add selected IP address to UserIP database.")  # Extra spaces for alignment
                    for database_path in userip_database_filepaths:
                        add_action(
                            add_userip_menu,
                            str(database_path.relative_to(USERIP_DATABASES_PATH).with_suffix("")),
                            tooltip="Add selected IP address to this UserIP database.",
                            handler=lambda _, database_path=database_path: self.userip_manager__add([ip], database_path),
                        )
                else:
                    # TODO(BUZZARDGTA): Add a "Rename" UserIP method
                    #add_action(
                    #    userip_menu,
                    #    "Rename  ", # Extra spaces for alignment
                    #    tooltip="Rename this IP address from UserIP databases.",
                    #    handler=lambda: self.userip_manager__rename([ip]),
                    #)
                    move_userip_menu = add_menu(userip_menu, "Move    ", "Move selected IP address to another database.")
                    for database_path in userip_database_filepaths:
                        add_action(
                            move_userip_menu,
                            str(database_path.relative_to(USERIP_DATABASES_PATH).with_suffix("")),
                            tooltip="Move selected IP address to this UserIP database.",
                            handler=lambda _, database_path=database_path: self.userip_manager__move([ip], database_path),
                            enabled=player.userip.database_path != database_path,
                        )
                    add_action(
                        userip_menu,
                        "Delete  ",  # Extra spaces for alignment
                        tooltip="Delete selected IP address from UserIP databases.",
                        handler=lambda: self.userip_manager__del([ip]),
                    )

        # Check if all selected cells are in the "IP Address" column
        elif all(
            selected_model.headerData(index.column(), Qt.Orientation.Horizontal) == "IP Address"
            for index in selected_indexes
        ):
            all_ips: list[str] = []

            # Get the IP addreses from the selected cells
            for index in selected_indexes:
                ip = selected_model.data(index)
                if not isinstance(ip, str):
                    raise TypeError(f'Expected "str", got "{type(ip).__name__}"')
                ip = ip.removesuffix(" 👑")
                all_ips.append(ip)

            if all(ip not in UserIPDatabases.ips_set for ip in all_ips):
                userip_menu = add_menu(context_menu, "UserIP  ")
                add_userip_menu = add_menu(userip_menu, "Add Selected")
                for database_path in UserIPDatabases.get_userip_database_filepaths():
                    add_action(
                        add_userip_menu,
                        str(database_path.relative_to(USERIP_DATABASES_PATH).with_suffix("")),
                        tooltip="Add selected IP addresses to this UserIP database.",
                        handler=lambda _, database_path=database_path: self.userip_manager__add(all_ips, database_path),
                    )
            elif all(ip in UserIPDatabases.ips_set for ip in all_ips):
                userip_menu = add_menu(context_menu, "UserIP  ")

                # TODO(BUZZARDGTA):
                #add_action(
                #    userip_menu,
                #    "Rename Selected", # Extra spaces for alignment
                #    tooltip="Rename these IP addresses from UserIP databases.",
                #    handler=lambda: self.userip_manager__rename([ip]),
                #)

                move_userip_menu = add_menu(userip_menu, "Move Selected")
                for database_path in UserIPDatabases.get_userip_database_filepaths():
                    add_action(
                        move_userip_menu,
                        str(database_path.relative_to(USERIP_DATABASES_PATH).with_suffix("")),
                        tooltip="Move selected IP addresses to this UserIP database.",
                        handler=lambda _, database_path=database_path: self.userip_manager__move(all_ips, database_path),
                    )
                add_action(
                    userip_menu,
                    "Delete Selected",  # Extra spaces for alignment
                    tooltip="Delete selected IP addresses from UserIP databases.",
                    handler=lambda: self.userip_manager__del(all_ips),
                )

        # Execute the context menu at the right-click position
        context_menu.exec(self.mapToGlobal(pos))

    def copy_selected_cells(self, selected_model: SessionTableModel, selected_indexes: list[QModelIndex]):
        """Copy the selected cells data from the table to the clipboard."""
        # Access the system clipboard
        clipboard = QApplication.clipboard()
        if not isinstance(clipboard, QClipboard):
            raise TypeError(f'Expected "QClipboard", got "{type(clipboard).__name__}"')

        # Prepare a list to store text data from selected cells
        selected_texts: list[str] = []

        # Iterate over each selected index and retrieve its display data
        for index in selected_indexes:
            cell_text = selected_model.data(index)
            if cell_text is None:
                return  # Added this return cuz some rare times it would raise.
            if not isinstance(cell_text, str):
                raise TypeError(f'Expected "str", got "{type(cell_text).__name__}"')

            selected_texts.append(cell_text)

        # Return if no text was selected
        if not selected_texts:
            return

        # Join all selected text entries with a newline to format for copying
        clipboard_content = "\n".join(selected_texts)

        # Set the formatted text in the system clipboard
        clipboard.setText(clipboard_content)

    def show_detailed_ip_lookup_player_cell(self, ip: str):
        from modules.constants.standard import USERIP_DATABASES_PATH

        player = PlayersRegistry.get_player(ip)
        if not isinstance(player, Player):
            raise TypeError(f'Expected "Player", got "{type(player).__name__}"')

        msgbox_message = textwrap.dedent(f"""
            ############ Player Infos #############
            IP Address: {player.ip}
            Hostname: {player.reverse_dns.hostname}
            Username{pluralize(len(player.usernames))}: {', '.join(player.usernames) or "N/A"}
            In UserIP database: {(player.userip_detection is not None and f"{player.userip and player.userip.database_path.relative_to(USERIP_DATABASES_PATH).with_suffix('')}") or "No"}
            Last Port: {player.ports.last}
            Intermediate Port{pluralize(len(player.ports.intermediate))}: {', '.join(map(str, player.ports.intermediate))}
            First Port: {player.ports.first}

            ########## IP Lookup Details ##########
            Continent: {player.iplookup.ipapi.continent}
            Country: {player.iplookup.geolite2.country}
            Country Code: {player.iplookup.geolite2.country_code}
            Region: {player.iplookup.ipapi.region}
            Region Code: {player.iplookup.ipapi.region_code}
            City: {player.iplookup.geolite2.city}
            District: {player.iplookup.ipapi.district}
            ZIP Code: {player.iplookup.ipapi.zip_code}
            Lat: {player.iplookup.ipapi.lat}
            Lon: {player.iplookup.ipapi.lon}
            Time Zone: {player.iplookup.ipapi.time_zone}
            Offset: {player.iplookup.ipapi.offset}
            Currency: {player.iplookup.ipapi.currency}
            Organization: {player.iplookup.ipapi.org}
            ISP: {player.iplookup.ipapi.isp}
            ASN / ISP: {player.iplookup.geolite2.asn}
            AS: {player.iplookup.ipapi.asn}
            ASN: {player.iplookup.ipapi.as_name}
            Mobile (cellular) connection: {player.iplookup.ipapi.mobile}
            Proxy, VPN or Tor exit address: {player.iplookup.ipapi.proxy}
            Hosting, colocated or data center: {player.iplookup.ipapi.hosting}

            ############ Ping Response ############
            Ping Times: {player.ping.ping_times}
            Packets Transmitted: {player.ping.packets_transmitted}
            Packets Received: {player.ping.packets_received}
            Packet Loss: {player.ping.packet_loss}
            Packet Errors: {player.ping.packet_errors}
            Round-Trip Time Minimum: {player.ping.rtt_min}
            Round-Trip Time Average: {player.ping.rtt_avg}
            Round-Trip Time Maximum: {player.ping.rtt_max}
            Round-Trip Time Mean Deviation: {player.ping.rtt_mdev}
        """).removeprefix("\n").removesuffix("\n")
        QMessageBox.information(self, TITLE, msgbox_message)

    def ping(self, ip: str):
        """Runs a continuous ping to a specified IP address in a new terminal window."""
        from modules.constants.standard import CMD_EXE

        subprocess.Popen(
            [CMD_EXE, "/K", "ping", ip, "-t"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

    def ping_spoofed(self, ip: str):
        """Runs a continuous ping to a specified IP address in a new terminal window."""
        from modules.constants.standard import CMD_EXE
        from modules.constants.local import SCRIPTS_PATH

        subprocess.Popen(
            [CMD_EXE, "/K", "py", SCRIPTS_PATH / "spoofed_ping.py", ip],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

    def tcp_port_ping(self, ip: str):
        """Runs paping to check TCP connectivity to a host on a user-specified port indefinitely."""

        def run_paping(host: str, port: int):
            """Runs paping in a new terminal window to check TCP connectivity continuously."""
            from modules.constants.standard import CMD_EXE
            from modules.constants.local import BIN_PATH

            # Start the subprocess and keep it running
            subprocess.Popen(
                [CMD_EXE, "/K", BIN_PATH / "paping.exe", host, "-p", str(port)],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )

        from modules.constants.standalone import MIN_PORT, MAX_PORT

        port_str, ok = QInputDialog.getText(self, "Input Port", "Enter the port number to check TCP connectivity:")

        if not ok:
            return

        if not port_str.isdigit():
            QMessageBox.warning(self, "Error", "No valid port number provided.")
            return

        port = int(port_str)

        if not MIN_PORT <= port <= MAX_PORT:
            QMessageBox.warning(self, "Error", "Please enter a valid port number between 1 and 65535.")
            return

        run_paping(ip, port)

    # TODO(BUZZARDGTA): Add a "Rename" UserIP method
    #def userip_manager__rename(self, ip_addresses: list[str]):
    #    # Prompt the user for the new username
    #    new_username, ok = QInputDialog.getText(self, "Input New Username", F"Please enter the new username to associate with the selected IP{pluralize(len(ip_addresses))}:")
    #
    #    if ok and new_username:
    #        ...

    def userip_manager__add(self, ip_addresses: list[str], selected_database: Path):
        from modules.constants.standard import USERIP_DATABASES_PATH
        from modules.utils import write_lines_to_file

        # Prompt the user for a username
        username, ok = QInputDialog.getText(self, "Input Username", f"Please enter the username to associate with the selected IP{pluralize(len(ip_addresses))}:")

        if ok and username:  # Only proceed if the user clicked 'OK' and provided a username
            # Append the username and associated IP(s) to the corresponding database file
            write_lines_to_file(selected_database, "a", [f"{username}={ip}\n" for ip in ip_addresses])

            QMessageBox.information(self, TITLE, f'Selected IP{pluralize(len(ip_addresses))} {ip_addresses} has been added with username "{username}" to UserIP database "{selected_database.relative_to(USERIP_DATABASES_PATH).with_suffix("")}".')
        else:
            # If the user canceled or left the input empty, show an error
            QMessageBox.warning(self, TITLE, "ERROR:\nNo username was provided.")

    def userip_manager__move(self, ip_addresses: list[str], selected_database: Path):
        from modules.constants.standard import RE_USERIP_INI_PARSER_PATTERN, USERIP_DATABASES_PATH
        from modules.utils import write_lines_to_file

        # Dictionary to store removed entries by database
        deleted_entries_by_database: dict[Path, list[str]] = {}

        # Iterate over each UserIP database
        for database_path in UserIPDatabases.get_userip_database_filepaths():
            if database_path == selected_database:
                continue

            # Read the database file
            lines = database_path.read_text(encoding="utf-8").splitlines(keepends=True)
            if not lines:
                continue

            # List to store deleted entries in this particular database
            deleted_entries_in_this_database: list[str] = []

            # Remove any lines containing the IP address
            lines_to_keep: list[str] = []
            for line in lines:
                match = RE_USERIP_INI_PARSER_PATTERN.search(line)
                if match:
                    # Extract username and ip using named groups
                    username, ip = match.group("username").strip(), match.group("ip").strip()

                    # Ensure both username and ip are non-empty strings
                    if isinstance(username, str) and isinstance(ip, str) and ip in ip_addresses:
                        deleted_entries_in_this_database.append(line.strip())  # Store the deleted entry
                        continue

                lines_to_keep.append(line)

            if deleted_entries_in_this_database:
                # Only update the database file if there were any deletions
                write_lines_to_file(database_path, "w", lines_to_keep)

                # Store the deleted entries for this database
                deleted_entries_by_database[database_path] = deleted_entries_in_this_database

                # Move the deleted entries to the target database
                write_lines_to_file(selected_database, "a", [f"{entry}\n" for entry in deleted_entries_in_this_database])

        # After processing all databases, show a detailed report
        if deleted_entries_by_database:
            report = f'<b>Selected IP{pluralize(len(ip_addresses))} {ip_addresses} moved from the following UserIP database{pluralize(len(deleted_entries_by_database))} to UserIP database "{selected_database.relative_to(USERIP_DATABASES_PATH).with_suffix("")}":</b><br><br><br>'
            for database_path, deleted_entries in deleted_entries_by_database.items():
                report += f"<b>{database_path.relative_to(USERIP_DATABASES_PATH).with_suffix("")}:</b><br>"
                report += "<ul>"
                for entry in deleted_entries:
                    report += f"<li>{entry}</li>"
                report += "</ul><br>"
            report = report.removesuffix("<br>")

            QMessageBox.information(self, TITLE, report)

    def userip_manager__del(self, ip_addresses: list[str]):
        from modules.constants.standard import RE_USERIP_INI_PARSER_PATTERN, USERIP_DATABASES_PATH
        from modules.utils import write_lines_to_file

        # Dictionary to store removed entries by database
        deleted_entries_by_database: dict[Path, list[str]] = {}

        # Iterate over each UserIP database
        for database_path in UserIPDatabases.get_userip_database_filepaths():
            # Read the database file
            lines = database_path.read_text(encoding="utf-8").splitlines(keepends=True)
            if not lines:
                continue

            # List to store deleted entries in this particular database
            deleted_entries_in_this_database: list[str] = []

            # Remove any lines containing the IP address
            lines_to_keep: list[str] = []
            for line in lines:
                match = RE_USERIP_INI_PARSER_PATTERN.search(line)
                if match:
                    # Extract username and ip using named groups
                    username, ip = match.group("username").strip(), match.group("ip").strip()

                    # Ensure both username and ip are non-empty strings
                    if isinstance(username, str) and isinstance(ip, str) and ip in ip_addresses:
                        deleted_entries_in_this_database.append(line.strip())  # Store the deleted entry
                        continue

                lines_to_keep.append(line)

            if deleted_entries_in_this_database:
                # Only update the database file if there were any deletions
                write_lines_to_file(database_path, "w", lines_to_keep)

                # Store the deleted entries for this database
                deleted_entries_by_database[database_path] = deleted_entries_in_this_database

        # After processing all databases, show a detailed report
        if deleted_entries_by_database:
            report = f"<b>Selected IP{pluralize(len(ip_addresses))} {ip_addresses} removed from the following UserIP database{pluralize(len(deleted_entries_by_database))}:</b><br><br><br>"
            for database_path, deleted_entries in deleted_entries_by_database.items():
                report += f"<b>{database_path.relative_to(USERIP_DATABASES_PATH).with_suffix("")}:</b><br>"
                report += "<ul>"
                for entry in deleted_entries:
                    report += f"<li>{entry}</li>"
                report += "</ul><br>"
            report = report.removesuffix("<br>")

            QMessageBox.information(self, TITLE, report)

    def _select_all_cells_helper(self, *, select: bool):
        """Helper function to select or deselect all cells in the table.

        Args:
            select: If True, select all cells; if False, deselect them.
        """
        selected_model = self.model()
        if not isinstance(selected_model, SessionTableModel):
            raise TypeError(f'Expected "SessionTableModel", got "{type(selected_model).__name__}"')

        selection_model = self.selectionModel()
        if not isinstance(selection_model, QItemSelectionModel):
            raise TypeError(f'Expected "QItemSelectionModel", got "{type(selection_model).__name__}"')

        # Get the top-left and bottom-right QModelIndex for the entire table
        top_left = selected_model.createIndex(0, 0)  # Top-left item (first row, first column)
        bottom_right = selected_model.createIndex(
            selected_model.rowCount() - 1, selected_model.columnCount() - 1,
        )  # Bottom-right item (last row, last column)

        # Create a selection range from top-left to bottom-right
        selection = QItemSelection(top_left, bottom_right)

        # Use the appropriate selection flag based on the `select` argument
        flag = QItemSelectionModel.SelectionFlag.Select if select else QItemSelectionModel.SelectionFlag.Deselect
        selection_model.select(selection, flag)

    def select_all_cells(self):
        """Select all cells in the table."""
        self._select_all_cells_helper(select=True)

    def unselect_all_cells(self):
        """Unselect all cells in the table."""
        self._select_all_cells_helper(select=False)

    def _select_row_cells_helper(self, row: int, *, select: bool):
        """Helper function to select or unselect all cells in a specific row.

        Args:
            row: The index of the row to modify selection.
            select: If True, select the row; if False, unselect it.
        """
        selected_model = self.model()
        if not isinstance(selected_model, SessionTableModel):
            raise TypeError(f'Expected "SessionTableModel", got "{type(selected_model).__name__}"')

        selection_model = self.selectionModel()
        if not isinstance(selection_model, QItemSelectionModel):
            raise TypeError(f'Expected "QItemSelectionModel", got "{type(selection_model).__name__}"')

        top_index = selected_model.createIndex(row, 0)  # First column of the specified row
        bottom_index = selected_model.createIndex(row, selected_model.columnCount() - 1)  # Last column of the specified row

        # Create a selection range for the entire row
        selection = QItemSelection(top_index, bottom_index)

        # Use the appropriate selection flag based on the `select` argument
        flag = QItemSelectionModel.SelectionFlag.Select if select else QItemSelectionModel.SelectionFlag.Deselect
        selection_model.select(selection, flag)

    def select_row_cells(self, row: int):
        """Select all cells in the specified row."""
        self._select_row_cells_helper(row, select=True)

    def unselect_row_cells(self, row: int):
        """Unselect all cells in the specified row."""
        self._select_row_cells_helper(row, select=False)

    def _select_column_cells_helper(self, column: int, *, select: bool):
        """Helper function to select or unselect all cells in a given column.

        Args:
            column: The index of the column to modify selection.
            select: If True, select the column; if False, unselect it.
        """
        selected_model = self.model()
        if not isinstance(selected_model, SessionTableModel):
            raise TypeError(f'Expected "SessionTableModel", got "{type(selected_model).__name__}"')

        selection_model = self.selectionModel()
        if not isinstance(selection_model, QItemSelectionModel):
            raise TypeError(f'Expected "QItemSelectionModel", got "{type(selection_model).__name__}"')

        top_index = selected_model.createIndex(0, column)  # First row of the specified column
        bottom_index = selected_model.createIndex(selected_model.rowCount() - 1, column)  # Last row of the specified column

        # Create a selection range for the entire column
        selection = QItemSelection(top_index, bottom_index)

        # Use the appropriate selection flag based on the `select` argument
        flag = QItemSelectionModel.SelectionFlag.Select if select else QItemSelectionModel.SelectionFlag.Deselect
        selection_model.select(selection, flag)

    def select_column_cells(self, column: int):
        """Select all cells in the specified column."""
        self._select_column_cells_helper(column, select=True)

    def unselect_column_cells(self, column: int):
        """Unselect all cells in the specified column."""
        self._select_column_cells_helper(column, select=False)


class GUIWorkerThread(QThread):
    update_signal = pyqtSignal(
        str,
        list,
        list,
        int,
        list,
        list,
        int,
    )  # Signal to send updated table data and new size

    def __init__(
        self,
        connected_table_model: SessionTableModel,
        connected_table_view: SessionTableView,
        disconnected_table_model: SessionTableModel,
        disconnected_table_view: SessionTableView,
    ):
        super().__init__()

        self.connected_table_model = connected_table_model
        self.connected_table_view = connected_table_view
        self.disconnected_table_model = disconnected_table_model
        self.disconnected_table_view = disconnected_table_view

    def run(self):
        # While the GUI is not closed, we repeat this loop
        while not gui_closed__event.is_set():
            # Retrieve the sorted column for both tables
            GUIrenderingData.session_connected_sorted_column_name, GUIrenderingData.session_connected_sort_order = self.connected_table_view.get_sorted_column()
            GUIrenderingData.session_disconnected_sorted_column_name, GUIrenderingData.session_disconnected_sort_order = self.disconnected_table_view.get_sorted_column()

            # Wait for the gui_rendering data to be ready (timeout of 0.1 second)
            # If the event is not set within the timeout, just continue
            if not GUIrenderingData.gui_rendering_ready_event.wait(timeout=0.1):
                continue
            GUIrenderingData.gui_rendering_ready_event.clear()

            self.update_signal.emit(
                GUIrenderingData.header_text,
                GUIrenderingData.session_connected_table__processed_data,
                GUIrenderingData.session_connected_table__compiled_colors,
                GUIrenderingData.session_connected_table__num_rows,
                GUIrenderingData.session_disconnected_table__processed_data,
                GUIrenderingData.session_disconnected_table__compiled_colors,
                GUIrenderingData.session_disconnected_table__num_rows,
            )


class MainWindow(QMainWindow):
    def __init__(self, screen_width: int, screen_height: int):
        super().__init__()

        from modules.guis.utils import resize_window_for_screen

        # Set up the window
        self.setWindowTitle(f"{TITLE}")
        # Set a minimum size for the window
        self.setMinimumSize(800, 600)
        resize_window_for_screen(self, screen_width, screen_height)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout for the central widget
        self.main_layout = QVBoxLayout(central_widget)

        # Header text
        self.header_text = QLabel()
        self.header_text.setTextFormat(Qt.TextFormat.RichText)
        self.header_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_text.setWordWrap(True)
        self.header_text.setFont(QFont("Courier", 10, QFont.Weight.Bold))

        # Custom header for the Session Connected table with matching background as first column
        self.session_connected_header = QLabel("Players connected in your session (0):")
        self.session_connected_header.setTextFormat(Qt.TextFormat.RichText)
        self.session_connected_header.setStyleSheet("background-color: green; color: white; font-size: 16px; font-weight: bold; padding: 5px;")
        self.session_connected_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_connected_header.setFont(QFont("Courier", 9, QFont.Weight.Bold))

        # Create the table model and view
        while not GUIrenderingData.GUI_CONNECTED_PLAYERS_TABLE__FIELD_NAMES:  # Wait for the GUI rendering data to be ready
            gui_closed__event.wait(0.1)
        # Determine the sort order
        _sort_column = GUIrenderingData.GUI_CONNECTED_PLAYERS_TABLE__FIELD_NAMES.index(Settings.GUI_FIELD_CONNECTED_PLAYERS_SORTED_BY)
        _sort_order = Qt.SortOrder.DescendingOrder
        self.connected_table_model = SessionTableModel(GUIrenderingData.GUI_CONNECTED_PLAYERS_TABLE__FIELD_NAMES)
        self.connected_table_view = SessionTableView(self.connected_table_model, _sort_column, _sort_order)
        del _sort_column, _sort_order
        self.connected_table_model.set_view(self.connected_table_view)

        # Add a horizontal line separator
        self.tables_separator = QFrame(self)
        self.tables_separator.setFrameShape(QFrame.Shape.HLine)
        self.tables_separator.setFrameShadow(QFrame.Shadow.Sunken)  # Optional shadow effect

        # Custom header for the Session Disconnected table with matching background as first column
        self.session_disconnected_header = QLabel("Players who've left your session (0):")
        self.session_disconnected_header.setTextFormat(Qt.TextFormat.RichText)
        self.session_disconnected_header.setStyleSheet("background-color: red; color: white; font-size: 16px; font-weight: bold; padding: 5px;")
        self.session_disconnected_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_disconnected_header.setFont(QFont("Courier", 9, QFont.Weight.Bold))

        # Create the table model and view
        while not GUIrenderingData.GUI_DISCONNECTED_PLAYERS_TABLE__FIELD_NAMES:  # Wait for the GUI rendering data to be ready
            gui_closed__event.wait(0.1)
        # Determine the sort order
        _sort_column = GUIrenderingData.GUI_DISCONNECTED_PLAYERS_TABLE__FIELD_NAMES.index(Settings.GUI_FIELD_DISCONNECTED_PLAYERS_SORTED_BY)
        if Settings.GUI_FIELD_DISCONNECTED_PLAYERS_SORTED_BY in {"Last Rejoin", "Last Seen"}:
            _sort_order = Qt.SortOrder.AscendingOrder
        else:
            _sort_order = Qt.SortOrder.DescendingOrder
        self.disconnected_table_model = SessionTableModel(GUIrenderingData.GUI_DISCONNECTED_PLAYERS_TABLE__FIELD_NAMES)
        self.disconnected_table_view = SessionTableView(self.disconnected_table_model, _sort_column, _sort_order)
        del _sort_column, _sort_order
        self.disconnected_table_model.set_view(self.disconnected_table_view)

        # Layout to organize the widgets
        self.main_layout.addWidget(self.header_text)
        self.main_layout.addWidget(self.session_connected_header)
        self.main_layout.addWidget(self.connected_table_view)
        self.main_layout.addWidget(self.tables_separator)
        self.main_layout.addWidget(self.session_disconnected_header)
        self.main_layout.addWidget(self.disconnected_table_view)

        # Raise and activate window to ensure it gets focus
        self.raise_()
        self.activateWindow()

        # Create the worker thread for table updates
        self.worker_thread = GUIWorkerThread(
            self.connected_table_model,
            self.connected_table_view,
            self.disconnected_table_model,
            self.disconnected_table_view,
        )
        self.worker_thread.update_signal.connect(self.update_gui)
        self.worker_thread.start()

    def closeEvent(self, event: QCloseEvent):  # pylint: disable=invalid-name  # noqa: N802
        gui_closed__event.set()  # Signal the thread to stop
        self.worker_thread.quit()  # Stop the QThread
        self.worker_thread.wait()  # Wait for the thread to finish

        event.accept()  # Accept the close event

        terminate_script("EXIT")

    # Custom Methods:

    def update_gui(
        self,
        header_text: str,
        session_connected_table__processed_data: list[list[str]],
        session_connected_table__compiled_colors: list[list[CellColor]],
        session_connected_table__num_rows: int,
        session_disconnected_table__processed_data: list[list[str]],
        session_disconnected_table__compiled_colors: list[list[CellColor]],
        session_disconnected_table__num_rows: int,
    ):
        """Update header text and table data for connected and disconnected players."""
        self.header_text.setText(header_text)

        self.session_connected_header.setText(f"Players connected in your session ({session_connected_table__num_rows}):")

        for processed_data, compiled_colors in zip(session_connected_table__processed_data, session_connected_table__compiled_colors, strict=True):
            ip = processed_data[self.connected_table_model.IP_COLUMN_INDEX].removesuffix(" 👑")

            disconnected_row_index = self.disconnected_table_model.get_row_index_by_ip(ip)
            if disconnected_row_index is not None:
                self.disconnected_table_model.delete_row(disconnected_row_index)

            connected_row_index = self.connected_table_model.get_row_index_by_ip(ip)
            if connected_row_index is None:
                self.connected_table_model.add_row_without_refresh(processed_data, compiled_colors)
            else:
                self.connected_table_model.update_row_without_refresh(connected_row_index, processed_data, compiled_colors)

        self.connected_table_model.sort_current_column()
        self.connected_table_view.adjust_table_column_widths()

        self.session_disconnected_header.setText(f"Players who've left your session ({session_disconnected_table__num_rows}):")

        for processed_data, compiled_colors in zip(session_disconnected_table__processed_data, session_disconnected_table__compiled_colors, strict=True):
            ip = processed_data[self.disconnected_table_model.IP_COLUMN_INDEX].removesuffix(" 👑")

            connected_row_index = self.connected_table_model.get_row_index_by_ip(ip)
            if connected_row_index is not None:
                self.connected_table_model.delete_row(connected_row_index)

            disconnected_row_index = self.disconnected_table_model.get_row_index_by_ip(ip)
            if disconnected_row_index is None:
                self.disconnected_table_model.add_row_without_refresh(processed_data, compiled_colors)
            else:
                self.disconnected_table_model.update_row_without_refresh(disconnected_row_index, processed_data, compiled_colors)

        self.disconnected_table_model.sort_current_column()
        self.disconnected_table_view.adjust_table_column_widths()


class ClickableLabel(QLabel):
    clicked = pyqtSignal()  # Custom signal

    def mousePressEvent(self, event: QMouseEvent):  # pylint: disable=invalid-name  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()  # Emit the signal when clicked


class DiscordIntro(QDialog):
    def __init__(self):
        super().__init__()

        # Ensure the dialog is modal, blocking interaction with the main window
        self.setModal(True)

        WINDOW_TITLE = "🏆 Join our Discord Community! 🤝"

        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(460, 160)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.Dialog)  # | Qt.WindowType.WindowStaysOnTopHint

        # Set window opacity to 0 for fade-in animation
        self.setWindowOpacity(0)

        # Styling for the main container window
        self.setStyleSheet("""
            background-color: #222244;  /* Dark blueish background */
            border-radius: 15px;        /* Rounded corners */
            color: white;
        """)

        self.fade_out = QPropertyAnimation(self, b"windowOpacity")

        # Exit button in the top right corner
        self.exit_button = QPushButton("x", self)
        self.exit_button.setFixedSize(16, 16)  # Make the width and height equal
        self.exit_button.setStyleSheet("""
            font-size: 10px;
            color: white;
            background-color: #FF4C4C;  /* Light red background */
            border-radius: 15px;        /* Make it circular */
        """)
        self.exit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_button.clicked.connect(self.close_popup)

        # Layout for the window content
        layout = QVBoxLayout()

        # Add the exit button to the top right
        exit_layout = QHBoxLayout()
        exit_layout.addStretch(1)  # Spacer
        exit_layout.addWidget(self.exit_button)
        layout.addLayout(exit_layout)

        # Label for the Discord message
        self.title_label = QLabel(
            f"<font size='6' color='#5865F2'><b>{WINDOW_TITLE}</b></font>",
            self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.title_label)

        layout.addItem(QSpacerItem(0, 4, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))  # Spacer

        # Join button container
        self.join_button = QPushButton("🔥 Join Now - Session Sniffer Discord! 🔥", self)
        self.join_button.setStyleSheet("""
            font-size: 14px;
            padding: 7px;
            background-color: #5865F2;  /* Discord blue */
            color: white;
            border-radius: 10px;
            border: none;
        """)
        self.join_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.join_button.clicked.connect(self.open_discord)

        # Set button width to 75% of the window width
        self.join_button.setMaximumWidth(int(self.width() * 0.75))

        # Center the button horizontally using a layout
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # Spacer before the button
        button_layout.addWidget(self.join_button)
        button_layout.addStretch(1)  # Spacer after the button

        layout.addLayout(button_layout)  # Add the button layout to the main layout

        # Clickable text "Don't remind me again"
        self.dont_remind_me_label = ClickableLabel("<font size='3' color='#B0B0B0'><u>Don't remind me again</u></font>", self)
        self.dont_remind_me_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dont_remind_me_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dont_remind_me_label.clicked.connect(self.dont_remind_me)

        layout.addItem(QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))  # Spacer
        layout.addWidget(self.dont_remind_me_label)

        # Apply margin here to adjust widget spacing
        layout.setContentsMargins(10, 10, 10, 10)  # Add margin to the layout

        # Set the main layout of the window
        self.setLayout(layout)

        # Show the window to allow size calculations
        self.show()

        # After the window is shown, center it
        self.center_window()

        # Fade-in animation
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(1000)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_in.start()

        # Raise and activate window to ensure it gets focus
        self.raise_()
        self.activateWindow()

        # Initialize variables to track mouse position
        self._drag_pos = None

    # pylint: disable=invalid-name
    def mousePressEvent(self, event: QMouseEvent):  # noqa: N802
        if (
            event.button() == Qt.MouseButton.LeftButton
            and not self.exit_button.underMouse() and not self.join_button.underMouse() and not self.dont_remind_me_label.underMouse()  # Only allow dragging if the click is not on a button
        ):
            self._drag_pos = event.globalPosition().toPoint()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):  # noqa: N802
        if self._drag_pos is not None:  # If mouse is pressed, move the window
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):  # noqa: N802
        self._drag_pos = None  # Reset drag position when mouse is released

        super().mouseReleaseEvent(event)
    # pylint: enable=invalid-name

    def center_window(self):
        screen = QApplication.primaryScreen()
        if screen is None:
            raise RuntimeError("No primary screen detected.")

        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def open_discord(self):
        from modules.constants.standalone import DISCORD_INVITE_URL

        webbrowser.open(DISCORD_INVITE_URL)

        Settings.SHOW_DISCORD_POPUP = False
        Settings.reconstruct_settings()

        self.close_popup()

    def dont_remind_me(self):
        Settings.SHOW_DISCORD_POPUP = False
        Settings.reconstruct_settings()

        self.close_popup()

    def close_popup(self):
        # Smooth fade-out before closing
        self.fade_out.setDuration(500)
        self.fade_out.setStartValue(1)  # Start from fully opaque
        self.fade_out.setEndValue(0)    # Fade to fully transparent
        self.fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out.finished.connect(self.close)  # Close the window after the fade-out finishes
        self.fade_out.start()


if __name__ == "__main__":
    # Initialize the main application
    window = MainWindow(screen_width, screen_height)
    window.show()

    if Settings.SHOW_DISCORD_POPUP:
        # Delay the popup opening by 3 seconds
        QTimer.singleShot(3000, lambda: DiscordIntro().exec())

    # Start the application's event loop
    sys.exit(app.exec())
