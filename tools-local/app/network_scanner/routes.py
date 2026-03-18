from fastapi import APIRouter, Query

from app.network_scanner.scanner import NetworkScanner
from app.network_scanner.ping import PingTester
from app.network_scanner.speedtest_runner import SpeedTestRunner

router = APIRouter(prefix="/api/network-scanner")


@router.post("/scan")
async def scan_network():
    devices = NetworkScanner.scan_devices()
    return {"devices": devices}


@router.get("/ping")
async def ping_host(host: str = Query("8.8.8.8")):
    output = PingTester.ping(host)
    return {"output": output}


@router.post("/speedtest")
async def run_speedtest():
    return SpeedTestRunner.run()
