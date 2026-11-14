@echo off
echo ================================================================
echo Particle Cosmos - FULL .geo Physics Simulation
echo ================================================================
echo.
echo ALL physics calculations are done by .geo scripts:
echo   - F = G*m1*m2/r^2 (gravitational attraction)
echo   - Like-charge boost (2.5x stronger)
echo   - Fusion with E=mc^2 flare
echo   - Black hole formation
echo   - Velocity damping
echo.
echo Python ONLY handles:
echo   - Rendering
echo   - User input
echo   - Grid management
echo.
echo Controls:
echo   Left Click  - Add particle
echo   Right Click - Add black hole
echo   Space       - Pause/Resume
echo   C           - Clear all
echo   S           - Spawn solar system
echo   Esc         - Quit
echo.
echo Starting .geo physics simulation...
echo.
cd /d "%~dp0\..\.."
python examples\cosmos\particle_cosmos.py
pause
