@echo off
REM Serve the dashboard in a browser. Open http://localhost:8080/dashboard.html on the VPS.
REM For remote access, open port 8080 in the Azure Network Security Group, then use http://VPS_IP:8080/dashboard.html
cd /d "%~dp0"
echo Dashboard at http://localhost:8080/dashboard.html  (Ctrl+C to stop)
python -m http.server 8080
