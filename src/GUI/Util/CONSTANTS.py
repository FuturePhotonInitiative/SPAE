import wx
from os.path import dirname, join, abspath


MAIN_PAGE_TITLE = "PIC Test Control Software"
PAGE_SIZE = (900, 500)
QUEUE_PAGE_NAME = "Queue"
HARDWARE_PAGE_NAME = "Hardware"
BUILD_EXPERIMENTS_PAGE_NAME = "Build"
RESULTS_PAGE_NAME = "Results"
TEST_BUILD_PAGE_NAME = "Build Test"
SPACE_SIZE = 4

QUEUE_PANEL_PROPORTION = 1
QUEUE_CONTROL_PANEL_PROPORTION = 2

HARDWARE_PANEL_PROPORTION = 1
HARDWARE_CONTROL_PANEL_PROPORTION = 1

BUILD_PANEL_PROPORTION = 3
BUILD_SCRIPT_PANEL_PROPORTION = 1

RESULTS_EXPERIMENT_PANEL_PROPORTION = 1
RESULTS_FILE_PANEL_PROPORTION = 1

TEST_BUILD_PANEL_PROPORTION = 1
TEST_BUTTON_PANEL_PROPORTION = 3

TEST_BUILD_PANEL_COLOR = wx.Colour(255, 200, 100)
TEST_BUILD_PANEL_FOREGROUND_COLOR = wx.Colour(0, 0, 0)

LIST_PANEL_COLOR = wx.Colour(50, 50, 50)
LIST_PANEL_FOREGROUND_COLOR = wx.WHITE#wx.Colour(100, 100, 100)

CONTROL_PANEL_COLOR = wx.WHITE
CONTROL_PANEL_FOREGROUND_COLOR = wx.BLACK#wx.Colour(100, 100, 100)

LABEL_PROPORTION = .1

# directories of interest
PROJ_DIR = dirname(dirname(dirname(dirname(abspath(__file__)))))
TEMP_DIR = join(join(PROJ_DIR, "System"), "temp")
CONFIGS = join(PROJ_DIR, "Configs")
SCRIPTS_DIR = join(join(PROJ_DIR, "src"), "Scripts")
SAVED_EXPERIMENTS_DIR = join(PROJ_DIR, "Saved_Experiments")
DRIVERS_DIR = join(join(PROJ_DIR, "src"), "Instruments")
RESULTS_DIR = join(PROJ_DIR, "Results")
DEVICES_CONFIG = join(join(PROJ_DIR, "System"), "Devices.json")
RESULTS_CONFIG_DIR = join(join(PROJ_DIR, "System"), "ResultsConfiguration")
JSON_SCHEMA_FILE_NAME = join(join(PROJ_DIR, "System"), "ConfigFileValidationSchema.json")
CUSTOM_TESTS_DIR = join(PROJ_DIR, "Custom_Tests")

VIVADO_LOCATION = "C:/Xilinx/Vivado/2017.4/bin/vivado"

EXPERIMENT_QUEUE_RESULT_ROOT = "Experiment Queues"

QUEUE_FILE_TITLE = "queue_result"
