import configparser
import logging
import os
from escpos.printer import Serial
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
logging.basicConfig(level=logging.DEBUG, filename="logs/fastapi.log")

logger = logging.getLogger(__name__)

CONFIG_FILE_NAME = 'config.ini'
COMMAND_TEXT = "text"
COMMAND_CUT = "cut"
COMMAND_FEED = "feed"
COMMAND_BARCODE = "barcode"

DEFAULT_PRINTER_BAUDRATE = 19200
DEFAULT_PRINTER_RATELIMIT = 5000

PRINTER_BAUDRATE = DEFAULT_PRINTER_BAUDRATE
PRINTER_RATELIMIT = DEFAULT_PRINTER_RATELIMIT

# load config
config = configparser.ConfigParser()
config["printer"] = {}
config.read(CONFIG_FILE_NAME)
PRINTER_BAUDRATE = config["printer"]["baudrate"]
if "printer" in config:
    if "baudrate" in config["printer"]: PRINTER_BAUDRATE = config["printer"]["baudrate"]
    if "ratelimit" in config["printer"]: PRINTER_RATELIMIT = config["printer"]["ratelimit"]

# REST API models
class Style(BaseModel):
    double_height: bool | None = False
    double_width: bool | None = False
    bold: bool | None = False
    align: str | None = "left"
    underline: bool | None = False

class Command(BaseModel):
    type: str | None = None
    content: str | None = None
    style: int | None = None

class PrintJob(BaseModel):
    styles: list[Style] | None = None
    commands: list[Command] | None = None

def get_printer():
    # works on linux
    for file_name in os.listdir("/dev"):
        if file_name.startswith("ttyUSB"):
            file_path = f"/dev/{file_name}"
            return Serial(file_path, baudrate=PRINTER_BAUDRATE)
    return None

def print_error_message(e: Exception):
    p = get_printer()
    p.textln("------------")
    p.textln("!! ERROR !!")
    p.textln(e.message)
    p.textln("------------")

# define api
app = FastAPI()

@app.get("/api")
def get_root():
    return {"Hello": "World"}

@app.post("/api/print")
def post_job(job: PrintJob):
    p = get_printer()
    if p is None:
        raise HTTPException(status_code=500, detail="Unable to connect to the printer.") 

    try:
        style_index = -1
        for command in job.commands:
            if command.type == COMMAND_TEXT: 
                if command.style != style_index and style_index < len(job.styles):
                    style_index = command.style
                    style = job.styles[style_index]
                    p.set_with_default(
                        align=style.align,
                        double_height=style.double_height,
                        double_width=style.double_width,
                        bold=style.bold,
                        underline=style.underline)
                p.textln(command.content[:PRINTER_RATELIMIT])
            elif command.type == COMMAND_FEED: 
                p.feed(5)
            elif command.type == COMMAND_CUT:
                p.cut()
            elif command.type == COMMAND_BARCODE:
                p.barcode(command.content, "UPC-A")
            
    except Exception as e:
        print("Uh oh, had an error")
        print(e.message)
        p.textln("!! ERROR !!")

app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

logger.info("API Initialised.")